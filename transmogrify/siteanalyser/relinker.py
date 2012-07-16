
from zope.interface import implements
from zope.interface import classProvides
from zope.component import queryUtility
from plone.i18n.normalizer.interfaces import IURLNormalizer

from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
import urllib
from lxml import etree
import lxml
from urlparse import urljoin
import urllib
from external.relative_url import relative_url
from sys import stderr
from collective.transmogrifier.utils import Expression
import logging
from external.normalize import urlnormalizer as normalizer
import urlparse
from sys import stderr
#from plone.i18n.normalizer import urlnormalizer as normalizer



class Relinker(object):
    classProvides(ISectionBlueprint)
    implements(ISection)
    
    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.name = name
        self.logger = logging.getLogger(name)

    def __iter__(self):
        
        #TODO need to fix relative links
        

        changes = {}
        bad = {}
        
        self.missing = set([])
        
        for item in self.previous:
            path = item.get('_path',None)
            if path is None:
                url = item.get('_bad_url')
                if url:
                    bad[url] = item
                yield item
                continue
            base = item.get('_site_url','')

            origin = item.get('_origin')
            if not origin:
                origin = item['_origin'] = path
            link = urllib.unquote_plus(base+origin)

            changes[link] = item
            self.logger.debug("%s <- %s (relinked)" % (path, origin))

        for item in changes.values():
            if '_defaultpage' in item:
                index = item['_site_url'] + item['_origin'] + '/' + item['_defaultpage']
                newindex = changes.get(index)
                #need to work out if the new index is still in this folder
                if newindex is not None:
                    # is the parent of our indexpage still 'item'?
                    indexparentpath = '/'.join(newindex['_path'].split('/')[:-1])
                    indexparent = changes.get(newindex['_site_url'] + indexparentpath)
                    if indexparent == item:
                        newindexid = newindex['_path'].split('/')[-1]
                        item['_defaultpage'] = newindexid
                        self.logger.debug("'%s' default page stay" % (item['_path']))
                    else:
                        import pdb; pdb.set_trace()
                else:
                    # why was it set then?? #TODO
                    # index moved elsewhere so defaultpage setting is off
                    del item['_defaultpage']
                    self.logger.debug("'%s' default page remove" % (item['_path']))

            if item.get('_mimetype') in ['text/xhtml', 'text/html']:
                self.relinkHTML(item, changes, bad)

            del item['_origin']
            #rewrite the backlinks too
            backlinks = item.get('_backlinks',[])
            newbacklinks = []
            for origin,name in backlinks:
                #assume absolute urls
                backlinked= changes.get(origin)
                if backlinked:
                    backlink = backlinked['_site_url']+backlinked['_path']
                    newbacklinks.append((backlink,name))
                else:
                    newbacklinks.append((origin,name))
            if backlinks:
                item['_backlinks'] = newbacklinks
    
            yield item
        if self.missing:
            self.logger.warning("%d broken internal links. Content maybe missing. Debug to see details." % len(self.missing) )


    def relinkHTML(self, item, changes, bad={}):        
        path = item['_path']
        oldbase = item['_site_url']+item['_origin']
        newbase = item['_site_url']+path
        def swapfragment(link, newfragment):
            t = urlparse.urlparse(link)
            fragment = t[-1]
            t = t[:-1] + (newfragment,)
            link = urlparse.urlunparse(t)
            return link, fragment

        counter = 0

        def replace(link):
            link, fragment = swapfragment(link, '')
    
            linked = changes.get(link)
            if not linked:
                linked = changes.get(urllib.unquote_plus(link))
                
            if linked:
                linkedurl = item['_site_url']+linked['_path']
                newlink = swapfragment(relative_url(newbase, linkedurl), fragment)[0]
                counter += 1
            else:
                if link not in bad and link.startswith(item['_site_url']):
                    self.logger.debug("%s broken link '%s'" % (path, link))
                    self.missing.add(link)
                newlink = swapfragment(relative_url(newbase, link), fragment)[0]
            # need to strip out null chars as lxml spits the dummy
            newlink = ''.join([c for c in newlink if ord(c) > 32])
#            self.logger.debug("'%s' -> '%s'" %(link,newlink))
            return newlink

        # guess which fields are html by trying to parse them
        html = {}
        for key, value in item.items():
            if value is None:
                continue
            try:
                html[key] = lxml.html.fromstring(text)
            except:
                try:
                    html[key] = lxml.html.fragment_fromstring(text, create_parent=True)
                except:
                    pass

        for field, tree in html.items():
            old_counter = counter

            try:
                tree.rewrite_links(replace, base_href=oldbase)
            except:
                self.logger.error("Error rewriting links in %s" % item['_origin'])
                raise
                #import pdb; pdb.set_trace()
            # only update fields which had links in
            if counter != old_counter:
                item[field] = etree.tostring(tree, pretty_print=True, encoding=unicode, method='html')
        self.logger.debug("'%s' relinked %s links in %s" % (item['_path'], counter, html.keys()))

     #   except Exception:
     #       msg = "ERROR: relinker parse error %s, %s" % (path,str(Exception))
     #       logger.log(logging.ERROR, msg, exc_info=True)

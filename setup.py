from setuptools import setup, find_packages
import os
import re

version = '1.3'

def docstring(file):
    py = open(os.path.join("transmogrify", "siteanalyser", file)).read()
    return re.findall('"""(.*?)"""', py, re.DOTALL)[0]



setup(name='transmogrify.siteanalyser',
      version=version,
      description="transmogrifier source blueprints for crawling html",
      long_description=open('README.rst').read() +'\n' + \
                       docstring('sitemapper.py') + \
                       docstring('urltidy.py') + \
                       docstring('makeattachments.py') + \
                       docstring('backlinkstitle.py') + \
                       docstring('guesshidefromnav.py') + \
                       docstring('isindex.py') + \
                       docstring('relinker.py') + \
                       docstring('treeserializer.py') + \

#                       open(os.path.join("transmogrify", "siteanalyser", "isindex.txt")).read() + "\n" +
#                       open(os.path.join("transmogrify", "siteanalyser", "relinker.txt")).read() + "\n" +
#                       open(os.path.join("transmogrify", "siteanalyser", "makeattachments.txt")).read() + "\n" +
                       #open(os.path.join("transmogrify", "siteanalyser", "backlinkstitle.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='transmogrifier blueprint funnelweb source plone import conversion microsoft office',
      author='Dylan Jay',
      author_email='software@pretaweb.com',
      url='http://github.com/collective/transmogrify.siteanalyser',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['transmogrify'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'lxml',
          'BeautifulSoup',
          'collective.transmogrifier',
          ],
      entry_points="""
            [z3c.autoinclude.plugin]
            target = transmogrify
            """,
            )

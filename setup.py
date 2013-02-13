#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.command.install_egg_info import install_egg_info
from distutils.command.build import build
from distutils.versionpredicate import VersionPredicate
import time
import sys

class check_and_build( build ):
    def run(self):
        chk = True
        for req in require_pyt:
            chk &= self.chkpython(req)
        for req in require_mod:
            chk &= self.chkmodule(req)
        if not chk:
            sys.exit(1)
        build.run( self )

    def chkpython(self, req):
        chk = VersionPredicate(req)
        ver = '.'.join([str(v) for v in sys.version_info[:2]])
        if not chk.satisfied_by(ver):
            print >> sys.stderr, "Invalid python version, expected %s" % req
            return False
        return True

    def chkmodule(self, req):
        chk = VersionPredicate(req)
        try:
            mod = __import__(chk.name)
        except:
            print >> sys.stderr, "Missing mandatory %s python module" % chk.name
            return False
        for v in [ '__version__', 'version' ]:
            ver = getattr(mod, v, None)
            break
        try:
            if ver and not chk.satisfied_by(ver):
                print >> sys.stderr, "Invalid module version, expected %s" % req
                return False
        except:
            pass
        return True


require_pyt = [ 'python (>=2.7, <3.0)' ]
require_mod = []

setup(name        = 'mobyle.datamanager',
      version     =  time.strftime("%Y-%m-%d"),
      author      = "Olivier Sallou",
      author_email = "olivier.sallou@irisa.fr",
      license      = "GPLv3" ,
      url = "https://github.com/mobyle2/mobyle2.datamanager",
      download_url = "https://github.com/mobyle2/mobyle2.datamanager",
      description  = "common libraries to Mobyle2 project to manage datasets",
      classifiers = [
                     'License :: GPLv3' ,
                     'Operating System :: POSIX' ,
                     'Programming Language :: Python' ,
                     'Topic :: Bioinformatics' ,
                    ] ,
      packages    = ['mobyle' , 'mobyle.data', 'mobyle.data.manager'],
      package_dir = {'': '.'},
      cmdclass= { 'build' : check_and_build },
      entry_points = """\
      [paste.app_factory]
      main = mobyle.data.webmanager:main
      """,
      )


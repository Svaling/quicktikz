#!/usr/bin/env python3
#-*-coding:utf-8-*-

from setuptools import setup ,find_packages

setup(
  name='quicktikz',
  version='0.08',
  description='the software short description',
  url='https://github.com/a358003542/quicktikz',
  author='wanze',
  author_email='a358003542@gmail.com',
  maintainer = 'wanze',
  maintainer_email = 'a358003542@gmail.com',
  license='GPL 2',
  platforms = 'Linux',
  keywords =['quicktikz','python'],
  classifiers = ['Development Status :: 2 - Pre-Alpha',
  'Environment :: Console',
  'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
  'Operating System :: POSIX :: Linux',
  'Programming Language :: Python :: 3.4',],
  packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
  include_package_data=True,
  package_data = {"quicktikz":['main.ui','imageview.ui','template.ui',
    'options.ui','loginfo.ui'],},
#  install_requires=['click'],
#  setup_requires,
  entry_points = {
 # 'console_scripts' :[ 'quicktikz=quicktikz.main:console',],
  'gui_scripts':['quicktikz=quicktikz.main:gui'],
  }
)




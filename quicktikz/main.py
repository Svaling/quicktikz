#!/usr/bin/env python3
#-*-coding:utf-8-*-

import sys

#
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTranslator,QLocale

from quicktikz.gui import MainWindow

#
def gui():
    app = QApplication(sys.argv)

 #   translator = QTranslator()
 #   if translator.load('editor_'+ QLocale.system().name()+'.qm',":/translations/"):
 #       app.installTranslator(translator)
#
 #   translator_qt = QTranslator()
 #   if translator_qt.load('qt_'+ QLocale.system().name()+'.qm',":/translations/"):
  #      print('i found qt')
  #      app.installTranslator(translator_qt)


    mainwindow = MainWindow()
    mainwindow.setWindowTitle('drawing in tikz')
    mainwindow.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    gui()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import  *
from PyQt5.uic import loadUi


class MainWindow(QMainWindow):
    def __init__(self,parent=None, *args):
        super().__init__(parent, *args)

        self.curFile = ''
        self.dpi = 90

        self.mainUi = loadUi('main.ui', self)

        #中间窗体
        self.mainLayout = QHBoxLayout()
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget)
        self.textEdit = TextEdit()
        self.mainLayout.addWidget(self.textEdit)
        self.previewer = ImageView()
        self.mainLayout.addWidget(self.previewer)

#############preview
        self.mainUi.action_Compile.triggered.connect(self.compileFile)
        self.mainUi.action_ZoomIn.triggered.connect(self.zoomIn)

#######################editor
        self.mainUi.action_About.triggered.connect(self.about)
        self.mainUi.action_AboutQt.triggered.connect(QApplication.instance().aboutQt)
        self.mainUi.action_Quit.triggered.connect(self.close)

        ###
        self.textEdit.title_changed.connect(self.setCurrentFile)

        self.mainUi.action_New.triggered.connect(self.textEdit.newFile)
        self.mainUi.action_Open.triggered.connect(self.textEdit.openFile)

        self.mainUi.action_Save.triggered.connect(self.save)
        self.mainUi.action_SaveAs.triggered.connect(self.saveAs)

        self.mainUi.action_Cut.triggered.connect(self.textEdit.cut)
        self.mainUi.action_Copy.triggered.connect(self.textEdit.copy)
        self.mainUi.action_Paste.triggered.connect(self.textEdit.paste)


        self.getaction_Cut().setEnabled(False)
        self.getaction_Copy().setEnabled(False)
        self.textEdit.copyAvailable.connect(self.getaction_Cut().setEnabled)
        self.textEdit.copyAvailable.connect(self.getaction_Copy().setEnabled)

        self.statusBar().showMessage(self.tr("Ready..."))

        self.readSettings()

        self.textEdit.textChanged.connect(self.setWindowModified)

        self.setCurrentFile('')

    @pyqtSlot()
    def compileFile(self):
        self.dpi = 90
        self.save()
        import os
        import subprocess
        fileName, fileExt = os.path.splitext(self.curFile)


        subprocess.call(['xelatex','-synctex=1',
        '--enable-write18','-interaction=nonstopmode',self.curFile])

        subprocess.call(['wiseimage','-c','png','-d',str(self.dpi),fileName+'.pdf'])

        self.previewer.loadImage(fileName+'.png')

    @pyqtSlot()
    def zoomIn(self):
        self.dpi += 10
        self.save()
        import os
        import subprocess
        fileName, fileExt = os.path.splitext(self.curFile)

        subprocess.call(['xelatex','-synctex=1',
        '-interaction=nonstopmode','--enable-write18',self.curFile])

        subprocess.call(['wiseimage','-c','png','-d',str(self.dpi),fileName+'.pdf'])

        self.previewer.loadImage(fileName+'.png')





    @pyqtSlot()
    def closeEvent(self, event):
        if self.maybeSave():
            self.writeSettings()
            event.accept()
        else:
            event.ignore()

    @pyqtSlot()
    def about(self):
        QMessageBox.about(self, self.tr("About Application"),
                self.tr("The <b>Application</b> example demonstrates how to write "
                "modern GUI applications using Qt, with a menu bar, "
                "toolbars, and a status bar."))

    @pyqtSlot()
    def save(self):
        if self.curFile:
            return self.textEdit.saveFile(self.curFile)
        return self.saveAs()

    @pyqtSlot()
    def saveAs(self):
        fileName, _ = QFileDialog.getSaveFileName(self)
        if fileName:
            return self.textEdit.saveFile(fileName)

    def readSettings(self):
        settings = QSettings("QuickTikz", "quicktikz")
        pos = settings.value("pos", QPoint(200, 200))
        size = settings.value("size", QSize(400, 400))
        self.resize(size)
        self.move(pos)

    def writeSettings(self):
        settings = QSettings("QuickTikz", "quicktikz")
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())


    def setCurrentFile(self, fileName):
        print('title changed')
        self.curFile = fileName
        self.textEdit.setModified(False)
        if self.curFile:
            shownName = self.strippedName(self.curFile)
        else:
            shownName = 'untitled.txt'
        self.setWindowTitle("%s-Application" % shownName)


    def setWindowModified(self):
        if self.curFile:
            shownName = self.strippedName(self.curFile)
        else:
            shownName = 'untitled.txt'
        self.setWindowTitle("-*-%s-Application" % shownName)

    def strippedName(self, fullFileName):
        return QFileInfo(fullFileName).fileName()

########################################
    def getaction_New(self):
        return self.mainUi.action_New
    def getaction_Cut(self):
        return self.mainUi.action_Cut
    def getaction_Copy(self):
        return self.mainUi.action_Copy



############################
from PyQt5.Qsci import QsciScintilla
class TextEdit(QsciScintilla):
    title_changed = pyqtSignal(str)

    def __init__(self,parent=None):
        super().__init__(parent)

        self.setUtf8(True)


    @pyqtSlot()
    def newFile(self):
        if self.maybeSave():
            self.clear()
            self.title_changed.emit('')

    def maybeSave(self):
        if self.isModified():
            ret = QMessageBox.warning(self, self.tr("Application"),
                    self.tr('''The document has been modified.
                    Do you want to save your changes?'''),
                    QMessageBox.Save | QMessageBox.Discard \
                    | QMessageBox.Cancel)

            if ret == QMessageBox.Save:
                return self.save()

            if ret == QMessageBox.Cancel:
                return False

        return True

    @pyqtSlot()
    def openFile(self):
        if self.maybeSave():
            fileName, _ = QFileDialog.getOpenFileName(self)
            if fileName:
                self.loadFile(fileName)

    def loadFile(self, fileName):
        file = QFile(fileName)
        if not file.open(QIODevice.ReadOnly | QIODevice.Text):
            QMessageBox.warning(self, self.tr("Application"),
                    self.tr("Cannot read file %s:\n%s." % (fileName, file.errorString())) )
            return

        inf = QTextStream(file)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.setText(inf.readAll())
        QApplication.restoreOverrideCursor()

        self.title_changed.emit(fileName)

    def saveFile(self, fileName):
        file = QFile(fileName)
        if not file.open(QIODevice.WriteOnly | QIODevice.Text):
            QMessageBox.warning(self, "Application",
                    "Cannot write file %s:\n%s." % (fileName, file.errorString()))
            return False

        outf = QTextStream(file)
        QApplication.setOverrideCursor(Qt.WaitCursor)
        outf << self.text()
        QApplication.restoreOverrideCursor()

        self.title_changed.emit(fileName);


##############################预览面板
class ImageView(QWidget):
    def __init__(self,parent=None, *args):

        super().__init__(parent, *args)

        self.mainUi = loadUi('imageview.ui', self)

        self.scene = QGraphicsScene()
        self.mainUi.graphicsView.setScene(self.scene)

    def loadImage(self,filename):

        pic = QPixmap(filename)
        self.scene.addItem(QGraphicsPixmapItem(pic))





#if __name__ == '__main__':
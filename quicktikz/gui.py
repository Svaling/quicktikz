#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import  *
from PyQt5.uic import loadUi

from quicktikz import main_rc
import os

def ui_path(module,uiname):
    from pkg_resources import resource_filename
    uifile_path = resource_filename(module,uiname)
    return uifile_path

default_template = r'''% !Mode:: "TeX:UTF-8"%確保文檔utf-8編碼
\documentclass[tikz,border=2pt]{standalone}
\usepackage{fontspec}
\usepackage{xeCJK}
\setCJKmainfont[BoldFont=Adobe 黑体 Std,
ItalicFont=Adobe 楷体 Std]{Adobe 宋体 Std}
\setCJKsansfont{Adobe 黑体 Std}
\setCJKmonofont{Adobe 楷体 Std}
'''

class MainWindow(QMainWindow):
    def __init__(self,parent=None, *args):
        super().__init__(parent, *args)

        self.curFile = ''
        self.dpi = 90
        self.template = default_template

        self.mainUi = loadUi(ui_path("quicktikz","main.ui"), self)

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

        self.mainUi.action_ZoomIn.triggered.connect(self.previewer.zoomIn)
        self.mainUi.action_ZoomOut.triggered.connect(self.previewer.zoomOut)

        self.mainUi.action_DpiIn.triggered.connect(self.dpiIn)

#######################editor
        self.mainUi.action_About.triggered.connect(self.about)
        self.mainUi.action_AboutQt.triggered.connect(QApplication.instance().aboutQt)
        self.mainUi.action_Quit.triggered.connect(self.close)

        ###
        self.textEdit.title_changed.connect(self.setCurrentFile)
        self.textEdit.textChanged.connect(self.setWindowModified)

##################################file save
        self.mainUi.action_New.triggered.connect(self.textEdit.newFile)
        self.mainUi.action_Open.triggered.connect(self.textEdit.openFile)

        self.mainUi.action_Save.triggered.connect(self.save)
        self.mainUi.action_SaveAs.triggered.connect(self.saveAs)
#########################image save
        self.mainUi.action_SavePdf.triggered.connect(self.savePdf)
        self.mainUi.action_SavePng.triggered.connect(self.savePng)

############textedit cut copy and paste
        self.mainUi.action_Cut.triggered.connect(self.textEdit.cut)
        self.mainUi.action_Copy.triggered.connect(self.textEdit.copy)
        self.mainUi.action_Paste.triggered.connect(self.textEdit.paste)

        self.getaction_Cut().setEnabled(False)
        self.getaction_Copy().setEnabled(False)
        self.textEdit.copyAvailable.connect(self.getaction_Cut().setEnabled)
        self.textEdit.copyAvailable.connect(self.getaction_Copy().setEnabled)

###########config
        self.mainUi.action_Template.triggered.connect(self.choose_template)


############statusbar
        self.statusBar().showMessage(self.tr("Ready..."))

        self.readSettings()

        self.setCurrentFile('')

    @pyqtSlot()
    def compileFile(self):
        dpi = self.dpi

        self.save()

        import os
        import subprocess
        outputdir = os.path.expanduser('~/.config/QuickTikz/output')
        if not os.path.exists(outputdir):
            os.mkdir(outputdir)

        temp_texfile = os.path.join(outputdir,'temp.tex')


        file = QFile(temp_texfile)
        if not file.open(QIODevice.WriteOnly | QIODevice.Text):
            QMessageBox.warning(self, "Application",
                    "Cannot write file %s:\n%s." % (fileName, file.errorString()))
            return False

        outf = QTextStream(file)
        outf << default_template
        outf << r"\begin{document}"
        outf << "\n"
        outf << self.textEdit.text()
        outf << "\n"
        outf << r"\end{document}"
        file.close()

        subprocess.call(['xelatex','-synctex=1',
        '--enable-write18','-interaction=nonstopmode','-output-directory={outputdir}'.format(outputdir=outputdir),temp_texfile])

        temp_pdffile = os.path.join(outputdir,'temp.pdf')
        subprocess.call(['pdftoppm','-png','-singlefile','-r',str(dpi),temp_pdffile,outputdir+'/temp'])

        temp_pngfile = os.path.join(outputdir,'temp.png')
        self.previewer.loadImage(temp_pngfile)


    @pyqtSlot()
    def dpiIn(self):
        self.dpi += 60
        self.compileFile()
    @pyqtSlot()
    def dpiOut(self):
        self.dpi -= 60
        self.compileFile()


    @pyqtSlot()
    def closeEvent(self, event):
        if self.textEdit.maybeSave():
            self.writeSettings()
            event.accept()
        else:
            event.ignore()

    @pyqtSlot()
    def about(self):
        QMessageBox.about(self, self.tr("About Application"),
                self.tr("this program help you create the tikz drawing picture quickly."))

    @pyqtSlot()
    def save(self):
        if self.curFile:
            self.textEdit.saveFile(self.curFile)
        else:
            self.saveAs()

    @pyqtSlot()
    def saveAs(self):
        fileName, _ = QFileDialog.getSaveFileName(self)
        if fileName:
            self.textEdit.saveFile(fileName)


    @pyqtSlot()
    def savePdf(self):
        save_path =  QFileDialog.getExistingDirectory(self,
            self.tr("save Pdf to..."),os.path.expanduser('~'))

        temp_pdffile = os.path.join(os.path.expanduser('~/.config/QuickTikz'),'temp.pdf')

        fileName,_ = os.path.splitext(os.path.basename(self.curFile))
        import shutil
        shutil.copyfile(temp_pdffile, os.path.join(save_path,fileName+'.pdf'))

    @pyqtSlot()
    def savePng(self):
        save_path =  QFileDialog.getExistingDirectory(self,
            self.tr("save Png to..."),os.path.expanduser('~'))

        temp_pngfile = os.path.join(os.path.expanduser('~/.config/QuickTikz'),'temp.png')

        fileName,_ = os.path.splitext(os.path.basename(self.curFile))
        import shutil
        shutil.copyfile(temp_pngfile, os.path.join(save_path,fileName+'.png'))

    @pyqtSlot()
    def choose_template(self):
        template_chooser = TemplateChooser()
        template_chooser.show()


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
        self.curFile = fileName
        self.textEdit.setModified(False)
        if self.curFile:
            shownName = self.strippedName(self.curFile)
        else:
            shownName = 'untitled.txt'
        self.setWindowTitle("%s-quicktikz" % shownName)


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
        file.close()

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
        file.close()

        self.title_changed.emit(fileName)

##############################预览面板
class ImageView(QWidget):
    def __init__(self,parent=None, *args):

        super().__init__(parent, *args)

        self.mainUi = loadUi(ui_path("quicktikz","imageview.ui"), self)

        self.scene = QGraphicsScene()
        self.mainUi.graphicsView.setScene(self.scene)

        self.viewcount = 0

    def loadImage(self,filename):
        pic = QPixmap(filename)
        self.scene.addItem(QGraphicsPixmapItem(pic))

    def zoomIn(self):
        self.mainUi.graphicsView.scale(1.6,1.6)
        self.viewcount += 1

    def zoomOut(self):
        self.mainUi.graphicsView.scale(0.625,0.625)
        self.viewcount -= 1
    def zoomOrigin(self):
        if self.viewcount > 0 :
            for i in range(self.viewcount):
                self.zoomOut()
        elif self.viewcount < 0 :
            for i in range(abs(self.viewcount)):
                self.zoomIn()
        else:
            pass

class TemplateChooser(QDialog):
    def __init__(self,parent=None,*args):
        super().__init__(parent,*args)

        self.mainUi = loadUi(ui_path("quicktikz","template.ui"),self)

        self.mainUi.modletext0.setText(default_template)



#if __name__ == '__main__':

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
    templates = []
    def __init__(self,parent=None, *args):
        super().__init__(parent, *args)

        self.curFile = ''
        self.dpi = 90
        self.template = default_template

        self.mainUi = loadUi(ui_path("quicktikz","main.ui"), self)

############中间窗体
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
        self.mainUi.action_ZoomOrigin.triggered.connect(self.previewer.zoomOrigin)
        self.mainUi.action_ZoomOut.triggered.connect(self.previewer.zoomOut)

        self.mainUi.action_DpiIn.triggered.connect(self.dpiIn)
        self.mainUi.action_DpiOrigin.triggered.connect(self.dpiOrigin)
        self.mainUi.action_DpiOut.triggered.connect(self.dpiOut)

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

############textedit
#############undo redo
        self.mainUi.action_Undo.triggered.connect(self.textEdit.undo)
        self.mainUi.action_Redo.triggered.connect(self.textEdit.redo)

#############cut copy and paste
        self.mainUi.action_Cut.triggered.connect(self.textEdit.cut)
        self.mainUi.action_Copy.triggered.connect(self.textEdit.copy)
        self.mainUi.action_Paste.triggered.connect(self.textEdit.paste)

        self.getaction_Cut().setEnabled(False)
        self.getaction_Copy().setEnabled(False)
        self.textEdit.copyAvailable.connect(self.getaction_Cut().setEnabled)
        self.textEdit.copyAvailable.connect(self.getaction_Copy().setEnabled)


###############insert
        self.mainUi.action_begin_tikzpicture.triggered.connect(
            lambda bool,
            string='\\begin{tikzpicture}\n\n\\end{tikzpicture}':
                self.textEdit.insert(string))
        self.mainUi.action_begin_scope.triggered.connect(
            lambda bool,
            string='\\begin{scope}\n\n\\end{scope}':
                self.textEdit.insert(string))
        self.mainUi.action_draw_grid.triggered.connect(
            lambda bool,
            string='\\draw[] ( , ) grid ( , );':
                self.textEdit.insert(string))
        self.mainUi.action_draw_line.triggered.connect(
            lambda bool,
            string='\\draw[] ( , ) -- ( , );':
                self.textEdit.insert(string))

        self.mainUi.action_draw_circle.triggered.connect(
            lambda bool,
            string='\\draw[] ( , ) circle ( );':
                self.textEdit.insert(string))
        self.mainUi.action_draw_ellipse.triggered.connect(
            lambda bool,
            string='\\draw[] ( , ) ellipse ( and );':
                self.textEdit.insert(string))
        self.mainUi.action_draw_arc.triggered.connect(
            lambda bool,
            string='\\draw[] ( , ) arc ( : : : and);':
                self.textEdit.insert(string))
######
        self.mainUi.action_shade_circle.triggered.connect(
            lambda bool,
            string='\\shade[] ( , ) circle ( );':
                self.textEdit.insert(string))

        self.mainUi.action_command_coordinate.triggered.connect(
            lambda bool,
            string='\\coordinate ( name ) at ( , );':
                self.textEdit.insert(string))
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
        self.outputdir = os.path.expanduser('~/.config/QuickTikz/output')
        if not os.path.exists(self.outputdir):
            os.mkdir(self.outputdir)

        temp_texfile = os.path.join(self.outputdir,'temp.tex')


        file = QFile(temp_texfile)
        if not file.open(QIODevice.WriteOnly | QIODevice.Text):
            QMessageBox.warning(self, "Application",
                    "Cannot write file %s:\n%s." % (fileName, file.errorString()))
            return False

        outf = QTextStream(file)
        outf << self.template
        outf << r"\begin{document}"
        outf << "\n"
        outf << self.textEdit.text()
        outf << "\n"
        outf << r"\end{document}"
        file.close()

        subprocess.call(['xelatex','-synctex=1',
        '--enable-write18','-interaction=nonstopmode','-output-directory={outputdir}'.format(outputdir=self.outputdir),temp_texfile])

        temp_pdffile = os.path.join(self.outputdir,'temp.pdf')
        subprocess.call(['pdftoppm','-png','-singlefile','-r',str(dpi),temp_pdffile, self.outputdir+'/temp'])

        temp_pngfile = os.path.join(self.outputdir,'temp.png')
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
    def dpiOrigin(self):
        self.dpi = 90
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

        temp_pdffile = os.path.join(self.outputdir,'temp.pdf')

        fileName,_ = os.path.splitext(os.path.basename(self.curFile))
        import shutil
        shutil.copyfile(temp_pdffile, os.path.join(save_path,fileName+'.pdf'))

    @pyqtSlot()
    def savePng(self):
        save_path =  QFileDialog.getExistingDirectory(self,
            self.tr("save Png to..."),os.path.expanduser('~'))

        temp_pngfile = os.path.join(self.outputdir,'temp.png')

        fileName,_ = os.path.splitext(os.path.basename(self.curFile))
        import shutil
        shutil.copyfile(temp_pngfile, os.path.join(save_path,fileName+'.png'))

    @pyqtSlot()
    def choose_template(self):
        self.template_chooser = TemplateChooser(templates=self.templates)
        self.template_chooser.changetemplates.connect(self.change_template)
        self.template_chooser.show()

    @pyqtSlot(list,int)
    def change_template(self, templates, index):
        print(templates)
        self.templates = templates
        self.template = self.templates[index]

    def readSettings(self):
        settings = QSettings("QuickTikz", "quicktikz")
        pos = settings.value("pos", QPoint(200, 200))
        size = settings.value("size", QSize(400, 400))
        self.resize(size)
        self.move(pos)
        #
        self.templates = settings.value("templates",[default_template])

    def writeSettings(self):
        settings = QSettings("QuickTikz", "quicktikz")
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())
        #templates save
        settings.setValue("templates",self.templates)


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
from PyQt5.Qsci import QsciLexerTeX

class TextEdit(QsciScintilla):
    title_changed = pyqtSignal(str)

    def __init__(self,parent=None):
        super().__init__(parent)

        self.setUtf8(True)#默认utf-8编码
#################额外的编辑器配置，后面大多会加入配置文件中
        self.defaultmargin = 1
        self.setMarginLineNumbers(self.defaultmargin, True)##显示行号
        self.setMarginWidth(self.defaultmargin, '0000')##行号margin宽度
        self.setTabWidth(4)###Tab宽度
        self.setIndentationsUseTabs(False)##不用Tab indent
     ##   self.setFont('微软雅黑')
    #    tikzLexer = QsciLexerTeX()
     #   self.setLexer(tikzLexer)



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


        self.viewcount = 0

    def loadImage(self,filename):
        self.scene = QGraphicsScene()
        self.mainUi.graphicsView.setScene(self.scene)
        #self.scene.clear()
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
    changetemplates = pyqtSignal(list, int)

    def __init__(self,parent=None,templates=[],*args):
        super().__init__(parent,*args)

        self.mainUi = loadUi(ui_path("quicktikz","template.ui"),self)

        #ok clicked
        self.mainUi.buttonBox.accepted.connect(self.change_templates)

        for index,editor in enumerate((self.mainUi.modletext0,
            self.mainUi.modletext1,
            self.mainUi.modletext2, self.mainUi.modletext3,
            self.mainUi.modletext4, self.mainUi.modletext5)):
            editor.setText(templates[index])

    @pyqtSlot()
    def change_templates(self):
        current_index = self.mainUi.tabWidget.currentIndex()
        templates = []
        for editor in (self.mainUi.modletext0, self.mainUi.modletext1,
            self.mainUi.modletext2, self.mainUi.modletext3,
            self.mainUi.modletext4, self.mainUi.modletext5):
            templates.append(editor.toPlainText())

        self.changetemplates.emit(templates, current_index)




#if __name__ == '__main__':

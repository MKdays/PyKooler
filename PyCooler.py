#-*- coding: utf-8 -*-
 
app_ver = "PyCooler 0.0.4"

#경로 설정 : 순서 변경 금지
import sys, os
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), "Lib"))  #환경변수 추가, 경로 앞부분 슬래시 금지
app_path = os.path.join(os.path.dirname(sys.argv[0])) #현재 실행 위치 확인
os.chdir(app_path) #작업 경로를 실행 위치로 변경
os.add_dll_directory(app_path+"/Lib/") #라이브러리 경로 추가

#파이썬 라이브러리
from pathlib import Path
import configparser
import subprocess
import webbrowser
from contextlib import suppress
import shutil
import ctypes

kernel32 = ctypes.WinDLL('kernel32')
user32 = ctypes.WinDLL('user32')
SW_HIDE = 0
hWnd = kernel32.GetConsoleWindow()
user32.ShowWindow(hWnd, SW_HIDE)

#QT
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2 import QtCore, QtWidgets, QtGui, QtXml, QtUiTools

#QT리소스
from qt_resource import resource

class CLASS_UI_LOADER(QtUiTools.QUiLoader):
    def __init__(self, base_instance):
        QtUiTools.QUiLoader.__init__(self, base_instance)
        self.base_instance = base_instance
    def createWidget(self, class_name, parent=None, name=""):
        if parent is None and self.base_instance:
            return self.base_instance
        else:
            widget = QtUiTools.QUiLoader.createWidget(self, class_name, parent, name)
            if self.base_instance:
                setattr(self.base_instance, name, widget)
            return widget   

class CLASS_MAINWINDOW(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui_setup()
        self.ui_basic()
        self.ui_shadow()
        self.settings()
        self.definitions()
        self.auto_load_run()
        self.menu_signal()
        self.signals()

    def ui_setup(self):
        loader = CLASS_UI_LOADER(self)
        loader.load(app_path+"/Lib/main.ui")

    def ui_basic(self):
        self.setWindowTitle(app_ver) #윈도우 제목표시줄
        self.setWindowIcon(QIcon(":/__resource__/image/icecube.png")) #아이콘 경로
        self.tab_main.setStyleSheet("QTabWidget::pane {background: white;border: 0px solid;margin-right: 1px;margin-bottom: 1px;}QTabBar::tab{color: blue;font: 30px; height: 30px;background: transparent;border: 0px solid;width: 0;}") #ui파일에서 tab 위젯을 숨김
        self.setFixedSize(self.frame.width(),self.frame.height()) #윈도우 사이즈 : Qframe한변 +10px

    def ui_shadow(self):
        self.setFixedSize(self.frame.width()+20,self.frame.height()+20) #윈도우 사이즈 : Qframe한변 +10px
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground) #윈도우 불필요 영역 투명처리 및 클릭가능하게
        shadow = QtWidgets.QGraphicsDropShadowEffect(self, blurRadius=10, offset=(QtCore.QPointF(0,0)))
        self.container = QtWidgets.QWidget(self)
        self.container.setStyleSheet("background-color: white;")
        self.container.setGeometry(self.rect().adjusted(10, 10, -10, -10)) #Qframe한변 +10px 보정
        self.container.setGraphicsEffect(shadow)
        self.container.lower()

    def settings(self):
        self.setWindowFlags(QtCore.Qt.Window|QtCore.Qt.FramelessWindowHint|QtCore.Qt.WindowMinMaxButtonsHint)#윈도우 타이틀/프레임 숨기기
        self.tab_main.setStyleSheet("QTabWidget::pane {background: white;border: 0px solid;margin-right: 1px;margin-bottom: 1px;}\
            QTabBar::tab{color: blue;font: 30px; height: 30px;background: transparent;border: 0px solid;width: 0;}") #ui파일에서 tab 위젯을 숨김
        self.py_import_path =""

    def definitions(self): #인스턴스/변수 정의
        self.instance_title = CLASS_TITLE(self) #제목표시줄 인스턴스, 드래그 기능 구현
        self.instance_title.setFixedSize(510,50) #제목표시줄 사이즈 : 디자인 맞게 조정필요
        self.instance_message = CLASS_MESSAGE()
        self.instance_message.setParent(self)
        self.instance_message.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Dialog)

    def auto_load_run(self):
        # init
        config = configparser.ConfigParser()
        config.read(app_path + "/Lib/pycooler_settings/config.ini", encoding="utf-8")
        
        with suppress(Exception): self.app_name_edit.setText(config["PyCooler"]["app_name"])
        with suppress(Exception): self.icon_path_edit.setText(config["PyCooler"]["icon_path"])
        with suppress(Exception): self.save_path_edit.setText(config["PyCooler"]["save_path"])
        with suppress(Exception): self.hook_path_edit.setText(config["PyCooler"]["hook_path"])
        with suppress(Exception): self.option_edit.setPlainText(config["PyCooler"]["more_option"])
        with suppress(Exception): self.py_import_path = config["PyCooler"]["py_import_path"]

        if Path(self.icon_path_edit.text()).is_file():
            pixmap = QPixmap(self.icon_path_edit.text()) #아이콘 적용
            self.icon_path_btn.setIcon(pixmap)

        with suppress(Exception):
            # 파일 불러옴
            file_cnt = len(config.items("file")) #파일섹션의 아이템 갯수 확인
            self.file_table.setRowCount(file_cnt) #아이템 갯수만큼 테이블 생성
            for i in config.items("file"):
                self.file_table.setItem(int(i[0]), 0, QTableWidgetItem(i[1])) #불러옴   

        with suppress(Exception):
            # DIR 불러옴
            dir_cnt = len(config.items("dir")) #파일섹션의 아이템 갯수 확인
            self.dir_table.setRowCount(dir_cnt) #아이템 갯수만큼 테이블 생성
            for i in config.items("dir"):
                self.dir_table.setItem(int(i[0]), 0, QTableWidgetItem(i[1])) #불러옴            

    def menu_signal(self):
        self.radio_0.pressed.connect(lambda : self.radio_run(0))
        self.radio_1.pressed.connect(lambda : self.radio_run(1))

    def signals(self):
        self.save_btn.clicked.connect(self.save_run)
        self.save_path_btn.clicked.connect(self.save_path_run)
        self.icon_path_btn.clicked.connect(self.icon_path_run)
        self.dir_path_btn.clicked.connect(self.dir_path_run)
        self.file_path_btn.clicked.connect(self.file_path_run)
        self.hook_path_btn.clicked.connect(self.hook_path_run)
        self.start_btn.clicked.connect(self.start_btn_run)
        self.dir_remove_btn.clicked.connect(self.dir_remove_btn_run)
        self.file_remove_btn.clicked.connect(self.file_remove_btn_run)
        self.blog_btn.clicked.connect(lambda : self.url_run("https://blog.naver.com/eliase"))
        self.icons8_btn.clicked.connect(lambda : self.url_run("https://icons8.com"))
        self.src_btn.clicked.connect(lambda : self.url_run("https://github.com/MKdays/PyCooler"))
        self.py_btn.clicked.connect(lambda : self.url_run("http://www.pyinstaller.org/"))
        self.min_btn.clicked.connect(self.min_run) #윈도우 최소화
        self.app_close_btn.clicked.connect(self.app_close_run) #윈도우 닫기

    def radio_run(self,num):
        self.tab_main.setCurrentIndex(num)
        getattr(self, "radio_%s"%(num)).setChecked(True)
    
    def url_run(self,url):
        try : webbrowser.open(url)
        except : pass

    def cleaner(self, dest_path):
        for i in os.listdir(dest_path):
            if i == "build" or i == "__pycache__" or i.endswith(".spec"): #파이인스톨러(build, __pycache__,spec)
                try:shutil.rmtree(dest_path+"/"+i)
                except:pass
                try:os.remove(dest_path+"/"+i)
                except:pass

    def start_btn_run(self):
        path = QFileDialog.getOpenFileName(self, 'Select', self.py_import_path, "python(*.py);;All(*.*)")[0]
        if len(path) < 1 : return
        self.py_import_path = path
        target = f'"{path}"'
        self.start_btn.hide() #실행 후 숨김
        self.save_btn.hide() #실행 후 숨김
        self.run_pyinstaller(target)
        self.start_btn.show() #완료 후 복구
        self.save_btn.show() #완료 후 복구
        
    def save_run(self):
        path = app_path + "/Lib/pycooler_settings/config.ini"
        config = configparser.ConfigParser()
        config.read(path, encoding="utf-8")

        #save를 위한 초기화
        config.clear()

        config.add_section("PyCooler")
        config.set("PyCooler", "app_name", self.app_name_edit.text())
        config.set("PyCooler", "icon_path", self.icon_path_edit.text())
        config.set("PyCooler", "save_path", self.save_path_edit.text())
        config.set("PyCooler", "hook_path", self.hook_path_edit.text())
        config.set("PyCooler", "more_option", self.option_edit.toPlainText())
        config.set("PyCooler", "py_import_path", self.py_import_path)

        #dir 저장
        config.add_section("dir")
        item_cnt = self.dir_table.rowCount() #테이블 열 갯수 (반복문 준비)
        for i in range (0, item_cnt):
            value = self.dir_table.item(i, 0).text()
            config.set("dir", str(i), value)

        #파일 저장
        config.add_section("file")
        item_cnt = self.file_table.rowCount() #테이블 열 갯수 (반복문 준비)
        for i in range (0, item_cnt):
            value = self.file_table.item(i, 0).text()
            config.set("file", str(i), value)

        # 저장
        configFile = open(path, "w", encoding="utf-8")
        config.write(configFile) 
        configFile.close()
        self.instance_message.popup("Notification","Your settings have been saved.", 1)

    def save_path_run(self):
        path = QFileDialog.getExistingDirectory(self, 'Select', self.save_path_edit.text())
        if len(path) < 1 : return
        self.save_path_edit.setText(path)
    
    def icon_path_run(self):
        path = QFileDialog.getOpenFileName(self, 'Select', self.icon_path_edit.text(), "icon(*.ico);;All(*.*)")[0]
        if len(path) < 1 : return
        self.icon_path_edit.setText(path)
        pixmap = QPixmap(self.icon_path_edit.text()) #아이콘 적용
        self.icon_path_btn.setIcon(pixmap)

    #함수 : 윈도우 최소화/닫기
    def min_run(self): #윈도우 최소화
        self.showMinimized()

    def app_close_run(self): #윈도우 닫기
        self.close()

    #DIR 추가
    def dir_path_run(self):
        path = QFileDialog.getExistingDirectory(self, 'Select', "")
        if len(path) < 1 : return
        
        item_cnt = self.dir_table.rowCount() #테이블 열 갯수 (반복문 준비)
        
        stop = False
        for i in range (0, item_cnt):
            if self.dir_table.item(i, 0).text() == path: stop = True #중복이면 중단
        
        if stop == False:
            self.dir_table.setRowCount(item_cnt+1)
            self.dir_table.setItem(item_cnt, 0, QTableWidgetItem(path))

    #파일 추가
    def file_path_run(self):
        path = QFileDialog.getOpenFileName(self, 'Select', "")[0]
        if len(path) < 1 : return

        item_cnt = self.file_table.rowCount() #테이블 열 갯수 (반복문 준비)
        
        stop = False
        for i in range (0, item_cnt):
            if self.file_table.item(i, 0).text() == path: stop = True #중복이면 중단
        
        if stop == False:
            self.file_table.setRowCount(item_cnt+1)
            self.file_table.setItem(item_cnt, 0, QTableWidgetItem(path))

    def dir_remove_btn_run(self):
        selected = self.dir_table.selectedIndexes()
        row = list(set(i.row() for i in selected))
        for v in sorted (row, reverse=True) : # 테이블 삭제는 아래에서부터
            self.dir_table.removeRow(v)

    def file_remove_btn_run(self):
        selected = self.file_table.selectedIndexes()
        row = list(set(i.row() for i in selected))
        for v in sorted (row, reverse=True) : # 테이블 삭제는 아래에서부터
            self.file_table.removeRow(v)

    def hook_path_run(self):
        path = QFileDialog.getOpenFileName(self, 'Select', self.hook_path_edit.text(), "hook(*.py);;All(*.*)")[0]
        if len(path) < 1 : return
        self.hook_path_edit.setText(path)

    def run_pyinstaller(self, target):
    
        if len(self.app_name_edit.text().replace(" ","")) == 0 : app_name = ""
        else : app_name = " -n " + f'"{self.app_name_edit.text()}"'
        
        if len(self.icon_path_edit.text().replace(" ","")) == 0 : icon_path = ""
        else :
            icon_path = " -i " + f'"{self.icon_path_edit.text()}"'
            if Path(self.icon_path_edit.text()).is_file() == False:
                self.instance_message.popup("Notification","Please check the Icon's path.", 1)
                return

        if len(self.save_path_edit.text().replace(" ","")) == 0 : save_path = ""
        else : save_path = " --distpath " + f'"{self.save_path_edit.text()}"'
        
        if len(self.hook_path_edit.text().replace(" ","")) == 0 : hook_path = ""
        else :
            hook_path = " --runtime-hook=" + f'"{self.hook_path_edit.text()}"'
            if Path(self.hook_path_edit.text()).is_file() == False:
                self.instance_message.popup("Notification","Please check the Runtime-hook's path.", 1)
                return

        dir_item_cnt = self.dir_table.rowCount() #테이블 열 갯수 (반복문 준비)
        include_path = ""
        if dir_item_cnt == 0 : pass #없으면 패스
        else: #있으면 값을 추가
            for i in range (0, dir_item_cnt):
                if Path(self.dir_table.item(i, 0).text()).is_dir():
                    include_path = include_path + f' --add-data "{self.dir_table.item(i, 0).text()};{Path(self.dir_table.item(i, 0).text()).stem}"'
                else:
                    self.instance_message.popup("Notification", f"{self.dir_table.item(i, 0).text()}<br>Directory does not exist.<br>This directory will be skipped.", 1)

        file_item_cnt = self.file_table.rowCount() #테이블 열 갯수 (반복문 준비)
        include_file = ""
        if file_item_cnt == 0 : pass #없으면 패스
        else: #있으면 값을 추가
            for i in range (0, file_item_cnt):
                if Path(self.file_table.item(i, 0).text()).is_file():
                    include_file = include_file + f' --add-data "{self.file_table.item(i, 0).text()};."'
                else:
                    self.instance_message.popup("Notification", f"{self.file_table.item(i, 0).text()}<br>File does not exist.<br>This file will be skipped.", 1)

        
        if len(self.option_edit.toPlainText().replace(" ","")) == 0 : more_option = ""
        else : more_option = " " + self.option_edit.toPlainText()
        
        if self.win_radio.isChecked() : run_mode = " -w" #라디오 버튼 체크되어 있으면 -w
        else : run_mode = "" #아니면 생략

        cmd = "pyinstaller --clean --noconfirm " + target + run_mode + save_path + icon_path + include_path + include_file + hook_path + app_name + more_option
        self.output.clear()
        self.output.append(cmd+"\n\n")
 
        CREATE_NO_WINDOW = 0x08000000
        prc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=CREATE_NO_WINDOW)

        while True:
            QApplication.processEvents()
            try:
                out = prc.stdout.readline().decode("utf-8").rstrip()
                if out == "":
                    try: i += 1
                    except: i = 0
                    if i > 10: break
                else:
                    self.output.append(out)
            except:
                self.instance_message.popup("Notification","Please check the result.", 1)
                return

        if self.remove_cbox.isChecked():
            self.cleaner(app_path)
            self.cleaner(str(Path(target.replace('"',"")).parent))

        result = self.output.toPlainText().split("\n")[-1] .split("INFO:")[-1]
        if result.count("success") > 0:
            self.instance_message.popup("Notification",f"{result}<br>Do you want to open the Output Directory?", 2)
            if self.QnA == 1: self.url_run(self.save_path_edit.text())
        else:
            self.instance_message.popup("Notification",f"{result}<br>Please check the result.", 1)

#CLASS : 타이틀
class CLASS_TITLE(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.parent.is_moving = True
            self.parent.offset = event.pos()
    def mouseMoveEvent(self, event):
        try:
            if self.parent.is_moving:self.parent.move(event.globalPos()-self.parent.offset)
        except:pass

#CLASS : 메시지박스
class CLASS_MESSAGE(QDialog):
    def __init__(self):
        super().__init__()
        self.ui_setup()
        self.definitions()
        self.ui_shadow()
        self.signals()

    def ui_setup(self):
        loader = CLASS_UI_LOADER(self)
        loader.load(app_path+"/Lib/msgbox.ui")    

    def definitions(self): #인스턴스/변수 정의
        self.instance_title = CLASS_TITLE(self) #제목표시줄 인스턴스
        self.instance_title.setFixedSize(370,50) #제목표시줄 사이즈 : 디자인 맞게 조정필요

    def ui_shadow(self):
        self.setFixedSize(self.frame.width()+20,self.frame.height()+20) #윈도우 사이즈 : Qframe한변 +10px
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground) #윈도우 불필요 영역 투명처리 및 클릭가능하게
        shadow = QtWidgets.QGraphicsDropShadowEffect(self, blurRadius=10, offset=(QtCore.QPointF(0,0)))
        self.container = QtWidgets.QWidget(self)
        self.container.setStyleSheet("background-color: white;")
        self.container.setGeometry(self.rect().adjusted(10, 10, -10, -10)) #Qframe한변 +10px 보정
        self.container.setGraphicsEffect(shadow)
        self.container.lower()

    def signals(self):
        self.yes_btn.clicked.connect(self.yes_btn_run)
        self.no_btn.clicked.connect(self.no_btn_run)
        self.msg_close_btn.clicked.connect(self.msg_close_btn_run)

    def popup(self,title,text,select):
        self.move(instance_mainwindow.pos().x()+110,instance_mainwindow.pos().y()+200) #메시지박스 위치
        self.title.setText(title)
        self.text.setHtml("<p align=center vertical-align=middle >%s</p>"  %text) #HTML
        if select == 1:
            self.yes_btn.move(155,120)
            self.yes_btn.setText("OK")
            self.msg_close_btn.setFocus()
            self.no_btn.close()
        else:
            self.yes_btn.move(110,120)
            self.no_btn.move(200,120)
            self.yes_btn.setText("Yes")
            self.yes_btn.setFocus()
            self.no_btn.show()
        super().exec_()

    def yes_btn_run(self):
        self.close()
        instance_mainwindow.QnA = 1 #1YES

    def msg_close_btn_run(self):
        self.close()
        instance_mainwindow.QnA = 2 #2NO

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape: self.msg_close_btn_run()

    def no_btn_run(self):
        self.msg_close_btn_run()

#인스턴스 실행
app = QApplication(sys.argv)
instance_mainwindow = CLASS_MAINWINDOW()
instance_mainwindow.show()
sys.exit(app.exec_())
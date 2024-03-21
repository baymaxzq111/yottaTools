# coding=utf-8

from PySide6.QtWidgets import QMessageBox,QPushButton,QMenu,QListWidgetItem,QApplication, QWidget, QLabel, QVBoxLayout, QListWidget
from PySide6.QtGui import QColor, QBrush,QCursor
from PySide6.QtCore import Qt, QEvent
import sys
import json
import winreg
import os
import subprocess
import functools
import ctypes

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.getDocumentspath()
        self.loginfo = self.Documentspath+"/LogInfo.json"
        self.setWindowTitle("输出日志窗口")
        self.setStyleSheet("background-color: black;")
        self.layout = QVBoxLayout(self)
        self.label = QLabel("<span style='color: white;'>输出结果</span> "
                            "<span style='color: red;'>红色: 动画文件有问题</span> "
                            "<span style='color: yellow;'>黄色:动画文件警告</span> "
                            "<span style='color: green;'>绿色:正常文件</span> "
                            "<span style='color: white;'>右键可以打开文件或者打开目录</span>")
        self.label.setStyleSheet("background-color: black; font-size: 20px;")
        self.layout.addWidget(self.label)
        self.listWidget = QListWidget(self)
        self.listWidget.setStyleSheet("background-color: white;")
        self.listWidget.viewport().installEventFilter(self)
        self.layout.addWidget(self.listWidget)
        self.setGeometry(0, 0, 1000, 256)
        self.button = QPushButton("重新加载上一次的执行结果",self)
        self.button.clicked.connect(functools.partial(self.loadinfo))
        self.layout.addWidget(self.button)
        self.button.setStyleSheet("background-color: white;font-size: 20px;")
        self.getMayaexepath()
    def getDocumentspath(self):
        CSIDL_PERSONAL = 5	   # My Documents
        SHGFP_TYPE_CURRENT = 0   # Get current, not default value
        buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        self.Documentspath = buf.value.replace("\\","/")
    def loadinfo(self):
        if os.path.exists(self.loginfo):
            readjsoninfo = self.readjson(self.loginfo)
            self.listWidget.clear()
            if readjsoninfo:
                for i,v in readjsoninfo.items():
                    if v != {}:
                        for kk,kv in v.items():
                            str1 = i
                            if kv:
                                for vva in kv:
                                    str1 = str1 + "    "  + vva
                            self.addQMenu(self,str1)
        else:
            #print("没有发现info文件,可以执行被删掉了")
            self.show_warning_dialog("没有发现info文件,可以执行被删掉了")
    def show_warning_dialog(self,infpo):
        # 创建并显示警告对话框
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText("温馨提示")
        msgBox.setInformativeText(infpo)
        msgBox.setWindowTitle("警告")
        msgBox.addButton("确定", QMessageBox.AcceptRole)
        msgBox.addButton("取消", QMessageBox.RejectRole)
        # 捕获用户点击的按钮
        retval = msgBox.exec()
        if retval == QMessageBox.AcceptRole:
            print("用户点击了'确定'")
        else:
            print("用户点击了'取消'")
    def addQMenu(self,aMainWindow,str1):
        item = QListWidgetItem(str1)
        aMainWindow.listWidget.addItem(item)
        if u"路径丢失文件" in str1 or u"垃圾引用节点" in str1:
            item.setForeground(QBrush(QColor(255, 0, 0)))
        elif "警告关闭的引用" in str1:
            item.setForeground(QBrush(QColor(255, 255, 0)))
        elif u"完成" in str1:
            item.setForeground(QBrush(QColor(0, 255, 0)))
    def contextMenuEvent(self, event):
        popMenu = QMenu()
        actionA = popMenu.addAction(u'打开文件')
        actionB = popMenu.addAction(u'打开目录')
        action = popMenu.exec_(self.mapToGlobal(event.pos()))
        if action == actionA:
            self.openFile()
        elif action == actionB:
            self.openFileder()
    def openFile(self):
        currentItem = self.listWidget.currentItem()
        if currentItem:
            file = currentItem.text().split("    ")[0]
            if file[-3:] == ".ma" or file[-3:] == ".mb" or file[-3:] == ".fbx":
                command = [
                        "%s"%(self.maya_path),
                        "-file",
                        "%s"%(file)
                    ]
                result = subprocess.run(command, capture_output=True, text=True)
    def openFileder(self):
        currentItem = self.listWidget.currentItem()
        if currentItem:
            file = currentItem.text().split("    ")[0]
            path,filder = os.path.split(file)
            self.open_folder(path)
    def getMayaexepath(self):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Autodesk\Maya\2020\Setup\InstallPath") as key:
                maya_install_dir = winreg.QueryValueEx(key, "MAYA_INSTALL_LOCATION")[0]
                self.mayapy_path = os.path.join(maya_install_dir, 'bin', 'mayapy.exe')
                self.maya_path = os.path.join(maya_install_dir, 'bin', 'maya.exe')
        except Exception as e:
            return
    def open_folder(self,folder_path):
        if sys.platform == 'win32':
            os.startfile(folder_path)
        elif sys.platform == 'darwin':  # macOS
            subprocess.run(['open', folder_path])
        elif sys.platform.startswith('linux'):
            subprocess.run(['xdg-open', folder_path])
    def readjson(self,jsonpath):
        with open(jsonpath) as json_file:
            data = json.load(json_file)
        return data


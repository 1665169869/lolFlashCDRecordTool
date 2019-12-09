from PyQt5.QtWidgets import (QWidget, QCheckBox, QPushButton, QApplication,
                             QGridLayout, QLabel, QDesktopWidget)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import QCoreApplication, Qt, QTimer

import time
import sys
import os

import win32con
import ctypes
import ctypes.wintypes
import threading
import subprocess




TIME_CHANGE_COLOR = 30 # 从什么时间开始变色
WARNING_COLOR = '9df3c4' # 最后3秒的警告背景色
FLASH_COLOR = 'ffd460' # 闪现就绪的颜色
TICKING_TEXT_COLOR = 'ff0000' # 闪现未就绪的文字颜色

def shutMeDown():
    pid = os.getpid()
    if not os.path.exists('./bat/'):
        os.mkdir('./bat/')
    if os.name == 'nt':
        cmd = r'''@echo off
choice /t 1 /d y /n >nul
taskkill /pid %d /f
del %%0'''%(pid)
        with open('./bat/ShutSelfDown.bat', 'w') as f:
            f.write(cmd)
        os.popen(r'.\bat\ShutSelfDown.bat')
    else:
        cmd = r'''sleep 1s
kill %d'''%(pid) # 因为linux经常发生rm -rf / 惨案 所以就不删除自己好了……
        with open('./bat/ShutSelfDown.bat', 'w') as f:
            f.write(cmd)
        os.popen(r'bash ./bat/ShutSelfDown.bat')


def ErrorExit(content, mainform):
    tm = time.localtime()
    if not os.path.exists('./error_log/'):
        os.mkdir('./error_log/')
    with open('./error_log/Error_%d%02d%02d_%02d.%02d.%02d.log'%(tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec), 'w') as f:
        f.write(content)
    shutMeDown()
    mainform.close()
    sys.exit(1)


#########################################################################
# 热键绑定
user32 = ctypes.windll.user32  #加载user32.dll
hkid1=101 # 选定TOP玩家/TOP玩家闪现
hkid2=102 # 选定JUG玩家/JUG玩家闪现
hkid3=103 # 选定MID玩家/MID玩家闪现
hkid4=104 # 选定ADC玩家/ADC玩家闪现
hkid5=105 # 选定SUP玩家/SUP玩家闪现
hkid6=106 # 重置玩家闪现时间
hkid7=107 # 玩家星界洞悉天赋切换
hkid8=108 # 玩家CD鞋切换

class Hotkey(threading.Thread):
    def __init__(self, father):
        super().__init__()
        self.father = father
        self.running = True
        self.hasF6 = False
        self.hasF7 = False
        self.hasF8 = False
        self.lastKey = ''

    def terminate(self):
        self.running = False

    def run(self):
        if not user32.RegisterHotKey(None, hkid1, 0, win32con.VK_F1):
            ErrorExit(r'''ERROR on 'user32.RegisterHotKey(None, hkid1, 0, win32con.VK_F1)'
Register Hotkey(F1) Fail.''', self.father)
        if not user32.RegisterHotKey(None, hkid2, 0, win32con.VK_F2):
            ErrorExit(r'''ERROR on 'user32.RegisterHotKey(None, hkid1, 0, win32con.VK_F2)'
Register Hotkey(F2) Fail.''', self.father)
        if not user32.RegisterHotKey(None, hkid3, 0, win32con.VK_F3):
            ErrorExit(r'''ERROR on 'user32.RegisterHotKey(None, hkid1, 0, win32con.VK_F3)'
Register Hotkey(F3) Fail.''', self.father)
        if not user32.RegisterHotKey(None, hkid4, 0, win32con.VK_F4):
            ErrorExit(r'''ERROR on 'user32.RegisterHotKey(None, hkid1, 0, win32con.VK_F4)'
Register Hotkey(F4) Fail.''', self.father)
        if not user32.RegisterHotKey(None, hkid5, 0, win32con.VK_F5):
            ErrorExit(r'''ERROR on 'user32.RegisterHotKey(None, hkid1, 0, win32con.VK_F5)'
Register Hotkey(F5) Fail.''', self.father)
        if not user32.RegisterHotKey(None, hkid6, 0, win32con.VK_F6):
            ErrorExit(r'''ERROR on 'user32.RegisterHotKey(None, hkid1, 0, win32con.VK_F6)'
Register Hotkey(F6) Fail.''', self.father)
        if not user32.RegisterHotKey(None, hkid7, 0, win32con.VK_F7):
            ErrorExit(r'''ERROR on 'user32.RegisterHotKey(None, hkid1, 0, win32con.VK_F7)'
Register Hotkey(F7) Fail.''', self.father)
        if not user32.RegisterHotKey(None, hkid8, 0, win32con.VK_F8):
            ErrorExit(r'''ERROR on 'user32.RegisterHotKey(None, hkid1, 0, win32con.VK_F8)'
Register Hotkey(F8) Fail.''', self.father)

        #以下为检测热键是否被按下，并在最后释放快捷键  
        try:  
            msg = ctypes.wintypes.MSG()  
            while self.running:
                if user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
                    if msg.message == win32con.WM_HOTKEY:  
                        if msg.wParam == hkid1:
                            if self.lastKey == 'F1': # 连按两次
                                self.father.recordCD(0, True) # 强制记录
                                self.lastKey = ''
                            if self.hasF6: # 重置CD
                                self.father.cd[0] = None
                                self.hasF6 = False
                            elif self.hasF7: # 切换星界洞悉状态
                                self.father.cdcb[0][0].toggle()
                                self.hasF7 = False
                            elif self.hasF8: # 切换CD鞋状态
                                self.father.cdcb[0][1].toggle()
                                self.hasF8 = False
                            else: # 记录CD
                                ret = self.father.recordCD(0)
                                if not ret:
                                    self.lastKey = 'F1'
                        elif msg.wParam == hkid2:
                            if self.lastKey == 'F2': # 连按两次
                                self.father.recordCD(1, True) # 强制记录
                                self.lastKey = ''
                            if self.hasF6: # 重置CD
                                self.father.cd[1] = None
                                self.hasF6 = False
                            elif self.hasF7: # 切换星界洞悉状态
                                self.father.cdcb[1][0].toggle()
                                self.hasF7 = False
                            elif self.hasF8: # 切换CD鞋状态
                                self.father.cdcb[1][1].toggle()
                                self.hasF8 = False
                            else: # 记录CD
                                ret = self.father.recordCD(1)
                                if not ret:
                                    self.lastKey = 'F2'
                        elif msg.wParam == hkid3:
                            if self.lastKey == 'F3': # 连按两次
                                self.father.recordCD(2, True) # 强制记录
                                self.lastKey = ''
                            if self.hasF6: # 重置CD
                                self.father.cd[2] = None
                                self.hasF6 = False
                            elif self.hasF7: # 切换星界洞悉状态
                                self.father.cdcb[2][0].toggle()
                                self.hasF7 = False
                            elif self.hasF8: # 切换CD鞋状态
                                self.father.cdcb[2][1].toggle()
                                self.hasF8 = False
                            else: # 记录CD
                                ret = self.father.recordCD(2)
                                if not ret:
                                    self.lastKey = 'F3'
                        elif msg.wParam == hkid4:
                            if self.lastKey == 'F4': # 连按两次
                                self.father.recordCD(3, True) # 强制记录
                                self.lastKey = ''
                            if self.hasF6: # 重置CD
                                self.father.cd[3] = None
                                self.hasF6 = False
                            elif self.hasF7: # 切换星界洞悉状态
                                self.father.cdcb[3][0].toggle()
                                self.hasF7 = False
                            elif self.hasF8: # 切换CD鞋状态
                                self.father.cdcb[3][1].toggle()
                                self.hasF8 = False
                            else: # 记录CD
                                ret = self.father.recordCD(3)
                                if not ret:
                                    self.lastKey = 'F4'
                        elif msg.wParam == hkid5:
                            if self.lastKey == 'F5': # 连按两次
                                self.father.recordCD(4, True) # 强制记录
                                self.lastKey = ''
                            if self.hasF6: # 重置CD
                                self.father.cd[4] = None
                                self.hasF6 = False
                            elif self.hasF7: # 切换星界洞悉状态
                                self.father.cdcb[4][0].toggle()
                                self.hasF7 = False
                            elif self.hasF8: # 切换CD鞋状态
                                self.father.cdcb[4][1].toggle()
                                self.hasF8 = False
                            else: # 记录CD
                                ret = self.father.recordCD(4)
                                if not ret:
                                    self.lastKey = 'F5'
                        elif msg.wParam == hkid6:
                            self.hasF6 = not self.hasF6
                            self.hasF7 = False
                            self.hasF8 = False
                        elif msg.wParam == hkid7:
                            self.hasF6 = False
                            self.hasF7 = not self.hasF7
                            self.hasF8 = False
                        elif msg.wParam == hkid8:
                            self.hasF6 = False
                            self.hasF7 = False
                            self.hasF8 = not self.hasF8

                    user32.TranslateMessage(ctypes.byref(msg))
                    user32.DispatchMessageA(ctypes.byref(msg))

        finally:
            for e in [hkid1, hkid2, hkid3, hkid4, hkid5, hkid6, hkid7, hkid8]:
                user32.UnregisterHotKey(None, e)



'''
星界洞悉 5%召唤师技能CD
明朗之靴 10%召唤师技能CD
'''


class MainForm(QWidget):
    def __init__(self):
        super().__init__()
        self.hotkey = Hotkey(self)  
        self.hotkey.start()
        self.minusCD_checked = [
            [False, False],
            [False, False],
            [False, False],
            [False, False],
            [False, False]
        ]
        self.minusCD = [0, 0, 0, 0, 0]
        self.cd = [None, None, None, None, None]
        self.bgcolor = (
            int(WARNING_COLOR[:2],16),
            int(WARNING_COLOR[2:4],16),
            int(WARNING_COLOR[4:],16)
        )
        self.initUI()
        self.showBoard = BoardForm(self)
        self.showBoard.hide()
        self.helpPage = None

    def initUI(self):
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        #######################################################
        # 首排文本框 用于展示位置信息（TOP, JUG, MID, ADC, SUP）
        # 后期将加入设置文本 可以由设定文件自定义
        style_sheet = r'color: black; font-size: 45px; font-weight: bold; text-align: center;'
        self.poslb = [
            QLabel('TOP'),
            QLabel('JUG'),
            QLabel('MID'),
            QLabel('ADC'),
            QLabel('SUP')
        ]
        for i,e in enumerate(self.poslb):
            e.setMinimumSize(140, 35)
            e.setMaximumSize(140, 35)
            e.setFont(QFont('SimHei'))
            e.setStyleSheet(style_sheet)
            self.grid.addWidget(e, 0, i)
        
        #######################################################
        # CheckBox组 用于设定天赋装备对召唤师技能CD的影响
        style_sheet = r'color: black; font-size: 20px; text-align: center;'
        self.cdcb = [
            (QCheckBox('星界洞悉'), QCheckBox('CD鞋')),
            (QCheckBox('星界洞悉'), QCheckBox('CD鞋')),
            (QCheckBox('星界洞悉'), QCheckBox('CD鞋')),
            (QCheckBox('星界洞悉'), QCheckBox('CD鞋')),
            (QCheckBox('星界洞悉'), QCheckBox('CD鞋'))
        ]
        tmp_list = [
            ((self.cdcb[0][0], self.cdcb[0][1]), (lambda x: self.skillCb(0, 0, x), lambda x: self.skillCb(0, 1, x))),
            ((self.cdcb[1][0], self.cdcb[1][1]), (lambda x: self.skillCb(1, 0, x), lambda x: self.skillCb(1, 1, x))),
            ((self.cdcb[2][0], self.cdcb[2][1]), (lambda x: self.skillCb(2, 0, x), lambda x: self.skillCb(2, 1, x))),
            ((self.cdcb[3][0], self.cdcb[3][1]), (lambda x: self.skillCb(3, 0, x), lambda x: self.skillCb(3, 1, x))),
            ((self.cdcb[4][0], self.cdcb[4][1]), (lambda x: self.skillCb(4, 0, x), lambda x: self.skillCb(4, 1, x)))
        ]
        for i,e in enumerate(tmp_list):
            for ef,ff in zip(e[0],e[1]):
                ef.setMinimumSize(140, 30)
                ef.setFont(QFont('SimHei'))
                ef.setStyleSheet(style_sheet)
                ef.stateChanged.connect(ff)
            self.grid.addWidget(e[0][0], 1, i)
            self.grid.addWidget(e[0][1], 2, i)

        #######################################################
        # 重置CD按钮
        style_sheet = r'color: red; font-size: 15px; text-align: center;'
        self.refreshbtn = [
            (QPushButton('重置CD'), lambda: self.refreshcd(0)),
            (QPushButton('重置CD'), lambda: self.refreshcd(1)),
            (QPushButton('重置CD'), lambda: self.refreshcd(2)),
            (QPushButton('重置CD'), lambda: self.refreshcd(3)),
            (QPushButton('重置CD'), lambda: self.refreshcd(4))
        ]
        for i,e in enumerate(self.refreshbtn):
            e[0].setMaximumSize(60,30)
            e[0].setFont(QFont('SimHei'))
            e[0].setStyleSheet(style_sheet)
            e[0].clicked.connect(e[1])
            self.grid.addWidget(e[0], 3, i)

        #######################################################
        # 计时文本
        # 注意这里的文本最多只能有两行 为了对齐 必须刚好是两行
        style_sheet = r'color: red; font-size: 20px; text-align: center;'
        self.timelb = [
            QLabel('未开始计时\n'),
            QLabel('未开始计时\n'),
            QLabel('未开始计时\n'),
            QLabel('未开始计时\n'),
            QLabel('未开始计时\n')
        ]
        for i,e in enumerate(self.timelb):
            e.setMinimumSize(140, 50)
            e.setMaximumSize(140, 50)
            e.setFont(QFont('SimHei'))
            e.setStyleSheet(style_sheet)
            self.grid.addWidget(e, 4, i)

        #######################################################
        # 填充label 空位
        tmp = QLabel('')
        tmp.setMaximumHeight(20)
        tmp.setMinimumHeight(20)
        self.grid.addWidget(tmp, 5, 0, 1, 5)

        #######################################################
        # 按钮行
        self.clearbtn = QPushButton('清空选择')
        self.clearbtn.clicked.connect(self.clearSelect)
        self.clearbtn.setFont(QFont('SimHei'))
        self.clearbtn.setStyleSheet(r'color: black; font-size: 22px;')
        self.clearbtn.setMinimumHeight(40)
        self.grid.addWidget(self.clearbtn, 6, 0)

        self.clearbtn = QPushButton('帮助')
        self.clearbtn.clicked.connect(self.helpPageOpen)
        self.clearbtn.setFont(QFont('SimHei'))
        self.clearbtn.setStyleSheet(r'color: black; font-size: 22px;')
        self.clearbtn.setMinimumHeight(40)
        self.grid.addWidget(self.clearbtn, 6, 2)

        self.startbtn = QPushButton('显示计时板')
        self.startbtn.setObjectName('btndown')
        self.startbtn.clicked.connect(self.startClicked)
        self.startbtn.setFont(QFont('SimHei'))
        self.startbtn.setStyleSheet(r'font-size: 22px;')
        self.startbtn.setMinimumHeight(40)
        self.grid.addWidget(self.startbtn, 6, 3)

        self.endbtn = QPushButton('隐藏计时板')
        self.endbtn.setObjectName('btndown')
        self.endbtn.clicked.connect(self.endClicked)
        self.endbtn.setFont(QFont('SimHei'))
        self.endbtn.setEnabled(False)
        self.endbtn.setStyleSheet(r'font-size: 22px;')
        self.endbtn.setMinimumHeight(40)
        self.grid.addWidget(self.endbtn, 6, 4)

        #######################################################
        # 计时器 用于刷新文本
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refreshTime)
        self.timer.start(200)
        
        #######################################################
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setGeometry(0, 0, 0, 0) # 将在resizeEvent中重设
        self.setWindowTitle('lol快捷计时工具Ver0.1.0 - Made by Moying')
        self.setWindowIcon(QIcon('icon.ico'))
        self.show()

    def center(self):
        # 居中
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) / 2,
            (screen.height() - size.height()) / 2.3
        )

    def recordCD(self, index, force=False):
        if self.cd[index] != None and not force:
            return False
        tm = round(300 * ((100-self.minusCD[index])/100))
        self.cd[index] = time.time() + tm
        return True

    def skillCb(self, index, skillIndex, state):
        # 当减CD选项被激活时 记录并计算当前减CD
        self.minusCD_checked[index][skillIndex] = (state == Qt.Checked)
        if skillIndex == 0:
            self.showBoard.cd1lb[index].setVisible(self.minusCD_checked[index][skillIndex])
        elif skillIndex == 1:
            self.showBoard.cd2lb[index].setVisible(self.minusCD_checked[index][skillIndex])
        self.minusCD[index] = (5 if self.minusCD_checked[index][0] else 0) + (10 if self.minusCD_checked[index][1] else 0)

    def refreshcd(self, index):
        # 重置对应位置的技能CD记录
        self.cd[index] = 0

    def clearSelect(self):
        # 取消所有选中情况
        for e in self.cdcb:
            for ef in e:
                ef.setChecked(False)

    def helpPageOpen(self):
        if self.helpPage == None:
            self.helpPage = HelpForm()
        else:
            self.helpPage.show()
            self.helpPage.setWindowState(Qt.WindowActive)

    def startClicked(self):
        # 启用计时面板并最小化自己
        self.showBoard.show()
        self.startbtn.setEnabled(False)
        self.endbtn.setEnabled(True)
        self.setWindowState(Qt.WindowMinimized)

    def endClicked(self):
        # 关闭计时面板
        self.showBoard.hide()
        self.startbtn.setEnabled(True)
        self.endbtn.setEnabled(False)

    def refreshTime(self):
        for i,e in enumerate(self.cd):
            if e == None:
                tm = 0
            else:
                tm = e-time.time()
                if tm<=0:
                    self.cd[i] = None
                    tm = 0
                else:
                    tm = int(tm)
            self.timelb[i].setText('闪现:%ds\n快捷键:F%d'%(tm,i+1))
            self.showBoard.timelb[i].setText('闪现:%ds'%(tm))
            if tm == 0:
                self.showBoard.timelb[i].setStyleSheet(r'border-top: 2px solid gray; color: black; font-size: 15px; font-weight: bold;')
                self.showBoard.widgets[i].setStyleSheet(r'background-color: #%s'%(FLASH_COLOR))
            else:
                self.showBoard.timelb[i].setStyleSheet(r'border-top: 2px solid gray; color: %s; font-size: 15px; font-weight: bold;'%(TICKING_TEXT_COLOR))
                if tm < TIME_CHANGE_COLOR:
                    cc = (hex(int(e+(255-e)*(tm/TIME_CHANGE_COLOR)))[2:] for e in self.bgcolor)
                    cc = ''.join(cc)
                else:
                    cc = 'ffffff'
                self.showBoard.widgets[i].setStyleSheet(r'background-color: #%s'%(cc))
    
    def resizeEvent(self, event):
        # 锁定窗体大小
        if event.oldSize().width() == -1 and event.oldSize().height() == -1:
            self.setFixedSize(event.size())
            self.center()

    def closeEvent(self, event):
        for e in [hkid1, hkid2, hkid3, hkid4, hkid5, hkid6, hkid7, hkid8]:
            user32.UnregisterHotKey(None, e)
        self.hotkey.terminate()
        if self.helpPage != None:
            self.helpPage.close()
        try:
            self.showBoard.close()
        except:
            pass
        shutMeDown()

####################################################################################

class BoardForm(QWidget):
    def __init__(self, father):
        super().__init__()
        self.father = father
        self.initUI()

    def initUI(self):
        self.grid = QGridLayout()
        self.grid.setContentsMargins(0,0,5,5)
        self.setLayout(self.grid)

        #######################################################
        # 五个子区域 分别对应5个位置
        self.widgets = [
            QWidget(),
            QWidget(),
            QWidget(),
            QWidget(),
            QWidget()
        ]
        for i,e in enumerate(self.widgets):
            e.setMinimumSize(90, 90)
            e.setMaximumSize(90, 90)
            e.setFont(QFont('SimHei'))
            e.setStyleSheet(r'background-color: #ffd460;')
            self.grid.addWidget(e, i, 0)

        #######################################################
        # 初始化5个区域的控件
        self.poslb = []
        self.timelb = []
        self.cd1lb = []
        self.cd2lb = []
        try:
            self.cd1pic = QPixmap('./images/cd1.png')
            self.cd2pic = QPixmap('./images/cd2.png')
        except:
            ErrorExit(r'''Error on 'self.cd1pic = QPixmap('./images/cd1.png')
self.cd2pic = QPixmap('./images/cd2.png')'
Fail to load pictures
''', self.father)
        self.initSubUI(self.widgets[0], 'TOP')
        self.initSubUI(self.widgets[1], 'JUG')
        self.initSubUI(self.widgets[2], 'MID')
        self.initSubUI(self.widgets[3], 'ADC')
        self.initSubUI(self.widgets[4], 'SUP')

        #######################################################
        # 无边框、置顶和窗口透明
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        #######################################################
        # 设定位置
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, (screen.height()-490)/4, 90, 490)
        self.setMaximumSize(90, 490)
        self.setMinimumSize(90, 490)
        self.setWindowTitle('lol计时面板')
        self.show()

    def initSubUI(self, target, pos):
        # 子区域初始化
        self.poslb.append(QLabel(pos, target))
        self.poslb[-1].setFont(QFont('SimHei'))
        self.poslb[-1].setAlignment(Qt.AlignCenter)
        self.poslb[-1].setStyleSheet(r'color: black; font-size: 30px; font-weight: bold;')
        self.poslb[-1].setGeometry(0, 0, 90, 30)

        self.timelb.append(QLabel('闪现:0s', target))
        self.timelb[-1].setFont(QFont('SimHei'))
        self.timelb[-1].setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.timelb[-1].setStyleSheet(r'border-top: 2px solid gray; color: black; font-size: 15px; font-weight: bold;')
        self.timelb[-1].setGeometry(0, 30, 90, 40)

        self.cd1lb.append(QLabel(target))
        self.cd1lb[-1].setVisible(False)
        self.cd1lb[-1].setPixmap(self.cd1pic)
        self.cd1lb[-1].setScaledContents(True)
        self.cd1lb[-1].setGeometry(50, 70, 20, 20)

        self.cd2lb.append(QLabel(target))
        self.cd2lb[-1].setVisible(False)
        self.cd2lb[-1].setPixmap(self.cd2pic)
        self.cd2lb[-1].setScaledContents(True)
        self.cd2lb[-1].setGeometry(70, 70, 20, 20)

class HelpForm(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        text = r'''
<h2>请使用<b>窗口模式</b>或<b>无边框模式</b>进行游戏，因为计时板无法在全屏游戏中显示！</h2>
打开以后直接点击"<b>显示计时板</b>"即可。

    计时板会显示在屏幕左侧，上单(TOP),打野(JUG),中单(MID),ADC,辅助(SUP)分别对应着<b>按键F1,F2,F3,F4,F5</b>。
    这5个按键在游戏里<b>默认是</b>切屏观察队友，当然绝大部分普通玩家都没有切屏的需求，可以酌情<b>解绑</b>游戏里的按键。
    点击对应的按键，就会记录对应位置玩家"交闪"。闪现<b>默认</b>是300秒，会根据<b>你设置的天赋和装备情况</b>(见下方)而计算减CD。
    先按<b>F6</b>，再按<b>对应位置按键</b>，会把对应位置闪现时间<b>重置到0秒</b>。
    先按<b>F7/F8</b>，再按<b>对应位置按键</b>，会切换对应位置的"<b>星界洞悉</b>"/"<b>CD鞋</b>"状态。
    如果某个位置的闪现时间<b>还未到0s</b>，此时按下对应按键是<b>没有反应的</b>(为了防止误按)。如果<b>连按两下按键</b>，就会<b>覆盖</b>之前的记录。
    
    闪现CD剩余30秒的时候，计时板的颜色会慢慢变成绿色。当完全冷却时，计时板会变成黄色。

<b>Made by Moying</b>'''.replace('\t','&emsp;').replace(' ','&nbsp;').replace('\n','<br />')
        tmp = QLabel(self)
        tmp.setTextFormat(Qt.RichText)
        tmp.setText(text)
        tmp.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        tmp.setFont(QFont('SimHei', 13))
        tmp.setWordWrap(True)
        tmp.setGeometry(10, -30, 780, 680)

        self.setGeometry(0, 0, 800, 650)
        self.setWindowTitle('帮助')
        self.setWindowIcon(QIcon('./icon.ico'))
        self.center()
        self.show()

    def center(self):
        # 居中
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) / 2,
            (screen.height() - size.height()) / 2.3
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(r'''
    QPushButton#btndown:disabled {
        color: gray;
        background-color: lightgray;
        border: 0;
    }
    ''')
    form = MainForm()
    sys.exit(app.exec_())
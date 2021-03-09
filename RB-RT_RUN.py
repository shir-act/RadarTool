import sys
from socket import gethostbyaddr, herror
from src.cmd_modules.Mimo77L import Mimo77L
import src.cmd_modules.RadarProc as RadarProc
import matplotlib as mpl
from matplotlib import figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FCA
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NTb
from PyQt5 import QtGui
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QApplication, QPushButton, QLineEdit, QMessageBox, QAction,
                             QMenu, QRadioButton, QButtonGroup, QGridLayout, QLabel, QListWidget, QScrollArea,
                             QVBoxLayout, QComboBox, QFileDialog)
import numpy as np
import pandas as pd
import cv2
import os
import glob

mpl.use("Qt5Agg")

app = QApplication(sys.argv)


# MainWindow-class
class MainWindow(QMainWindow):
#---QMainWindow.__init__-function---#
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

#-------Define RadarTool version-------#
        self.version = "v0.0.0"

#-------Define standard RadarBook-IP-------#
        self.IP_Brd = "192.168.1.1"

#-------Define User-IP-------#
        self.IP_Usr = "192.168.1.10"

#-------Define connection-status-variable-------#
        self.connected = False

#-------Define Cancel-variable-------#
        self.cancel = False

#-------Define Lock-Variable-------#
        self.Lock = False
        global lock
        lock = False

#-------Define original StyleSheet-------#
        self.origStyleSheet = self.styleSheet()

#-------Define Standard-Cfg-------#
        self.BCfg = {}
        self.BCfg["fStrt"] = 76e9
        self.BCfg["fStop"] = 79e9
        self.BCfg["TRampUp"] = 25.6e-6
        self.BCfg["TRampDo"] = 1e-6
        self.BCfg["TInt"] = 1000e-3
        self.BCfg["Tp"] = 126.6e-6
        self.BCfg["N"] = 504
        self.BCfg["Np"] = 4
        self.BCfg["NrFrms"] = 1000
        self.BCfg["TxSeq"] = np.array([1, 2, 3, 4])
        self.BCfg["IniEve"] = 1
        self.BCfg["IniTim"] = 2e-3
        self.BCfg["CfgTim"] = 30e-6
        self.BCfg["ExtEve"] = 0
        self.BCfg["Start"] = None

        self.StdCfg = self.BCfg
        self.TCfg = self.BCfg

#-------define Beamforming-Config-------#
        Chn = np.arange(32)
        Chn = np.delete(Chn,[7, 15, 23])

        self.BFCfg = {}
        self.BFCfg["fs"] = -1
        self.BFCfg["kf"] = -1
        self.BFCfg["RangeFFT"] = 1024
        self.BFCfg["AngFFT"] = 256
        self.BFCfg["Abs"] = 1
        self.BFCfg["Ext"] = 1
        self.BFCfg["RMin"] = 1
        self.BFCfg["RMax"] = 10
        self.BFCfg["CalData"] = None
        self.BFCfg["ChnOrder"] = Chn
        self.BFCfg["NIni"] = 1
        self.BFCfg["RemoveMean"] = 1
        self.BFCfg["Window"] = 1
        self.BFCfg["dB"] = 1
        self.BFCfg["FuSca"] = 2/2048


        self.SBCfg = self.BFCfg
        self.TBCfg = self.BFCfg

#-------define standard RangeDoppler-Config
        self.RDCfg = {}
        self.RDCfg["fs"] = -1
        self.RDCfg["kf"] = -1
        self.RDCfg["RangeFFT"] = 1024
        self.RDCfg["VelFFT"] = 1024
        self.RDCfg["Abs"] = 1
        self.RDCfg["Ext"] = 1
        self.RDCfg["RMin"] = 1
        self.RDCfg["RMax"] = 10
        self.RDCfg["N"] = self.BCfg["N"]
        self.RDCfg["Np"] = self.BCfg["Np"]
        self.RDCfg["RemoveMean"] = 1
        self.RDCfg["Window"] = 1
        self.RDCfg["dB"] = 1
        self.RDCfg["FuSca"] = 2/2048
        self.RDCfg["fc"] = (self.BCfg["fStrt"] + self.BCfg["fStop"]) / 2
        self.RDCfg["Tp"] = self.BCfg["Tp"]
        self.RDCfg["ThresdB"] = 0

        self.SRCfg = self.RDCfg
        self.TRCfg = self.RDCfg


#-------define standard RangeProfile-Config
        self.RPCfg = {}
        self.RPCfg["fs"] = -1
        self.RPCfg["kf"] = -1
        self.RPCfg["NFFT"] = 4096
        self.RPCfg["Abs"] = 1
        self.RPCfg["Ext"] = 1
        self.RPCfg["RMin"] = 1
        self.RPCfg["RMax"] = 10
        self.RPCfg["RemoveMean"] = 1
        self.RPCfg["Window"] = 1
        self.RPCfg["XPos"] = 1
        self.RPCfg["dB"] = 1
        self.RPCfg["FuSca"] = 2/2048

        self.SPCfg = self.RPCfg
        self.TPCfg = self.RPCfg

#-------define standard TxChn and TxPwr-------#
        self.TxChn = 1
        self.TxPwr = 61

#-------start GUI-Creation-------#
        self.start_gui()

#---GUI-startup-function---#
    def start_gui(self):
#-------Create matplotlib canvas and toolbar-------#
        self.figure = figure.Figure()
        self.canvas = FCA(self.figure)
        self.toolbar = NTb(self.canvas, self)
        self.figure.subplots_adjust(top=0.86, bottom=0.05, left=0.085, right=0.74, hspace=0, wspace=0)

#-------Create QButtonGroup for every type of connection and a way to disconnect-------#
        self.Con_Group = QButtonGroup()
        self.set_USB = QRadioButton("USB")
        self.set_USB.setToolTip("needs a RadarBook-USB-PC connection to work")
        self.set_USB.setChecked(False)
        self.set_W_LAN = QRadioButton("LAN or WLAN")
        self.set_W_LAN.setToolTip("needs a RadarBook-(W)LAN-PC connection to work")
        self.set_W_LAN.setChecked(True)
        self.Con_Group.addButton(self.set_USB)
        self.Con_Group.addButton(self.set_W_LAN)

#-------Create a Button to connect to the RadarBook
        self.Con_PshBtn = QPushButton("connect...")
        self.Con_PshBtn.setToolTip("try to connect to INRAS-RadarBook")
        self.Con_PshBtn.clicked.connect(self.CON_TRY)

#-------Create a Button that stops/resets Measurement and closes QApplication
        self.Quit_PshBtn = QPushButton("quit...")
        self.Quit_PshBtn.setToolTip("Stops the measurement, resets connected Board and closes RadarBook-RadarTool.exe")
        self.Quit_PshBtn.clicked.connect(self.QUIT_MW)

#-------Create a Button that stops/resets Measurement without disconnecting
        self.Rst_PshBtn = QPushButton("reset Board...")
        self.Rst_PshBtn.setToolTip("Stops the measurement and resets the connected Board")
        self.Rst_PshBtn.clicked.connect(self.BRD_RST)
        self.Rst_PshBtn.setEnabled(False)

#-------Create a RadarBook-RadarTool-version-display
        self.Vrs_Lbl = QLabel("RadarBookRadarTool.exe " + str(self.version))
        self.Vrs_Lbl.setFont(QtGui.QFont("Times", 8, QtGui.QFont.Bold))
        self.Vrs_Lbl.setFixedHeight(15)

#-------Create a Connectionstatus-display
        self.Con_Sts_Pic = QLabel()
        self.Con_Sts_Pic.setPixmap(QtGui.QPixmap("pics/red.png").scaled(30, 30))
        self.Con_Sts_Pic.setFixedSize(50, 30)
        self.Con_Sts_Txt = QLabel("Status:")
        self.Con_Sts_Txt.setFixedSize(125, 30)
        self.Con_Sts_Txt.setFont(QtGui.QFont("Times", 20, QtGui.QFont.Bold))
        self.Con_Sts_Leg = QLabel("Connection-light:\n"
                                  "red:________no Connection!\n"
                                  "yellow:_____working on Connection!\n"
                                  "green:______Connected!")
        self.Con_Sts_Leg.setFont(QtGui.QFont("Times", 7))

#-------Create a Button to turn on/off Board
        self.Brd_Pwr_Btn = QPushButton("Power: ?")
        self.Brd_Pwr_Btn.setCheckable(True)
        self.Brd_Pwr_Btn.setToolTip("Turn on/off the Power!")
        self.Brd_Pwr_Btn.clicked.connect(self.BRD_PWR)
        self.Brd_Pwr_Btn.setEnabled(False)

#-------Create a Button to start FMCW-Measurements
        self.Brd_Msr_FMCW = QPushButton("BeamformingUla:\nRange|Angle...")
        self.Brd_Msr_FMCW.setToolTip("starts the FMCW measurement with before set variables")
        self.Brd_Msr_FMCW.clicked.connect(self.BRD_MSR_FMCW)
        self.Brd_Msr_FMCW.setEnabled(False)

#-------Create a Button to start RangeDoppler-Measurements
        self.Brd_Msr_RD = QPushButton("RangeDoppler:\nRange|Velocity...")
        self.Brd_Msr_RD.setToolTip("starts the RangeDoppler measurement with before set variables")
        self.Brd_Msr_RD.clicked.connect(self.BRD_MSR_RD)
        self.Brd_Msr_RD.setEnabled(False)

#-------Create a Button for RangeProfile-Measurements
        self.Brd_Msr_RP = QPushButton("RangeProfile:\nRange|dBV...")
        self.Brd_Msr_RP.setToolTip("starts the RangeProfile measurement with before set variables")
        self.Brd_Msr_RP.clicked.connect(self.BRD_MSR_RP)
        self.Brd_Msr_RP.setEnabled(False)

#-------Create a Button to cancel measurements
        self.Brd_Ccl = QPushButton("cancel...")
        self.Brd_Ccl.setToolTip("stop all measurements at the next possible point")
        self.Brd_Ccl.clicked.connect(self.BRD_MSR_CNCL)
        self.Brd_Ccl.setEnabled(False)

#-------Create a Button to show active Config etc.
        self.Brd_Shw_Cfgs = QPushButton("showConfigs...")
        self.Brd_Shw_Cfgs.setToolTip("show a lot of Config-Information on Screen")
        self.Brd_Shw_Cfgs.clicked.connect(self.CFG_SHW)

#-------Create and fill up menubar
        self.mnbr = self.menuBar()

        self.mnbr_file = QMenu()
        self.mnbr_opts = QMenu()
        self.mnbr_info = QMenu()
        self.mnbr_file = self.mnbr.addMenu("&file")
        self.mnbr_opts = self.mnbr.addMenu("&options")
        self.mnbr_info = self.mnbr.addMenu("&info")

#-------Add an info-section to the
        self.mnbr_info_gnrl = QAction("general information...")
        self.mnbr_info_gnrl.triggered.connect(self.SHW_INFO)
        self.mnbr_info.addAction(self.mnbr_info_gnrl)

#-------Add special Board-info-section
        self.mnbr_info_Brd = QAction("Board...")
        self.mnbr_info_Brd.triggered.connect(self.BRD_INFO)
        self.mnbr_info.addAction(self.mnbr_info_Brd)
        self.mnbr_info_Brd.setEnabled(False)

#-------Add configmenu to optionmenu
        self.mnbr_opts_cfg = QAction("Board-Config...")
        self.mnbr_opts_cfg.triggered.connect(self.BRD_CFG)
        self.mnbr_opts.addAction(self.mnbr_opts_cfg)

#-------Add Beamforming-Config to optionmenu
        self.mnbr_opts_bmf = QAction("Beamforming-Config(FMCW)...")
        self.mnbr_opts_bmf.triggered.connect(self.BMF_CFG)
        self.mnbr_opts.addAction(self.mnbr_opts_bmf)

#-------Add RangeDoppler-Config to optionmenu
        self.mnbr_opts_rd = QAction("RangeDoppler-Config...")
        self.mnbr_opts_rd.triggered.connect(self.RD_CFG)
        self.mnbr_opts.addAction(self.mnbr_opts_rd)

#-------Add RangeProfile-Config to optionmenu
        self.mnbr_opts_rp = QAction("RangeProfile-Config...")
        self.mnbr_opts_rp.triggered.connect(self.RP_CFG)
        self.mnbr_opts.addAction(self.mnbr_opts_rp)

#-------Add Pre-set-Configs
        self.mnbr_opts_ps = QAction("Pre-Set-Configs...")
        self.mnbr_opts_ps.triggered.connect(self.CFG_PS)
        self.mnbr_opts.addAction(self.mnbr_opts_ps)

#-------Add a clear-figure-action
        self.mnbr_file_clf = QAction("clear figure...")
        self.mnbr_file_clf.triggered.connect(self.FGR_CLR)
        self.mnbr_file_clf.setShortcut("CTRL+R")
        self.mnbr_file.addAction(self.mnbr_file_clf)

#-------Add video function action
        self.mnbr_file_video = QAction("get Video...")
        self.mnbr_file_video.triggered.connect(self.VIDEO)
        self.mnbr_file.addAction(self.mnbr_file_video)

#-------Add data function action
        self.mnbr_file_data = QAction("get Data...")
        self.mnbr_file_data.triggered.connect(self.DATA)
        self.mnbr_file.addAction(self.mnbr_file_data)

#-------Create the MainWindow and MainWindowLayout
        self.MW = QWidget()
        self.MWLayout = QGridLayout()
        self.MWLayout.addWidget(self.canvas, 0, 0, 11, 11)
        self.MWLayout.addWidget(self.Con_Sts_Txt, 0, 0, 1, 1)
        self.MWLayout.addWidget(self.Con_Sts_Pic, 0, 1, 1, 1)
        self.MWLayout.addWidget(self.Con_Sts_Leg, 0, 2, 1, 1)
        self.MWLayout.addWidget(self.set_USB, 0, 9, 1, 1)
        self.MWLayout.addWidget(self.set_W_LAN, 0, 10, 1, 1)
        self.MWLayout.addWidget(self.toolbar, 1, 0, 1, 11)
        self.MWLayout.addWidget(self.Con_PshBtn, 1, 9, 1, 2)
        self.MWLayout.addWidget(self.Brd_Pwr_Btn, 2, 0, 1, 1)
        self.MWLayout.addWidget(self.Brd_Msr_FMCW, 3, 0, 1, 1)
        self.MWLayout.addWidget(self.Brd_Msr_RD, 4, 0, 1, 1)
        self.MWLayout.addWidget(self.Brd_Ccl, 6, 0, 1, 1)
        self.MWLayout.addWidget(self.Brd_Msr_RP, 5, 0, 1, 1)
        self.MWLayout.addWidget(self.Rst_PshBtn, 7, 0, 1, 1)
        self.MWLayout.addWidget(self.Brd_Shw_Cfgs, 8, 0, 1, 1)
        self.MWLayout.addWidget(self.Vrs_Lbl, 10, 10, 1, 1)

#-------set MainWindowLayout to defined MWLayout
        self.MW.setLayout(self.MWLayout)
        self.setCentralWidget(self.MW)
        self.setGeometry(220, 420, 1080, 640)
        self.showMaximized()
        self.setWindowTitle("RB-RT --- RadarBook-RadarTool.exe")
        self.show()

#---closeEvent-Function
    def closeEvent(self, event):
#-------safety-question
        Qstn = self.errmsg("Close RB-RT?", "Are you sure you want to quit?", "q")
#-------check answer and continue with closing or igrnoring
        if Qstn == 0:
            self.Lock = False
            super(MainWindow, self).closeEvent(event)
            self.QUIT_MW()
            app = QApplication(sys.argv)
            app.closeAllWindows()
            app.quit()
            app.exit()
        else:
            event.ignore()

#---function with QMessageBox displaying Errors
    def errmsg(self, title="critError!", text="Error-type unknown!", icon="c"):
#-------set icon type
        if icon == "c":
            icon = QMessageBox.Critical
        elif icon == "i":
            icon = QMessageBox.Information
        elif icon == "w":
            icon = QMessageBox.Warning
        elif icon == "q":
            icon = QMessageBox.Question

#-------create QMessageBox
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon)

#-------set diffrent Buttons if icon == "q"
        if icon == QMessageBox.Question:
            msg.addButton(QPushButton("Yes!"), QMessageBox.YesRole)
            msg.addButton(QPushButton("No!"), QMessageBox.NoRole)
        else:
            msg.addButton(QMessageBox.Ok)

#-------execute QMessageBox and receive result
        result = msg.exec_()

#-------return result if icon == "q"
        if icon == QMessageBox.Question:
            return result

#---delete Widgets in layout-function
    def deleteLayout(self, layout):
#-------check if widgets are in layout
        if layout is not None:

#-----------loop as long as widgets are in layout and delete them
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.deleteLayout(item.layout())

#---Quit-programm-function
    def QUIT_MW(self):
#-------check if a connection is active and if so reset Board, disable Power and close connection
        if self.connected:
            self.Board.BrdRst()
            self.Board.BrdPwrDi()
            self.Board.ConClose()
            self.connected = False
#-------close RadarBook-Radartool.exe and quit QApplication
        self.close()
        app = QApplication(sys.argv)
        app.closeAllWindows()
        app.quit()

#-------try to close cfg_Wndw 4 safetyreasons
        try:
            self.Cfg_Wndw.close()

#-------except if it did not exist
        except AttributeError:
            pass

#-------try to close bmf_cfg-Wndw 4 safetyreasons
        try:
            self.Bmf_Wndw.close()

#-------except if not existed
        except AttributeError:
            pass

#-------try to close rd_cfg-Wndw 4 safetyreasons
        try:
            self.RD_Wndw.close()

#-------except if not existing
        except AttributeError:
            pass

#-------try to close rp_cfg_wndw 4 safetyreasons
        try:
            self.RP_Wndw.close()

#-------except if not existing
        except AttributeError:
            pass

#-------try to close PresetWindow
        try:
            self.PS_Wndw.close()

#-------except if not existing
        except AttributeError:
            pass

#-------try to close BrdInfo
        try:
            self.Brd_Info_Wndw.close()

#-------except if not existing
        except AttributeError:
            pass

#-------try to close infowindow
        try:
            self.info.close()

#-------except if not existing
        except AttributeError:
            pass

#-------try to close videowindow
        try:
            self.name_Wndw.close()

#-------except if not existing
        except AttributeError:
            pass

#-------try to close datawindow
        try:
            self.data_Wndw.close()

#-------except if not existing
        except AttributeError:
            pass

#-------try to close videodatawindow
        try:
            self.VD_Wndw.close()

#-------except if not existing
        except AttributeError:
            pass

#---Reset Board and disable Power
    def BRD_RST(self):
#-------Security-question
        Qstn = self.errmsg("Are you sure?", "Do you want to continue reseting and powering-off the Board?\n"
                           "Connection is not lost during this process!", "q")

#-------check answer and continue or abort after checking
        if Qstn == 0:
            cont = True
        elif Qstn == 1:
            cont = False
        else:
            cont = False

#-------check if a connection is available and reset Board and disable Power
        if self.connected and cont:
            self.Board.BrdRst()
            self.Board.BrdPwrDi()

#-------if not connected or answer=No
        else:
            if cont:
                self.errmsg("ConnectionError!", "There is no Board connected to Reset!", "i")
            else:
                pass

#---Connection-Try-function
    def CON_TRY(self):
#-------change Con_Sts_Pic to yellow.png
        self.Con_Sts_Pic.setPixmap(QtGui.QPixmap("pics/yellow.png").scaled(30, 30))
#-------Find active QRadioButton
        try:
            if self.set_USB.isChecked():
                self.CON_USB()
            elif self.set_W_LAN.isChecked():
                self.CON_W_LAN()
            else:
                raise TypeError

#-------Except any errors that may come up and if one does change Con_Sts_Pic to red.png
        except TypeError:
            self.Con_Sts_Pic.setPixmap(QtGui.QPixmap("pics/red.png").scaled(30, 30))
            self.errmsg("TypeError!", "No connection-type selected!\nPlease choose between USB or (W)LAN!", "i")

#---USB-connection-function
    def CON_USB(self):
#-------Define Board-variable for further steps and set Con_Sts_Pic to green.png if no Errors occur
        try:
            self.Board = Mimo77L("Usb")
            self.Con_Sts_Pic.setPixmap(QtGui.QPixmap("pics/green.png").scaled(30, 30))
#-----------set self.connected to true
            self.connected = True

#-------Except Error if Board is not found and set Con_Sts_Pic to red.png if an Error occurs
        except TypeError:
            self.Con_Sts_Pic.setPixmap(QtGui.QPixmap("pics/red.png").scaled(30, 30))
            self.errmsg("ConnectionError!", "Please check your USB-connection!\nTry again if check is finished!", "w")

#---(W)LAN-connection-function
    def CON_W_LAN(self):
#-------Define Board-variable for further steps and set Con_Sts_Pic to green.png if no Errors occur
        try:
            self.Board = Mimo77L("PNet", self.IP_Brd)
#-----------Check if Board responds (is connected) and if so set Con_Sts_Pic to green.png an set self.connected to true
            try:
                self.Board.BrdDispSts()
                self.Con_Sts_Pic.setPixmap(QtGui.QPixmap("pics/green.png").scaled(30, 30))
                self.connected = True
#---------------continue with CON_DNE
                self.CON_DNE()
#-----------If Board is not reachable, except Error and raise ConnectionError
            except IndexError:
                raise ConnectionError

#-------Except Error if Board is not found and set Con_Sts_Pic to red.png
        except ConnectionError:
            self.Con_Sts_Pic.setPixmap(QtGui.QPixmap("pics/red.png").scaled(30, 30))
#-----------Ask for IPv4-address-check
            Qstn = self.errmsg("ConnectionError!", "Please check your WiFi- or cable-connection!\nDo you want to check "
                               "the IPv4-adress of the computer?", "q")
#-----------check if answer is yes or no and check IPv4 if yes
            if Qstn == 0:
                try:
                    IPv4 = gethostbyaddr("192.168.1.10")
                    print("found IPv4-adress: " + str((IPv4[2])[0]) + " at Ethernet-port named: " + IPv4[0])
                    self.errmsg("ConnectionError!", "Correct IPv4-adress has been found!\nMake sure all cables are "
                                "plugged in or connection with the right WiFi is active!\nIf your PC has multiple "
                                "Ethernet-ports, make sure the right one is used!", "w")
                except herror:
                    self.errmsg("IPConfigError!", "Please try changing your IPv4-adress!", "c")

            elif Qstn == 1:
                self.errmsg("ConnectionError!", "Check if you're connected with the right WiFi if wireless access is "
                            "used!\nIf you want to access via Ethernet, check if all cables are plugged in!", "i")
            else:
                self.errmsg("ConnectionError!", "Check if you're connected with the right WiFi if wireless access is "
                            "used!\nIf you want to access via Ethernet, check if all cables are plugged in!", "i")

#---Connection-Done function
    def CON_DNE(self):
#-------safetycheck if connection is true
        if self.connected == False:
            self.errmsg("TimeOutError", "Connection to Board has been lost!\nTry connecting again!", "c")
            return
#-------continue with changeing the connect-button
        else:
            self.Con_PshBtn.setText("disconnect...")
            self.Con_PshBtn.setToolTip("stop connection with current Board!")
            self.Con_PshBtn.disconnect()
            self.Con_PshBtn.clicked.connect(self.CON_DSC)
#-----------Enable Powercontrol
            self.Brd_Pwr_Btn.setText("Power: OFF")
            self.Brd_Pwr_Btn.setEnabled(True)
#-----------Enable Measurements
            self.Brd_Msr_FMCW.setEnabled(True)
            self.Brd_Msr_RD.setEnabled(True)
            self.Brd_Msr_RP.setEnabled(True)
#-----------Enable ResetButton
            self.Rst_PshBtn.setEnabled(True)
#-----------Enable BoardInfo
            self.mnbr_info_Brd.setEnabled(True)

#---disconnect function
    def CON_DSC(self):
#-------disable and reset Power Control
        try:
            self.Board.BrdRst()
            self.Board.BrdPwrDi()
            self.Brd_Pwr_Btn.setChecked(False)
            self.Brd_Pwr_Btn.setText("Power: ?")
            self.Brd_Pwr_Btn.setEnabled(False)
#-----------disable Measurement
            self.Brd_Msr_FMCW.setEnabled(False)
            self.Brd_Msr_RD.setEnabled(False)
            self.Brd_Msr_RP.setEnabled(False)
#-----------disable ResetButton
            self.Rst_PshBtn.setEnabled(False)
#-----------disable BoardInfo
            self.mnbr_info_Brd.setEnabled(False)

#-------except AttributeError if no Connection is obtained but disconnect is tried
        except AttributeError:
            pass

#-------erase Board-Variable reset connection variable and set Con_Sts_Pic to red.png
        self.Board = None
        self.connected = False
        self.Con_Sts_Pic.setPixmap(QtGui.QPixmap("pics/red.png").scaled(30, 30))

#-------change disconnect button back to connect button
        self.Con_PshBtn.setText("connect...")
        self.Con_PshBtn.setToolTip("try to connect to INRAS-RadarBook")
        self.Con_PshBtn.clicked.connect(self.CON_TRY)

#---create a little window with information
    def SHW_INFO(self):
#-------create Window
        self.info = QWidget()

#-------Add a Label with info
        lbl = QLabel()
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setText("Radarbook-Radartool:\n"+self.version+"\ncreated by shir\n\nThis Tool has been created for:\n"
                    "INRAS RadarBook 'Mimo-77-Tx4Rx8'\n\nRadarbook IPv4:\n"+self.IP_Brd+"\nrequired User IPv4:\n"+self.IP_Usr)

#-------Layout
        lay = QGridLayout()
        lay.addWidget(lbl, 0, 0, 1, 1)

#-------show window
        self.info.setLayout(lay)
        self.info.resize(256, 128)
        self.info.setWindowTitle("Information")
        self.info.show()

#---Clear-figure-function
    def FGR_CLR(self):
        self.figure.clear()
        self.canvas.draw()

#---Board-info-function
    def BRD_INFO(self):
#-------get BoardInfo
        self.Brd_RfVers = self.Board.RfGetVers()
        self.Brd_RfVers = QLabel("RadarBook-Frontendversion: " + str(self.Brd_RfVers))

        self.Brd_Name = self.Board.Get("Name")
        self.Brd_Name = QLabel("Name of Board: " + str(self.Brd_Name))

        self.Brd_frqncy_SamplingClock = self.Board.Get("fAdc")
        self.Brd_frqncy_SamplingClock = QLabel("Frequency SamplingClock: " + str(self.Brd_frqncy_SamplingClock * 1e-6) + " [MHz]")

        self.Brd_frqncy_PostCIC = self.Board.Get("fs")
        self.Brd_frqncy_PostCIC = QLabel("Frequency Post-CIC-Filter: " + str(self.Brd_frqncy_PostCIC * 1e-6) + " [MHz]")

        self.BrdDispInf = self.Board.BrdDispInf()

        self.Brd_Temp_SamplingClock = self.BrdDispInf[0]
        self.Brd_Temp_SamplingClock = QLabel("Temperature SamplingClock: " + str(self.Brd_Temp_SamplingClock) + " [°C]")

        self.Brd_Temp_Supply = self.BrdDispInf[1]
        self.Brd_Temp_Supply = QLabel("Temperature PowerAdapter: " + str(self.Brd_Temp_Supply) + " [°C]")

        self.Brd_Volt_Supply = self.BrdDispInf[2]
        self.Brd_Volt_Supply = QLabel("Voltage PowerAdapter: " + str(self.Brd_Volt_Supply) + " [V]")

        self.Brd_Curr_Supply = self.BrdDispInf[3]
        self.Brd_Curr_Supply = QLabel("Current PowerAdapter: " + str(self.Brd_Curr_Supply) + " [A]")

        try:
            if self.Brd_Info_Wndw.isVisible():
                pass

        except AttributeError:
#-----------create a window
            self.Brd_Info_Wndw = QWidget()

#-----------create layout and add data
            self.Brd_Info_Layout = QVBoxLayout()
            self.Brd_Info_Layout.addWidget(self.Brd_Name)
            self.Brd_Info_Layout.addWidget(self.Brd_RfVers)
            self.Brd_Info_Layout.addWidget(self.Brd_frqncy_SamplingClock)
            self.Brd_Info_Layout.addWidget(self.Brd_frqncy_PostCIC)
            self.Brd_Info_Layout.addWidget(self.Brd_Temp_SamplingClock)
            self.Brd_Info_Layout.addWidget(self.Brd_Temp_Supply)
            self.Brd_Info_Layout.addWidget(self.Brd_Volt_Supply)
            self.Brd_Info_Layout.addWidget(self.Brd_Curr_Supply)

#-----------setup window
            self.Brd_Info_Wndw.setLayout(self.Brd_Info_Layout)
            self.Brd_Info_Wndw.resize(256, 126)
            self.Brd_Info_Wndw.setWindowTitle("BoardInfo")

        self.Brd_Info_Wndw.show()

#---Power On/Off function
    def BRD_PWR(self):
#-------Check if Power is on or off and change on or off
        if self.Brd_Pwr_Btn.isChecked():
            self.Board.BrdPwrEna()
            self.Brd_Pwr_Btn.setChecked(True)
            self.Brd_Pwr_Btn.setText("Power: ON")
        else:
            self.Board.BrdPwrDi()
            self.Brd_Pwr_Btn.setChecked(False)
            self.Brd_Pwr_Btn.setText("Power: OFF")

#---Start measurement-function
    def BRD_MSR_FMCW(self):
#-------reset figure
        self.FGR_CLR()
#-------check if connection is still active or raise ConnectionError
        try:
            if self.connected:
                pass
            else:
                self.connected = False
                self.Con_Sts_Pic.setPixmap(QtGui.QPixmap("pics/red.png").scaled(30, 30))
                raise ConnectionError

#-----------check if power is on or raise ValueError
            if self.Brd_Pwr_Btn.isChecked():
                pass
            else:
                raise ValueError

#-------except any Errors
        except ConnectionError:
            self.errmsg("ConnectionError!", "Connection to FrontEnd has been lost!\nTry to connect again!", "c")
            self.start_gui()
            return

        except ValueError:
            self.errmsg("ValueError!", "The connected Board has no Power!\nPlease activate the Power first!", "w")
            return

#-------enable cancel-button
        self.Brd_Ccl.setEnabled(True)

#-------disable RangeDoppler
        self.Brd_Msr_RD.setEnabled(False)

#-------disable RangeProfile
        self.Brd_Msr_RP.setEnabled(False)

#-------enable Beamforming
        self.Proc = RadarProc.RadarProc()

#-------get calibrationdata
        self.calcData = self.Board.BrdGetCalData({"Mask":1, "Len": 64})

#-------enable Rx and Tx
        self.Board.RfRxEna()

        self.Board.RfTxEna(self.TxChn, self.TxPwr)

#-------set Config and triggermode
        self.Board.RfMeas("ExtTrigUp_TxSeq", self.BCfg)

#-------get values needed for Beamforming
        N = self.Board.Get("N")
        fs = self.Board.Get("fs")
        kf = self.Board.RfGet("kf")
        NrFrms = self.BCfg["NrFrms"]

#-------Beamformingconfig
        self.BFCfg["fs"] = fs
        self.BFCfg["kf"] = kf
        self.BFCfg["CalData"] = self.calcData

#-------set Beamformingconfig
        self.Proc.CfgBeamformingUla(self.BFCfg)

#-------create DataContainer
        self.MeasData = np.zeros((int(N), int(32)))
        self.n = np.arange(int(self.BCfg["N"]))
        self.AllData = np.zeros((int(N), int(8*NrFrms)))

#-------create Scaling-Data-Container: Range
        self.JRan = self.Proc.GetBeamformingUla("Range")
        lRan = len(self.JRan)
        self.ARan = np.zeros(lRan)
        self.ARan[:lRan] = self.JRan
        self.ARan[-1] = np.ediff1d(self.JRan)[-1] + self.JRan[-1]

#-------create Scaling-Data-Container: Angle
        self.JAng = self.Proc.GetBeamformingUla("AngFreqNorm")
        lAng = len(self.JAng)
        self.JAng = np.arange(int(lAng/2)*-1, int(lAng/2))
        self.AAng = np.zeros(lAng)
        self.AAng[:lAng] = self.JAng
        self.AAng[-1] = np.ediff1d(self.JAng)[-1] + self.JAng[-1]

#-------create Plot
        self.plt = self.figure.add_subplot(111)

#-------Start Measurement
        for MeasIdx in range(0, int(self.BCfg["NrFrms"])):
            Data = self.Board.BrdGetData()
            Id = ((Data[0, 0] - 1) % 4) + 1
            self.AllData[:, MeasIdx*8:(MeasIdx+1)*8] = Data
            self.AllData[1, MeasIdx*8:(MeasIdx+1)*8] = Id

#-----------Place Data in DataContainer
            if Id == 1:
                self.MeasData[:, 0:8] = Data
                self.plt.clear()
            elif Id == 2:
                self.MeasData[:, 8:16] = Data
            elif Id == 3:
                self.MeasData[:, 16:24] = Data
            elif Id == 4:
                self.MeasData[:, 24:32] = Data

#---------------Use Beamforming on obtained Data
                JOpt = self.Proc.BeamformingUla(self.MeasData)

#---------------get peak values
                JMax = np.amax(JOpt)

#---------------Use peak values to calculate normalized Data
                self.JNorm = JOpt - JMax

#---------------limit values for better plot visuals
                self.JNorm[self.JNorm < -15] = -15

#---------------draw Plot
                self.plt.pcolormesh(self.AAng, self.ARan, self.JNorm)
                self.plt.set_xlabel("Angle [deg]")
                self.plt.set_ylabel("Range [m]")
                self.plt.set_ylim(self.BFCfg["RMin"], self.BFCfg["RMax"])
                self.canvas.draw()
                self.figure.savefig("vc/FMCW_"+str(MeasIdx)+".png")

#---------------proccess Events
                QApplication.processEvents()

#---------------check for cancel-commands
                if self.cancel:
                    self.Brd_Ccl.setEnabled(False)
                    self.Brd_Msr_RD.setEnabled(True)
                    self.Brd_Msr_RP.setEnabled(True)
                    self.cancel = False
                    self.errmsg("Canceled!", "Measurement after User-Input abortet!", "i")
                    return

#-------reset when done
        self.Brd_Ccl.setEnabled(False)
        self.Brd_Msr_RD.setEnabled(True)
        self.Brd_Msr_RP.setEnabled(True)
        self.errmsg("Measurement Done", "Measurement completed succesfully!", "i")
        self.BRD_MSR_DN()

#---Start RangeDoppler-Measurement
    def BRD_MSR_RD(self):
#-------reset figure
        self.FGR_CLR()
#-------check if connection is still active or raise ConnectionError
        try:
            if self.connected:
                pass
            else:
                self.connected = False
                self.Con_Sts_Pic.setPixmap(QtGui.QPixmap("pics/red.png").scaled(30, 30))
                raise ConnectionError

#-----------check if power is on or raise ValueError
            if self.Brd_Pwr_Btn.isChecked():
                pass
            else:
                raise ValueError

#-------except any Errors
        except ConnectionError:
            self.errmsg("ConnectionError!", "Connection to FrontEnd has been lost!\nTry to connect again!", "c")
            self.start_gui()
            return

        except ValueError:
            self.errmsg("ValueError!", "The connected Board has no Power!\nPlease activate the Power first!", "w")
            return

#-------enable cancel-button
        self.Brd_Ccl.setEnabled(True)

#-------disable FMCW
        self.Brd_Msr_FMCW.setEnabled(False)

#-------disabled RangeProfile
        self.Brd_Msr_RP.setEnabled(False)

#-------enable RangeDoppler
        self.Proc = RadarProc.RadarProc()

#-------enable Rx and Tx
        self.Board.RfRxEna()
        self.Board.RfTxEna(2, 63)

#-------set Board-Config
        self.Board.Set("NrChn", 1)
        self.Board.RfMeas("ExtTrigUpNp", self.BCfg)

#-------set RangeDoppler-Config
        N = self.BCfg["N"]
        fs = self.Board.Get("fs")
        kf = self.Board.RfGet("kf")
        Frms = self.BCfg["Np"]
        Tp = self.BCfg["Tp"]
        fc = self.Board.RfGet("fc")

        self.RDCfg["fs"] = fs
        self.RDCfg["kf"] = kf
        self.RDCfg["N"] = N
        self.RDCfg["Np"] = Frms
        self.RDCfg["Tp"] = Tp
        self.RDCfg["fc"] = fc

        self.Proc.CfgRangeDoppler(self.RDCfg)

#-------create Plot
        self.plt = self.figure.add_subplot(111)

#-------create Scaling-Data-Container: Range
        self.JRan = self.Proc.GetRangeDoppler("Range")
        lRan = len(self.JRan)
        self.ARan = np.zeros(lRan)
        self.ARan[:lRan] = self.JRan
        self.ARan[-1] = np.ediff1d(self.JRan)[-1] + self.JRan[-1]

#-------create Scaling-Data-Container: Velocity
        self.JVel = self.Proc.GetRangeDoppler("Vel")
        lVel = len(self.JVel)
        self.AVel = np.zeros(lVel)
        self.AVel[:lVel] = self.JVel
        self.AVel[-1] = np.ediff1d(self.JVel)[-1] + self.JVel[-1]

#-------Get Data
        for MeasIdx in range(0, int(self.BCfg["NrFrms"])):
            Data = self.Board.BrdGetData(Frms)

#-----------Calculate RangeDoppler
            RD = self.Proc.RangeDoppler(Data)

#-----------get Peak-Values
            RDMax = np.amax(RD)

#-----------Use Peak-Values to get Normalized Data
            self.RDNorm = RD - RDMax

#-----------limit Values for better plot-visibility
            self.RDNorm[self.RDNorm < -45] = -45

#-----------plot values
            self.plt.pcolormesh(self.AVel, self.ARan, self.RDNorm)
            self.plt.set_xlabel("Velocity [deg/sec]")
            self.plt.set_ylabel("Range [m]")
            self.plt.set_ylim(self.RDCfg["RMin"], self.RDCfg["RMax"])
            self.canvas.draw()
            self.figure.savefig("vc/RD_"+str(MeasIdx)+".png")

#-----------process Events
            QApplication.processEvents()

#-----------check for cancel-commands
            if self.cancel:
                self.Brd_Ccl.setEnabled(False)
                self.Brd_Msr_FMCW.setEnabled(True)
                self.Brd_Msr_RP.setEnabled(True)
                self.cancel = False
                self.errmsg("Canceled!", "Measurement after User-Input abortet!", "i")
                return

#-------reset when done
        self.Brd_Ccl.setEnabled(False)
        self.Brd_Msr_FMCW.setEnabled(True)
        self.Brd_Msr_RP.setEnabled(True)
        self.errmsg("Measurement Done", "Measurement completed successfully!", "i")
        self.BRD_MSR_DN()

#---RangeProfile-function
    def BRD_MSR_RP(self):
#-------reset figure
        self.FGR_CLR()
#-------check if connection is still active or raise ConnectionError
        try:
            if not self.connected:
                self.connected = False
                self.Con_Sts_Pic.setPixmap(QtGui.QPixmap("pics/red.png").scaled(30, 30))
                raise ConnectionError

#-----------check if power is on or raise ValueError
            if not self.Brd_Pwr_Btn.isChecked():
                raise ValueError

#-------except any Errors
        except ConnectionError:
            self.errmsg("ConnectionError!", "Connection to FrontEnd has been lost!\nTry to connect again!", "c")
            self.start_gui()
            return

        except ValueError:
            self.errmsg("ValueError!", "The connected Board has no Power yet!\nPlease activate the Power first!", "w")
            return

#-------enable cancel button
        self.Brd_Ccl.setEnabled(True)

#-------disable FMCW & RangeDoppler
        self.Brd_Msr_FMCW.setEnabled(False)
        self.Brd_Msr_RD.setEnabled(False)

#-------enable RangeProfile
        self.Proc = RadarProc.RadarProc()

#-------enable Rx and Tx
        self.Board.RfRxEna()
        self.Board.RfTxEna(2, 63)

#-------set BoardConfig
        self.Board.Set("NrChn", 1)
        self.Board.RfMeas("ExtTrigUp_TxSeq", self.BCfg)

#-------get calibrationData
        self.calcData = self.Board.BrdGetCalData({"Mask":1, "Len": 64})

#-------get needed values
        fs = self.Board.Get("fs")
        kf = self.Board.RfGet("kf")
        N = self.Board.Get("N")
        NrFrms = self.BCfg["NrFrms"]

#-------set values to Config
        self.TPCfg["fs"] = fs
        self.TPCfg["kf"] = kf
        self.TPCfg["CalData"] = self.calcData

#-------set Config for measurement
        self.Proc.CfgRangeProfile(self.TPCfg)

#-------create DataContainer
        self.MeasData = np.zeros((int(N), int(32)))
        self.AllData = np.zeros((int(N), int(8*NrFrms)))

#-------get RangeScale
        self.RanSca = self.Proc.GetRangeProfile("Range")

#-------create Plot
        self.plt = self.figure.add_subplot(111)

#-------Start Measurement
        for MeasIdx in range(0, int(self.BCfg["NrFrms"])):
            Data = self.Board.BrdGetData()
            Id = ((Data[0, 0] -1) % 4) + 1
            self.AllData[:, MeasIdx*8:(MeasIdx+1)*8] = Data

#-----------Place Data in DataContainer
            if Id == 1:
                self.MeasData[:, :8] = Data
                self.plt.clear()
            elif Id == 2:
                self.MeasData[:, 8:16] = Data
            elif Id == 3:
                self.MeasData[:, 16:24] = Data
            elif Id == 4:
                self.MeasData[:, 24:32] = Data

#---------------get RangeProfile of measured Data
                self.RP = self.Proc.RangeProfile(self.MeasData)

#---------------draw plot
                self.plt.plot(self.RanSca, self.RP)
                self.plt.set_xlabel("Range [m]")
                self.plt.set_ylabel("dB")
                self.plt.set_ylim(-200, 0)
                self.canvas.draw()
                self.figure.savefig("vc/RP_"+str(MeasIdx)+".png")

#---------------process Events
                QApplication.processEvents()

#---------------check for cancel-commands
                if self.cancel:
                    self.Brd_Ccl.setEnabled(False)
                    self.Brd_Msr_FMCW.setEnabled(True)
                    self.Brd_Msr_RD.setEnabled(True)
                    self.cancel=False
                    self.errmsg("Canceled!", "Measurement after User-Input abortet", "i")
                    return

#-------reset when done
        print(self.AllData)
        self.Brd_Ccl.setEnabled(False)
        self.Brd_Msr_FMCW.setEnabled(True)
        self.Brd_Msr_RD.setEnabled(True)
        self.errmsg("Measurement Done!", "Measurement completed successfully!", "i")
        self.BRD_MSR_DN()

#---Cancel measurement-function
    def BRD_MSR_CNCL(self):
        self.cancel = True

#---Measurement-finished-function
    def BRD_MSR_DN(self):
#-------Question Video save
        Qstn = self.errmsg("Save Video?", "Do you want to save the Measurement as .mp4?", "q")

#-------check answer
        if Qstn == 0:
            Q2 = self.errmsg("save Data?", "Save Data with Video?", "q")

            if Q2 == 0:
                self.VIDEO_DATA()
                return
            else:
                self.VIDEO()

        else:
            for image in glob.glob("vc/*.png"):
                os.remove(image)

#-------Question Data save
        Qstn = self.errmsg("Save Data?", "Do you want to save Measurementdata as .csv?", "q")

#-------check answer
        if Qstn == 0:
            self.DATA()
        else:
            pass

#---Configmenu function
    def BRD_CFG(self):
#-------Create a new Window
        self.Cfg_Wndw = LockWindow()

#-------Create a List with all changeable config-variables
        self.Cfg_Lst = QListWidget()
        self.Cfg_Lst.setFixedWidth(150)

#-------Add the some names to the list
        Opts = ["fStrt", "fStop", "TRampUp", "TRampDo", "Np",
                "N", "NrFrms", "Tp", "TInt", "TxSeq", "IniEve",
                "IniTim", "CfgTim", "ExtEve", "Start"]
        self.Cfg_Lst.addItems(Opts)
        self.Cfg_Lst.currentItemChanged.connect(self.BRD_CFG_UPDATE)

#-------Create a Title that changes
        self.Cfg_Ttl = QLabel("")
        self.Cfg_Ttl.setFont(QtGui.QFont("Times", 20, QtGui.QFont.Bold))
        self.Cfg_Ttl.setFixedHeight(50)

#-------Create a Button that saves changes
        self.Cfg_Save = QPushButton("save...")
        self.Cfg_Save.setToolTip("save set options!")
        self.Cfg_Save.clicked.connect(self.BRD_CFG_SAVE)

#-------Create a Button that resets Config
        self.Cfg_Rst = QPushButton("Reset Config...")
        self.Cfg_Rst.setToolTip("Reset all Configs!")
        self.Cfg_Rst.clicked.connect(self.BRD_CFG_RST)

#-------Create Pic-Display
        self.Cfg_Pic = QLabel("Picture-Display")
        self.Cfg_Pic.setPixmap(QtGui.QPixmap("pics/Cfg.png"))

#-------Create Explain-Display
        self.Cfg_Exp = QLabel("Explain-Display")

#-------Create a Variable-Display
        self.Cfg_Var = QLabel("Variable-Display")

#-------Create a Original-Value-Display
        self.Cfg_Orig = QLabel("Original-Value-Display")

#-------Create a New-Value-Display with check function
        self.Cfg_New = QLineEdit()
        self.Cfg_New.setPlaceholderText("Enter new value here!")
        self.Cfg_New.textChanged.connect(self.BRD_CFG_CHCK)

#-------Create a Convert-Value-Display
        self.Cfg_Conv = QLabel("Convert-Value-Display")

#-------Create a Layout and fill it up
        self.Cfg_Layout = QGridLayout()
        self.Cfg_Layout.addWidget(self.Cfg_Lst, 0, 0, 5, 1, Qt.AlignLeft)
        self.Cfg_Layout.addWidget(self.Cfg_Ttl, 0, 1, 1, 4, Qt.AlignTop)
        self.Cfg_Layout.addWidget(self.Cfg_Var, 1, 1, 1, 1, Qt.AlignLeft)
        self.Cfg_Layout.addWidget(self.Cfg_Orig, 1, 2, 1, 1, Qt.AlignCenter)
        self.Cfg_Layout.addWidget(self.Cfg_New, 1, 3, 1, 1, Qt.AlignCenter)
        self.Cfg_Layout.addWidget(self.Cfg_Conv, 1, 4, 1, 1, Qt.AlignRight)
        self.Cfg_Layout.addWidget(self.Cfg_Pic, 2, 1, 1, 4, Qt.AlignCenter)
        self.Cfg_Layout.addWidget(self.Cfg_Exp, 3, 1, 1, 4, Qt.AlignCenter)
        self.Cfg_Layout.addWidget(self.Cfg_Rst, 4, 1, 1, 1, Qt.AlignBottom)
        self.Cfg_Layout.addWidget(self.Cfg_Save, 4, 4, 1, 1, Qt.AlignBottom)

#-------Set Window geometry etc.
        self.Cfg_Wndw.setLayout(self.Cfg_Layout)
        self.Cfg_Wndw.resize(720, 640)
        self.Cfg_Wndw.setWindowTitle("Board-Configuration")
        self.Cfg_Wndw.show()

#---update CfgWindow function
    def BRD_CFG_UPDATE(self):
#-------get current item of list
        showMe = self.Cfg_Lst.currentItem().text()

#-------Check for Lock
        if self.Lock:
            self.Cfg_New.setStyleSheet("border: 3px solid red; background: yellow; color: red")
            self.Cfg_Conv.setText("invalid Value!")
            self.Cfg_Save.setEnabled(False)
            return
        else:
            self.Cfg_New.setStyleSheet(self.origStyleSheet)
            self.Cfg_Save.setEnabled(True)

#-------check what to display
        if showMe == "fStrt":
            self.Cfg_Ttl.setText("Frequency@Start - Frequency-BottomValue")
            self.Cfg_Var.setText("Variable Name:\nfStrt")
            original = str(self.StdCfg["fStrt"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [Hz]")
            self.Cfg_Conv.setText("Converter: Ready!")
            self.Cfg_Exp.setText("The Start-Frequency needs to be lower than the Stop-Frequency! This variable should be between 70 and 80 GHz!")
            self.Cfg_New.setText(str(self.TCfg["fStrt"]))
            self.Cfg_Pic.setPixmap(QtGui.QPixmap("pics/Cfg.png"))

        elif showMe == "fStop":
            self.Cfg_Ttl.setText("Frequency@Stop - Frequency-TopValue")
            self.Cfg_Var.setText("Variable Name:\nfStop")
            original = str(self.StdCfg["fStop"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [Hz]")
            self.Cfg_Conv.setText("Converter: Ready!")
            self.Cfg_Exp.setText("The Stop-Frequency needs to be higher than the Start-Frequency! This variable should be between 70 and 80 GHz")
            self.Cfg_New.setText(str(self.TCfg["fStop"]))
            self.Cfg_Pic.setPixmap(QtGui.QPixmap("pics/Cfg.png"))

        elif showMe == "TRampUp":
            self.Cfg_Ttl.setText("Duration Start2Stop - linear-RampUpwards")
            self.Cfg_Var.setText("Variable Name:\nTRampUp")
            original = str(self.StdCfg["TRampUp"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [ms]")
            self.Cfg_Conv.setText("Converter: Ready!")
            self.Cfg_Exp.setText("This variable describes the time needed to make a linear jump from Start- to Stop-Frequency!\n"
                                 "The time needed for the so called Up-Ramp should be a little higher than the time needed for the Down-Ramp.\n"
                                 "The numeric value of this variable should be around 20-50 ms!")
            self.Cfg_New.setText(str(self.TCfg["TRampUp"]))
            self.Cfg_Pic.setPixmap(QtGui.QPixmap("pics/Cfg.png"))

        elif showMe == "TRampDo":
            self.Cfg_Ttl.setText("Duration Stop2Start - linear-RampDownwards")
            self.Cfg_Var.setText("Variable Name:\nTRampDo")
            original = str(self.StdCfg["TRampDo"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [ms]")
            self.Cfg_Conv.setText("Converter: Ready!")
            self.Cfg_Exp.setText("This variable describes the time needed to make a linear drop from Stop- to StartFrequency!\n"
                                 "The time needed for the so called Down-Ramp should be a little less than the time needed for the Up-Ramp.\n"
                                 "The numeric value of this variableshould be around 1-10 ms!")
            self.Cfg_New.setText(str(self.TCfg["TRampDo"]))
            self.Cfg_Pic.setPixmap(QtGui.QPixmap("pics/Cfg.png"))

        elif showMe == "NrFrms":
            self.Cfg_Ttl.setText("Number Sequences - Repeat n-Times")
            self.Cfg_Var.setText("Variable Name:\nNrFrms")
            original = str(self.StdCfg["NrFrms"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [repeats]")
            self.Cfg_Conv.setText("No Convertion!")
            self.Cfg_Exp.setText("This variable defines how often the defined Sequence (Tx-activation-order) is repeated.\n"
                                 "This means a increase will lenghten the time needed for completion but also allow to measure moving objects.")
            self.Cfg_New.setText(str(self.TCfg["NrFrms"]))
            self.Cfg_Pic.setPixmap(QtGui.QPixmap("pics/Cfg2.png"))

        elif showMe == "N":
            self.Cfg_Ttl.setText("Number Samples - Measure n-Samples")
            self.Cfg_Var.setText("Variable Name:\nN")
            original = str(self.StdCfg["N"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [samples]")
            self.Cfg_Conv.setText("No Convertion!")
            self.Cfg_Exp.setText("This Value describes how many sample-values are saved.\nTo be precise, this value is the lenght of the x-axis while "
                                 "the lenght of the y-axis is defined by the Channels.\nIncreasing this value means increasing the resolution of the plot "
                                 "beacuse more single-values are obtained.")
            self.Cfg_New.setText(str(self.TCfg["N"]))
            self.Cfg_Pic.setPixmap(QtGui.QPixmap("pics/Cfg2.png"))

        elif showMe == "Np":
            self.Cfg_Ttl.setText("Number Frames - Collect n-Frames")
            self.Cfg_Var.setText("Variable Name:\nNp")
            original = str(self.StdCfg["Np"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [frames]")
            self.Cfg_Conv.setText("No Convertion!")
            self.Cfg_Exp.setText("Number of Frames means the chirp-loop. This variable defines how often a chirp (Up-Down-Cycle) is looped for every\n"
                                 "Sequence!")
            self.Cfg_New.setText(str(self.TCfg["Np"]))
            self.Cfg_Pic.setPixmap(QtGui.QPixmap("pics/Cfg2.png"))

        elif showMe == "Tp":
            self.Cfg_Ttl.setText("Time Between Tx - Wait-Time")
            self.Cfg_Var.setText("Variable Name:\nTp")
            original = str(self.StdCfg["Tp"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [ms]")
            self.Cfg_Conv.setText("Converter: Ready!")
            self.Cfg_Exp.setText("This is the time that passes after every single Tx-Sequence (TRampUp -> TRampDo -> Tp -> TRampUp...) has finished."
                                 "\nThe RadarBook itself needs about 30µs to set the Config.To ensure this, here is the calculation:\n"
                                 "CfgTime = Tp - (TRampUp + TRampDo) -> Tp = CfgTime + (TRampUp + TRampDo)\n"
                                 "This means the minimum Tp can be calculated if TRampUp and TRampDo are allready set to a specific value!\n"
                                 "To Ensure that the Config is really set, CfgTime is 5µs longer.\n\n"
                                 "minimum calculated Tp = " + str(self.TCfg["TRampUp"] + self.TCfg["TRampDo"] + self.TCfg["CfgTim"]))
            self.Cfg_New.setText(str(self.TCfg["Tp"]))
            self.Cfg_Pic.setPixmap(QtGui.QPixmap("pics/Cfg2.png"))

        elif showMe == "TInt":
            self.Cfg_Ttl.setText("Time Between Sequences - Wait-Time")
            self.Cfg_Var.setText("Variable Name:\nTInt")
            original = str(self.StdCfg["TInt"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [ms]")
            self.Cfg_Conv.setText("Converter: Ready!")
            self.Cfg_Exp.setText("This is the time that passes after every Sequence-Order (Tx1-Tx2-Tx3-Tx4) has finished. There is even a way to calc. TInt!\n"
                                 "The variable 'WaitTime' describes the total time when no signals are transmitted. When using simple math this can be done:\n"
                                 "WaitTime = TInt - Tp * len(TxSeq) * Np -> TInt = WaitTime + Tp * len(TxSeq) * Np\n"
                                 "The longest, by the RadarBook accepted WaitTime is 1ms! To ensure no Errors come up this calc. expects WaitTime to be 0.9ms!\n\n"
                                 "minimum calculated TInt = " + str(0.9e-3 + self.TCfg["Tp"] * 4 * self.TCfg["Np"]))
            self.Cfg_New.setText(str(self.TCfg["TInt"]))
            self.Cfg_Pic.setPixmap(QtGui.QPixmap("pics/Cfg2.png"))

        elif showMe == "TxSeq":
            self.Cfg_Ttl.setText("Order of Activation - Tx-Sequence")
            self.Cfg_Var.setText("Variable Name:\nTxSeq")
            original = str(self.StdCfg["TxSeq"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [order]")
            self.Cfg_Conv.setText("No Convertion!")
            self.Cfg_Exp.setText("This variable just describes the activation of the 4 diffrent Tx-Sensors.\n"
                                 "To change the Sequence, change this variable!\n"
                                 "Please enter a sequence like '1423', '1,2,4,3', (1,2,3,4) or [1,2,3,4]!")
            self.Cfg_New.setText(str(self.TCfg["TxSeq"]))
            self.Cfg_Pic.setPixmap(QtGui.QPixmap("pics/Cfg.png"))

        elif showMe == "IniEve":
            self.Cfg_Ttl.setText("MeasureInitEvent - Start Event")
            self.Cfg_Var.setText("VariableName:\n" + showMe)
            original = str(self.StdCfg["IniEve"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [event]")
            self.Cfg_Conv.setText("No Conversion!")
            self.Cfg_Exp.setText("Defining a start-event may be helpful for other measurements!")
            self.Cfg_New.setText(str(self.TCfg["IniEve"]))

        elif showMe == "IniTim":
            self.Cfg_Ttl.setText("InitTimeWindow - Time for init")
            self.Cfg_Var.setText("Variable Name:\n" + showMe)
            original = str(self.StdCfg["IniTim"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [ms]")
            self.Cfg_Conv.setText("Converter: Ready!")
            self.Cfg_Exp.setText("The total timewindow for init-phase - if this value gets higher you should consider setting a delay.\n"
                                 "This way measurement and init dont overlap!")
            self.Cfg_New.setText(str(self.TCfg["IniTim"]))

        elif showMe == "CfgTim":
            self.Cfg_Ttl.setText("Re-Config-Time of PLL")
            self.Cfg_Var.setText("Variable Name:\n" + showMe)
            original = str(self.StdCfg["CfgTim"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [ms]")
            self.Cfg_Conv.setText("Converter: Ready!")
            self.Cfg_Exp.setText("CfgTim = Tp - (TRampUp + TRampDo)\ncalculated CfgTim: " + str(self.TCfg["Tp"] - (self.TCfg["TRampUp"] + self.TCfg["TRampDo"])))
            self.Cfg_New.setText(str(self.TCfg["CfgTim"]))

        elif showMe == "ExtEve":
            self.Cfg_Ttl.setText("ExternalEvent")
            self.Cfg_Var.setText("Variable Name:\n" + showMe)
            original = str(self.StdCfg["ExtEve"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [event]")
            self.Cfg_Conv.setText("No Conversion!")
            self.Cfg_Exp.setText("")
            self.Cfg_New.setText(str(self.TCfg["ExtEve"]))

        elif showMe == "Start":
            self.Cfg_Ttl.setText("Start/Stop FPGA-Timing")
            self.Cfg_Var.setText("Variable Name:\n" + showMe)
            original = str(self.StdCfg["Start"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [bool]")
            self.Cfg_Conv.setText("No Conversion!")
            self.Cfg_Exp.setText("")
            self.Cfg_New.setText(str(self.TCfg["Start"]))

        else:
            self.errmsg("NameError!", "Item '" + showMe + "' not found!", "c")
            self.Cfg_Wndw.close()
            return

#-------show chosen options
        self.Cfg_Wndw.show()

#---check input function
    def BRD_CFG_CHCK(self):
#-------get chosen variable
        showMe = self.Cfg_Lst.currentItem().text()

#-------get value after change
        value = self.Cfg_New.text()

#-------check if value is convertable, if so display it, if not do nothing
        try:
            if float(value) >= 0:
                if showMe in ["fStrt", "fStop"]:
                    new_value = str(float(value) * 1e-9)
                    self.Cfg_Conv.setText("Converted Value:\n"+new_value+" [GHz]")
                    if showMe == "fStrt":
                        if float(value) >= 70e9:
                            self.TCfg["fStrt"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "fStop":
                        if float(value) > float(self.TCfg["fStrt"]):
                            self.TCfg["fStop"] = float(value)
                        else:
                            raise LookupError

                elif showMe in ["TRampUp", "TRampDo", "Tp", "TInt", "CfgTim", "IniTim"]:
                    new_value = str(float(value) * 1e3)
                    self.Cfg_Conv.setText("Converted Value:\n"+new_value+" [µs]")
                    if showMe == "TRamUp":
                        if float(value) > 0:
                            self.TCfg["TRampUp"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "TRampDo":
                        if float(value) > 0:
                            self.TCfg["TRampDo"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "Tp":
                        if float(value) > 0:
                            self.TCfg["Tp"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "TInt":
                        if float(value) > 0:
                            self.TCfg["TInt"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "CfgTim":
                        if float(value) > 0:
                            self.TCfg["CfgTim"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "IniTim":
                        if float(value) > 0:
                            self.TCfg["IniTim"] = float(value)
                        else:
                            raise LookupError

                elif showMe in ["NrFrms", "N", "Np", "IniEve", "ExtEve", "Start"]:
                    if showMe == "NrFrms":
                        if float(value) >= 1:
                            self.TCfg["NrFrms"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "N":
                        if float(value) > 0:
                            self.TCfg["N"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "Np":
                        if float(value) >= 1 and float(value) <= 256:
                            self.TCfg["Np"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "IniEve":
                        if float(value) == 0 or float(value) == 1:
                            self.TCfg["IniEve"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "ExtEve":
                        if float(value) == 0 or float(value) == 1:
                            self.TCfg["ExtEve"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "Start":
                        self.TCfg["Start"] = float(value)

                else:
                    raise ValueError

            else:
                raise LookupError

            self.Lock = False
            global lock
            lock = self.Lock
            self.Cfg_New.setStyleSheet(self.origStyleSheet)
            self.Cfg_Save.setEnabled(True)

#-------except all possible Errors
        except ValueError:
            if showMe == "activation_TxSeq":
                vallen = len(value)
                try:
                    if vallen == 4:
                        int(value)
                        F1st = int(value[0])
                        S2nd = int(value[1])
                        T3rd = int(value[2])
                        F4th = int(value[3])
                    elif vallen == 7:
                        value = value.replace(",", "")
                        int(value)
                        F1st = int(value[0])
                        S2nd = int(value[1])
                        T3rd = int(value[2])
                        F4th = int(value[3])
                    elif vallen == 9:
                        value = value[1:-1]
                        value = value.replace(",", "")
                        int(value)
                        F1st = int(value[0])
                        S2nd = int(value[1])
                        T3rd = int(value[2])
                        F4th = int(value[3])
                    elif vallen >= 4:
                        F1st = 0
                        S2nd = 0
                        T3rd = 0
                        F4th = 0
                    else:
                        raise ValueError

                    if int(value) != 0:
                        if F1st in [S2nd, T3rd, F4th]:
                            raise LookupError
                        if S2nd in [F1st, T3rd, F4th]:
                            raise LookupError
                        if T3rd in [F1st, S2nd, F4th]:
                            raise LookupError
                        if F4th in [F1st, S2nd, T3rd]:
                            raise LookupError

                    self.TCfg["TxSeq"] = np.array([F1st, S2nd, T3rd, F4th])

                except ValueError:
                    pass

                except AttributeError:
                    pass

                except UnboundLocalError:
                    pass

                except LookupError:
                    raise LookupError

        except LookupError:
            self.Lock = True
            lock = self.Lock
            self.Cfg_New.setStyleSheet("border: 3px solid red; background: yellow; color: red")
            self.Cfg_Conv.setText("invalid Value!")
            self.Cfg_Save.setEnabled(False)
            return

#---save config function
    def BRD_CFG_SAVE(self):
#-------safety-question
        Qstn = self.errmsg("Set Config?", "Are you sure you want to set new Config?\nIf some variables are not set right Measurement may Stop!", "q")

#-------check answer
        if Qstn == 0:
            cont = True
        else:
            cont = False

#-------continue if answer was yes, else abort
        if cont:
            for value in self.TCfg:
                if value == 0:
                    self.errmsg("ValueError!", "It seems that not all Config-Variables have been set to a specific value!\nThis means some variables are still set to 0!\n"
                                "If this is not wanted please check variables and save again!", "w")
                    self.BCfg = self.StdCfg
                    return
            self.BCfg = self.TCfg
            self.errmsg("Confirmed!", "Config saved successfully!", "i")
        else:
            self.errmsg("Config not set!", "The User-Config is not set, but still saved in the ConfigWindow.", "i")

#---Reset-Config-Function
    def BRD_CFG_RST(self):
#-------safety-question
        Qstn = self.errmsg("Are you sure?", "If you reset Board-Config, everything except the standard Config is lost!\nContinue anyways?", "q")

#-------check answer
        if Qstn == 0:
            cont = True
        else:
            cont = False

#-------continue or abort
        if cont:
            self.BCfg = self.StdCfg
            self.TCfg = self.BCfg
            self.Lock = False
            global lock
            lock = self.Lock
            self.BRD_CFG_UPDATE()
            self.errmsg("Confirmed!", "Board-Config has been reset!", "i")

        else:
            self.errmsg("Config not reset!", "The Board-Config has not been reset!", "i")

#---Display-Config-function
    def CFG_SHW(self):
#-------Create a ScollArea and add Displays to it
        self.Display = QWidget()

        self.DspLay = QVBoxLayout()

        self.Scroll = QScrollArea()
        self.Scroll.setWidgetResizable(True)

        self.ScrDsp = QWidget()

        self.ScrLay = QVBoxLayout()

        self.Dspl_ttl = QLabel("Configs:")
        self.Dspl_ttl.setFont(QtGui.QFont("Times", 16, QtGui.QFont.Bold))

        self.Dspl_Brd_tl = QLabel("Board-Configuration:")
        self.Dspl_Brd_tl.setFont(QtGui.QFont("Times", 14))

        self.Dspl_Bmf_tl = QLabel("Beamforming-Configuration:")
        self.Dspl_Bmf_tl.setFont(QtGui.QFont("Times", 14))

        self.Dspl_RD_tl = QLabel("RangeDoppler-Configuration:")
        self.Dspl_RD_tl.setFont(QtGui.QFont("Times", 14))

        self.Dspl_RP_tl = QLabel("RangeProfile-Configuration:")
        self.Dspl_RP_tl.setFont(QtGui.QFont("Times", 14))

        self.Dspl_Frqncy = QLabel("Frequencys:")
        self.Dspl_Frqncy.setFont(QtGui.QFont("Times", 10))
        self.Dspl_Frqncy1 = QLabel("Frequencys:")
        self.Dspl_Frqncy1.setFont(QtGui.QFont("Times", 10))

        self.value_fStrt = str(self.BCfg["fStrt"] * 1e-9) + " GHz"
        self.Dspl_fStrt = QLabel("'fStrt' - @Start:    ->    " + self.value_fStrt)

        self.value_fStop = str(self.BCfg["fStop"] * 1e-9) + " GHz"
        self.Dspl_fStop = QLabel("'fStop' - @Stop:    ->    " + self.value_fStop)

        self.Dspl_Drtn = QLabel("Durations:")
        self.Dspl_Drtn.setFont(QtGui.QFont("Times", 10))
        self.Dspl_Drtn1 = QLabel("Durations:")
        self.Dspl_Drtn1.setFont(QtGui.QFont("Times", 10))

        self.value_TRampUp = str(self.BCfg["TRampUp"] * 1e6) + " µs"
        self.Dspl_TRampUp = QLabel("'TRampUp' - Start2Stop:    ->    " + self.value_TRampUp)

        self.value_TRampDo = str(self.BCfg["TRampDo"] * 1e6) + " µs"
        self.Dspl_TRampDo = QLabel("'TRampDo' - Stop2Start:    ->    " + self.value_TRampDo)

        self.value_Tp = str(self.BCfg["Tp"] * 1e6) + " µs"
        self.Dspl_Tp = QLabel("'Tp' - Transmit2Transmit:    ->    " + self.value_Tp)

        self.value_TInt = str(self.BCfg["TInt"] * 1e3) + " ms"
        self.Dspl_TInt = QLabel("'TInt' - Sequence2Sequence:    ->    " + self.value_TInt)

        self.value_IniTim = str(self.BCfg["IniTim"] * 1e3) + " ms"
        self.Dspl_IniTim = QLabel("'IniTim' - InitTime:    ->    " + self.value_IniTim)

        self.value_CfgTim = str(self.BCfg["CfgTim"] * 1e6) + " µs"
        self.Dspl_CfgTim = QLabel("'CfgTim' - ConfigTime:    ->    " + self.value_CfgTim)

        self.Dspl_Cnstnt1 = QLabel("Constants:")
        self.Dspl_Cnstnt1.setFont(QtGui.QFont("Times", 10))
        self.Dspl_Cnstnt2 = QLabel("Constants:")
        self.Dspl_Cnstnt2.setFont(QtGui.QFont("Times", 10))
        self.Dspl_Cnstnt3 = QLabel("Constants:")
        self.Dspl_Cnstnt3.setFont(QtGui.QFont("Times", 10))
        self.Dspl_Cnstnt4 = QLabel("Constants:")
        self.Dspl_Cnstnt4.setFont(QtGui.QFont("Times", 10))

        self.value_NrFrms = str(self.BCfg["NrFrms"])
        self.Dspl_NrFrms = QLabel("'NrFrms' - SequenceRepeats:    ->    " + self.value_NrFrms)

        self.value_N = str(self.BCfg["N"])
        self.Dspl_N = QLabel("'N' - SampleAmount:    ->    " + self.value_N)

        self.value_Np = str(self.BCfg["Np"])
        self.Dspl_Np = QLabel("'Np' - FrameAmount:    ->    " + self.value_Np)

        self.value_RemoveMean = str(bool(self.BFCfg["RemoveMean"]))
        self.Dspl_RemoveMean = QLabel("'RemoveMean' - RemoveMeanValues:    ->    " + self.value_RemoveMean)

        self.value_Window = str(bool(self.BFCfg["Window"]))
        self.Dspl_Window = QLabel("'Window' - DataUseWindow:    ->    " + self.value_Window)

        self.value_dB = str(bool(self.BFCfg["dB"]))
        self.Dspl_dB = QLabel("'dB' - Data as dB:    ->    " + self.value_dB)

        self.value_Abs = str(bool(self.BFCfg["Abs"]))
        self.Dspl_Abs = QLabel("'Abs' - MagnitudeInterval:    ->    " + self.value_Abs)

        self.value_Ext = str(bool(self.BFCfg["Ext"]))
        self.Dspl_Ext = QLabel("'Ext' - RangeInterval:    ->    " + self.value_Ext)

        self.Dspl_Dstnc = QLabel("Distances:")
        self.Dspl_Dstnc.setFont(QtGui.QFont("Times", 10))
        self.Dspl_Dstnc1 = QLabel("Distances:")
        self.Dspl_Dstnc1.setFont(QtGui.QFont("Times", 10))
        self.Dspl_Dstnc2 = QLabel("Distances:")
        self.Dspl_Dstnc2.setFont(QtGui.QFont("Times", 10))

        self.value_RMin = str(self.BFCfg["RMin"]) + " m"
        self.Dspl_RMin = QLabel("'RMin' - min.Distance:    ->    " + self.value_RMin)

        self.value_RMax = str(self.BFCfg["RMax"]) + " m"
        self.Dspl_RMax = QLabel("'RMax' - max.Distance:    ->    " + self.value_RMax)

        self.value_RangeFFT = str(self.BFCfg["RangeFFT"])
        self.Dspl_RangeFFT = QLabel("'RangeFFT' - FFT-RangeWindow:    ->    " + self.value_RangeFFT)

        self.value_AngFFT = str(self.BFCfg["AngFFT"])
        self.Dspl_AngFFT = QLabel("'AngFFT' - FFT-AngleWindow:    ->    " + self.value_AngFFT)

        self.Dspl_Chnnls1 = QLabel("Channels:")
        self.Dspl_Chnnls1.setFont(QtGui.QFont("Times", 10))
        self.Dspl_Chnnls2 = QLabel("Channels:")
        self.Dspl_Chnnls2.setFont(QtGui.QFont("Times", 10))

        self.value_ChnOrder = str(self.BFCfg["ChnOrder"])
        self.Dspl_ChnOrder = QLabel("'ChnOrder' - DataChannels:    ->    " + self.value_ChnOrder)

        self.value_TxSeq = str(self.BCfg["TxSeq"])
        self.Dspl_TxSeq = QLabel("'TxSeq' - TransmitSequence:    ->    " + self.value_TxSeq)

        self.value_RDRangeFFT = str(self.RDCfg["RangeFFT"])
        self.Dspl_RDRangeFFT = QLabel("'RangeFFT' - FFT-RangeWindow    ->    " + self.value_RDRangeFFT)

        self.value_RDVelFFT = str(self.RDCfg["VelFFT"])
        self.Dspl_RDVelFFT = QLabel("'VelFFT' - FFT-VelocityWindow    ->    " + self.value_RDVelFFT)

        self.value_RDAbs = str(bool(self.RDCfg["Abs"]))
        self.Dspl_RDAbs = QLabel("'Abs' - MagnitudeInterval    ->    " + self.value_RDAbs)

        self.value_RDExt = str(bool(self.RDCfg["Ext"]))
        self.Dspl_RDExt = QLabel("'Ext' - RangeInterval    ->    " + self.value_RDExt)

        self.value_RDRMin = str(self.RDCfg["RMin"]) + " m"
        self.Dspl_RDRMin = QLabel("'RMin' - min. Distance    ->    " + self.value_RDRMin)

        self.value_RDRMax = str(self.RDCfg["RMax"]) + " m"
        self.Dspl_RDRMax = QLabel("'RMax' - max. Distance    ->    " + self.value_RDRMax)

        self.value_RDRemoveMean = str(bool(self.RDCfg["RemoveMean"]))
        self.Dspl_RDRemoveMean = QLabel("'RemoveMean' - RemoveMeanValues    ->    " + self.value_RDRemoveMean)

        self.value_RDN = str(self.RDCfg["N"])
        self.Dspl_RDN = QLabel("'N' - SampleAmount:    ->    " + self.value_RDN)

        self.value_RDNp = str(self.RDCfg["Np"])
        self.Dspl_RDNp = QLabel("'Np' - FrameAmount:    ->    " + self.value_RDNp)

        self.value_RDWindow = str(bool(self.RDCfg["Window"]))
        self.Dspl_RDWindow = QLabel("'Window' - DataUseWindow:    ->    " + self.value_RDWindow)

        self.value_RDdB = str(bool(self.RDCfg["dB"]))
        self.Dspl_RDdB = QLabel("'dB' - Data as dB:    ->    " + self.value_RDdB)

        self.value_RDfc = str(self.RDCfg["fc"] * 1e-9) + " GHz"
        self.Dspl_RDfc = QLabel("'fc' - centered Frequency:    ->    " + self.value_RDfc)

        self.value_RDTp = str(self.RDCfg["Tp"] * 1e6) + " µs"
        self.Dspl_RDTp = QLabel("'Tp' - Transmit2Transmit:    ->    " + self.value_RDTp)

        self.value_NFFT = str(self.RPCfg["NFFT"])
        self.Dspl_NFFT = QLabel("'NFFT' - FFT-Window    ->    " + self.value_NFFT)

        self.value_RPAbs = str(bool(self.RPCfg["Abs"]))
        self.Dspl_RPAbs = QLabel("'Abs' - MagnitudeInterval    ->    " + self.value_RPAbs)

        self.value_RPExt = str(bool(self.RPCfg["Ext"]))
        self.Dspl_RPExt = QLabel("'Ext' - RangeInterval    ->    " + self.value_RPExt)

        self.value_RPRMin = str(self.RPCfg["RMin"]) + " m"
        self.Dspl_RPRMin = QLabel("'RMin' - min. Distance:    ->    " + self.value_RPRMin)

        self.value_RPRMax = str(self.RPCfg["RMax"]) + " m"
        self.Dspl_RPRMax = QLabel("'RMax' - max. Distance:    ->    " + self.value_RPRMax)

        self.value_RPRemoveMean = str(bool(self.RPCfg["RemoveMean"]))
        self.Dspl_RPRemoveMean = QLabel("'RemoveMean' - RemoveMeanValues:    ->    " + self.value_RPRemoveMean)

        self.value_RPWindow = str(bool(self.RPCfg["Window"]))
        self.Dspl_RPWindow = QLabel("'Window' - DataUseWindow:    ->    " + self.value_RPWindow)

        self.value_RPXPos = str(bool(self.RPCfg["XPos"]))
        self.Dspl_RPXPos = QLabel("'XPos' - positiveRangeProfile:     ->    " + self.value_RPXPos)

        self.value_RPdB = str(bool(self.RPCfg["dB"]))
        self.Dspl_RPdB = QLabel("'dB' - Data as dB:    ->    " + self.value_RPdB)

        self.Brd_Shw_Cfgs.setText("hideConfigs...")
        self.Brd_Shw_Cfgs.disconnect()
        self.Brd_Shw_Cfgs.clicked.connect(self.CFG_HDE)

        self.ScrLay.addWidget(self.Dspl_Brd_tl)
        self.ScrLay.addWidget(self.Dspl_Frqncy)
        self.ScrLay.addWidget(self.Dspl_fStrt)
        self.ScrLay.addWidget(self.Dspl_fStop)
        self.ScrLay.addWidget(self.Dspl_Drtn)
        self.ScrLay.addWidget(self.Dspl_TRampUp)
        self.ScrLay.addWidget(self.Dspl_TRampDo)
        self.ScrLay.addWidget(self.Dspl_Tp)
        self.ScrLay.addWidget(self.Dspl_TInt)
        self.ScrLay.addWidget(self.Dspl_IniTim)
        self.ScrLay.addWidget(self.Dspl_CfgTim)
        self.ScrLay.addWidget(self.Dspl_Cnstnt1)
        self.ScrLay.addWidget(self.Dspl_NrFrms)
        self.ScrLay.addWidget(self.Dspl_N)
        self.ScrLay.addWidget(self.Dspl_Np)
        self.ScrLay.addWidget(self.Dspl_Chnnls1)
        self.ScrLay.addWidget(self.Dspl_TxSeq)
        self.ScrLay.addWidget(self.Dspl_Bmf_tl)
        self.ScrLay.addWidget(self.Dspl_Cnstnt2)
        self.ScrLay.addWidget(self.Dspl_RangeFFT)
        self.ScrLay.addWidget(self.Dspl_AngFFT)
        self.ScrLay.addWidget(self.Dspl_Abs)
        self.ScrLay.addWidget(self.Dspl_Ext)
        self.ScrLay.addWidget(self.Dspl_RemoveMean)
        self.ScrLay.addWidget(self.Dspl_Window)
        self.ScrLay.addWidget(self.Dspl_dB)
        self.ScrLay.addWidget(self.Dspl_Dstnc)
        self.ScrLay.addWidget(self.Dspl_RMax)
        self.ScrLay.addWidget(self.Dspl_RMin)
        self.ScrLay.addWidget(self.Dspl_Chnnls2)
        self.ScrLay.addWidget(self.Dspl_ChnOrder)
        self.ScrLay.addWidget(self.Dspl_RD_tl)
        self.ScrLay.addWidget(self.Dspl_Frqncy1)
        self.ScrLay.addWidget(self.Dspl_RDfc)
        self.ScrLay.addWidget(self.Dspl_Drtn1)
        self.ScrLay.addWidget(self.Dspl_RDTp)
        self.ScrLay.addWidget(self.Dspl_Cnstnt3)
        self.ScrLay.addWidget(self.Dspl_RDRangeFFT)
        self.ScrLay.addWidget(self.Dspl_RDVelFFT)
        self.ScrLay.addWidget(self.Dspl_RDN)
        self.ScrLay.addWidget(self.Dspl_RDNp)
        self.ScrLay.addWidget(self.Dspl_RDAbs)
        self.ScrLay.addWidget(self.Dspl_RDExt)
        self.ScrLay.addWidget(self.Dspl_RDRemoveMean)
        self.ScrLay.addWidget(self.Dspl_RDWindow)
        self.ScrLay.addWidget(self.Dspl_RDdB)
        self.ScrLay.addWidget(self.Dspl_Dstnc1)
        self.ScrLay.addWidget(self.Dspl_RDRMin)
        self.ScrLay.addWidget(self.Dspl_RDRMax)
        self.ScrLay.addWidget(self.Dspl_RP_tl)
        self.ScrLay.addWidget(self.Dspl_Cnstnt4)
        self.ScrLay.addWidget(self.Dspl_NFFT)
        self.ScrLay.addWidget(self.Dspl_RPAbs)
        self.ScrLay.addWidget(self.Dspl_RPExt)
        self.ScrLay.addWidget(self.Dspl_RPRemoveMean)
        self.ScrLay.addWidget(self.Dspl_RPWindow)
        self.ScrLay.addWidget(self.Dspl_RPdB)
        self.ScrLay.addWidget(self.Dspl_RPXPos)
        self.ScrLay.addWidget(self.Dspl_Dstnc2)
        self.ScrLay.addWidget(self.Dspl_RPRMin)
        self.ScrLay.addWidget(self.Dspl_RPRMax)
        self.ScrDsp.setLayout(self.ScrLay)
        self.Scroll.setWidget(self.ScrDsp)
        self.DspLay.addWidget(self.Dspl_ttl)
        self.DspLay.addWidget(self.Scroll)
        self.Display.setLayout(self.DspLay)

        self.MWLayout.addWidget(self.Display, 2, 9, 8, 2)
        self.itemAt = self.MWLayout.count() - 1
        self.show()

#---hide Configs-function
    def CFG_HDE(self):
#-------Find Widget and delete it
        item = self.MWLayout.itemAt(self.itemAt)
        widget = item.widget()
        widget.setParent(None)

#-------redirect showConfigButton
        self.Brd_Shw_Cfgs.setText("showConfigs...")
        self.Brd_Shw_Cfgs.disconnect()
        self.Brd_Shw_Cfgs.clicked.connect(self.CFG_SHW)

#---Preset-Config-Menu
    def CFG_PS(self):
#-------create menuWindow
        self.PS_Wndw = QWidget()

#-------create a small layout
        self.PS_Layout = QVBoxLayout()

#-------create Combobox with Presets
        self.PS_CB = QComboBox()
        Presets = ["FMCW", "RangeDoppler", "RangeProfile"]
        self.PS_CB.addItems(Presets)

#-------create a load Button
        self.PS_PshBtn = QPushButton("load...")
        self.PS_PshBtn.setToolTip("load Config-Preset")
        self.PS_PshBtn.clicked.connect(self.CFG_PS_LOAD)
        self.PS_PshBtn.setFixedWidth(50)

#-------fill layout and define Window
        self.PS_Layout.addWidget(self.PS_CB, Qt.AlignCenter|Qt.AlignTop)
        self.PS_Layout.addWidget(self.PS_PshBtn, Qt.AlignRight|Qt.AlignBottom)

        self.PS_Wndw.setLayout(self.PS_Layout)
        self.PS_Wndw.resize(256, 128)
        self.PS_Wndw.setWindowTitle("Preset Configs")
        self.PS_Wndw.show()

#---Preset-load-function
    def CFG_PS_LOAD(self):
#-------get choosen preset
        choosen = self.PS_CB.currentText()

#-------load preset
        if choosen == "FMCW":
            self.BCfg = self.StdCfg
            self.BCfg["fStrt"] = 76e9
            self.BCfg["fStop"] = 79e9
            self.BCfg["TRampUp"] = 25.6e-6
            self.BCfg["TRampDo"] = 1e-6
            self.BCfg["TInt"] = 1
            self.BCfg["Tp"] = 126.6e-6
            self.BCfg["N"] = 504
            self.BCfg["Np"] = 4
            self.BCfg["NrFrms"] = 100
            self.BCfg["TxSeq"] = np.array([1, 2, 3, 4])

            self.BFCfg = self.SBCfg
            self.BFCfg["RangeFFT"] = 2**10
            self.BFCfg["AngFFT"] = 2**8
            self.BFCfg["Abs"] = 1
            self.BFCfg["Ext"] = 1
            self.BFCfg["RMin"] = 1
            self.BFCfg["RMax"] = 10
            self.BFCfg["ChnOrder"] = np.array([0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                                               18, 19, 20,21, 22, 24, 25, 26, 27, 28, 29, 30, 31])

        elif choosen == "RangeDoppler":
            self.BCfg = self.StdCfg
            self.BCfg["fStrt"] = 76e9
            self.BCfg["fStop"] = 78e9
            self.BCfg["TRampUp"] = 128e-6
            self.BCfg["TRampDo"] = 16e-6
            self.BCfg["TInt"] = 500e-3
            self.BCfg["Tp"] = 400e-6
            self.BCfg["N"] = 256
            self.BCfg["Np"] = 32
            self.BCfg["NrFrms"] = 100

            self.RDCfg = self.SRCfg
            self.RDCfg["RangeFFT"] = 2**10
            self.RDCfg["VelFFT"] = 2**10
            self.RDCfg["Abs"] = 1
            self.RDCfg["Ext"] = 1
            self.RDCfg["RMin"] = 1
            self.RDCfg["RMax"] = 10
            self.RDCfg["RemoveMean"] = 0

        elif choosen == "RangeProfile":
            self.BCfg = self.StdCfg
            self.BCfg["fStrt"] = 76e9
            self.BCfg["fStop"] = 78e9
            self.BCfg["TRampUp"] = 25.6e-6
            self.BCfg["TRampDo"] = 1e-6
            self.BCfg["TInt"] = 1
            self.BCfg["Tp"] = 126.6e-6
            self.BCfg["N"] = 504
            self.BCfg["Np"] = 4
            self.BCfg["NrFrms"] = 100
            self.BCfg["TxSeq"] = np.array([1, 2, 3, 4])

            self.RPCfg = self.SPCfg
            self.RPCfg["NFFT"] = 2**12
            self.RPCfg["Abs"] = 1
            self.RPCfg["Ext"] = 1
            self.RPCfg["RMin"] = 1
            self.RPCfg["RMax"] = 10

        else:
            self.errmsg("NameError!", "No Presets found!\nPlease try again!", "c")
            return

        self.errmsg("Preset loaded!", "Successfully loaded Preset: " + choosen, "i")
        self.PS_Wndw.close()

#---Beamforming config function

    def BMF_CFG(self):
#-------Create a new Window
        self.Bmf_Wndw = LockWindow()

#-------Create a list for all Entries
        self.Bmf_Lst = QListWidget()
        self.Bmf_Lst.setFixedWidth(150)
#-------Add all editable options
        Opts = ["RangeFFT", "AngFFT", "Abs", "Ext", "RMin", "RMax", "ChnOrder", "NIni", "RemoveMean", "Window", "dB", "FuSca"]
        self.Bmf_Lst.addItems(Opts)
        self.Bmf_Lst.currentItemChanged.connect(self.BMF_CFG_UPDATE)

#-------Create a changeable title
        self.Bmf_Ttl = QLabel("")
        self.Bmf_Ttl.setFixedHeight(50)
        self.Bmf_Ttl.setFont(QtGui.QFont("Times", 20, QtGui.QFont.Bold))

#-------Create a Button to save config
        self.Bmf_Save = QPushButton("save...")
        self.Bmf_Save.setToolTip("save all set options!")
        self.Bmf_Save.clicked.connect(self.BMF_CFG_SAVE)

#-------Create a button to reset all Bmf-Configs
        self.Bmf_Rst = QPushButton("Reset Config...")
        self.Bmf_Rst.setToolTip("Reset Beamforming-Config")
        self.Bmf_Rst.clicked.connect(self.BMF_CFG_RST)

#-------Create Variable-Display
        self.Bmf_Var = QLabel("Variable-Display")

#-------Create original-value-display
        self.Bmf_Orig = QLabel("Orig-Value-Display")

#-------Create a New-Value-Display with check-function
        self.Bmf_New = QLineEdit()
        self.Bmf_New.setPlaceholderText("Enter new value here!")
        self.Bmf_New.textChanged.connect(self.BMF_CFG_CHCK)

#-------Create Pic-Display
        self.Bmf_Pic = QLabel("Pic-Display")

#-------Create Explain-Display
        self.Bmf_Exp = QLabel("Explain-Display")

#-------Create Convert-Display
        self.Bmf_Conv = QLabel("Convert-Display")

#-------Create a Layout and fill it up
        self.Bmf_Layout = QGridLayout()
        self.Bmf_Layout.addWidget(self.Bmf_Lst, 0, 0, 5, 1, Qt.AlignLeft)
        self.Bmf_Layout.addWidget(self.Bmf_Ttl, 0, 1, 1, 4, Qt.AlignTop)
        self.Bmf_Layout.addWidget(self.Bmf_Var, 1, 1, 1, 1, Qt.AlignLeft)
        self.Bmf_Layout.addWidget(self.Bmf_Orig, 1, 2, 1, 1, Qt.AlignCenter)
        self.Bmf_Layout.addWidget(self.Bmf_New, 1, 3, 1, 1, Qt.AlignCenter)
        self.Bmf_Layout.addWidget(self.Bmf_Conv, 1, 4, 1, 1, Qt.AlignRight)
        self.Bmf_Layout.addWidget(self.Bmf_Pic, 2, 1, 1, 4, Qt.AlignCenter)
        self.Bmf_Layout.addWidget(self.Bmf_Exp, 3, 1, 1, 4, Qt.AlignCenter)
        self.Bmf_Layout.addWidget(self.Bmf_Rst, 4, 1, 1, 1, Qt.AlignBottom)
        self.Bmf_Layout.addWidget(self.Bmf_Save, 4, 4, 1, 1, Qt.AlignBottom)

#-------set Window geometry etc.
        self.Bmf_Wndw.setLayout(self.Bmf_Layout)
        self.Bmf_Wndw.resize(720, 640)
        self.Bmf_Wndw.setWindowTitle("Beamforming-Configuration")
        self.Bmf_Wndw.show()

#---Beamforming-Window-update-function
    def BMF_CFG_UPDATE(self):
#-------get current item
        showMe = self.Bmf_Lst.currentItem().text()

#-------check for Lock
        if self.Lock:
            return

#-------clear Input
        self.Bmf_New.clear()

#-------check what to display and show
        if showMe == "RangeFFT":
            self.Bmf_Ttl.setText("RangeFFT - Range Fast Fourier Transform")
            self.Bmf_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SBCfg["RangeFFT"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [const]")
            self.Bmf_Conv.setText("No Convertion!")
            self.Bmf_Exp.setText("This variable defines the window in which the FFT is performed. This means it is only for calculation.\n"
                                 "Calculation works the fastest if this value is 2 by the power of n!")
            self.Bmf_New.setText(str(self.TBCfg["RangeFFT"]))

        elif showMe == "AngFFT":
            self.Bmf_Ttl.setText("AngFFT - Angle Fast Fourier Transform")
            self.Bmf_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SBCfg["AngFFT"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [const]")
            self.Bmf_Conv.setText("No Convertion!")
            self.Bmf_Exp.setText("This variable defines the window in which the FFT is performed. This means it is only for calculation.\n"
                                 "Calculation works the fastest if this value is 2 by the power of n!")
            self.Bmf_New.setText(str(self.TBCfg["AngFFT"]))

        elif showMe == "Abs":
            self.Bmf_Ttl.setText("Abs - Calculated Magnitude Spectrum")
            self.Bmf_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SBCfg["Abs"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [bool]")
            self.Bmf_Conv.setText("Converter: Ready!")
            self.Bmf_Exp.setText("Choose if the absolut values should be used or not!")
            self.Bmf_New.setText(str(self.TBCfg["Abs"]))

        elif showMe == "Ext":
            self.Bmf_Ttl.setText("Ext - Extract Range Interval")
            self.Bmf_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SBCfg["Ext"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [bool]")
            self.Bmf_Conv.setText("Converter: Ready")
            self.Bmf_Exp.setText("Choose if you want to take RMin and RMax into account!")
            self.Bmf_New.setText(str(self.TBCfg["Ext"]))

        elif showMe == "RMin":
            self.Bmf_Ttl.setText("RMin - Range Minimum")
            self.Bmf_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SBCfg["RMin"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [m]")
            self.Bmf_Conv.setText("Converter: Ready!")
            self.Bmf_Exp.setText("Defines the minimum Range. Everything in front of this point will get ignored.\nUse this Variable to Scale the y-axis of the plot!")
            self.Bmf_New.setText(str(self.TBCfg["RMin"]))

        elif showMe == "RMax":
            self.Bmf_Ttl.setText("RMax - Range Maximum")
            self.Bmf_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SBCfg["RMax"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [m]")
            self.Bmf_Conv.setText("Converter: Ready!")
            self.Bmf_Exp.setText("Defines the maximum Range. Everything behind this point will get ignored. Use this Variable to Scale the y-axis of the plot!")
            self.Bmf_New.setText(str(self.TBCfg["RMax"]))

        elif showMe == "ChnOrder":
            self.Bmf_Ttl.setText("ChnOrder - Channel-Order")
            self.Bmf_Var.setText("Variable Name:\n"+showMe)
            original = str([7, 15, 23])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [array]")
            self.Bmf_Conv.setText("No Convertion!")
            self.Bmf_Exp.setText("Enter the 3 Channels that should be deleted! Seperation works with ';'! -> 3;17;29")

        elif showMe == "NIni":
            self.Bmf_Ttl.setText("NIni - ignore samples")
            self.Bmf_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SBCfg["NIni"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [const]")
            self.Bmf_Conv.setText("No Conversion!")
            self.Bmf_Exp.setText("This variable defines how many samples are left ignored at the Start of a MeasData-array e.g.")
            self.Bmf_New.setText(str(self.TBCfg["NIni"]))

        elif showMe == "RemoveMean":
            self.Bmf_Ttl.setText("RemoveMean - Remove Mean from Data")
            self.Bmf_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SBCfg["RemoveMean"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [bool]")
            self.Bmf_Conv.setText("Converter: Ready!")
            self.Bmf_Exp.setText("If True, all meanData will be removed from the MeasData-array!")
            self.Bmf_New.setText(str(self.TBCfg["RemoveMean"]))

        elif showMe == "Window":
            self.Bmf_Ttl.setText("Window - Lay Window over Data")
            self.Bmf_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SBCfg["Window"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [bool]")
            self.Bmf_Conv.setText("Converter: Read!")
            self.Bmf_Exp.setText("If true, lays a special cost-function over Data/DataShape!")
            self.Bmf_New.setText(str(self.TBCfg["Window"]))

        elif showMe == "dB":
            self.Bmf_Ttl.setText("dB - Returned Data-Scale")
            self.Bmf_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SBCfg["dB"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [bool]")
            self.Bmf_Conv.setText("Converter: Ready!")
            self.Bmf_Exp.setText("Choose between Raw Data and Data as dBV!")
            self.Bmf_New.setText(str(self.TBCfg["dB"]))

        elif showMe == "FuSca":
            self.Bmf_Ttl.setText("FuSca - FFT-Scaling-Constant")
            self.Bmf_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SBCfg["FuSca"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [const]")
            self.Bmf_Conv.setText("No Conversion!")
            self.Bmf_Exp.setText("This is the Data-Scaling-value for post-FFT arrays.")
            self.Bmf_New.setText(str(self.TBCfg["FuSca"]))

        else:
            self.errmsg("NameError!", "Item '" + showMe + "' not found!", "c")
            self.Bmf_Wndw.close()
            return

#-------show chosen options
        self.Bmf_Wndw.show()

#---check input-function
    def BMF_CFG_CHCK(self):
#-------get current item
        showMe = self.Bmf_Lst.currentItem().text()

#-------get value after change
        value = self.Bmf_New.text()

#-------check value and save&convert if possible
        try:
            if float(value) >= 0:
                if showMe in ["RMin", "RMax"]:
                    new_value = str(float(value) * 1e-3)
                    self.Bmf_Conv.setText("Converted Value:\n"+new_value+" [km]")
                    if showMe == "RMin":
                        if float(value) >= 0:
                            self.TBCfg["RMin"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "RMax":
                        if float(value) > self.TBCfg["RMin"]:
                            self.TBCfg["RMax"] = float(value)
                        else:
                            raise LookupError

                elif showMe in ["AngFFT", "RangeFFT", "FuSca", "NIni"]:
                    if showMe == "AngFFT":
                        if float(value) > 0:
                            self.TBCfg["AngFFT"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "RangeFFT":
                        if float(value) > 0:
                            self.TBCfg["RangeFFT"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "FuSca":
                        if float(value) > 0:
                            self.TBCfg["Fusca"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "NIni":
                        if float(value) >= 0:
                            self.TBCfg["NIni"] = float(value)
                        else:
                            raise LookupError

                elif showMe in ["Abs", "Ext", "dB", "Window", "RemoveMean"]:
                    if float(value) == 0:
                        self.Bmf_Conv.setText("Converted Value:\nFalse! [bool]")
                    elif float(value) == 1:
                        self.Bmf_Conv.setText("Converted Value:\nTrue! [bool]")
                    else:
                        raise LookupError
                    if showMe == "Abs":
                        self.TBCfg["Abs"] = float(value)
                    elif showMe == "Ext":
                        self.TBCfg["Ext"] = float(value)
                    elif showMe == "dB":
                        self.TBCfg["dB"] = float(value)
                    elif showMe == "Window":
                        self.TBCfg["Window"] = float(value)
                    elif showMe == "RemoveMean":
                        self.TBCfg["RemoveMean"] = float(value)

                else:
                    raise ValueError

            else:
                raise ValueError

#-------except all possible Errors
        except ValueError:
            if showMe == "ChnOrder":
                Channels = np.arange(32)
                try:
                    n = 0
                    lst = []
                    while n < len(value):
                        if value[n] != ";" and value[n] !=" ":
                            nr = value[n]

                            if value[n+1] != ";" and value[n+1] != " ":
                                nr = nr + value[n+1]
                                lst.append(int(nr))
                                n += 2

                            else:
                                lst.append(int(nr))
                                n += 1
                        else:
                            n += 1
                    Chn = np.delete(Channels, lst)

                    self.TBCfg["ChnOrder"] = Chn

                except ValueError:
                    pass
                except UnboundLocalError:
                    pass
                except AttributeError:
                    pass
                except IndexError:
                    try:
                        lst.append(int(nr))
                        Chn = np.delete(Channels, lst)
                        self.TBCfg["ChnOrder"] = Chn
                    except ValueError:
                        pass

        except LookupError:
            self.Lock = True
            global lock
            lock = self. Lock
            self.Bmf_New.setStyleSheet("border: 3px solid red; background: yellow; color: red")
            self.Bmf_Conv.setText("invalid Value!")
            self.Bmf_Save.setEnabled(False)
            return

        self.Lock = False
        lock = self.Lock
        self.Bmf_New.setStyleSheet(self.origStyleSheet)
        self.Bmf_Save.setEnabled(True)

#---save Beamforming-Config-function
    def BMF_CFG_SAVE(self):
#-------safety-question
        Qstn = self.errmsg("Set Config?", "Are you sure you want to set new Config?\nIf some variables are not set right plotting may not work!", "q")

#-------check answer
        if Qstn == 0:
            cont = True
        else:
            cont = False

#-------continue if answer is yes, else abort
        if cont:
            for value in self.TBCfg:
                if value == 0:
                    self.errmsg("ValueError!", "It seems that not all Config-Variables have been set to a specific value!\nThis means some variables are still set to 0!\n"
                                "If this is not wanted please set variables again!", "w")
                    self.BFCfg = self.TBCfg
                    return
            self.BFCfg = self.TBCfg
            self.errmsg("Confirmed!", "Config saved successfully!", "i")
        else:
            self.errmsg("Config not set!", "The User-Config is not set, but still saved in the Window!", "i")

#---Reset Config-Function
    def BMF_CFG_RST(self):
#-------safety-question
        Qstn = self.errmsg("Are you sure?", "If you reset the BeamForming-Config, everything except the standard-Config is lost!\nContinue anyways?", "q")

#-------check answer
        if Qstn == 0:
            cont = True
        else:
            cont = False

#-------continue or abort
        if cont:
            self.BFCfg = self.SBCfg
            self.TBCfg = self.BFCfg
            self.errmsg("Confirmed!", "All Configs have been reset!", "i")
        else:
            self.errmsg("Config not reset!", "The Beamforming-Config has not been reset!", "i")

#---RangeDoppler-Config-Function
    def RD_CFG(self):
#-------Create a new Window
        self.RD_Wndw = LockWindow()

#-------Create a List with all changeable config-variables
        self.RD_Lst = QListWidget()
        self.RD_Lst.setFixedWidth(150)

#-------Add names to list
        Opts = ["RangeFFT", "VelFFT", "Abs", "Ext", "RMin", "RMax", "RemoveMean", "N", "Np", "Window", "dB", "FuSca", "fc", "Tp", "ThresdB"]
        self.RD_Lst.addItems(Opts)
        self.RD_Lst.currentItemChanged.connect(self.RD_CFG_UPDATE)

#-------Create Title
        self.RD_Ttl = QLabel("")
        self.RD_Ttl.setFixedHeight(50)
        self.RD_Ttl.setFont(QtGui.QFont("Times", 20, QtGui.QFont.Bold))

#-------create a save-Button
        self.RD_Save = QPushButton("save...")
        self.RD_Save.setToolTip("save all set options!")
        self.RD_Save.clicked.connect(self.RD_CFG_SAVE)

#-------create a reset-Button
        self.RD_Rst = QPushButton("Reset Config...")
        self.RD_Rst.setToolTip("Reset RangeDoppler-Config")
        self.RD_Rst.clicked.connect(self.RD_CFG_RST)

#-------create Variabel-Display
        self.RD_Var = QLabel("Variabel-Display")

#-------create original-value-Display
        self.RD_Orig = QLabel("Orig-Value-Display")

#-------create New-Value_Display with check-function
        self.RD_New = QLineEdit()
        self.RD_New.setPlaceholderText("Enter new value here!")
        self.RD_New.textChanged.connect(self.RD_CFG_CHCK)

#-------create Pic-Display
        self.RD_Pic = QLabel("Pic-Display")

#-------create a explain-display
        self.RD_Exp = QLabel("Explain-Display")

#-------create a Convert-Display
        self.RD_Conv = QLabel("Convert-Display")

#-------create a Layout to fill up
        self.RD_Layout = QGridLayout()
        self.RD_Layout.addWidget(self.RD_Lst, 0, 0, 5, 1, Qt.AlignLeft)
        self.RD_Layout.addWidget(self.RD_Ttl, 0, 1, 1, 4, Qt.AlignTop)
        self.RD_Layout.addWidget(self.RD_Var, 1, 1, 1, 1, Qt.AlignLeft)
        self.RD_Layout.addWidget(self.RD_Orig, 1, 2, 1, 1, Qt.AlignCenter)
        self.RD_Layout.addWidget(self.RD_New, 1, 3, 1, 1, Qt.AlignCenter)
        self.RD_Layout.addWidget(self.RD_Conv, 1, 4, 1, 1, Qt.AlignRight)
        self.RD_Layout.addWidget(self.RD_Pic, 2, 1, 1, 4, Qt.AlignCenter)
        self.RD_Layout.addWidget(self.RD_Exp, 3, 1, 1, 4, Qt.AlignCenter)
        self.RD_Layout.addWidget(self.RD_Rst, 4, 1, 1, 1, Qt.AlignBottom)
        self.RD_Layout.addWidget(self.RD_Save, 4, 4, 1, 1, Qt.AlignBottom)

#-------set Window geometry etc.
        self.RD_Wndw.setLayout(self.RD_Layout)
        self.RD_Wndw.resize(720, 640)
        self.RD_Wndw.setWindowTitle("RangeDoppler-Configuration")
        self.RD_Wndw.show()

#---RangeDopplerConfigWindow-Update-function
    def RD_CFG_UPDATE(self):
#-------get current item
        showMe = self.RD_Lst.currentItem().text()

#-------check for lock
        if self.Lock:
            return

#-------clear input
        self.RD_New.clear()

#-------check what to display and show
        if showMe == "RangeFFT":
            self.RD_Ttl.setText("RangeFFT - Range Fast Fourier Transform")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["RangeFFT"])
            self.RD_Orig.setText("Original Value:\n" + original + " [const]")
            self.RD_Conv.setText("No Conversion!")
            self.RD_Exp.setText("This variable defines the window in which the FFT is performed. This means it is only for calculation.\n"
                                "Calculation works the fastest if this value is 2 by the power of n!")
            self.RD_New.setText(str(self.TRCfg["RangeFFT"]))

        elif showMe == "VelFFT":
            self.RD_Ttl.setText("VelFFT - Velocity Fast Fourier Transform")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["VelFFT"])
            self.RD_Orig.setText("Original Value:\n" + original + " [const]")
            self.RD_Conv.setText("No Conversion!")
            self.RD_Exp.setText("This variable defines the window in which the FFT is performed. This means it is only for calculation.\n"
                                "Calculation works the fastest if this value is 2 by the power of n!")
            self.RD_New.setText(str(self.TRCfg["VelFFT"]))

        elif showMe == "RemoveMean":
            self.RD_Ttl.setText("RemoveMean - Remove Mean Values")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["RemoveMean"])
            self.RD_Orig.setText("Original Value:\n" + original + " [bool]")
            self.RD_Conv.setText("Converter: Ready!")
            self.RD_Exp.setText("Choose if mean values are taken into account or not!")
            self.RD_New.setText(str(self.TRCfg["RemoveMean"]))

        elif showMe == "Abs":
            self.RD_Ttl.setText("Abs - Calculated Magnitude Spectrum")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["Abs"])
            self.RD_Orig.setText("Original Value:\n" + original + " [bool]")
            self.RD_Conv.setText("Converter: Ready!")
            self.RD_Exp.setText("Choose if the absolut values should be used or not!")
            self.RD_New.setText(str(self.TRCfg["Abs"]))

        elif showMe == "Ext":
            self.RD_Ttl.setText("Ext - Extract Range Interval")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["Ext"])
            self.RD_Orig.setText("Original Value:\n" + original + " [bool]")
            self.RD_Conv.setText("Converter: Ready!")
            self.RD_Exp.setText("Choose if you want to take RMin and RMax into account!")
            self.RD_New.setText(str(self.TRCfg["Ext"]))

        elif showMe == "RMin":
            self.RD_Ttl.setText("RMin - Range Minimum")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["RMin"])
            self.RD_Orig.setText("Original Value:\n" + original + " [m]")
            self.RD_Conv.setText("Converter: Ready!")
            self.RD_Exp.setText("Defines the minimum Range. Everything in front of this point will get ignored.\n"
                                "Use this variable to Scale the y-axis of the plot!")
            self.RD_New.setText(str(self.TRCfg["RMin"]))

        elif showMe == "RMax":
            self.RD_Ttl.setText("RMax - Range Maximum")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["RMax"])
            self.RD_Orig.setText("Original Name:\n" + original + " [m]")
            self.RD_Conv.setText("Converter: Ready!")
            self.RD_Exp.setText("Defines the maximum Range. Everything behind this point will get ignored.\n"
                                "Use this variable to Scale the y-axis of the plot!")
            self.RD_New.setText(str(self.TRCfg["RMax"]))

        elif showMe == "N":
            self.RD_Ttl.setText("N samples - like Board-Config")
            self.RD_Ttl.setText("Variable Name:\n"+ showMe)
            original = str(self.SRCfg["N"])
            self.RD_Orig.setText("Original Value:\n"+original+" [samples]")
            self.RD_Conv.setText("No Convertion!")
            self.RD_Exp.setText("Like 'N' from the Board-Config!")
            self.RD_New.setText(str(self.TRCfg["N"]))

        elif showMe == "Np":
            self.RD_Ttl.setText("Np - collect n-Frames")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["Np"])
            self.RD_Orig.setText("Original Value:\n" + original + " [frames]")
            self.RD_Conv.setText("No Convertion!")
            self.RD_Exp.setText("Like 'Np' from the Board-Config!")
            self.RD_New.setText(str(self.TRCfg["Np"]))

        elif showMe == "Window":
            self.RD_Ttl.setText("Window - Lay Window over Data")
            self.RD_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SRCfg["Window"])
            self.RD_Orig.setText("Original Name:\n"+original+" [bool]")
            self.RD_Conv.setText("Converter: Ready!")
            self.RD_Exp.setText("If true, lays a special cost-function over Data/DataShape!")
            self.RD_New.setText(str(self.TRCfg["Window"]))

        elif showMe == "dB":
            self.RD_Ttl.setText("dB - Returned Data-Scale")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["dB"])
            self.RD_Orig.setText("Original Value:\n"+original+" [bool]")
            self.RD_Conv.setText("Converter: Ready!")
            self.RD_Exp.setText("Choose between Raw Data and Data as dBV!")
            self.RD_New.setText(str(self.TRCfg["dB"]))

        elif showMe == "FuSca":
            self.RD_Ttl.setText("FuSca - FFT-Scaling-Constant")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["FuSca"])
            self.RD_Orig.setText("Original Value:\n"+original+" [const]")
            self.RD_Conv.setText("No Conversion!")
            self.RD_Exp.setText("This is the Data-Scaling-value for post-FFT arrays.")
            self.RD_New.setText(str(self.TRCfg["FuSca"]))

        elif showMe == "fc":
            self.RD_Ttl.setText("fc - Frequency Centered")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["fc"])
            self.RD_Orig.setText("Original Value:\n"+original+" [Hz]")
            self.RD_Conv.setText("Converter: Ready!")
            self.RD_Exp.setText("This variable describes the middle of fStrt and fStop!")
            self.RD_New.setText(str(self.TRCfg["fc"]))

        elif showMe == "Tp":
            self.RD_Ttl.setText("Tp - TimeBetweenChirps")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["Tp"])
            self.RD_Orig.setText("Original Value:\n"+original+" [ms]")
            self.RD_Conv.setText("Converter: Ready!")
            self.RD_Exp.setText("Like 'Tp' from Board-Config")
            self.RD_New.setText(str(self.TRCfg["Tp"]))

        elif showMe == "ThresdB":
            self.RD_Ttl.setText("ThresdB - thresholdValue as dB")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["ThresdB"])
            self.RD_Orig.setText("Original Value:\n"+original+" [dBV]")
            self.RD_Conv.setText("No Convertion!")
            self.RD_Exp.setText("array with the threshold values of a Data-array -> Scaled values to dBV!")
            self.RD_New.setText(str(self.TRCfg["ThresdB"]))

        else:
            self.errmsg("NameError!", "Item '" + showMe + "' not found!", "c")
            self.RD_Wndw.close()
            return

#-------show chosen option
        self.RD_Wndw.show()

#---RangeDopplerConfigInput-check-function
    def RD_CFG_CHCK(self):
#-------get current Item
        showMe = self.RD_Lst.currentItem().text()

#-------get value after change
        value = self.RD_New.text()

#-------check value and save&convert if possible
        try:
            if float(value) >= 0:
                if showMe in ["RMax", "RMin"]:
                    new_value = str(float(value) * 10e-3)
                    self.RD_Conv.setText("Converted Value:\n" + new_value + " [km]")
                    if showMe == "RMin":
                        if float(value) >= 0:
                            self.TRCfg["RMin"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "RMax":
                        if float(value) > self.TRCfg["RMin"]:
                            self.TRCfg["RMax"] = float(value)
                        else:
                            raise LookupError

                elif showMe in  ["Abs", "Ext", "RemoveMean", "Window", "dB"]:
                    if float(value) == 0:
                        new_value = "False!"
                    elif float(value) == 1:
                        new_value = "True!"
                    else:
                        raise LookupError
                    self.RD_Conv.setText("Converted Value:\n" + new_value + " [bool]")
                    if showMe == "Abs":
                        self.TRCfg["Abs"] = float(value)
                    elif showMe == "Ext":
                        self.TRCfg["Ext"] = float(value)
                    elif showMe == "RemoveMean":
                        self.TRCfg["RemoveMean"] = float(value)
                    elif showMe == "Window":
                        self.TRCfg["Window"] = float(value)
                    elif showMe == "dB":
                        self.TRCfg["dB"] = float(value)

                elif showMe in ["RangeFFT", "VelFFT", "FuSca", "N", "Np"]:
                    if showMe == "RangeFFT":
                        if float(value) > 0:
                            self.TRCfg["RangeFFT"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "VelFFT":
                        if float(value) > 0:
                            self.TRCfg["VelFFT"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "FuSca":
                        if float(value) > 0:
                            self.TRCfg["FuSca"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "N":
                        if float(value) > 0:
                            self.TRCfg["N"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "Np":
                        if float(value) > 0:
                            self.TRCfg["Np"] = float(value)
                        else:
                            raise LookupError

                elif showMe == "fc":
                    if float(value) > 70e9:
                        self.RD_Conv.setText("Converted Value:\n" + str(float(value)*1e-9) +" [GHz]")
                        self.TRCfg["fc"] = float(value)
                    else:
                        raise LookupError

                elif showMe == "Tp":
                    if float(value) > 0:
                        self.RD_Conv.setText("Converted Value:\n" + str(float(value)*1e6) + " [µs]")
                        self.TRCfg["Tp"] = float(value)
                    else:
                        raise LookupError

                else:
                    raise ValueError

            else:
                raise LookupError

        except ValueError:
            pass
        except UnboundLocalError:
            pass
        except AttributeError:
            pass
        except IndexError:
            pass

        except LookupError:
            self.Lock = True
            global lock
            lock = self.Lock
            self.RD_New.setStyleSheet("border: 3px solid red; background: yellow; color: red")
            self.RD_Conv.setText("Invalid Value!")
            self.RD_Save.setEnabled(False)
            return

        self.Lock = False
        lock = self.Lock
        self.RD_New.setStyleSheet(self.origStyleSheet)
        self.RD_Save.setEnabled(True)

#---RangeDopplerConfig-save-function
    def RD_CFG_SAVE(self):
#-------safetyquestion
        Qstn = self.errmsg("Set Config?", "Are you sure that you want to set a new Config?\nIf some variables are not set right plotting may not work!", "q")

#-------check answer
        if Qstn == 0:
            cont = True
        else:
            cont = False

#-------continue if yes, abort if no
        if cont:
            self.RDCfg = self.TRCfg
            self.errmsg("Confirmed!", "Config set successfully!", "i")
        else:
            self.errmsg("Config not set!", "The User-Config is not set, but still temporarly saved in the Window!", "i")

#---RangeDopplerConfig-reset-function
    def RD_CFG_RST(self):
#-------safetyquestion
        Qstn = self.errmsg("Are you sure?", "If you reset the RangeDoppler-Config everything except the Standard-Config is lost!\nContinue anyways?", "q")

#-------check answer
        if Qstn == 0:
            cont = True
        else:
            cont = False

#-------continue or abort
        if cont:
            self.RDCfg = self.SRCfg
            self.TRCfg = self.RDCfg
            self.errmsg("Confirmed!", "RangeDoppler-Config has been reset!", "i")
        else:
            self.errmsg("Config not reset!", "The RangeDoppler-Config has not been reset!", "i")

#---RangeProfile-Config-Window
    def RP_CFG(self):
#-------Create a new Window
        self.RP_Wndw = LockWindow()

#-------create a List with all changeable config-variables
        self.RP_Lst = QListWidget()
        self.RP_Lst.setFixedWidth(150)

#-------add names to listwidget
        Opts = ["NFFT", "Abs", "Ext", "RMin", "RMax", "RemoveMean", "Window", "XPos", "dB", "FuSca"]
        self.RP_Lst.addItems(Opts)
        self.RP_Lst.currentItemChanged.connect(self.RP_CFG_UPDATE)

#-------create Titel
        self.RP_Ttl = QLabel("")
        self.RP_Ttl.setFixedHeight(50)
        self.RP_Ttl.setFont(QtGui.QFont("Times", 20, QtGui.QFont.Bold))

#-------create a button to save config
        self.RP_Save = QPushButton("save...")
        self.RP_Save.setToolTip("save all set options!")
        self.RP_Save.clicked.connect(self.RP_CFG_SAVE)

#-------create a button to reset all RangeProfile-Configs
        self.RP_Rst = QPushButton("Reset Config...")
        self.RP_Rst.setToolTip("reset RangeProfile-Config!")
        self.RP_Rst.clicked.connect(self.RP_CFG_RST)

#-------create Variabel-Display
        self.RP_Var = QLabel("Variable-Display")

#-------create original-Value-Display
        self.RP_Orig = QLabel("Orig-Value-Display")

#-------New-Value-Display
        self.RP_New = QLineEdit()
        self.RP_New.setPlaceholderText("Enter new value here!")
        self.RP_New.textChanged.connect(self.RP_CFG_CHCK)

#-------create Pic-Display
        self.RP_Pic = QLabel("Pic-Display")

#-------create Explain-Display
        self.RP_Exp = QLabel("Explain-Display")

#-------create Converter-Display
        self.RP_Conv = QLabel("Converter-Dislpay")

#-------create a Layout and fill it up
        self.RP_Layout = QGridLayout()
        l = Qt.AlignLeft
        r = Qt.AlignRight
        t = Qt.AlignTop
        c = Qt.AlignCenter
        b = Qt.AlignBottom
        self.RP_Layout.addWidget(self.RP_Lst, 0, 0, 5, 1, l)
        self.RP_Layout.addWidget(self.RP_Ttl, 0, 1, 1, 4, t)
        self.RP_Layout.addWidget(self.RP_Var, 1, 1, 1, 1, l)
        self.RP_Layout.addWidget(self.RP_Orig, 1, 2, 1, 1, c)
        self.RP_Layout.addWidget(self.RP_New, 1, 3, 1, 1, c)
        self.RP_Layout.addWidget(self.RP_Conv, 1, 4, 1, 1, r)
        self.RP_Layout.addWidget(self.RP_Pic, 2, 1, 1, 4, c)
        self.RP_Layout.addWidget(self.RP_Exp, 3, 1, 1, 4, c)
        self.RP_Layout.addWidget(self.RP_Rst, 4, 1, 1, 1, b)
        self.RP_Layout.addWidget(self.RP_Save, 4, 4, 1, 1, b)

#-------set Windowgeometry etc.
        self.RP_Wndw.setLayout(self.RP_Layout)
        self.RP_Wndw.resize(720, 640)
        self.RP_Wndw.setWindowTitle("RangeProfile-Configuration")
        self.RP_Wndw.show()

#---RangeDoppler-Config-Update-function
    def RP_CFG_UPDATE(self):
#-------get current item
        showMe = self.RP_Lst.currentItem().text()

#-------check for Lock
        if self.Lock:
            return

#-------clear Input
        self.RP_New.clear()

#-------check what to display and show
        if showMe == "NFFT":
            self.RP_Ttl.setText("NFFT - Size Fast Fourier Transform")
            self.RP_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SPCfg["NFFT"])
            self.RP_Orig.setText("Original Value:\n"+original+" [const]")
            self.RP_Conv.setText("No Convertion!")
            self.RP_Exp.setText("This variable defines the window in which the FFT is performed. This means it is only for calculation.\n"
                                "Calculation works the fastest if this value is 2 by the power of n!")
            self.RP_New.setText(str(self.TPCfg["NFFT"]))

        elif showMe == "Abs":
            self.RP_Ttl.setText("Abs - Calculated Magnitude Spectrum")
            self.RP_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SPCfg["Abs"])
            self.RP_Orig.setText("Original Value:\n"+original+" [bool]")
            self.RP_Conv.setText("Converter: Ready!")
            self.RP_Exp.setText("Choose if the absolut values should be used or not!")
            self.RP_New.setText(str(self.TPCfg["Abs"]))

        elif showMe == "Ext":
            self.RP_Ttl.setText("Ext - Extract Range Interval")
            self.RP_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SPCfg["Ext"])
            self.RP_Orig.setText("Original Value:\n"+original+" [bool]")
            self.RP_Conv.setText("Converter: Ready!")
            self.RP_Exp.setText("Choose if you want to take RMin and RMax into account!")
            self.RP_New.setText(str(self.TPCfg["Ext"]))

        elif showMe == "RMin":
            self.RP_Ttl.setText("RMin - Range Minimum")
            self.RP_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SPCfg["RMin"])
            self.RP_Orig.setText("Original Value:\n"+original+" [m]")
            self.RP_Conv.setText("Converter: Ready!")
            self.RP_Exp.setText("Defines the minimum Range. Everything before this point will get ignored!")
            self.RP_New.setText(str(self.TPCfg["RMin"]))

        elif showMe == "RMax":
            self.RP_Ttl.setText("RMax - Range Maximum")
            self.RP_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SPCfg["RMax"])
            self.RP_Orig.setText("Original Value:\n"+original+" [m]")
            self.RP_Conv.setText("Converter: Ready!")
            self.RP_Exp.setText("Defines the maximum Range. Everything behind this point will get ignored!")
            self.RP_New.setText(str(self.TPCfg["RMax"]))

        elif showMe == "RemoveMean":
            self.RP_Ttl.setText("RemoveMean - Remove Mean Values")
            self.RP_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SPCfg["RemoveMean"])
            self.RP_Orig.setText("Original Value:\n"+original+" [bool]")
            self.RP_Conv.setText("Converter: Ready!")
            self.RP_Exp.setText("Choose if mean values should be ignored or not!")
            self.RP_New.setText(str(self.TPCfg["RemoveMean"]))

        elif showMe == "Window":
            self.RP_Ttl.setText("Window - Lay Window over Data")
            self.RP_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SPCfg["Window"])
            self.RP_Orig.setText("Original Value:\n"+original+" [bool]")
            self.RP_Conv.setText("Converter: Ready!")
            self.RP_Exp.setText("If true, lays a special cost-function over Data/DataShape!")
            self.RP_New.setText(str(self.TPCfg["Window"]))

        elif showMe == "XPos":
            self.RP_Ttl.setText("XPos - only positive RangeProfile")
            self.RP_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SPCfg["XPos"])
            self.RP_Orig.setText("Original Value:\n"+original+" [bool]")
            self.RP_Conv.setText("Converter: Ready!")
            self.RP_Exp.setText("If true, only takes positive RangeProfileValues!")
            self.RP_New.setText(str(self.TPCfg["XPos"]))

        elif showMe == "dB":
            self.RP_Ttl.setText("dB - Returned Data-Scale")
            self.RP_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SPCfg["dB"])
            self.RP_Orig.setText("Original Value:\n"+original+" [bool]")
            self.RP_Conv.setText("Converter: Ready!")
            self.RP_Exp.setText("Choose between Raw Data and Data as dBV!")
            self.RP_New.setText(str(self.TPCfg["dB"]))

        elif showMe == "FuSca":
            self.RP_Ttl.setText("FuSca - FFT-Scaling-Constant")
            self.RP_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SPCfg["FuSca"])
            self.RP_Orig.setText("Original Value:\n"+original+" [const]")
            self.RP_Conv.setText("No Conversion!")
            self.RP_Exp.setText("This is the Data-Scaling-value for post-FFT arrays.")
            self.RP_New.setText(str(self.TPCfg["FuSca"]))

        else:
            self.errmsg("NameError!", "Item '" + showMe + "' not found!", "c")
            self.RP_Wndw.close()
            return

#-------show chosen option
        self.RP_Wndw.show()

#---check-input-function
    def RP_CFG_CHCK(self):
#-------get current Item
        showMe = self.RP_Lst.currentItem().text()

#-------get value
        value = self.RP_New.text()

#-------check and save&convert if possible
        try:
            if float(value) >= 0:
                if showMe in ["RMin", "RMax"]:
                    new_value = str(float(value) * 1e-3)
                    self.RP_Conv.setText("Converted Value:\n" + new_value + " [km]")
                    if showMe == "RMin":
                        if float(value) >= 0.0 and float(value) < float(self.TPCfg["RMax"]):
                            self.TPCfg["RMin"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "RMax":
                        if float(value) > self.TPCfg["RMin"]:
                            self.TPCfg["RMax"] = float(value)
                        else:
                            raise LookupError

                elif showMe in ["Abs", "Ext", "RemoveMean", "Window", "XPos", "dB"]:
                    if float(value) == 0:
                        self.RP_Conv.setText("Converted Value:\nFalse! [bool]")
                    elif float(value) == 1:
                        self.RP_Conv.setText("Converted Value:\nTrue! [bool]")
                    else:
                        raise LookupError
                    if showMe == "Abs":
                        self.TPCfg["Abs"] = float(value)
                    elif showMe == "Ext":
                        self.TPCfg["Ext"] = float(value)
                    elif showMe == "RemoveMean":
                        self.TPCfg["RemoveMean"] = float(value)
                    elif showMe == "Window":
                        self.TPCfg["Window"] = float(value)
                    elif showMe == "Xpos":
                        self.TPCfg["XPos"] = float(value)
                    elif showMe == "dB":
                        self.TPCfg["dB"] = float(value)

                elif showMe == "NFFT":
                    if float(value) > 0:
                        self.TPCfg["NFFT"] = float(value)
                    else:
                        raise LookupError

                elif showMe == "FuSca":
                    if float(value) > 0:
                        self.TPCfg["FuSca"] = float(value)
                    else:
                        raise LookupError

                else:
                    raise ValueError
            else:
                raise ValueError

#-------except all Erros
        except ValueError:
            pass

        except LookupError:
            self.Lock = True
            global lock
            lock = self.Lock
            self.RP_New.setStyleSheet("border: 3px solid red; background: yellow; color: red")
            self.RP_Conv.setText("invalid Value!")
            self.RP_Save.setEnabled(False)
            return

        self.Lock = False
        lock = self.Lock
        self.RP_New.setStyleSheet(self.origStyleSheet)
        self.RP_Save.setEnabled(True)

#---save RangeProfile-Config
    def RP_CFG_SAVE(self):
#-------safetyquestion
        Qstn = self.errmsg("Set Config?", "Are you sure you want to set new Config?\nIf some variables are not set right plotting may not work!", "q")

#-------check answer
        if Qstn == 0:
            cont = True
        else:
            cont = False

#-------continue or abort
        if cont:
            self.RPCfg = self.TPCfg
            self.errmsg("Confirmed!", "Config set successfully!", "i")
        else:
            self.errmsg("Config not set!", "The User-defined-Config is not set, but still saved in the Window!", "i")

#---reset RangeProfile-Config
    def RP_CFG_RST(self):
#-------safetyquestion
        Qstn = self.errmsg("Reset Config?", "If you reset the RangeProfile-Config, everything except the standard-Config is lost!\nContinue anyways?", "q")

#-------check answer
        if Qstn == 0:
            cont = True
        else:
            cont = False

#-------continue or abort
        if cont:
            self.RPCfg = self.SPCfg
            self.TPCfg = self.RPCfg
            self.errmsg("Confirmed!", "All Configs have been reset!", "i")
        else:
            self.errmsg("Config not reset!", "The RangeDoppler-Config has not been reset!", "i")

#---get-Video-function
    def VIDEO(self):
#-------create a Window
        self.name_Wndw = QWidget()
#-------get Userinput
        self.name_str = QLineEdit()
        self.name_str.setPlaceholderText("for example: 210308_shir_act_FBs014-EPTa")
#-------create Title
        self.name_Ttl = QLabel("Enter VideoName without fileEnding here: ")
#-------create a button
        self.name_btn = QPushButton("ok...")
        self.name_btn.setToolTip("create video")
        self.name_btn.clicked.connect(self.VIDEO_CREATE)
#-------create a Layout and fill it
        self.name_Lay = QGridLayout()
        self.name_Lay.addWidget(self.name_Ttl, 0, 0, 1, 2)
        self.name_Lay.addWidget(self.name_str, 1, 0, 1, 2)
        self.name_Lay.addWidget(self.name_btn, 2, 1, 1, 1)
#-------set Window attributes
        self.name_Wndw.setLayout(self.name_Lay)
        self.name_Wndw.setWindowTitle("get Measurment as Video...")
        self.name_Wndw.resize(256, 128)
        self.name_Wndw.show()

#---create-Video-function
    def VIDEO_CREATE(self):
#-------close Window
        self.name_Wndw.close()
        try:
#-----------check input
            self.videoname = self.name_str.text()
            if len(self.videoname) < 1:
                raise NameError

            images = [img for img in os.listdir("vc") if img.endswith(".png")]

            frame = cv2.imread(os.path.join("vc", images[0]))

            height, width, layers = frame.shape

            self.saveplace = QFileDialog.getExistingDirectory()

            self.savefull = self.saveplace + "/" + self.videoname + ".mp4"

            self.video = cv2.VideoWriter(self.savefull, 0, 1, (width, height))

            for image in images:
                self.video.write(cv2.imread(os.path.join("vc", image)))

            self.video.release()
            self.errmsg("Video created!", "Creation of Video succesfull!", "i")

            for image in glob.glob("vc/*.png"):
                os.remove(image)

        except NameError:
            self.errmsg("NameError!", "Please try again and enter a valid Name!", "w")
            self.VIDEO()

        except IndexError:
            self.errmsg("IndexError!", "VideoCache is empty!\nStart a new Measurement and try again!", "c")

#---get Data function
    def DATA(self):
#-------create a Window
        self.data_Wndw = QWidget()
#-------get User Input
        self.data_str = QLineEdit()
        self.data_str.setPlaceholderText("for example: 210308_shir_act_FBl011-C2V75")
#-------get Title
        self.data_Ttl = QLabel("Enter a fileName without fileEnding here:")
#-------create a button
        self.data_btn = QPushButton("ok...")
        self.data_btn.setToolTip("create a file with data")
        self.data_btn.clicked.connect(self.DATA_CREATE)
#-------create a Layout and fill it
        self.data_Lay = QGridLayout()
        self.data_Lay.addWidget(self.data_Ttl, 0, 0, 1, 2)
        self.data_Lay.addWidget(self.data_str, 1, 0, 1, 2)
        self.data_Lay.addWidget(self.data_btn, 2, 1, 1, 1)
#-------set Window attributes
        self.data_Wndw.setLayout(self.data_Lay)
        self.data_Wndw.setWindowTitle("get Measurement as Dataframe...")
        self.data_Wndw.resize(256,128)
        self.data_Wndw.show()

#---create Data-function
    def DATA_CREATE(self):
#-------close Window
        self.data_Wndw.close()
        try:
#-----------check input
            self.dataname = self.data_str.text()
            if len(self.dataname) < 1:
                raise NameError

            DF = pd.DataFrame(self.AllData)

            self.saveplace = QFileDialog.getExistingDirectory()

            self.savefull = self.saveplace + "/" + self.dataname + ".csv"

            DF.to_csv(self.savefull, sep=";", decimal=",")

            self.errmsg("Data exported!", "Data export to .csv successful!", "i")

        except NameError:
            self.errmsg("NameError!", "Please try again and enter a valid Name!", "w")
            self.DATA()

        except AttributeError:
            self.errmsg("AttributeError!", "There is no data that could be exported!\nPlease start measurement and try again!", "c")

#---Data-Video-function
    def VIDEO_DATA(self):
#-------create Window
        self.VD_Wndw = QWidget()
#-------get Input
        self.VD_str = QLineEdit()
        self.VD_str.setPlaceholderText("for example: 210311_shir_act_FBs045-PTW")
#-------create Title
        self.VD_Ttl = QLabel("enter Name without fileEnding here:")
#-------create button
        self.VD_btn = QPushButton("ok...")
        self.VD_btn.setToolTip("create Video+Data")
        self.VD_btn.clicked.connect(self.VIDEO_DATA_CREATE)
#-------create Layout and fill
        self.VD_Lay = QGridLayout()
        self.VD_Lay.addWidget(self.VD_Ttl, 0, 0, 1, 2)
        self.VD_Lay.addWidget(self.VD_str, 1, 0, 1, 2)
        self.VD_Lay.addWidget(self.VD_btn, 2, 1, 1, 1)
#-------set Window attributes
        self.VD_Wndw.setLayout(self.VD_Lay)
        self.VD_Wndw.setWindowTitle("Video+Data...")
        self.VD_Wndw.resize(256, 128)
        self.VD_Wndw.show()

#---create Data-Video-function
    def VIDEO_DATA_CREATE(self):
#-------close Window
        self.VD_Wndw.close()
        try:
#-----------check input
            self.savename = self.VD_str.text()
            if len(self.savename) < 1:
                raise NameError

            self.saveplace = QFileDialog.getExistingDirectory()

            self.vidname = self.saveplace + "/" + self.savename + ".mp4"
            self.datname = self.saveplace + "/" + self.savename + ".csv"

            images = [i for i in os.listdir("vc") if i.endswith(".png")]
            frame = cv2.imread(os.path.join("vc", images[0]))
            height, width, layoers = frame.shape
            DF = pd.DataFrame(self.AllData)

            self.video = cv2.VideoWriter(self.vidname, 0, 1, (width, height))
            for image in images:
                self.video.write(cv2.imread(os.path.join("vc", image)))
            self.video.release()
            DF.to_csv(self.datname, sep=";", decimal=",")

            self.errmsg("Success!", "Successfully created Video+Data!", "i")

        except NameError:
            self.errmsg("NameError!", "Please try again and enter a valid Name!", "w")
            self.VIDEO_DATA()

        except IndexError:
            self.errmsg("IndexError!", "VideoCache is empty! Video could not be created!", "c")

        except AttributeError:
            self.errmsg("AttributeError!", "DataFrame is empty! .csv could not be created!", "c")

#---Get-Lock-Function
    def GET_LCK():
        global lock
        return lock


# Create Lockable QWidget
class LockWindow(QWidget):
#---redefine closeEvent actions and decide if closeable or not
    def closeEvent(self, event):
        if MainWindow.GET_LCK():
            event.ignore()
        else:
            super(LockWindow, self).closeEvent(event)
            MainWindow.CFG_SHW(self)


# start QApplication if __name__=="__main__"
if __name__ == "__main__":
    Wndw = MainWindow()
    Wndw.show()
    sys.exit(app.exec_())

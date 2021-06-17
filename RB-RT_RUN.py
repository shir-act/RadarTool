import sys
from socket import gethostbyaddr, herror
from Mimo77L import Mimo77L
import RadarProc
import matplotlib as mpl
from matplotlib import figure
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FCA
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NTb
from PyQt5 import QtGui
from PyQt5.Qt import Qt
from PyQt5.QtWidgets import (QMainWindow, QWidget, QApplication, QPushButton, QLineEdit, QMessageBox, QAction,
                             QMenu, QRadioButton, QButtonGroup, QGridLayout, QLabel, QListWidget, QScrollArea,
                             QVBoxLayout, QComboBox, QFileDialog, QDoubleSpinBox, QCheckBox, QSlider, QSpinBox,
                             QTableWidget, QTableWidgetItem, QHeaderView)
import numpy as np
import pandas as pd
import imageio
import os
import glob
import jsonpickle
import time as ttime

mpl.use("Qt5Agg")

app = QApplication(sys.argv)

global Data

# MainWindow-class
class MainWindow(QMainWindow):
    #---QMainWindow.__init__-function---#
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

#-------Define RadarTool version-------#
        self.version = "v1.0.0"

#-------Define standard RadarBook-IP-------#
        self.IP_Brd = "192.168.1.1"

#-------Define User-IP-------#
        self.IP_Usr = "192.168.1.10"

#-------Define connection-status-variable-------#
        self.connected = False

#-------Define Cancel-variable-------#
        self.cancel = False

#-------Define Report-Variable-------#
        self.rep_rep = 0

#-------Define Lock-Variable-------#
        self.Lock = False
        global lock
        lock = False

#-------Define Endloop Variable------#
        self.endloop = False

#-------Define original StyleSheet-------#
        self.origStyleSheet = self.styleSheet()

#-------define cbar variable------#
        self.cbar = False

#-------define BmfPlt variable-------#
        self.Bcsv = pd.read_csv("plot/BMF_PLT.csv", sep=";", decimal=",")

#-------define RDPlt variable-------#
        self.RDcsv = pd.read_csv("plot/RD_PLT.csv", sep=";", decimal=",")

#-------define RPPlt variable-------#
        self.RPcsv = pd.read_csv("plot/RP_PLT.csv", sep=";", decimal=",")

#-------speed of light variable-------#
        self.c0 = 2.99792458e8

#-------define std. CalData-------#
        self.CD = np.array([ 0.82285863+0.67258483j,  0.1000405 -0.81363678j,
       -0.79736781+0.12721354j, -0.75715786+0.39749688j,
       -0.95434558+0.10437024j,  0.15147382+0.72004282j,
       -0.03418481-0.86520618j,  0.55770701+0.76097965j,
       -0.82436711-0.41615629j,  0.08028489+0.68713534j,
        0.66182697-0.26637542j,  0.5687353 -0.4781459j ,
        0.8125686 -0.27092874j, -0.26499802-0.57126367j,
        0.20278442+0.74778283j, -0.61734885-0.56242144j,
        1.        +0.j        , -0.40465695-0.65535796j,
       -0.50257176+0.55470431j, -0.31142795+0.72468185j,
       -0.62641764+0.62805271j,  0.53433669+0.42696893j,
       -0.52717626-0.5997014j ,  0.89064032+0.21475881j,
       -0.94618642-0.08320773j,  0.32728261+0.62191451j,
        0.52635169-0.49205393j,  0.35754097-0.6647526j ,
        0.6615324 -0.5499121j , -0.45985425-0.43874955j,
        0.46482307+0.62053144j, -0.80905557-0.30070472j])

#-------Define Standard-Cfg-------#
        self.StdCfg = {}
        self.StdCfg["fStrt"] = 76e9
        self.StdCfg["fStop"] = 77e9
        self.StdCfg["TRampUp"] = 256e-6
        self.StdCfg["TRampDo"] = 10e-6
        self.StdCfg["TInt"] = 5e-3
        self.StdCfg["Tp"] = 316e-6
        self.StdCfg["N"] = 640
        self.StdCfg["Np"] = 4
        self.StdCfg["NrFrms"] = 100
        self.StdCfg["TxSeq"] = np.array([1, 2, 3, 4])
        self.StdCfg["IniEve"] = 1
        self.StdCfg["IniTim"] = 5e-3
        self.StdCfg["CfgTim"] = 50e-6
        self.StdCfg["ExtEve"] = 0
        self.StdCfg["RMin"] = 1
        self.StdCfg["RMax"] = 10

        self.BCfg = dict(self.StdCfg)
        self.TCfg = dict(self.BCfg)

#-------define Beamforming-Config-------#
        Chn = np.arange(32)
        Chn = np.delete(Chn, [7, 15, 23])

        self.SBCfg = {}
        self.SBCfg["fs"] = -1
        self.SBCfg["kf"] = -1
        self.SBCfg["RangeFFT"] = 1024
        self.SBCfg["AngFFT"] = 128
        self.SBCfg["Abs"] = 1
        self.SBCfg["Ext"] = 1
        self.SBCfg["RMin"] = self.TCfg["RMin"]
        self.SBCfg["RMax"] = self.TCfg["RMax"]
        self.SBCfg["CalData"] = None
        self.SBCfg["ChnOrder"] = Chn
        self.SBCfg["NIni"] = 1
        self.SBCfg["RemoveMean"] = 1
        self.SBCfg["Window"] = 1
        self.SBCfg["dB"] = 1

        self.BFCfg = dict(self.SBCfg)
        self.TBCfg = dict(self.BFCfg)

#-------define standard RangeDoppler-Config-------#
        self.SRCfg = {}
        self.SRCfg["fs"] = -1
        self.SRCfg["kf"] = -1
        self.SRCfg["RangeFFT"] = 4096
        self.SRCfg["VelFFT"] = 1024
        self.SRCfg["Abs"] = 1
        self.SRCfg["Ext"] = 1
        self.SRCfg["RMin"] = self.TCfg["RMin"]
        self.SRCfg["RMax"] = self.TCfg["RMax"]
        self.SRCfg["N"] = self.BCfg["N"]
        self.SRCfg["Np"] = self.BCfg["Np"]
        self.SRCfg["RemoveMean"] = 1
        self.SRCfg["Window"] = 1
        self.SRCfg["dB"] = 1
        self.SRCfg["fc"] = (self.BCfg["fStrt"] + self.BCfg["fStop"]) / 2
        self.SRCfg["Tp"] = self.BCfg["Tp"]
        self.SRCfg["ThresdB"] = 0
        self.SRCfg["NIni"] = 1

        self.RDCfg = dict(self.SRCfg)
        self.TRCfg = dict(self.RDCfg)

#-------define standard RangeProfile-Config-------#
        self.SPCfg = {}
        self.SPCfg["fs"] = -1
        self.SPCfg["kf"] = -1
        self.SPCfg["NFFT"] = 4096
        self.SPCfg["Abs"] = 1
        self.SPCfg["Ext"] = 1
        self.SPCfg["RMin"] = self.TCfg["RMin"]
        self.SPCfg["RMax"] = self.TCfg["RMax"]
        self.SPCfg["RemoveMean"] = 1
        self.SPCfg["Window"] = 1
        self.SPCfg["XPos"] = 1
        self.SPCfg["dB"] = 1
        self.SPCfg["NIni"] = 1

        self.RPCfg = dict(self.SPCfg)
        self.TPCfg = dict(self.RPCfg)

#-------define standard RCS-Config-------#
        self.RCfg = {}
        self.RCfg["RFFT"] = 4096
        self.RCfg["AFFT"] = 512
        self.RCfg["RMin"] = self.TCfg["RMin"]
        self.RCfg["RMax"] = self.TCfg["RMax"]

#-------define standard TxChn and TxPwr-------#
        self.TxChn = 4
        self.TxPwr = 60

#-------define standard RCS Variables-------#
        self.PP = [-0.000007136913372, 0.001293223792425, -0.086184394495573,
                   2.521879013288421, -20.615765519181373]
        self.La = 3
        self.G_Tx = 16
        self.G_Rx = 14
        self.G_c = 17
        self.C1 = 100e-9
        self.R1 = 5e3

#-------start GUI-Creation-------#
        self.start_gui()

#---GUI-startup-function---#
    def start_gui(self):
        #-------Create matplotlib canvas and toolbar-------#
        self.figure = figure.Figure()
        self.canvas = FCA(self.figure)
        self.toolbar = NTb(self.canvas, self)
        self.figure.subplots_adjust(
            top=0.86, bottom=0.05, left=0.1, right=0.71, hspace=0, wspace=0)

#-------Create QButtonGroup for every type of connection and a way to disconnect-------#
        self.Con_Group = QButtonGroup()
        self.set_USB = QRadioButton("USB")
        self.set_USB.setToolTip("needs a RadarBook-USB-PC connection to work")
        self.set_USB.setChecked(False)
        self.set_W_LAN = QRadioButton("LAN or WLAN")
        self.set_W_LAN.setToolTip(
            "needs a RadarBook-(W)LAN-PC connection to work")
        self.set_W_LAN.setChecked(True)
        self.Con_Group.addButton(self.set_USB)
        self.Con_Group.addButton(self.set_W_LAN)

#-------Create a Button to connect to the RadarBook-------#
        self.Con_PshBtn = QPushButton("connect...")
        self.Con_PshBtn.setToolTip("try to connect to INRAS-RadarBook")
        self.Con_PshBtn.clicked.connect(self.CON_TRY)

#-------Create a Button that stops/resets Measurement and closes QApplication-------#
        self.Quit_PshBtn = QPushButton("quit...")
        self.Quit_PshBtn.setToolTip(
            "Stops the measurement, resets connected Board and closes RadarBook-RadarTool.exe")
        self.Quit_PshBtn.clicked.connect(self.QUIT_MW)

#-------Create a Button that stops/resets Measurement without disconnecting-------#
        self.Rst_PshBtn = QPushButton("reset Board...")
        self.Rst_PshBtn.setToolTip(
            "Stops the measurement and resets the connected Board")
        self.Rst_PshBtn.clicked.connect(self.BRD_RST)
        self.Rst_PshBtn.setEnabled(False)

#-------Create a RadarBook-RadarTool-version-display-------#
        self.Vrs_Lbl = QLabel("RadarBookRadarTool.exe " + str(self.version))
        self.Vrs_Lbl.setFont(QtGui.QFont("Times", 8, QtGui.QFont.Bold))
        self.Vrs_Lbl.setFixedHeight(15)

#-------Create a Connectionstatus-display-------#
        self.Con_Sts_Pic = QLabel()
        self.Con_Sts_Pic.setPixmap(
            QtGui.QPixmap("pics/red.png").scaled(30, 30))
        self.Con_Sts_Pic.setFixedSize(50, 30)
        self.Con_Sts_Txt = QLabel("Status:")
        self.Con_Sts_Txt.setFixedSize(125, 30)
        self.Con_Sts_Txt.setFont(QtGui.QFont("Times", 20, QtGui.QFont.Bold))
        self.Con_Sts_Leg = QLabel("Connection-light:\n"
                                  "red:________no Connection!\n"
                                  "yellow:_____working on Connection!\n"
                                  "green:______Connected!")
        self.Con_Sts_Leg.setFont(QtGui.QFont("Times", 7))

#-------Create a Button to turn on/off Board-------#
        self.Brd_Pwr_Btn = QPushButton("Power: ?")
        self.Brd_Pwr_Btn.setCheckable(True)
        self.Brd_Pwr_Btn.setToolTip("Turn on/off the Power!")
        self.Brd_Pwr_Btn.clicked.connect(self.BRD_PWR)
        self.Brd_Pwr_Btn.setEnabled(False)

#-------Create a Button to start FMCW-Measurements-------#
        self.Brd_Msr_FMCW = QPushButton("BeamformingUla:\nRange|Angle...")
        self.Brd_Msr_FMCW.setToolTip(
            "starts the FMCW measurement with before set variables")
        self.Brd_Msr_FMCW.clicked.connect(self.BRD_MSR_FMCW)
        self.Brd_Msr_FMCW.setEnabled(False)

#-------Create a Button for FMCW-RP hybrid measurements-------#
        self.Brd_Msr_RCS = QPushButton("RadarCrossSection:\nRange|Area...")
        self.Brd_Msr_RCS.setToolTip("starts the RCS measurement with "
                                       "before set variables...")
        self.Brd_Msr_RCS.clicked.connect(self.BRD_MSR_RCS)
        self.Brd_Msr_RCS.setEnabled(False)

#-------Create a Button to start RangeDoppler-Measurements-------#
        self.Brd_Msr_RD = QPushButton("RangeDoppler:\nRange|Velocity...")
        self.Brd_Msr_RD.setToolTip(
            "starts the RangeDoppler measurement with before set variables")
        self.Brd_Msr_RD.clicked.connect(self.BRD_MSR_RD)
        self.Brd_Msr_RD.setEnabled(False)

#-------Create a Button for RangeProfile-Measurements-------#
        self.Brd_Msr_RP = QPushButton("RangeProfile:\nRange|dBV...")
        self.Brd_Msr_RP.setToolTip(
            "starts the RangeProfile measurement with before set variables")
        self.Brd_Msr_RP.clicked.connect(self.BRD_MSR_RP)
        self.Brd_Msr_RP.setEnabled(False)

#-------Create a Button to cancel measurements-------#
        self.Brd_Ccl = QPushButton("cancel...")
        self.Brd_Ccl.setToolTip(
            "stop all measurements at the next possible point")
        self.Brd_Ccl.clicked.connect(self.BRD_MSR_CNCL)
        self.Brd_Ccl.setEnabled(False)

#-------Create Button for Post-Analysis-------#
        self.Rep_repeat = QPushButton("from .gif...")
        self.Rep_repeat.setToolTip("reload Measurement from Report .gif")
        self.Rep_repeat.clicked.connect(self.REPORT_RELOAD)

#-------Create button for .csv Post-Analysis-------#
        self.Rep_repcsv = QPushButton("from .csv...")
        self.Rep_repcsv.setToolTip("reload Measurement from Report .csv")
        self.Rep_repcsv.clicked.connect(self.REPORT_REPCSV)

#-------Create a Button to show active Config etc.-------#
        self.Brd_Shw_Cfgs = QPushButton("showConfigs...")
        self.Brd_Shw_Cfgs.setToolTip(
            "show a lot of Config-Information on Screen")
        self.Brd_Shw_Cfgs.clicked.connect(self.CFG_SHW)

#-------Create a spinbox for normalzing-------#
        self.NormBox = QSpinBox()
        self.NormBox.setRange(-200, 0)
        self.NormBox.setSuffix("dB")
        self.NormBox.setValue(-200)

#-------Create CheckBox for normalizing-------#
        self.CheckNorm = QCheckBox("Normalize: on/off")

#-------Create a TableWidget to show max values-------#
        self.MaxTab = QTableWidget()
        self.MaxTab.setFixedWidth(480)
        self.MaxTab.setColumnCount(3)
        self.MaxTab.setHorizontalHeaderItem(
            0, QTableWidgetItem("Measurement/Time:"))
        self.MaxTab.setHorizontalHeaderItem(
            1, QTableWidgetItem("SequenceRepeat [NrFrms]:"))
        self.MaxTab.setHorizontalHeaderItem(
            2, QTableWidgetItem("max. Value [dbV/dBm²]"))
        header = self.MaxTab.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

#-------Create and fill up menubar-------#
        self.mnbr = self.menuBar()

        self.mnbr_file = QMenu()
        self.mnbr_opts = QMenu()
        self.mnbr_info = QMenu()
        self.mnbr_file = self.mnbr.addMenu("&file")
        self.mnbr_opts = self.mnbr.addMenu("&options")
        self.mnbr_info = self.mnbr.addMenu("&info")

#-------Add an info-section to the-------#
        self.mnbr_info_gnrl = QAction("general information...")
        self.mnbr_info_gnrl.triggered.connect(self.SHW_INFO)
        self.mnbr_info.addAction(self.mnbr_info_gnrl)

#-------Add special Board-info-section-------#
        self.mnbr_info_Brd = QAction("Board...")
        self.mnbr_info_Brd.triggered.connect(self.BRD_INFO)
        self.mnbr_info.addAction(self.mnbr_info_Brd)
        self.mnbr_info_Brd.setEnabled(False)

#-------Add ConfigCreator to optionmenu-------#
        self.mnbr_opts_Cr = QAction("CfgCreator...")
        self.mnbr_opts_Cr.triggered.connect(self.CFG_CRTR)
        self.mnbr_opts.addAction(self.mnbr_opts_Cr)

#-------Add configmenu to optionmenu-------#
        self.mnbr_opts_cfg = QAction("Board-Config...")
        self.mnbr_opts_cfg.triggered.connect(self.BRD_CFG)
        self.mnbr_opts.addAction(self.mnbr_opts_cfg)

#-------Add Beamforming-Config to optionmenu-------#
        self.mnbr_opts_bmf = QAction("Beamforming-Config(FMCW)...")
        self.mnbr_opts_bmf.triggered.connect(self.BMF_CFG)
        self.mnbr_opts.addAction(self.mnbr_opts_bmf)

#-------Add RangeDoppler-Config to optionmenu-------#
        self.mnbr_opts_rd = QAction("RangeDoppler-Config...")
        self.mnbr_opts_rd.triggered.connect(self.RD_CFG)
        self.mnbr_opts.addAction(self.mnbr_opts_rd)

#-------Add RangeProfile-Config to optionmenu-------#
        self.mnbr_opts_rp = QAction("RangeProfile-Config...")
        self.mnbr_opts_rp.triggered.connect(self.RP_CFG)
        self.mnbr_opts.addAction(self.mnbr_opts_rp)

#-------Add Pre-set-Configs-------#
        self.mnbr_opts_ps = QAction("Pre-Set-Configs...")
        self.mnbr_opts_ps.triggered.connect(self.CFG_PS)
        self.mnbr_opts.addAction(self.mnbr_opts_ps)

#-------save as config-file-------#
        self.mnbr_opts_saveCfg = QAction("Save as .config...")
        self.mnbr_opts_saveCfg.triggered.connect(self.CFG_SAVE)
        self.mnbr_opts.addAction(self.mnbr_opts_saveCfg)

#-------load from .config-file-------#
        self.mnbr_opts_loadCfg = QAction("Load from .config...")
        self.mnbr_opts_loadCfg.triggered.connect(self.CFG_LOAD)
        self.mnbr_opts.addAction(self.mnbr_opts_loadCfg)

#-------Add a clear-figure-action-------#
        self.mnbr_file_clf = QAction("clear figure...")
        self.mnbr_file_clf.triggered.connect(self.FGR_CLR)
        self.mnbr_file_clf.setShortcut("CTRL+R")
        self.mnbr_file.addAction(self.mnbr_file_clf)

#-------Add video function action-------#
        self.mnbr_file_video = QAction("get Video...")
        self.mnbr_file_video.triggered.connect(self.VIDEO)
        self.mnbr_file.addAction(self.mnbr_file_video)

#-------Add data function action-------#
        self.mnbr_file_data = QAction("get Data...")
        self.mnbr_file_data.triggered.connect(self.DATA)
        self.mnbr_file.addAction(self.mnbr_file_data)

#-------Create the MainWindow and MainWindowLayout-------#
        self.MW = QWidget()
        self.MWLayout = QGridLayout()
        self.MWLayout.addWidget(self.canvas, 0, 0, 15, 11)
        self.MWLayout.addWidget(self.Con_Sts_Txt, 0, 0, 1, 1)
        self.MWLayout.addWidget(self.Con_Sts_Pic, 0, 1, 1, 1)
        self.MWLayout.addWidget(self.Con_Sts_Leg, 0, 2, 1, 1)
        self.MWLayout.addWidget(self.CheckNorm, 0, 4, 1, 1)
        self.MWLayout.addWidget(self.NormBox, 0, 5, 1, 1)
        self.MWLayout.addWidget(self.set_USB, 0, 9, 1, 1)
        self.MWLayout.addWidget(self.set_W_LAN, 0, 10, 1, 1)
        self.MWLayout.addWidget(self.toolbar, 1, 0, 1, 9)
        self.MWLayout.addWidget(self.Con_PshBtn, 1, 9, 1, 2)
        self.MWLayout.addWidget(self.Brd_Pwr_Btn, 2, 0, 1, 1)
        self.MWLayout.addWidget(self.MaxTab, 2, 9, 12, 2)
        self.MWLayout.addWidget(self.Brd_Msr_FMCW, 3, 0, 1, 1)
        self.MWLayout.addWidget(self.Brd_Msr_RCS, 4, 0, 1, 1)
        self.MWLayout.addWidget(self.Brd_Msr_RD, 5, 0, 1, 1)
        self.MWLayout.addWidget(self.Brd_Msr_RP, 6, 0, 1, 1)
        self.MWLayout.addWidget(self.Brd_Ccl, 7, 0, 1, 1)
        self.MWLayout.addWidget(self.Rst_PshBtn, 8, 0, 1, 1)
        self.MWLayout.addWidget(self.Brd_Shw_Cfgs, 9, 0, 1, 1)
        self.MWLayout.addWidget(self.Rep_repeat, 10, 0, 1, 1)
        self.MWLayout.addWidget(self.Rep_repcsv, 11, 0, 1, 1)
        self.MWLayout.addWidget(self.Vrs_Lbl, 14, 10, 1, 1)

#-------set MainWindowLayout to defined MWLayout-------#
        self.MW.setLayout(self.MWLayout)
        self.setCentralWidget(self.MW)
        self.setGeometry(220, 420, 1080, 640)
        self.showMaximized()
        self.setWindowTitle("RB-RT --- RadarBook-RadarTool.exe")
        self.show()

#---closeEvent-Function---#
    def closeEvent(self, event):
        #-------safety-question-------#
        Qstn = self.errmsg(
            "Close RB-RT?", "Are you sure you want to quit?", "q")
#-------check answer and continue with closing or igrnoring-------#
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

#---function with QMessageBox displaying Errors---#
    def errmsg(self, title="critError!", text="Error-type unknown!", icon="c"):
        #-------set icon type-------#
        if icon == "c":
            icon = QMessageBox.Critical
        elif icon == "i":
            icon = QMessageBox.Information
        elif icon == "w":
            icon = QMessageBox.Warning
        elif icon == "q":
            icon = QMessageBox.Question

#-------create QMessageBox-------#
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setIcon(icon)

#-------set diffrent Buttons if icon == "q"-------#
        if icon == QMessageBox.Question:
            msg.addButton(QPushButton("Yes!"), QMessageBox.YesRole)
            msg.addButton(QPushButton("No!"), QMessageBox.NoRole)
        else:
            msg.addButton(QMessageBox.Ok)

#-------execute QMessageBox and receive result-------#
        result = msg.exec_()

#-------return result if icon == "q"-------#
        if icon == QMessageBox.Question:
            return result

#---delete Widgets in layout-function---#
    def deleteLayout(self, layout):
        #-------check if widgets are in layout-------#
        if layout is not None:

            #-----------loop as long as widgets are in layout and delete them-----------#
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                else:
                    self.deleteLayout(item.layout())

#---Quit-programm-function---#
    def QUIT_MW(self):
        #-------check if a connection is active and if so reset Board, disable Power and close connection-------#
        if self.connected:
            self.Board.BrdRst()
            self.Board.BrdPwrDi()
            self.Board.ConClose()
            self.connected = False
#-------disable lock-------#
        global lock
        lock = False
#-------close RadarBook-Radartool.exe and quit QApplication-------#
        self.close()
        self.endloop = True
        app = QApplication(sys.argv)
        app.closeAllWindows()
        app.quit()

#-------try to close cfg_Wndw 4 safetyreasons-------#
        try:
            self.Cfg_Wndw.close()

#-------except if it did not exist-------#
        except AttributeError:
            pass

#-------try to close bmf_cfg-Wndw 4 safetyreasons-------#
        try:
            self.Bmf_Wndw.close()

#-------except if not existed-------#
        except AttributeError:
            pass

#-------try to close rd_cfg-Wndw 4 safetyreasons-------#
        try:
            self.RD_Wndw.close()

#-------except if not existing-------#
        except AttributeError:
            pass

#-------try to close rp_cfg_wndw 4 safetyreasons-------#
        try:
            self.RP_Wndw.close()

#-------except if not existing-------#
        except AttributeError:
            pass

#-------try to close PresetWindow-------#
        try:
            self.PS_Wndw.close()

#-------except if not existing-------#
        except AttributeError:
            pass

#-------try to close BrdInfo-------#
        try:
            self.Brd_Info_Wndw.close()

#-------except if not existing-------#
        except AttributeError:
            pass

#-------try to close infowindow-------#
        try:
            self.info.close()

#-------except if not existing-------#
        except AttributeError:
            pass

#-------try to close videowindow-------#
        try:
            self.name_Wndw.close()

#-------except if not existing-------#
        except AttributeError:
            pass

#-------try to close datawindow-------#
        try:
            self.data_Wndw.close()

#-------except if not existing-------#
        except AttributeError:
            pass

#-------try to close videodatawindow-------#
        try:
            self.VD_Wndw.close()

#-------except if not existing-------#
        except AttributeError:
            pass

#-------try to close reportwindow-------#
        try:
            self.Rep_Wndw.close()

#-------except if not existing-------#
        except AttributeError:
            pass

#-------try to close controlcenter simulation------#
        try:
            self.Rep_Ctrl.close()

#------except if not existing-------#
        except AttributeError:
            pass

#------try to close ConfigCreatorWindow-------#
        try:
            self.ScCr.close()

#------except if not existing-------#
        except AttributeError:
            pass

#---Connection-Try-function---#
    def CON_TRY(self):
        #-------change Con_Sts_Pic to yellow.png-------#
        self.Con_Sts_Pic.setPixmap(QtGui.QPixmap(
            "pics/yellow.png").scaled(30, 30))
#-------Find active QRadioButton-------#
        try:
            if self.set_USB.isChecked():
                self.CON_USB()
            elif self.set_W_LAN.isChecked():
                self.CON_W_LAN()
            else:
                raise TypeError

#-------Except any errors that may come up and if one does change Con_Sts_Pic to red.png-------#
        except TypeError:
            self.Con_Sts_Pic.setPixmap(
                QtGui.QPixmap("pics/red.png").scaled(30, 30))
            self.errmsg(
                "TypeError!", "No connection-type selected!\nPlease choose between USB or (W)LAN!", "i")

#---USB-connection-function---#
    def CON_USB(self):
        #-------Define Board-variable for further steps and set Con_Sts_Pic to green.png if no Errors occur-------#
        try:
            self.Board = Mimo77L("Usb")
            self.Con_Sts_Pic.setPixmap(
                QtGui.QPixmap("pics/green.png").scaled(30, 30))
#-----------set self.connected to true-----------#
            self.connected = True

#-------Except Error if Board is not found and set Con_Sts_Pic to red.png if an Error occurs-------#
        except TypeError:
            self.Con_Sts_Pic.setPixmap(
                QtGui.QPixmap("pics/red.png").scaled(30, 30))
            self.errmsg(
                "ConnectionError!", "Please check your USB-connection!\nTry again if check is finished!", "w")

#---(W)LAN-connection-function---#
    def CON_W_LAN(self):
        #-------Define Board-variable for further steps and set Con_Sts_Pic to green.png if no Errors occur-------#
        try:
            self.Board = Mimo77L("PNet", self.IP_Brd)
#-----------Check if Board responds (is connected) and if so set Con_Sts_Pic to green.png an set self.connected to true-----------#
            try:
                self.Board.BrdDispSts()
                self.Con_Sts_Pic.setPixmap(
                    QtGui.QPixmap("pics/green.png").scaled(30, 30))
                self.connected = True
#---------------continue with CON_DNE----------------#
                self.CON_DNE()
#-----------If Board is not reachable, except Error and raise ConnectionError-----------#
            except IndexError:
                raise ConnectionError

#-------Except Error if Board is not found and set Con_Sts_Pic to red.png-------#
        except ConnectionError:
            self.Con_Sts_Pic.setPixmap(
                QtGui.QPixmap("pics/red.png").scaled(30, 30))
#-----------Ask for IPv4-address-check-----------#
            Qstn = self.errmsg("ConnectionError!", "Please check your WiFi- or cable-connection!\nDo you want to check "
                               "the IPv4-adress of the computer?", "q")
#-----------check if answer is yes or no and check IPv4 if yes-----------#
            if Qstn == 0:
                try:
                    IPv4 = gethostbyaddr("192.168.1.10")
                    print("found IPv4-adress: " +
                          str((IPv4[2])[0]) + " at Ethernet-port named: " + IPv4[0])
                    self.errmsg("ConnectionError!", "Correct IPv4-adress has been found!\nMake sure all cables are "
                                "plugged in or connection with the right WiFi is active!\nIf your PC has multiple "
                                "Ethernet-ports, make sure the right one is used!", "w")
                except herror:
                    self.errmsg("IPConfigError!",
                                "Please try changing your IPv4-adress!", "c")

            elif Qstn == 1:
                self.errmsg("ConnectionError!", "Check if you're connected with the right WiFi if wireless access is "
                            "used!\nIf you want to access via Ethernet, check if all cables are plugged in!", "i")
            else:
                self.errmsg("ConnectionError!", "Check if you're connected with the right WiFi if wireless access is "
                            "used!\nIf you want to access via Ethernet, check if all cables are plugged in!", "i")

#---Connection-Done function---#
    def CON_DNE(self):
        #-------safetycheck if connection is true-------#
        if self.connected == False:
            self.errmsg(
                "TimeOutError", "Connection to Board has been lost!\nTry connecting again!", "c")
            return
#-------continue with changeing the connect-button-------#
        else:
            self.Con_PshBtn.setText("disconnect...")
            self.Con_PshBtn.setToolTip("stop connection with current Board!")
            self.Con_PshBtn.disconnect()
            self.Con_PshBtn.clicked.connect(self.CON_DSC)
#-----------Enable Powercontrol-----------#
            self.Brd_Pwr_Btn.setText("Power: OFF")
            self.Brd_Pwr_Btn.setEnabled(True)
#-----------Enable Measurements-----------#
            self.Brd_Msr_FMCW.setEnabled(True)
            self.Brd_Msr_RCS.setEnabled(True)
            self.Brd_Msr_RD.setEnabled(True)
            self.Brd_Msr_RP.setEnabled(True)
#-----------Enable ResetButton-----------#
            self.Rst_PshBtn.setEnabled(True)
#-----------Enable BoardInfo-----------#
            self.mnbr_info_Brd.setEnabled(True)

#---disconnect function---#
    def CON_DSC(self):
        #-------disable and reset Power Control-------#
        try:
            self.Board.BrdRst()
            self.Board.BrdPwrDi()
            self.Brd_Pwr_Btn.setChecked(False)
            self.Brd_Pwr_Btn.setText("Power: ?")
            self.Brd_Pwr_Btn.setEnabled(False)
#-----------disable Measurement-----------#
            self.Brd_Msr_FMCW.setEnabled(False)
            self.Brd_Msr_RCS.setEnabled(False)
            self.Brd_Msr_RD.setEnabled(False)
            self.Brd_Msr_RP.setEnabled(False)
#-----------disable ResetButton-----------#
            self.Rst_PshBtn.setEnabled(False)
#-----------disable BoardInfo-----------#
            self.mnbr_info_Brd.setEnabled(False)

#-------except AttributeError if no Connection is obtained but disconnect is tried-------#
        except AttributeError:
            pass

#-------erase Board-Variable reset connection variable and set Con_Sts_Pic to red.png-------#
        self.Board = None
        self.connected = False
        self.Con_Sts_Pic.setPixmap(
            QtGui.QPixmap("pics/red.png").scaled(30, 30))

#-------change disconnect button back to connect button-------#
        self.Con_PshBtn.setText("connect...")
        self.Con_PshBtn.setToolTip("try to connect to INRAS-RadarBook")
        self.Con_PshBtn.clicked.connect(self.CON_TRY)

#---create a little window with information---#
    def SHW_INFO(self):
        #-------create Window-------#
        self.info = QWidget()

#-------Add a Label with info-------#
        lbl = QLabel()
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setText("Radarbook-Radartool:\n"+self.version+"\ncreated by shir\n\nThis Tool has been created for:\n"
                    "INRAS RadarBook 'Mimo-77-Tx4Rx8'\n\nRadarbook IPv4:\n"+self.IP_Brd+"\nrequired User IPv4:\n"+self.IP_Usr)

#-------Layout-------#
        lay = QGridLayout()
        lay.addWidget(lbl, 0, 0, 1, 1)

#-------show window-------#
        self.info.setLayout(lay)
        self.info.resize(256, 128)
        self.info.setWindowTitle("Information")
        self.info.show()

#---Clear-figure-function---#
    def FGR_CLR(self):
        self.figure.clear()
        self.canvas.draw()

#---clear videocache function---#
    def VC_CLR(self):
        for image in glob.glob("vc/*.png"):
            os.remove(image)

#---Board-info-function---#
    def BRD_INFO(self):
        #-------get BoardInfo-------#
        self.Brd_RfVers = self.Board.RfGetVers()
        self.Brd_RfVers = QLabel(
            "RadarBook-Frontendversion: " + str(self.Brd_RfVers))

        self.Brd_Name = self.Board.Get("Name")
        self.Brd_Name = QLabel("Name of Board: " + str(self.Brd_Name))

        self.Brd_frqncy_SamplingClock = self.Board.Get("fAdc")
        self.Brd_frqncy_SamplingClock = QLabel(
            "Frequency SamplingClock: " + str(self.Brd_frqncy_SamplingClock * 1e-6) + " [MHz]")

        self.Brd_frqncy_PostCIC = self.Board.Get("fs")
        self.Brd_frqncy_PostCIC = QLabel(
            "Frequency Post-CIC-Filter: " + str(self.Brd_frqncy_PostCIC * 1e-6) + " [MHz]")

        self.BrdDispInf = self.Board.BrdDispInf()

        self.Brd_Temp_SamplingClock = self.BrdDispInf[0]
        self.Brd_Temp_SamplingClock = QLabel(
            "Temperature SamplingClock: " + str(self.Brd_Temp_SamplingClock) + " [°C]")

        self.Brd_Temp_Supply = self.BrdDispInf[1]
        self.Brd_Temp_Supply = QLabel(
            "Temperature PowerAdapter: " + str(self.Brd_Temp_Supply) + " [°C]")

        self.Brd_Volt_Supply = self.BrdDispInf[2]
        self.Brd_Volt_Supply = QLabel(
            "Voltage PowerAdapter: " + str(self.Brd_Volt_Supply) + " [V]")

        self.Brd_Curr_Supply = self.BrdDispInf[3]
        self.Brd_Curr_Supply = QLabel(
            "Current PowerAdapter: " + str(self.Brd_Curr_Supply) + " [A]")

        try:
            if self.Brd_Info_Wndw.isVisible():
                pass

        except AttributeError:
            #-----------create a window-----------#
            self.Brd_Info_Wndw = QWidget()

#-----------create layout and add data-----------#
            self.Brd_Info_Layout = QVBoxLayout()
            self.Brd_Info_Layout.addWidget(self.Brd_Name)
            self.Brd_Info_Layout.addWidget(self.Brd_RfVers)
            self.Brd_Info_Layout.addWidget(self.Brd_frqncy_SamplingClock)
            self.Brd_Info_Layout.addWidget(self.Brd_frqncy_PostCIC)
            self.Brd_Info_Layout.addWidget(self.Brd_Temp_SamplingClock)
            self.Brd_Info_Layout.addWidget(self.Brd_Temp_Supply)
            self.Brd_Info_Layout.addWidget(self.Brd_Volt_Supply)
            self.Brd_Info_Layout.addWidget(self.Brd_Curr_Supply)

#-----------setup window-----------#
            self.Brd_Info_Wndw.setLayout(self.Brd_Info_Layout)
            self.Brd_Info_Wndw.resize(256, 126)
            self.Brd_Info_Wndw.setWindowTitle("BoardInfo")

        self.Brd_Info_Wndw.show()

#---Power On/Off function---#
    def BRD_PWR(self):
        #-------Check if Power is on or off and change on or off-------#
        if self.Brd_Pwr_Btn.isChecked():
            self.Board.BrdPwrEna()
            self.Brd_Pwr_Btn.setChecked(True)
            self.Brd_Pwr_Btn.setText("Power: ON")
        else:
            self.Board.BrdPwrDi()
            self.Brd_Pwr_Btn.setChecked(False)
            self.Brd_Pwr_Btn.setText("Power: OFF")

#---Reset Board and disable Power---#
    def BRD_RST(self, F=0):
        #-------Security-question-------#
        if not F:
            Qstn = self.errmsg("Are you sure?", "Do you want to continue reseting and powering-off the Board?\n"
                               "Connection is not lost during this process!", "q")

#-----------check answer and continue or abort after checking-----------#
            if Qstn == 0:
                cont = True
            elif Qstn == 1:
                cont = False
            else:
                cont = False

#-----------check if a connection is available and reset Board and disable Power-----------#
            if self.connected and cont:
                self.Board.BrdRst()
                self.Board.BrdPwrDi()
                self.Brd_Pwr_Btn.setText("Power: OFF")
                self.Brd_Pwr_Btn.setChecked(False)

#-----------if not connected or answer=No-----------#
            else:
                if cont:
                    self.errmsg("ConnectionError!",
                                "There is no Board connected to Reset!", "i")
                else:
                    pass
#-------if F is True-------#
        else:
            self.Board.BrdRst()

#---Start measurement-function---#
    def BRD_MSR_FMCW(self):
        #-------reset figure etc-------#
        self.FGR_CLR()
        self.BRD_RST(F=True)
        self.RD = 0
        self.RP = 0
#-------check if connection is still active or raise ConnectionError-------#
        try:
            if self.connected:
                pass
            else:
                self.connected = False
                self.Con_Sts_Pic.setPixmap(
                    QtGui.QPixmap("pics/red.png").scaled(30, 30))
                raise ConnectionError

#-----------check if power is on or raise ValueError------------#
            if self.Brd_Pwr_Btn.isChecked():
                pass
            else:
                raise ValueError

#-------except any Errors-------#
        except ConnectionError:
            self.errmsg(
                "ConnectionError!", "Connection to FrontEnd has been lost!\nTry to connect again!", "c")
            self.start_gui()
            return

        except ValueError:
            self.errmsg(
                "ValueError!", "The connected Board has no Power!\nPlease activate the Power first!", "w")
            return

#-------clear vc-------#
        self.VC_CLR()

#-------enable cancel-button-------#
        self.Brd_Ccl.setEnabled(True)

#-------disable FMCW-RP-hybrid measurement-------#
        self.Brd_Msr_RCS.setEnabled(False)

#-------disable RangeDoppler-------#
        self.Brd_Msr_RD.setEnabled(False)

#-------disable RangeProfile-------#
        self.Brd_Msr_RP.setEnabled(False)

#-------disable Report reload-------#
        self.Rep_repeat.setEnabled(False)
        self.Rep_repcsv.setEnabled(False)

#-------enable Beamforming-------#
        self.Proc = RadarProc.RadarProc()

#-------get calibrationdata-------#
        self.calcData = self.Board.BrdGetCalData({"Mask": 1, "Len": 64})

#-------enable Rx and Tx-------#
        self.Board.RfRxEna()

        self.Board.RfTxEna(self.TxChn, self.TxPwr)

#-------set Config and triggermode-------#
        self.Board.RfMeas("ExtTrigUp", self.BCfg)

#-------get values needed for Beamforming-------#
        N = self.Board.Get("N")
        fs = self.Board.Get("fs")
        kf = self.Board.RfGet("kf")
        NrFrms = self.BCfg["NrFrms"]

#-------Beamformingconfig-------#
        self.BFCfg["fs"] = fs
        self.BFCfg["kf"] = kf
        self.BFCfg["CalData"] = self.calcData

#-------set Beamformingconfig-------#
        self.Proc.CfgBeamformingUla(self.BFCfg)

#-------create DataContainer-------#
        self.MeasData = np.zeros((int(N), int(32)))
        self.n = np.arange(int(self.BCfg["N"]))
        self.AllData = np.zeros((int(N), int(8*NrFrms)))

#-------create Scaling-Data-Container: Range-------#
        self.JRan = self.Proc.GetBeamformingUla("Range")
        self.ARan = np.append(self.JRan, self.BFCfg["RMax"])

#-------create Scaling-Data-Container: Angle-------#
        self.JAng = self.Proc.GetBeamformingUla("AngFreqNorm")
        self.AAng = np.append(self.JAng, (self.JAng[0]*-1))
        self.AAng = np.rad2deg(self.AAng)

#-------create Plot-------#
        self.plt = self.figure.add_subplot(111)

#-------maxtab update-------#
        self.MaxTab.clearContents()
        self.MaxTab.setRowCount(1)
        self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                            0, QTableWidgetItem("FMCW"))
        self.MaxTab.setItem((self.MaxTab.rowCount()-1), 1,
                            QTableWidgetItem(str(self.BCfg["NrFrms"])))
        self.MaxTab.setItem((self.MaxTab.rowCount()-1), 2,
                            QTableWidgetItem("<-- total"))

#-------get data-------#
        start = ttime.time()
        for MeasIdx in range(0, int(self.BCfg["NrFrms"])):
            Data = self.Board.BrdGetData()
            Id = ((Data[0, 0] - 1) % 4) + 1
            self.AllData[:, MeasIdx*8:(MeasIdx+1)*8] = Data
            self.AllData[1, MeasIdx*8:(MeasIdx+1)*8] = Id

#-----------Place Data in DataContainer-----------#
            if Id == 1:
                self.MeasData[:, 0:8] = Data
                self.plt.clear()
            elif Id == 2:
                self.MeasData[:, 8:16] = Data
            elif Id == 3:
                self.MeasData[:, 16:24] = Data
            elif Id == 4:
                self.MeasData[:, 24:32] = Data

#---------------Use Beamforming on obtained Data---------------#
                JOpt = self.Proc.BeamformingUla(self.MeasData)

#---------------get peak values---------------#
                JMax = np.amax(JOpt)

#---------------maxtab update---------------#
                delta = ttime.time() - start
                self.MaxTab.setRowCount(self.MaxTab.rowCount() + 1)
                self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                    0, QTableWidgetItem(str(delta)[:-3]))
                self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                    1, QTableWidgetItem(str(MeasIdx)))
                self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                    2, QTableWidgetItem(str(JMax)))

#---------------Use peak values to calculate normalized Data---------------#
                self.JNorm = JOpt - JMax

#---------------limit values for better plot visuals---------------#
                if self.CheckNorm.checkState():
                    self.NormVal = self.NormBox.value()
                    self.JNorm[self.JNorm < self.NormVal] = self.NormVal
                else:
                    self.JNorm = JOpt

#---------------draw Plot---------------#
                self.plt.pcolormesh(self.AAng, self.ARan, self.JNorm)
                self.plt.set_xlabel("Angle [deg]")
                self.plt.set_ylabel("Range [m]")
                self.plt.set_ylim(self.BFCfg["RMin"], self.BFCfg["RMax"])
                self.canvas.draw()
                self.figure.savefig("vc/FMCW_"+str(MeasIdx)+".png")

#---------------proccess Events---------------#
                QApplication.processEvents()

#---------------check for cancel-commands---------------#
                if self.cancel:
                    self.Brd_Ccl.setEnabled(False)
                    self.Brd_Msr_RCS.setEnabled(True)
                    self.Brd_Msr_RD.setEnabled(True)
                    self.Brd_Msr_RP.setEnabled(True)
                    self.Rep_repeat.setEnabled(True)
                    self.Rep_repcsv.setEnabled(True)
                    self.cancel = False
                    self.errmsg(
                        "Canceled!", "Measurement after User-Input abortet!", "i")
                    return

#-------reset when done-------#
        self.Brd_Ccl.setEnabled(False)
        self.Brd_Msr_RCS.setEnabled(True)
        self.Brd_Msr_RD.setEnabled(True)
        self.Brd_Msr_RP.setEnabled(True)
        self.Rep_repeat.setEnabled(True)
        self.Rep_repcsv.setEnabled(True)
        self.errmsg("Measurement Done",
                    "Measurement completed succesfully!", "i")
        self.FMCW = 1
        self.BRD_MSR_DN()

#---Start measurement-function---#
    def BRD_MSR_RCS(self):
#-------reset figure etc-------#
        self.FGR_CLR()
        self.BRD_RST(F=True)
        self.RD = 0
        self.RP = 0
        self.FMCW = 0
        global Data
#-------check if connection is still active or raise ConnectionError-------#
        try:
            if self.connected:
                pass
            else:
                self.connected = False
                self.Con_Sts_Pic.setPixmap(
                    QtGui.QPixmap("pics/red.png").scaled(30, 30))
                raise ConnectionError

#-----------check if power is on or raise ValueError------------#
            if self.Brd_Pwr_Btn.isChecked():
                pass
            else:
                raise ValueError

#-------except any Errors-------#
        except ConnectionError:
            self.errmsg(
                "ConnectionError!", "Connection to FrontEnd has been lost!\nTry to connect again!", "c")
            self.start_gui()
            return

        except ValueError:
            self.errmsg(
                "ValueError!", "The connected Board has no Power!\nPlease activate the Power first!", "w")
            return

#-------RangeProfile Question-------#
        Q = self.errmsg("Choose a Plot-Layout...", "Do you wish to plot the data into a single plot?\n"
                        "Single plot means a RangeProfile plot-layout!", "q")

        if Q == 0:
            RPL = True
        else:
            RPL = False

#-------clear vc-------#
        self.VC_CLR()

#-------enable cancel-button-------#
        self.Brd_Ccl.setEnabled(True)

#-------disable RangeDoppler-------#
        self.Brd_Msr_RD.setEnabled(False)

#-------disable RangeProfile-------#
        self.Brd_Msr_RP.setEnabled(False)

#-------disable std FMCW-------#
        self.Brd_Msr_FMCW.setEnabled(False)

#-------disable Report reload-------#
        self.Rep_repeat.setEnabled(False)
        self.Rep_repcsv.setEnabled(False)

#-------enable Beamforming-------#
        self.Proc = RadarProc.RadarProc()

#-------enable Rx and Tx-------#
        self.Board.RfRxEna()
        self.Board.RfTxEna(self.TxChn, self.TxPwr)

#-------set Config and triggermode-------#
        self.Board.Set('Fifo', 'On')
        self.Board.Set('NrChn', 8)
        self.Board.Set('ClkDiv', 1)
        self.Board.Set("CicEna")
        self.Board.Set('CicStages', 4)
        self.Board.Set('CicDelay', 8)
        self.Board.Set('CicR', 8)
        self.Board.Set("ClkSrc", 1)
        self.Board.Set("AdcImp", 100101)
        self.Board.Set("AdcChn", 4)
        self.Board.Set("AdcGain", 16)
        self.Board.RfMeas("ExtTrigUp", self.BCfg)

#-------get values needed for Calculation-------#
        N = self.Board.Get("N")
        fs = self.Board.Get("fs")
        fc = self.Board.RfGet("fc")
        kf = self.Board.RfGet("kf")
        FuSca = self.Board.Get("FuSca")
        NrChn = int(self.Board.Get("NrChn"))
        NrFrms = self.BCfg["NrFrms"]
        CalData = self.Board.BrdGetCalData({"Mask":1, "Len":72})

        self.RCfg["NFFT"]    = 1024
        self.RCfg["AFFT"]    = 64
        self.RCfg["fs"]      = fs
        self.RCfg["kf"]      = kf
        self.RCfg["fc"]      = fc
        self.RCfg["FuSca"]   = FuSca
        self.RCfg["CalData"] = CalData
        self.RCfg["TxPwr"] = self.TxPwr

        TRPCfg = dict(self.SPCfg)
        TRPCfg["fs"] = fs
        TRPCfg["kf"] = kf
        TRPCfg["FuSca"] = FuSca

        self.Proc.RCSCfg(self.RCfg)
        self.Proc.CfgRangeProfile(TRPCfg)

#-------create DataContainer-------#
        self.AllData = np.zeros((int(N), int(NrChn*NrFrms)))

#-------maxtab update-------#
        self.MaxTab.clearContents()
        self.MaxTab.setRowCount(1)
        self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                            0, QTableWidgetItem("RCS"))
        self.MaxTab.setItem((self.MaxTab.rowCount()-1), 1,
                            QTableWidgetItem(str(NrFrms)))
        self.MaxTab.setItem((self.MaxTab.rowCount()-1), 2,
                            QTableWidgetItem("<-- total"))

#-------create plot-------#
        if RPL:
            self.RCS = self.figure.add_subplot(111)
        else:
            gs = GridSpec(5, 5, figure=self.figure)
            self.RCS = self.figure.add_subplot(gs[:-1, 1:])
            self.ANG = self.figure.add_subplot(gs[-1, 1:])
            self.RAN = self.figure.add_subplot(gs[:-1, 0])
            self.RAN2 = self.RAN.twiny()     
            self.ANG2 = self.ANG.twinx()

#-------get data-------#
        start = ttime.time()
        for MeasIdx in range(0, int(NrFrms)):
            if RPL:
                self.RCS.clear()
                self.RCS.grid(True, "both")
            else:
                self.RAN.clear()
                self.RAN.grid(True, "both")
                self.RAN2.clear()
                self.ANG.clear()
                self.ANG.grid(True, "both")
                self.ANG2.clear()
                self.RCS.clear()
            Data = self.Board.BrdGetData()
            self.AllData[:, int(MeasIdx*NrChn):int((MeasIdx+1)*NrChn)] = Data

#-----------calc data-----------#
            if RPL:
                dBsm, dBV, Range = self.Proc.RCSRP(Data)
            else:
                dBsm, dBV, Range, Angle = self.Proc.RCSBeamformingUla(Data)

            if self.CheckNorm.isChecked():
                mindB = np.mean(dBsm)
            else:
                mindB = None        

#-----------maxtab update-----------#
            delta = ttime.time() - start
            self.MaxTab.setRowCount(self.MaxTab.rowCount() + 1)
            self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                0, QTableWidgetItem(str(delta)[:-3]))
            self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                1, QTableWidgetItem(str(MeasIdx)))
            self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                2, QTableWidgetItem(str(np.amax(dBsm))))

#-----------plotting-----------#
            if RPL:
                self.RCS.plot(Range, np.max(dBsm, axis=1))
                self.RCS.set_ylim(-120, 30)
                self.RCS.set_ylabel("dBm²")
                self.RCS.set_xlabel("Range [m]")
            else:
                self.RCS.pcolormesh(Angle, Range, dBsm, shading="auto", vmin=mindB)
                self.RAN.plot(np.max(dBsm, axis=1), Range)
                self.ANG.plot(Angle, np.max(dBsm, axis=0))
                if not self.CheckNorm.isChecked():
                    self.RAN2.plot(np.max(dBV, axis=1), Range, "r")
                    self.ANG2.plot(Angle, np.max(dBV, axis=0), "r")
                    self.RAN.set_xlim(-70, 20)
                    self.RAN2.set_xlim(-120, -20)
                    self.ANG.set_ylim(-30, 10)
                    self.ANG2.set_ylim(-90, -50)
                    self.RAN2.set_xlabel("dBV")
                    self.ANG2.set_ylabel("dBV")
                self.RAN.set_ylim(self.RCS.get_ylim())
                self.ANG.set_xlim(self.RCS.get_xlim())
                self.ANG.set_ylabel("dBm²")
                self.ANG.yaxis.label.set_rotation(305)
                self.ANG.set_xlabel("Angle [deg]")
                self.RAN.set_ylabel("Range [m]")

#-----------proccess Events-----------#
            self.canvas.draw()
            QApplication.processEvents()

#-----------check for cancel-commands----------#
            if self.cancel:
                self.Brd_Ccl.setEnabled(False)
                self.Brd_Msr_RD.setEnabled(True)
                self.Brd_Msr_RP.setEnabled(True)
                self.Brd_Msr_FMCW.setEnabled(True)
                self.Rep_repeat.setEnabled(True)
                self.Rep_repcsv.setEnabled(True)
                self.cancel = False
                self.errmsg(
                    "Canceled!", "Measurement after User-Input abortet!", "i")
                return

#-------reset when done-------#
        self.Brd_Ccl.setEnabled(False)
        self.Brd_Msr_RD.setEnabled(True)
        self.Brd_Msr_RP.setEnabled(True)
        self.Brd_Msr_FMCW.setEnabled(True)
        self.Rep_repeat.setEnabled(True)
        self.Rep_repcsv.setEnabled(True)
        self.errmsg("Measurement Done",
                    "Measurement completed succesfully!", "i")
        self.RCSM = 1
        self.BRD_MSR_DN()

#---Start RangeDoppler-Measurement---#
    def BRD_MSR_RD(self):
        #-------reset figure etc-------#
        self.FGR_CLR()
        self.BRD_RST(F=True)
        self.FMCW = 0
        self.RP = 0
#-------check if connection is still active or raise ConnectionError-------#
        try:
            if self.connected:
                pass
            else:
                self.connected = False
                self.Con_Sts_Pic.setPixmap(
                    QtGui.QPixmap("pics/red.png").scaled(30, 30))
                raise ConnectionError

#-----------check if power is on or raise ValueError-----------#
            if self.Brd_Pwr_Btn.isChecked():
                pass
            else:
                raise ValueError

#-------except any Errors-------#
        except ConnectionError:
            self.errmsg(
                "ConnectionError!", "Connection to FrontEnd has been lost!\nTry to connect again!", "c")
            self.start_gui()
            return

        except ValueError:
            self.errmsg(
                "ValueError!", "The connected Board has no Power!\nPlease activate the Power first!", "w")
            return

#-------clear vc-------#
        self.VC_CLR()

#-------enable cancel-button-------#
        self.Brd_Ccl.setEnabled(True)

#-------disable FMCW-------#
        self.Brd_Msr_FMCW.setEnabled(False)

#-------disable FMCW-RP-hybrid measurements-------#
        self.Brd_Msr_RCS.setEnabled(False)

#-------disabled RangeProfile-------#
        self.Brd_Msr_RP.setEnabled(False)

#-------disable Report reload-------#
        self.Rep_repeat.setEnabled(False)
        self.Rep_repcsv.setEnabled(False)

#-------enable RangeDoppler-------#
        self.Proc = RadarProc.RadarProc()

#-------enable Rx and Tx-------#
        self.Board.RfRxEna()
        self.Board.RfTxEna(self.TxChn, self.TxPwr)

#-------set Board-Config-------#
        self.Board.Set("NrChn", 1)
        self.Board.RfMeas("ExtTrigUpNp", self.BCfg)

#-------set RangeDoppler-Config-------#
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

#-------create Plot-------#
        self.plt = self.figure.add_subplot(111)

#-------create DataContainer------#
        self.AllData = pd.DataFrame()

#-------create Scaling-Data-Container: Range-------#
        self.JRan = self.Proc.GetRangeDoppler("Range")
        self.ARan = np.append(self.JRan, self.RDCfg["RMax"])

#-------create Scaling-Data-Container: Velocity-------#
        self.JVel = self.Proc.GetRangeDoppler("Vel")
        self.AVel = np.append(self.JVel, (self.JVel[0]*-1))

#-------add info to maxtab--------#
        self.MaxTab.clearContents()
        self.MaxTab.setRowCount(1)
        self.MaxTab.setItem((self.MaxTab.rowCount()-1), 0,
                            QTableWidgetItem("RangeDoppler"))
        self.MaxTab.setItem((self.MaxTab.rowCount()-1), 1,
                            QTableWidgetItem(str(self.BCfg["NrFrms"])))
        self.MaxTab.setItem((self.MaxTab.rowCount()-1), 2,
                            QTableWidgetItem("<-- total"))

#-------Get Data-------#
        start = ttime.time()
        for MeasIdx in range(0, int(self.BCfg["NrFrms"])):
            self.plt.clear()
            Data = self.Board.BrdGetData(Frms)
            self.AllData[MeasIdx] = Data[:, 0]

#-----------Calculate RangeDoppler------------#
            RD = self.Proc.RangeDoppler(Data)

#-----------get Peak-Values------------#
            RDMax = np.amax(RD)

#-----------Maxtab update-----------#
            delta = ttime.time() - start
            self.MaxTab.setRowCount(self.MaxTab.rowCount() + 1)
            self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                0, QTableWidgetItem(str(delta)[:-3]))
            self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                1, QTableWidgetItem(str(MeasIdx)))
            self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                2, QTableWidgetItem(str(RDMax)))

#-----------Use Peak-Values to get Normalized Data-----------#
            if self.CheckNorm.checkState():
                self.RDNorm = RD - RDMax
                self.NormVal = self.NormBox.value()
                self.RDNorm[self.RDNorm < self.NormVal] = self.NormVal
            else:
                self.RDNorm = RD

#-----------plot values-----------#
            self.plt.pcolormesh(self.AVel, self.ARan, self.RDNorm)
            self.plt.set_xlabel("Velocity [m/s]")
            self.plt.set_ylabel("Range [m]")
            self.plt.set_ylim(self.RDCfg["RMin"], self.RDCfg["RMax"])
            self.canvas.draw()
            self.figure.savefig("vc/RD_"+str(MeasIdx)+".png")

#-----------process Events------------#
            QApplication.processEvents()

#-----------check for cancel-commands-----------#
            if self.cancel:
                self.Brd_Ccl.setEnabled(False)
                self.Brd_Msr_FMCW.setEnabled(True)
                self.Brd_Msr_RCS.setEnabled(False)
                self.Brd_Msr_RP.setEnabled(True)
                self.Rep_repeat.setEnabled(True)
                self.Rep_repcsv.setEnabled(True)
                self.cancel = False
                self.errmsg(
                    "Canceled!", "Measurement after User-Input abortet!", "i")
                return

#-------reset when done-------#
        self.Brd_Ccl.setEnabled(False)
        self.Brd_Msr_FMCW.setEnabled(True)
        self.Brd_Msr_RCS.setEnabled(False)
        self.Brd_Msr_RP.setEnabled(True)
        self.Rep_repeat.setEnabled(True)
        self.Rep_repcsv.setEnabled(True)
        self.errmsg("Measurement Done",
                    "Measurement completed successfully!", "i")
        self.RD = 1
        self.BRD_MSR_DN()

#---RangeProfile-function---#
    def BRD_MSR_RP(self):
        #-------reset figure etc-------#
        self.FGR_CLR()
        self.FMCW = 0
        self.RD = 0
#-------check if connection is still active or raise ConnectionError-------#
        try:
            if not self.connected:
                self.connected = False
                self.Con_Sts_Pic.setPixmap(
                    QtGui.QPixmap("pics/red.png").scaled(30, 30))
                raise ConnectionError

#-----------check if power is on or raise ValueError------------#
            if not self.Brd_Pwr_Btn.isChecked():
                raise ValueError

#-------except any Errors-------#
        except ConnectionError:
            self.errmsg(
                "ConnectionError!", "Connection to FrontEnd has been lost!\nTry to connect again!", "c")
            self.start_gui()
            return

        except ValueError:
            self.errmsg(
                "ValueError!", "The connected Board has no Power yet!\nPlease activate the Power first!", "w")
            return

#-------clear vc-------#
        self.VC_CLR()

#-------enable cancel button-------#
        self.Brd_Ccl.setEnabled(True)

#-------disable FMCW & RangeDoppler-------#
        self.Brd_Msr_FMCW.setEnabled(False)
        self.Brd_Msr_RD.setEnabled(False)

#-------disable FMCW-RP-hybrid measurements-------#
        self.Brd_Msr_RCS.setEnabled(False)

#-------disable Report reload-------#
        self.Rep_repeat.setEnabled(False)
        self.Rep_repcsv.setEnabled(False)

#-------enable RangeProfile-------#
        self.Proc = RadarProc.RadarProc()

#-------enable Rx and Tx-------#
        self.Board.RfRxEna()
        self.Board.RfTxEna(self.TxChn, self.TxPwr)

#-------set BoardConfig-------#
        self.Board.RfMeas("ExtTrigUp", self.BCfg)

#-------get calibrationData-------#
        self.calcData = self.Board.BrdGetCalData({"Mask": 1, "Len": 64})

#-------get needed values-------#
        fs = self.Board.Get("fs")
        kf = self.Board.RfGet("kf")
        N = self.Board.Get("N")
        NrFrms = self.BCfg["NrFrms"]

#-------set values to Config-------#
        self.RPCfg["fs"] = fs
        self.RPCfg["kf"] = kf
        self.RPCfg["CalData"] = self.calcData

#-------set Config for measurement-------#
        self.Proc.CfgRangeProfile(self.RPCfg)

#-------create DataContainer-------#
        self.MeasData = np.zeros((int(N), int(32)))
        self.AllData = np.zeros((int(N), int(8*NrFrms)))

#-------get RangeScale-------#
        self.RanSca = self.Proc.GetRangeProfile("Range")

#-------create Plot-------#
        self.plt = self.figure.add_subplot(111)

#-------add info to maxtab--------#
        self.MaxTab.clearContents()
        self.MaxTab.setRowCount(1)
        self.MaxTab.setItem((self.MaxTab.rowCount()-1), 0,
                            QTableWidgetItem("RangeProfile"))
        self.MaxTab.setItem((self.MaxTab.rowCount()-1), 1,
                            QTableWidgetItem(str(self.BCfg["NrFrms"])))
        self.MaxTab.setItem((self.MaxTab.rowCount()-1), 2,
                            QTableWidgetItem("<-- total"))

#-------Get Data-------#
        start = ttime.time()
        for MeasIdx in range(0, int(self.BCfg["NrFrms"])):
            Data = self.Board.BrdGetData()
            Id = ((Data[0, 0] - 1) % 4) + 1
            self.AllData[:, MeasIdx*8:(MeasIdx+1)*8] = Data
            self.AllData[1, MeasIdx*8:(MeasIdx+1)*8] = Id
            self.plt.clear()

#-----------Place Data in DataContainer------------#
            if Id == 1:
                self.MeasData[:, :8] = Data
            elif Id == 2:
                self.MeasData[:, 8:16] = Data
            elif Id == 3:
                self.MeasData[:, 16:24] = Data
            elif Id == 4:
                self.MeasData[:, 24:32] = Data

#---------------get RangeProfile of measured Data---------------#
                self.RP = self.Proc.RangeProfile(self.MeasData)

                if self.CheckNorm.checkState():
                    self.RP = pd.DataFrame(self.RP)
                    self.RP = self.RP.mean(axis=1)
                    self.NormVal = self.NormBox.value()
                    self.RP.loc[self.RP < self.NormVal] = self.NormVal


#---------------draw plot---------------#
                self.plt.plot([-10, 100], [np.amax(self.RP), np.amax(self.RP)])
                self.plt.plot(self.RanSca, self.RP)
                self.plt.set_xlabel("Range [m]")
                self.plt.set_ylabel("dB")
                self.plt.set_ylim(-200, 0)
                self.plt.set_xlim(self.RPCfg["RMin"], self.RPCfg["RMax"])
                self.canvas.draw()
                self.figure.savefig("vc/RP_"+str(MeasIdx)+".png")

#---------------MaxTab update---------------#
                delta = ttime.time() - start
                self.MaxTab.setRowCount(self.MaxTab.rowCount() + 1)
                self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                    0, QTableWidgetItem(str(delta)[:-3]))
                self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                    1, QTableWidgetItem(str(MeasIdx)))
                self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                    2, QTableWidgetItem(str(np.amax(self.RP))))

#---------------process Events---------------#
                QApplication.processEvents()

#-----------check for cancel-commands-----------#
            if self.cancel:
                self.Brd_Ccl.setEnabled(False)
                self.Brd_Msr_FMCW.setEnabled(True)
                self.Brd_Msr_RCS.setEnabled(True)
                self.Brd_Msr_RD.setEnabled(True)
                self.Rep_repeat.setEnabled(True)
                self.Rep_repcsv.setEnabled(True)
                self.cancel = False
                self.errmsg(
                    "Canceled!", "Measurement after User-Input abortet", "i")
                return

#-------reset when done-------#
        self.Brd_Ccl.setEnabled(False)
        self.Brd_Msr_FMCW.setEnabled(True)
        self.Brd_Msr_RCS.setEnabled(True)
        self.Brd_Msr_RD.setEnabled(True)
        self.Rep_repeat.setEnabled(True)
        self.Rep_repcsv.setEnabled(True)
        self.errmsg("Measurement Done!",
                    "Measurement completed successfully!", "i")
        self.RP = 1
        self.BRD_MSR_DN()

#---Cancel measurement-function---#
    def BRD_MSR_CNCL(self):
        self.cancel = True

#---Measurement-finished-function---#
    def BRD_MSR_DN(self):
        #-------Question Video save-------#
        Qstn = self.errmsg(
            "create Report?", "Do you want to save the Measurement as report?", "q")

#-------check answer-------#
        if Qstn == 0:
            self.REPORT()
        else:
            pass

#---Configmenu function---#
    def BRD_CFG(self):
        #-------Create a new Window-------#
        self.Cfg_Wndw = LockWindow()

#-------Create a List with all changeable config-variables-------#
        self.Cfg_Lst = QListWidget()
        self.Cfg_Lst.setFixedWidth(150)

#-------Add the some names to the list-------#
        Opts = ["fStrt", "fStop", "TRampUp", "TRampDo", "Np",
                "N", "NrFrms", "Tp", "TInt", "TxSeq",
                "CfgTim", "RMin", "RMax"]
        self.Cfg_Lst.addItems(Opts)
        self.Cfg_Lst.currentItemChanged.connect(self.BRD_CFG_UPDATE)

#-------Create a Title that changes-------#
        self.Cfg_Ttl = QLabel("")
        self.Cfg_Ttl.setFont(QtGui.QFont("Times", 20, QtGui.QFont.Bold))
        self.Cfg_Ttl.setFixedHeight(50)

#-------Create a Button that saves changes-------#
        self.Cfg_Save = QPushButton("save...")
        self.Cfg_Save.setToolTip("save set options!")
        self.Cfg_Save.clicked.connect(self.BRD_CFG_SAVE)

#-------Create a Button that resets Config-------#
        self.Cfg_Rst = QPushButton("Reset Config...")
        self.Cfg_Rst.setToolTip("Reset all Configs!")
        self.Cfg_Rst.clicked.connect(self.BRD_CFG_RST)

#-------Create Pic-Display-------#
        self.Cfg_Pic = QLabel("Picture-Display")
        self.Cfg_Pic.setPixmap(QtGui.QPixmap("pics/Cfg.png"))

#-------Create Plot-Background-------#
        self.CfgFig = figure.Figure()
        self.Cfg_Plt = FCA(self.CfgFig)
        self.Cfg_Plt.setFixedSize(480, 300)
        self.CfgFig.subplots_adjust(
            top=0.925, bottom=0.2, left=0.125, right=0.95)
        self.CP = self.CfgFig.add_subplot(111)

#-------Create Explain-Display-------#
        self.Cfg_Exp = QLabel("Explain-Display")

#-------Create a Variable-Display-------#
        self.Cfg_Var = QLabel("Variable-Display")

#-------Create a Original-Value-Display-------#
        self.Cfg_Orig = QLabel("Original-Value-Display")

#-------Create a New-Value-Display with check function-------#
        self.Cfg_New = QLineEdit()
        self.Cfg_New.setPlaceholderText("Enter new value here!")
        self.Cfg_New.textChanged.connect(self.BRD_CFG_CHCK)

#-------Create a Convert-Value-Display-------#
        self.Cfg_Conv = QLabel("Convert-Value-Display")

#-------Create a Layout and fill it up-------#
        self.Cfg_Layout = QGridLayout()
        self.Cfg_Layout.addWidget(self.Cfg_Lst, 0, 0, 5, 1, Qt.AlignLeft)
        self.Cfg_Layout.addWidget(self.Cfg_Ttl, 0, 1, 1, 4, Qt.AlignTop)
        self.Cfg_Layout.addWidget(self.Cfg_Var, 1, 1, 1, 1, Qt.AlignLeft)
        self.Cfg_Layout.addWidget(self.Cfg_Orig, 1, 2, 1, 1, Qt.AlignCenter)
        self.Cfg_Layout.addWidget(self.Cfg_New, 1, 3, 1, 1, Qt.AlignCenter)
        self.Cfg_Layout.addWidget(self.Cfg_Conv, 1, 4, 1, 1, Qt.AlignRight)
        self.Cfg_Layout.addWidget(self.Cfg_Plt, 2, 1, 1, 4, Qt.AlignCenter)
        # self.Cfg_Layout.addWidget(self.Cfg_Pic, 2, 1, 1, 4, Qt.AlignCenter)
        self.Cfg_Layout.addWidget(self.Cfg_Exp, 3, 1, 1, 4, Qt.AlignCenter)
        self.Cfg_Layout.addWidget(self.Cfg_Rst, 4, 1, 1, 1, Qt.AlignBottom)
        self.Cfg_Layout.addWidget(self.Cfg_Save, 4, 4, 1, 1, Qt.AlignBottom)

#-------Set Window geometry etc.-------#
        self.Cfg_Wndw.setLayout(self.Cfg_Layout)
        self.Cfg_Wndw.resize(720, 640)
        self.Cfg_Wndw.setWindowTitle("Board-Configuration")
        self.Cfg_Wndw.show()

#---update CfgWindow function---#
    def BRD_CFG_UPDATE(self):
        #-------get current item of list-------#
        showMe = self.Cfg_Lst.currentItem().text()

#-------Check for Lock-------#
        if self.Lock:
            self.Cfg_New.setStyleSheet(
                "border: 3px solid red; background: yellow; color: red")
            self.Cfg_Conv.setText("invalid Value!")
            self.Cfg_Save.setEnabled(False)
            return
        else:
            self.Cfg_New.setStyleSheet(self.origStyleSheet)
            self.Cfg_Save.setEnabled(True)

#-------check what to display-------#
        if showMe == "fStrt":
            self.Cfg_Ttl.setText("Frequency@Start - Frequency-BottomValue")
            self.Cfg_Var.setText("Variable Name:\nfStrt")
            original = str(self.StdCfg["fStrt"]*1e-9)
            self.Cfg_Orig.setText("Original Value:\n"+original+" [GHz]")
            self.Cfg_Conv.setText("Converter: Ready!")
            self.Cfg_Exp.setText("The Start-Frequency needs to be lower than the Stop-Frequency! This variable should be between 70 and 80 GHz!\n"
                                 "In the End the centered Frequency should be 77GHz. This means: fc = 77GHz = (fStrt + fStop) / 2\n\n"
                                 "fc with now set Frequencys: " + str(1e-9*(self.TCfg["fStrt"] + self.TCfg["fStop"]) / 2) + " [GHz]")
            self.Cfg_New.setText(str(self.TCfg["fStrt"]*1e-9))
            self.Cfg_Pic.setPixmap(QtGui.QPixmap("pics/Cfg.png"))

        elif showMe == "fStop":
            self.Cfg_Ttl.setText("Frequency@Stop - Frequency-TopValue")
            self.Cfg_Var.setText("Variable Name:\nfStop")
            original = str(self.StdCfg["fStop"]*1e-9)
            self.Cfg_Orig.setText("Original Value:\n"+original+" [GHz]")
            self.Cfg_Conv.setText("Converter: Ready!")
            self.Cfg_Exp.setText("The Stop-Frequency needs to be higher than the Start-Frequency! This variable should be between 70 and 80 GHz\n"
                                 "In the End the centered Frequency should be 77GHz. This means: fc = 77GHz = (fStrt + fStop) / 2\n\n"
                                 "fc with now set Frequencys: " + str(1e-9*(self.TCfg["fStrt"] + self.TCfg["fStop"]) / 2) + " [GHz]")
            self.Cfg_New.setText(str(self.TCfg["fStop"]*1e-9))
            self.Cfg_Pic.setPixmap(QtGui.QPixmap("pics/Cfg.png"))

        elif showMe == "TRampUp":
            self.Cfg_Ttl.setText("Duration Start2Stop - linear-RampUpwards")
            self.Cfg_Var.setText("Variable Name:\nTRampUp")
            original = str(self.StdCfg["TRampUp"]*1e6)
            self.Cfg_Orig.setText("Original Value:\n"+original+" [µs]")
            self.Cfg_Conv.setText("Converter: Ready!")
            self.Cfg_Exp.setText("This variable describes the time needed to make a linear jump from Start- to Stop-Frequency!\n"
                                 "The time needed for the so called Up-Ramp should be a little higher than the time needed for the Down-Ramp.\n"
                                 "The numeric value of this variable should be around 20-50 µs!\n\nmax. calculated Upchirptime: "
                                 + str(1e6*(self.TCfg["Tp"] - self.TCfg["TRampDo"] - self.TCfg["CfgTim"])) + " [µs]")
            self.Cfg_New.setText(str(self.TCfg["TRampUp"]*1e6))
            self.Cfg_Pic.setPixmap(QtGui.QPixmap("pics/Cfg.png"))

        elif showMe == "TRampDo":
            self.Cfg_Ttl.setText("Duration Stop2Start - linear-RampDownwards")
            self.Cfg_Var.setText("Variable Name:\nTRampDo")
            original = str(self.StdCfg["TRampDo"]*1e6)
            self.Cfg_Orig.setText("Original Value:\n"+original+" [µs]")
            self.Cfg_Conv.setText("Converter: Ready!")
            self.Cfg_Exp.setText("This variable describes the time needed to make a linear drop from Stop- to StartFrequency!\n"
                                 "The time needed for the so called Down-Ramp should be a little less than the time needed for the Up-Ramp.\n"
                                 "The numeric value of this variableshould be around 1-10 µs!\n\nmax. calculated Downchirptime: "
                                 + str(1e6*(self.TCfg["Tp"] - self.TCfg["TRampUp"] - self.TCfg["CfgTim"])) + " [µs]")
            self.Cfg_New.setText(str(self.TCfg["TRampDo"]*1e6))
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
                                 "beacuse more single-values are obtained.\n"
                                 "sampling frequency fs = 1/(TRampUp/N)\ncalc. fs: "+str(1/(self.TCfg["TRampUp"]/self.TCfg["N"])))
            self.Cfg_New.setText(str(self.TCfg["N"]))
            self.Cfg_Pic.setPixmap(QtGui.QPixmap("pics/Cfg2.png"))

        elif showMe == "Np":
            self.Cfg_Ttl.setText("Number Frames - Collect n-Frames")
            self.Cfg_Var.setText("Variable Name:\nNp")
            original = str(self.StdCfg["Np"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [frames]")
            self.Cfg_Conv.setText("No Convertion!")
            self.Cfg_Exp.setText("Number of Frames means the number of repeats inside the chirp-loop.\nThis variable defines how often a chirp (Up-Down-Cycle) is looped for every"
                                 "Sequence!\nThe Higher this value gets, the longer the measurement gets!")
            self.Cfg_New.setText(str(self.TCfg["Np"]))
            self.Cfg_Pic.setPixmap(QtGui.QPixmap("pics/Cfg2.png"))

        elif showMe == "Tp":
            self.Cfg_Ttl.setText("Time for Sequence - Wait-Time")
            self.Cfg_Var.setText("Variable Name:\nTp")
            original = str(self.StdCfg["Tp"]*1e6)
            self.Cfg_Orig.setText("Original Value:\n"+original+" [µs]")
            self.Cfg_Conv.setText("Converter: Ready!")
            self.Cfg_Exp.setText("This is the time that passes after every single Tx-Sequence (TRampUp -> TRampDo -> Tp -> TRampUp...) has finished."
                                 "\nThe RadarBook itself needs about 30µs to set the Config.To ensure this, here is the calculation:\n"
                                 "CfgTime = Tp - (TRampUp + TRampDo) -> Tp = CfgTime + (TRampUp + TRampDo)\n"
                                 "This means the minimum Tp can be calculated if TRampUp and TRampDo are allready set to a specific value!\n\n"
                                 "minimum calculated Tp = " + str(1e6*(self.TCfg["TRampUp"] + self.TCfg["TRampDo"] + self.TCfg["CfgTim"])) + " [µs]")
            self.Cfg_New.setText(str(self.TCfg["Tp"]*1e6))
            self.Cfg_Pic.setPixmap(QtGui.QPixmap("pics/Cfg2.png"))

        elif showMe == "TInt":
            self.Cfg_Ttl.setText("Time Between Sequences - Wait-Time")
            self.Cfg_Var.setText("Variable Name:\nTInt")
            original = str(self.StdCfg["TInt"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [s]")
            self.Cfg_Conv.setText("Converter: Ready!")
            self.Cfg_Exp.setText("This is the time that passes for every Sequence-Order (Tx1-Tx2-Tx3-Tx4). There is even a way to calc. TInt!\n"
                                 "The variable 'WaitTime' describes the total time when no signals are transmitted. When using simple math this can be done:\n"
                                 "WaitTime = TInt - Tp * len(TxSeq) * Np -> TInt = WaitTime + Tp * len(TxSeq) * Np\n"
                                 "The longest, by the RadarBook accepted WaitTime is 1ms! To ensure no Errors come up this calc. expects WaitTime to be 0.9ms!\n\n"
                                 "minimum calculated TInt = " + str((0.9e-3 + self.TCfg["Tp"] * 4 * self.TCfg["Np"])) + " [s]")
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
            self.Cfg_Exp.setText("Enable or disable trigger event after start-phase. If set to 0 SeqTrigExtEve will start the measurement.\n"
                                 "If set to 1 the measurement will start automatically!")
            self.Cfg_New.setText(str(self.TCfg["IniEve"]))

        elif showMe == "IniTim":
            self.Cfg_Ttl.setText("InitTimeWindow - Time for init")
            self.Cfg_Var.setText("Variable Name:\n" + showMe)
            original = str(self.StdCfg["IniTim"]*1e6)
            self.Cfg_Orig.setText("Original Value:\n"+original+" [µs]")
            self.Cfg_Conv.setText("Converter: Ready!")
            self.Cfg_Exp.setText("The total timewindow for init-phase - if this value gets higher you should consider setting a delay.\n"
                                 "This way measurement and init dont overlap!")
            self.Cfg_New.setText(str(self.TCfg["IniTim"]*1e6))

        elif showMe == "CfgTim":
            self.Cfg_Ttl.setText("Re-Config-Time of PLL")
            self.Cfg_Var.setText("Variable Name:\n" + showMe)
            original = str(self.StdCfg["CfgTim"]*1e6)
            self.Cfg_Orig.setText("Original Value:\n"+original+" [µs]")
            self.Cfg_Conv.setText("Converter: Ready!")
            self.Cfg_Exp.setText("The CfgTim defines the time that passes while the Config is set after every chirp. This variable is connected with Tp!\n"
                                 "CfgTim = Tp - (TRampUp + TRampDo)\n\nmax. calculated CfgTim: "
                                 + str(1e6*(self.TCfg["Tp"] - (self.TCfg["TRampUp"] + self.TCfg["TRampDo"]))) + " [µs]")
            self.Cfg_New.setText(str(self.TCfg["CfgTim"]*1e6))

        elif showMe == "ExtEve":
            self.Cfg_Ttl.setText("ExternalEvent")
            self.Cfg_Var.setText("Variable Name:\n" + showMe)
            original = str(self.StdCfg["ExtEve"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [event]")
            self.Cfg_Conv.setText("No Conversion!")
            self.Cfg_Exp.setText("If set to 1, this means Measurement stops after every Sequence until a external Event (SeqTrigExtEve) is triggered.\n"
                                 "After triggering this Event the next Sequence ('Np'x'TxSeq') is started!")
            self.Cfg_New.setText(str(self.TCfg["ExtEve"]))

        elif showMe == "RMin":
            self.Cfg_Ttl.setText("shortest Distance accounted")
            self.Cfg_Var.setText("Variable Name:\n"+showMe)
            original =  str(self.StdCfg["RMin"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [m]")
            self.Cfg_Conv.setText("Converter: Ready!")
            self.Cfg_Exp.setText("This is the shortest Range taken into account for plotting! All Data in front of this "
                                 "Point will not be taken into account plotting-wise!")
            self.Cfg_New.setText(str(self.TCfg["RMin"]))

        elif showMe == "RMax":
            self.Cfg_Ttl.setText("longest Distance accounted")
            self.Cfg_Var.setText("Variable Name:\n"+showMe)
            original =  str(self.StdCfg["RMax"])
            self.Cfg_Orig.setText("Original Value:\n"+original+" [m]")
            self.Cfg_Conv.setText("Converter: Ready!")
            self.Cfg_Exp.setText("This is the longest Range taken into account for plotting! All Data further of this "
                                 "Point will not be taken into account plotting-wise!")
            self.Cfg_New.setText(str(self.TCfg["RMax"]))

        else:
            self.errmsg("NameError!", "Item '" + showMe + "' not found!", "c")
            self.Cfg_Wndw.close()
            return

#-------show chosen options-------#
        self.Cfg_Wndw.show()

#---check input function---#
    def BRD_CFG_CHCK(self):
        #-------get chosen variable-------#
        showMe = self.Cfg_Lst.currentItem().text()

#-------get value after change-------#
        value = self.Cfg_New.text()

#-------check if value is convertable, if so display it, if not do nothing-------#
        try:
            if float(value) >= 0:
                if showMe in ["fStrt", "fStop"]:
                    new_value = str(float(value) * 1e9)
                    self.Cfg_Conv.setText(
                        "Converted Value:\n"+new_value+" [Hz]")
                    if showMe == "fStrt":
                        if float(value) >= 70:
                            self.TCfg["fStrt"] = float(value) * 1e9
                        else:
                            raise LookupError
                    elif showMe == "fStop":
                        if float(value)*1e9 > float(self.TCfg["fStrt"]):
                            self.TCfg["fStop"] = float(value) * 1e9
                        else:
                            raise LookupError

                elif showMe in ["TRampUp", "TRampDo", "Tp", "TInt", "CfgTim", "IniTim"]:
                    new_value = str(float(value) * 1e3)
                    self.Cfg_Conv.setText(
                        "Converted Value:\n"+new_value+" [ns]")
                    if showMe == "TRampUp":
                        if float(value) > 0:
                            self.TCfg["TRampUp"] = float(value) * 1e-6
                        else:
                            raise LookupError
                    elif showMe == "TRampDo":
                        if float(value) > 0:
                            self.TCfg["TRampDo"] = float(value) * 1e-6
                        else:
                            raise LookupError
                    elif showMe == "Tp":
                        if float(value) > 0:
                            self.TCfg["Tp"] = float(value) * 1e-6
                        else:
                            raise LookupError
                    elif showMe == "TInt":
                        new_value = str(float(value) * 1e3)
                        self.Cfg_Conv.setText(
                            "Converted Value:\n"+new_value+" [ms]")
                        if float(value) > 0:
                            self.TCfg["TInt"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "CfgTim":
                        if float(value) > 0:
                            self.TCfg["CfgTim"] = float(value) * 1e-6
                        else:
                            raise LookupError
                    elif showMe == "IniTim":
                        if float(value) > 0:
                            self.TCfg["IniTim"] = float(value) * 1e-6
                        else:
                            raise LookupError

                elif showMe in ["NrFrms", "N", "Np", "IniEve", "ExtEve"]:
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

                elif showMe in ["RMax", "RMin"]:
                    new_value = str(float(value) * 1e-3)
                    self.Cfg_Conv.setText("Converted Value:\n"+new_value+" [km]")
                    if showMe == "RMin":
                        if float(value) >= 0 and float(value) < self.TCfg["RMax"]:
                            self.TCfg["RMin"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "RMax":
                        if float(value) > self.TCfg["RMin"]:
                            self.TCfg["RMax"] = float(value)
                        else:
                            raise LookupError

                else:
                    raise ValueError

            else:
                raise LookupError

            self.Lock = False
            global lock
            lock = self.Lock
            self.Cfg_New.setStyleSheet(self.origStyleSheet)
            self.Cfg_Save.setEnabled(True)

#-------except all possible Errors-------#
        except ValueError:
            if showMe == "TxSeq":
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
            self.Cfg_New.setStyleSheet(
                "border: 3px solid red; background: yellow; color: red")
            self.Cfg_Conv.setText("invalid Value!")
            self.Cfg_Save.setEnabled(False)
            return

#-------plot values into window for visual understanding-------#
        try:
            self.CP.clear()
            self.CP.tick_params(rotation=30)
            fS = self.TCfg["fStrt"]
            fs = self.TCfg["fStop"]
            tU = self.TCfg["TRampUp"]
            tD = self.TCfg["TRampDo"]
            # N  = self.TCfg["N"]
            tp = self.TCfg["Tp"]
            Np = self.TCfg["Np"]
            # NF = self.TCfg["NrFrms"]
            ti = self.TCfg["TInt"]
            tc = self.TCfg["CfgTim"]
            fline = [fS, fs, fS, fS, fs, fS, fS, fs, fS, fS, fs, fS]
            tline = [0, tU, (tU+tD), (tp), (tp+tU), (tp+tU+tD), (2*tp),
                     (2*tp+tU), (2*tp+tU+tD), (3*tp), (3*tp+tU), (3*tp+tU+tD)]

            if showMe == "TInt":
                fline = [fS, fs, fS, fS, fs, fS, fS, fs, fS, fS, fs, fS, fS,
                         fs, fS, fS, fs, fS, fS, fs, fS, fS, fs, fS]
                tline = [0, tU, (tU+tD), (tp), (tp+tU), (tp+tU+tD), (2*tp),
                         (2*tp+tU), (2*tp+tU+tD), (3*tp), (3*tp+tU),
                         (3*tp+tU+tD), ti, (ti+tU), (ti+tU+tD), (ti+tp),
                         (ti+tp+tU), (ti+tp+tU+tD), (2*tp+ti), (2*tp+ti+tU),
                         (2*tp+ti+tU+tD), (3*tp+ti), (3*tp+ti+tU),
                         (3*tp+ti+tU+tD)]

            if showMe == "TxSeq":
                fline.append(fS)
                tline.append(ti)
                fline = fline + fline
                pline = []
                for e in tline:
                    e += ti
                    pline.append(e)
                tline = tline + pline
                fline = fline + fline
                pline = []
                for e in tline:
                    e += 2*ti
                    pline.append(e)
                tline = tline + pline

            if showMe in ["fStrt", "fStop", "TRampUp", "TRampDo", "Tp"]:
                fline = [fS, fs, fS, fS, fs, fS]
                tline = [0, tU, (tU+tD), tp, (tp+tU), (tp+tU+tD)]

            if showMe == "N":
                fline = [fS, fs, fS, fS]
                tline = [0, tU, (tU+tD), tp]

            if showMe == "Np":
                fline = []
                tline = []
                for c in range(int(Np)):
                    fline.append(fS)
                    fline.append(fs)
                    fline.append(fS)
                    if c == 0:
                        tline.append(0)
                        tline.append(tU)
                        tline.append((tU+tD))
                    else:
                        tline.append((c*tp))
                        tline.append((c*tp+tU))
                        tline.append((c*tp+tU+tD))

            if showMe == "NrFrms":
                fline = []
                tline = []
                for r in range(int(Np)):
                    fline.append(fS)
                    fline.append(fs)
                    fline.append(fS)
                    if r == 0:
                        tline.append(0)
                        tline.append(tU)
                        tline.append(tU+tD)
                    else:
                        tline.append(r*tp)
                        tline.append(r*tp+tU)
                        tline.append(r*tp+tU+tD)
                Npf = fline.copy()
                Npt = tline.copy()

                for r in range(int(Np)):
                    fline.append(fS)
                    fline.append(fs)
                    fline.append(fS)
                    if r == 0:
                        tline.append(ti)
                        tline.append(ti+tU)
                        tline.append(ti+tU+tD)
                    else:
                        tline.append(ti+r*tp)
                        tline.append(ti+r*tp+tU)
                        tline.append(ti+r*tp+tU+tD)
                fline.append(fS)
                tline.append(2*ti)

            self.CP.grid(True, "both")
            self.CP.plot(tline, fline, c="black")
            self.CP.set_xlabel("time [s]")
            self.CP.set_ylabel("frequency [Hz]")

            if showMe == "TInt":
                if ti < (0.9e-3 + tp*4*Np):
                    clr = "red"
                else:
                    clr = "lime"

                fline = [(fS-1e8), (fS-1e8)]
                tline = [0, ti]
                self.CP.plot(tline, fline, c=clr, lw=3, label="TInt")
                fline = [fS, fS]
                tline = [(3*tp+tU+tD), ti]
                self.CP.plot(tline, fline, c="blue", lw=1.5,
                             label="WaitTime\nconst. 0.9 ms")
                self.CP.legend(frameon=True)

            if showMe == "CfgTim":
                if tp < (tU+tD+tc):
                    clr = "red"
                else:
                    clr = "lime"
                fline = [fS, fS]
                tline = [(tU+tD), (tU+tD+tc)]
                self.CP.plot(tline, fline, c=clr, lw=3, label="CfgTim")
                tline = [(tp+tU+tD), (tp+tU+tD+tc)]
                self.CP.plot(tline, fline, c=clr, lw=3)
                tline = [(2*tp+tU+tD), (2*tp+tU+tD+tc)]
                self.CP.plot(tline, fline, c=clr, lw=3)
                self.CP.legend(frameon=True)

            if showMe in ["fStrt", "fStop"]:
                fc = (fS+fs) / 2
                kf = (fs-fS) / tU
                fline = [fc, fc]
                tline = [0, (tp+tU+tD)]
                self.CP.plot(tline, fline, c="cyan",
                             label="fc = "+str(fc*1e-9)+" [GHz]")
                fline = [fS, fs]
                tline = [0, tU]
                self.CP.plot(tline, fline, c="lime",
                             label="kf = "+(str(kf*1e-9)[:-8])+" [GHz/s]")
                tline = [tp, (tp+tU)]
                self.CP.plot(tline, fline, c="lime")
                self.CP.legend(frameon=True)

            if showMe in ["TRampUp", "TRampDo"]:
                fline = [fS, fS]
                tline = [0, tU]
                self.CP.plot(tline, fline, c="cyan", label="TRampUp")
                tline = [tU, (tU+tD)]
                self.CP.plot(tline, fline, c="red", label="TRampDo")
                tline = [tp, (tp+tU)]
                self.CP.plot(tline, fline, c="cyan")
                tline = [(tp+tU), (tp+tU+tD)]
                self.CP.plot(tline, fline, c="red")
                fline = [fS, fs]
                tline = [tU, tU]
                # self.CP.plot(tline, fline, c="gold")
                tline = [(tp+tU), (tp+tU)]
                # self.CP.plot(tline, fline, c="gold")
                self.CP.legend(frameon=True)

            if showMe == "Tp":
                if tp < (tU+tD+tc):
                    clr = "red"
                else:
                    clr = "lime"
                fline = [(fS-1e8), (fS-1e8)]
                tline = [0, tp]
                self.CP.plot(tline, fline, c=clr, label="Tp")
                fline = [fS, fS]
                tline = [0, tU]
                self.CP.plot(tline, fline, c="orange", label="TRampUp")
                tline = [tU, (tU+tD)]
                self.CP.plot(tline, fline, c="cyan", label="TRampDo")
                tline = [(tU+tD), (tU+tD+tc)]
                self.CP.plot(tline, fline, c="blue", label="CfgTim")
                self.CP.legend(frameon=True)

            if showMe == "Np":
                fline = [fS, fs, fS]
                tline = [0, tU, (tU+tD)]
                self.CP.plot(tline, fline, c="lime", label="1/Np chirps")
                self.CP.legend(frameon=True)

            if showMe == "NrFrms":
                self.CP.plot(Npt, Npf, color="gold",
                             label="Np*chirps of NrFrms=1")
                Npt2 = []
                for entry in Npt:
                    entry += ti
                    Npt2.append(entry)
                self.CP.plot(Npt2, Npf, color="cyan",
                             label="Np*chirps of NrFrms=2")
                fline = [fS, fS]
                tline = [0, ti]
                self.CP.plot(tline, fline, color="lime", label="NrFrms=1")
                tline = [ti, 2*ti]
                self.CP.plot(tline, fline, color="red", label="NrFrms=2")
                self.CP.legend(frameon=True)

            if showMe == "N":
                fline = [fS, fs]
                tline = [0, tU]
                self.CP.plot(tline, fline, color="lime",
                             label="N*samples in chirp")
                self.CP.legend(frameon=True)

            if showMe == "TxSeq":
                seq = self.TCfg["TxSeq"]
                fline = [fS-1e8, fS-1e8]
                tline = [0, ti]
                for x in seq:
                    if x == 1:
                        self.CP.plot(tline, fline, color="red",
                                     label="Transmitter 1")
                    elif x == 2:
                        self.CP.plot(tline, fline, color="blue",
                                     label="Transmitter 2")
                    elif x == 3:
                        self.CP.plot(tline, fline, color="lime",
                                     label="Transmitter 3")
                    elif x == 4:
                        self.CP.plot(tline, fline, color="cyan",
                                     label="Transmitter 4")
                    tline[0] += ti
                    tline[1] += ti
                self.CP.legend(frameon=True)

            if showMe in ["RMax", "RMin"]:
                self.CP.clear()

            self.Cfg_Plt.draw()

        except:
            pass


#---save config function---#


    def BRD_CFG_SAVE(self):
        #-------safety-question-------#
        Qstn = self.errmsg(
            "Set Config?", "Are you sure you want to set new Config?\nIf some variables are not set right Measurement may Stop!", "q")

#-------check answer-------#
        if Qstn == 0:
            cont = True
        else:
            cont = False

#-------continue if answer was yes, else abort-------#
        if cont:
            self.BCfg = dict(self.TCfg)
            self.errmsg("Confirmed!", "Config saved successfully!", "i")
            self.Cfg_Wndw.close()
        else:
            self.errmsg(
                "Config not set!", "The User-Config is not set, but still saved in the ConfigWindow.", "i")

#---Reset-Config-Function---#
    def BRD_CFG_RST(self):
        #-------safety-question-------#
        Qstn = self.errmsg(
            "Are you sure?", "If you reset Board-Config, everything except the standard Config is lost!\nContinue anyways?", "q")

#-------check answer-------#
        if Qstn == 0:
            cont = True
        else:
            cont = False

#-------continue or abort-------#
        if cont:
            self.BCfg = dict(self.StdCfg)
            self.TCfg = dict(self.BCfg)
            self.Lock = False
            global lock
            lock = self.Lock
            self.BRD_CFG_UPDATE()
            self.errmsg("Confirmed!", "Board-Config has been reset!", "i")

        else:
            self.errmsg("Config not reset!",
                        "The Board-Config has not been reset!", "i")

#---Display-Config-function---#
    def CFG_SHW(self):
        #-------hide maxtab-------#
        self.MaxTab.hide()
#-------Create a ScollArea and add Displays to it-------#
        self.Display = QWidget()
        self.Display.setFixedWidth(480)

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
        self.Dspl_fStrt = QLabel(
            "'fStrt' - @Start:    ->    " + self.value_fStrt)

        self.value_fStop = str(self.BCfg["fStop"] * 1e-9) + " GHz"
        self.Dspl_fStop = QLabel(
            "'fStop' - @Stop:    ->    " + self.value_fStop)

        self.Dspl_Drtn = QLabel("Durations:")
        self.Dspl_Drtn.setFont(QtGui.QFont("Times", 10))
        self.Dspl_Drtn1 = QLabel("Durations:")
        self.Dspl_Drtn1.setFont(QtGui.QFont("Times", 10))

        self.value_TRampUp = str(self.BCfg["TRampUp"] * 1e6) + " µs"
        self.Dspl_TRampUp = QLabel(
            "'TRampUp' - Start2Stop:    ->    " + self.value_TRampUp)

        self.value_TRampDo = str(self.BCfg["TRampDo"] * 1e6) + " µs"
        self.Dspl_TRampDo = QLabel(
            "'TRampDo' - Stop2Start:    ->    " + self.value_TRampDo)

        self.value_Tp = str(self.BCfg["Tp"] * 1e6) + " µs"
        self.Dspl_Tp = QLabel(
            "'Tp' - Transmit2Transmit:    ->    " + self.value_Tp)

        self.value_TInt = str(self.BCfg["TInt"] * 1e3) + " ms"
        self.Dspl_TInt = QLabel(
            "'TInt' - Sequence2Sequence:    ->    " + self.value_TInt)

        self.value_IniTim = str(self.BCfg["IniTim"] * 1e3) + " ms"
        self.Dspl_IniTim = QLabel(
            "'IniTim' - InitTime:    ->    " + self.value_IniTim)

        self.value_CfgTim = str(self.BCfg["CfgTim"] * 1e6) + " µs"
        self.Dspl_CfgTim = QLabel(
            "'CfgTim' - ConfigTime:    ->    " + self.value_CfgTim)

        self.Dspl_Cnstnt1 = QLabel("Constants:")
        self.Dspl_Cnstnt1.setFont(QtGui.QFont("Times", 10))
        self.Dspl_Cnstnt2 = QLabel("Constants:")
        self.Dspl_Cnstnt2.setFont(QtGui.QFont("Times", 10))
        self.Dspl_Cnstnt3 = QLabel("Constants:")
        self.Dspl_Cnstnt3.setFont(QtGui.QFont("Times", 10))
        self.Dspl_Cnstnt4 = QLabel("Constants:")
        self.Dspl_Cnstnt4.setFont(QtGui.QFont("Times", 10))

        self.value_NrFrms = str(self.BCfg["NrFrms"])
        self.Dspl_NrFrms = QLabel(
            "'NrFrms' - SequenceRepeats:    ->    " + self.value_NrFrms)

        self.value_N = str(self.BCfg["N"])
        self.Dspl_N = QLabel("'N' - SampleAmount:    ->    " + self.value_N)

        self.value_Np = str(self.BCfg["Np"])
        self.Dspl_Np = QLabel("'Np' - FrameAmount:    ->    " + self.value_Np)

        self.value_RemoveMean = str(bool(self.BFCfg["RemoveMean"]))
        self.Dspl_RemoveMean = QLabel(
            "'RemoveMean' - RemoveMeanValues:    ->    " + self.value_RemoveMean)

        self.value_Window = str(bool(self.BFCfg["Window"]))
        self.Dspl_Window = QLabel(
            "'Window' - DataUseWindow:    ->    " + self.value_Window)

        self.value_dB = str(bool(self.BFCfg["dB"]))
        self.Dspl_dB = QLabel("'dB' - Data as dB:    ->    " + self.value_dB)

        self.value_Abs = str(bool(self.BFCfg["Abs"]))
        self.Dspl_Abs = QLabel(
            "'Abs' - MagnitudeInterval:    ->    " + self.value_Abs)

        self.value_Ext = str(bool(self.BFCfg["Ext"]))
        self.Dspl_Ext = QLabel(
            "'Ext' - RangeInterval:    ->    " + self.value_Ext)

        self.Dspl_Dstnc = QLabel("Distances:")
        self.Dspl_Dstnc.setFont(QtGui.QFont("Times", 10))
        self.Dspl_Dstnc1 = QLabel("Distances:")
        self.Dspl_Dstnc1.setFont(QtGui.QFont("Times", 10))
        self.Dspl_Dstnc2 = QLabel("Distances:")
        self.Dspl_Dstnc2.setFont(QtGui.QFont("Times", 10))

        self.value_RMin = str(self.BFCfg["RMin"]) + " m"
        self.Dspl_RMin = QLabel(
            "'RMin' - min.Distance:    ->    " + self.value_RMin)

        self.value_RMax = str(self.BFCfg["RMax"]) + " m"
        self.Dspl_RMax = QLabel(
            "'RMax' - max.Distance:    ->    " + self.value_RMax)

        self.value_RangeFFT = str(self.BFCfg["RangeFFT"])
        self.Dspl_RangeFFT = QLabel(
            "'RangeFFT' - FFT-RangeWindow:    ->    " + self.value_RangeFFT)

        self.value_AngFFT = str(self.BFCfg["AngFFT"])
        self.Dspl_AngFFT = QLabel(
            "'AngFFT' - FFT-AngleWindow:    ->    " + self.value_AngFFT)

        self.Dspl_Chnnls1 = QLabel("Channels:")
        self.Dspl_Chnnls1.setFont(QtGui.QFont("Times", 10))
        self.Dspl_Chnnls2 = QLabel("Channels:")
        self.Dspl_Chnnls2.setFont(QtGui.QFont("Times", 10))

        self.value_ChnOrder = str(self.BFCfg["ChnOrder"])
        self.Dspl_ChnOrder = QLabel(
            "'ChnOrder' - DataChannels:    ->    " + self.value_ChnOrder)

        self.value_TxSeq = str(self.BCfg["TxSeq"])
        self.Dspl_TxSeq = QLabel(
            "'TxSeq' - TransmitSequence:    ->    " + self.value_TxSeq)

        self.value_RDRangeFFT = str(self.RDCfg["RangeFFT"])
        self.Dspl_RDRangeFFT = QLabel(
            "'RangeFFT' - FFT-RangeWindow    ->    " + self.value_RDRangeFFT)

        self.value_RDVelFFT = str(self.RDCfg["VelFFT"])
        self.Dspl_RDVelFFT = QLabel(
            "'VelFFT' - FFT-VelocityWindow    ->    " + self.value_RDVelFFT)

        self.value_RDAbs = str(bool(self.RDCfg["Abs"]))
        self.Dspl_RDAbs = QLabel(
            "'Abs' - MagnitudeInterval    ->    " + self.value_RDAbs)

        self.value_RDExt = str(bool(self.RDCfg["Ext"]))
        self.Dspl_RDExt = QLabel(
            "'Ext' - RangeInterval    ->    " + self.value_RDExt)

        self.value_RDRMin = str(self.RDCfg["RMin"]) + " m"
        self.Dspl_RDRMin = QLabel(
            "'RMin' - min. Distance    ->    " + self.value_RDRMin)

        self.value_RDRMax = str(self.RDCfg["RMax"]) + " m"
        self.Dspl_RDRMax = QLabel(
            "'RMax' - max. Distance    ->    " + self.value_RDRMax)

        self.value_RDRemoveMean = str(bool(self.RDCfg["RemoveMean"]))
        self.Dspl_RDRemoveMean = QLabel(
            "'RemoveMean' - RemoveMeanValues    ->    " + self.value_RDRemoveMean)

        self.value_RDN = str(self.RDCfg["N"])
        self.Dspl_RDN = QLabel(
            "'N' - SampleAmount:    ->    " + self.value_RDN)

        self.value_RDNp = str(self.RDCfg["Np"])
        self.Dspl_RDNp = QLabel(
            "'Np' - FrameAmount:    ->    " + self.value_RDNp)

        self.value_RDWindow = str(bool(self.RDCfg["Window"]))
        self.Dspl_RDWindow = QLabel(
            "'Window' - DataUseWindow:    ->    " + self.value_RDWindow)

        self.value_RDdB = str(bool(self.RDCfg["dB"]))
        self.Dspl_RDdB = QLabel(
            "'dB' - Data as dB:    ->    " + self.value_RDdB)

        self.value_RDfc = str(self.RDCfg["fc"] * 1e-9) + " GHz"
        self.Dspl_RDfc = QLabel(
            "'fc' - centered Frequency:    ->    " + self.value_RDfc)

        self.value_RDTp = str(self.RDCfg["Tp"] * 1e6) + " µs"
        self.Dspl_RDTp = QLabel(
            "'Tp' - Transmit2Transmit:    ->    " + self.value_RDTp)

        self.value_NFFT = str(self.RPCfg["NFFT"])
        self.Dspl_NFFT = QLabel(
            "'NFFT' - FFT-Window    ->    " + self.value_NFFT)

        self.value_RPAbs = str(bool(self.RPCfg["Abs"]))
        self.Dspl_RPAbs = QLabel(
            "'Abs' - MagnitudeInterval    ->    " + self.value_RPAbs)

        self.value_RPExt = str(bool(self.RPCfg["Ext"]))
        self.Dspl_RPExt = QLabel(
            "'Ext' - RangeInterval    ->    " + self.value_RPExt)

        self.value_RPRMin = str(self.RPCfg["RMin"]) + " m"
        self.Dspl_RPRMin = QLabel(
            "'RMin' - min. Distance:    ->    " + self.value_RPRMin)

        self.value_RPRMax = str(self.RPCfg["RMax"]) + " m"
        self.Dspl_RPRMax = QLabel(
            "'RMax' - max. Distance:    ->    " + self.value_RPRMax)

        self.value_RPRemoveMean = str(bool(self.RPCfg["RemoveMean"]))
        self.Dspl_RPRemoveMean = QLabel(
            "'RemoveMean' - RemoveMeanValues:    ->    " + self.value_RPRemoveMean)

        self.value_RPWindow = str(bool(self.RPCfg["Window"]))
        self.Dspl_RPWindow = QLabel(
            "'Window' - DataUseWindow:    ->    " + self.value_RPWindow)

        self.value_RPXPos = str(bool(self.RPCfg["XPos"]))
        self.Dspl_RPXPos = QLabel(
            "'XPos' - positiveRangeProfile:     ->    " + self.value_RPXPos)

        self.value_RPdB = str(bool(self.RPCfg["dB"]))
        self.Dspl_RPdB = QLabel(
            "'dB' - Data as dB:    ->    " + self.value_RPdB)

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
        # self.ScrLay.addWidget(self.Dspl_Chnnls2)
        # self.ScrLay.addWidget(self.Dspl_ChnOrder)
        self.ScrLay.addWidget(self.Dspl_RD_tl)
        # self.ScrLay.addWidget(self.Dspl_Frqncy1)
        # self.ScrLay.addWidget(self.Dspl_RDfc)
        # self.ScrLay.addWidget(self.Dspl_Drtn1)
        # self.ScrLay.addWidget(self.Dspl_RDTp)
        self.ScrLay.addWidget(self.Dspl_Cnstnt3)
        self.ScrLay.addWidget(self.Dspl_RDRangeFFT)
        self.ScrLay.addWidget(self.Dspl_RDVelFFT)
        # self.ScrLay.addWidget(self.Dspl_RDN)
        # self.ScrLay.addWidget(self.Dspl_RDNp)
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

        self.MWLayout.addWidget(self.Display, 2, 9, 12, 2)
        self.itemAt = self.MWLayout.count() - 1
        self.show()

#---hide Configs-function---#
    def CFG_HDE(self):
        #-------Find Widget and delete it-------#
        item = self.MWLayout.itemAt(self.itemAt)
        widget = item.widget()
        widget.setParent(None)

#-------redirect showConfigButton-------#
        self.Brd_Shw_Cfgs.setText("showConfigs...")
        self.Brd_Shw_Cfgs.disconnect()
        self.Brd_Shw_Cfgs.clicked.connect(self.CFG_SHW)

#-------show maxtab-------#
        self.MaxTab.show()

#---check FS function---#
    def FS_check(self):
        try:
            inp = float(self.Cr_FS.text())
            if inp > 69 and inp < 81:
                self.Cr_FS.setStyleSheet(self.origStyleSheet)
                self.Cr_FSt.setPlaceholderText(
                    "recommended value: " + str(inp+2))
                self.Dic["FS"] = True
                if self.Dic["FS"] and self.Dic["FSt"]:
                    F1 = inp
                    F2 = float(self.Cr_FSt.text())
                    if F1 > F2:
                        self.Cr_FS.setStyleSheet("border: 1px solid red")
                        self.Cr_FS.clear()
                        self.Cr_FS.setPlaceholderText(
                            "@Stop must be higher than @Start!")
                        self.Dic["FS"] = False
                        return
                    fc = F1 + ((F2-F1)/2)
                    self.Cr_fc_L.setText(
                        "centered Freq. fc: " + str(fc) + " [GHz]")
                if self.Dic["TU"] and self.Dic["FS"] and self.Dic["FSt"]:
                    FS = inp * 1e9
                    FSt = float(self.Cr_FSt.text()) * 1e9
                    TU = float(self.Cr_TU.text()) * 1e-6
                    kf = str((FSt - FS) / TU)
                    self.Cr_kf.setText("Upchirp-Slope kf: " + kf + "[Hz/s]")
                return
            else:
                self.Cr_FS.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_FS.setStyleSheet("border: 1px solid red")
            self.Cr_FS.clear()
            self.Cr_FS.setPlaceholderText("please enter digits only!")

        except KeyError:
            return

        self.Dic["FS"] = False

#---check FSt function---#
    def FSt_check(self):
        try:
            inp = float(self.Cr_FSt.text())
            if inp > 69 and inp < 81:
                self.Cr_FSt.setStyleSheet(self.origStyleSheet)
                self.Cr_FS.setPlaceholderText(
                    "recommended value: " + str(inp-2))
                self.Dic["FSt"] = True
                if self.Dic["FS"] and self.Dic["FSt"]:
                    F2 = inp
                    F1 = float(self.Cr_FS.text())
                    if F1 > F2:
                        self.Cr_FSt.setStyleSheet("border: 1px solid red")
                        self.Cr_FSt.clear()
                        self.Cr_FSt.setPlaceholderText(
                            "@Stop must be higher than @Start!")
                        self.Dic["FSt"] = False
                        return
                    fc = F1 + ((F2-F1)/2)
                    self.Cr_fc_L.setText(
                        "centered Freq. fc: " + str(fc) + " [GHz]")
                if self.Dic["TU"] and self.Dic["FS"] and self.Dic["FSt"]:
                    FSt = inp * 1e9
                    FS = float(self.Cr_FS.text()) * 1e9
                    TU = float(self.Cr_TU.text()) * 1e-6
                    kf = str((FSt - FS) / TU)
                    self.Cr_kf.setText("Upchirp-Slope kf: " + kf + "[Hz/s]")
                return
            else:
                self.Cr_FSt.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_FSt.setStyleSheet("border 1px solid red")
            self.Cr_FSt.clear()
            self.Cr_FSt.setPlaceholderText("please enter digits only!")

        except KeyError:
            return

        self.Dic["FSt"] = False

#---check TU function---#
    def TU_check(self):
        try:
            inp = float(self.Cr_TU.text())
            if inp > 0 and inp < 1000:
                self.Cr_TU.setStyleSheet(self.origStyleSheet)
                self.Dic["TU"] = True
                if self.Dic["TU"] and self.Dic["TD"] and self.Dic["CT"]:
                    TU = inp
                    TD = float(self.Cr_TD.text())
                    CfgTim = float(self.Cr_CT.text())
                    Tp = str(CfgTim + TU + TD)
                    self.Cr_Tp.setPlaceholderText(
                        "min. calc. Tp: " + Tp + "[µs]")
                if self.Dic["TU"] and self.Dic["Tp"] and self.Dic["CT"]:
                    TU = inp
                    Tp = float(self.Cr_TP.text())
                    CfgTim = float(self.Cr_CT.text())
                    TD = str(Tp - TU - CfgTim)
                    self.Cr_TD.setPlaceholderText(
                        "min. calc. TRampDown: " + TD + "[µs]")
                if self.Dic["TU"] and self.Dic["FS"] and self.Dic["FSt"]:
                    TU = inp * 1e-6
                    FS = float(self.Cr_FS.text()) * 1e9
                    FSt = float(self.Cr_FSt.text()) * 1e9
                    kf = str((FSt - FS) / TU)
                    self.Cr_kf.setText("Upchirp-Slope kf: " + kf + "[Hz/s]")
                if self.Dic["TU"] and self.Dic["TD"] and self.Dic["Tp"]:
                    TU = inp
                    TD = float(self.Cr_TD.text())
                    Tp = float(self.Cr_Tp.text())
                    CfgTim = str(Tp - TU - TD)
                    self.Cr_CT.setPlaceholderText(
                        "max. calc. CfgTime: " + CfgTim + "[µs]")
                return
            else:
                self.Cr_TU.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_TU.setStyleSheet("border: 1px solid red")
            self.Cr_TU.clear()
            self.Cr_TU.setPlaceholderText("please enter digits only!")

        self.Dic["TU"] = False

#---check TD function---#
    def TD_check(self):
        try:
            inp = float(self.Cr_TD.text())
            if inp > 0 and inp < 1000:
                self.Cr_TD.setStyleSheet(self.origStyleSheet)
                self.Dic["TD"] = True
                if self.Dic["TU"] and self.Dic["TD"] and self.Dic["CT"]:
                    TU = inp
                    TD = float(self.Cr_TD.text())
                    CfgTim = float(self.Cr_CT.text())
                    Tp = str(CfgTim + TU + TD)
                    self.Cr_Tp.setPlaceholderText(
                        "min. calc. Tp: " + Tp + "[µs]")
                if self.Dic["TD"] and self.Dic["Tp"] and self.Dic["CT"]:
                    TD = inp
                    Tp = float(self.Cr_Tp.text())
                    CfgTim = float(self.Cr_CT.text())
                    TU = str(Tp - TD - CfgTim)
                    self.Cr_TU.setPlaceholderText(
                        "max. calc. TRampUp: " + TU + "[µs]")
                if self.Dic["TD"] and self.Dic["TU"] and self.Dic["Tp"]:
                    TD = inp
                    TU = float(self.Cr_TU.text())
                    Tp = float(self.Cr_Tp.text())
                    CfgTim = str(Tp - TU - TD)
                    self.Cr_CT.setPlaceholdeText(
                        "max. calc. CfgTime: " + CfgTim + "[µs]")
                return
            else:
                self.Cr_TD.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_TD.setStyleSheet("border: 1px solid red")
            self.Cr_TD.clear()
            self.Cr_TD.setPlaceholderText("please enter digits only!")

        self.Dic["TD"] = False

#---check TI function---#
    def TI_check(self):
        try:
            inp = float(self.Cr_TI.text())
            if inp > 0 and inp < 5:
                self.Cr_TI.setStyleSheet(self.origStyleSheet)
                self.Dic["TI"] = True
                if self.Dic["Tp"] and self.Dic["TI"]:
                    TI = inp
                    Tp = float(self.Cr_Tp.text()) * 1e-6
                    Np = (TI - 0.9e-3) / (4 * Tp)
                    if Np > 256:
                        Np = "256"
                    else:
                        Np = str(Np)
                    self.Cr_Np.setPlaceholderText("max. calc. Np: " + Np)
                return
            else:
                self.Cr_TI.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_TI.setStyleSheet("border: 1px solid red")
            self.Cr_TI.clear()
            self.Cr_TI.setPlaceholderText("please enter digits only!")

        self.Dic["TI"] = False

#---check Tp function---#
    def Tp_check(self):
        try:
            inp = float(self.Cr_Tp.text())
            if inp > 0 and inp < 1000:
                self.Cr_Tp.setStyleSheet(self.origStyleSheet)
                self.Dic["Tp"] = True
                if self.Dic["Tp"] and self.Dic["Np"]:
                    Tp = inp
                    Np = int(self.Cr_Np.text())
                    TI = str(0.9e-3 + Tp * Np * 4)
                    self.Cr_TI.setPlaceholderText(
                        "min. calc. TI: " + TI + "[µs]")
                if self.Dic["Tp"] and self.Dic["TU"] and self.Dic["CT"]:
                    Tp = inp
                    TU = float(self.Cr_TU.text())
                    CfgTim = float(self.Cr_CT.text())
                    TD = str(Tp - TU - CfgTim)
                    self.Cr_TD.setPlaceholderText(
                        "max. calc. TD: " + TD + "[µs]")
                if self.Dic["Tp"] and self.Dic["TD"] and self.Dic["CT"]:
                    Tp = inp
                    TD = float(self.Cr_TD.text())
                    CfgTim = float(self.Cr_CT.text())
                    TU = str(Tp - TD - CfgTim)
                    self.Cr_TU.setPlaceholderText(
                        "max. calc. TU: " + TU + "[µs]")
                if self.Dic["Tp"] and self.Dic["TD"] and self.Dic["TU"]:
                    Tp = inp
                    TD = float(self.Cr_TD.text())
                    TU = float(self.Cr_TU.text())
                    CfgTim = str(Tp - TD - TU)
                    self.Cr_CT.setPlaceholderText(
                        "max. calc. CfgTime: " + CfgTim + "[µs]")
                return
            else:
                self.Cr_Tp.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_Tp.setStyleSheet("border: 1px solid red")
            self.Cr_Tp.clear()
            self.Cr_Tp.setPlaceholderText("please enter digits only!")

        self.Dic["Tp"] = False

#---check NR function---#
    def NR_check(self):
        try:
            inp = int(self.Cr_NR.text())
            if inp > 0:
                self.Cr_NR.setStyleSheet(self.origStyleSheet)
                self.Dic["NR"] = True
                return
            else:
                self.Cr_NR.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_NR.setStyleSheet("border: 1px solid red")
            self.Cr_NR.clear()
            self.Cr_NR.setPlaceholderText("please enter integers only!")

        self.Dic["NR"] = False

#---check Np function---#
    def Np_check(self):
        try:
            inp = int(self.Cr_Np.text())
            if inp > 0 and inp <= 256:
                self.Cr_Np.setStyleSheet(self.origStyleSheet)
                self.Dic["Np"] = True
                if self.Dic["Np"] and self.Dic["Tp"]:
                    Np = inp
                    Tp = float(self.Cr_Tp.text()) * 1e-6
                    TI = str(0.9e-3 + (Tp * 4 * Np))
                    self.Cr_TI.setPlaceholderText(
                        "min. calc. TInt: " + TI + "[s]")
                return
            else:
                self.Cr_Np.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_Np.setStyleSheet("border: 1px solid red")
            self.Cr_Np.clear()
            self.Cr_Np.setPlaceholderText("please enter integers only!")

        self.Dic["Np"] = False

#---check N function---#
    def N_check(self):
        try:
            inp = int(self.Cr_N.text())
            if inp > 7 and inp < 3969:
                N = np.ceil(inp/8)*8
                if N != inp:
                    self.Cr_N.setStyleSheet("border: 1px solid red")
                    self.Cr_N.setPlaceholderText(
                        "please set to a multiple of 8!")
                    return
                self.Cr_N.setStyleSheet(self.origStyleSheet)
                self.Dic["N"] = True
                return
            else:
                self.Cr_N.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_N.setStyleSheet("border: 1px solid red")
            self.Cr_N.clear()
            self.Cr_N.setPlaceholderText("please enter integers only")

        self.Dic["N"] = False

#---check TS1 function---#
    def TS1_check(self):
        TS = 1
        self.TS_check(TS)

#---check TS2 function---#
    def TS2_check(self):
        TS = 2
        self.TS_check(TS)

#---check TS3 function---#
    def TS3_check(self):
        TS = 3
        self.TS_check(TS)

#---check TS4 function---#
    def TS4_check(self):
        TS = 4
        self.TS_check(TS)

#---check TxSeq function---#
    def TS_check(self, TS=None):
        try:
            T1 = int(self.Cr_TS1.value())
            T2 = int(self.Cr_TS2.value())
            T3 = int(self.Cr_TS3.value())
            T4 = int(self.Cr_TS4.value())

            if TS == 1:
                if T1 == T2:
                    if (T2+1) != T3 and (T2+1) != T4 and (T2+1) < 5:
                        self.Cr_TS2.setValue(T2+1)
                        return
                    else:
                        self.Cr_TS2.setValue(T2-1)
                        return
                elif T1 == T3:
                    if (T3+1) != T2 and (T3+1) != T4 and (T3+1) < 5:
                        self.Cr_TS3.setValue(T3+1)
                        return
                    else:
                        self.Cr_TS3.setValue(T3-1)
                        return
                elif T1 == T4:
                    if (T4+1) != T2 and (T4+1) != T3 and (T4+1) < 5:
                        self.Cr_TS4.setValue(T4+1)
                        return
                    else:
                        self.Cr_TS4.setValue(T4-1)
                        return

            if TS == 2:
                if T2 == T1:
                    if (T1+1) != T3 and (T1+1) != T4 and (T1+1) < 5:
                        self.Cr_TS1.setValue(T1+1)
                        return
                    else:
                        self.Cr_TS1.setValue(T1-1)
                        return
                elif T2 == T3:
                    if (T3+1) != T1 and (T3+1) != T4 and (T3+1) < 5:
                        self.Cr_TS3.setValue(T3+1)
                        return
                    else:
                        self.Cr_TS3.setValue(T3-1)
                        return
                elif T2 == T4:
                    if (T4+1) != T1 and (T4+1) != T3 and (T4+1) < 5:
                        self.Cr_TS4.setValue(T4+1)
                        return
                    else:
                        self.Cr_TS4.setValue(T4-1)
                        return

            if TS == 3:
                if T3 == T1:
                    if (T1+1) != T2 and (T1+1) != T4 and (T1+1) < 5:
                        self.Cr_TS1.setValue(T1+1)
                        return
                    else:
                        self.Cr_TS1.setValue(T1-1)
                        return
                elif T3 == T2:
                    if (T2+1) != T1 and (T2+1) != T4 and (T2+1) < 5:
                        self.Cr_TS2.setValue(T2+1)
                        return
                    else:
                        self.Cr_TS2.setValue(T2-1)
                        return
                elif T3 == T4:
                    if (T4+1) != T1 and (T4+1) != T2 and (T4+1) < 5:
                        self.Cr_TS4.setValue(T4+1)
                        return
                    else:
                        self.Cr_TS4.setValue(T4-1)
                        return

            if TS == 4:
                if T4 == T1:
                    if (T1+1) != T2 and (T1+1) != T3 and (T1+1) < 5:
                        self.Cr_TS1.setValue(T1+1)
                        return
                    else:
                        self.Cr_TS1.setValue(T1-1)
                        return
                elif T4 == T2:
                    if (T2+1) != T1 and (T2+1) != T3 and (T2+1) < 5:
                        self.Cr_TS2.setValue(T2+1)
                        return
                    else:
                        self.Cr_TS2.setValue(T2-1)
                        return
                elif T4 == T3:
                    if (T3+1) != T1 and (T3+1) != T2 and (T3+1) < 5:
                        self.Cr_TS3.setValue(T3+1)
                        return
                    else:
                        self.Cr_TS3.setValue(T3-1)
                        return

        except ValueError:
            pass

#---check InitTime function---#
    def IT_check(self):
        try:
            inp = float(self.Cr_IT.text())
            if inp > 0 and inp < 10000:
                self.Cr_IT.setStyleSheet(self.origStyleSheet)
                self.Dic["IT"] = True
                return
            else:
                self.Cr_IT.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_IT.setStyleSheet("border: 1px solid red")
            self.Cr_IT.clear()
            self.Cr_IT.setPlaceholderText("please enter digits only!")

        self.Dic["IT"] = False

#---check CfgTime function---#
    def CT_check(self):
        try:
            inp = float(self.Cr_CT.text())
            if inp > 0 and inp < 1000:
                self.Cr_CT.setStyleSheet(self.origStyleSheet)
                self.Dic["CT"] = True
                if self.Dic["CT"] and self.Dic["TD"] and self.Dic["TU"]:
                    CfgTim = inp
                    TD = float(self.Cr_TD.text())
                    TU = float(self.Cr_TU.text())
                    Tp = str(TU + TD + CfgTim)
                    self.Cr_Tp.setPlaceholderText(
                        "min. calc. Tp: " + Tp + "[µs]")
                if self.Dic["CT"] and self.Dic["Tp"] and self.Dic["TU"]:
                    CfgTim = inp
                    Tp = float(self.Cr_Tp.text())
                    TU = float(self.Cr_TU.text())
                    TD = str(Tp - TU - CfgTim)
                    self.Cr_TD.setPlaceholderText(
                        "max. calc. TRampDown: " + TD + "[µs]")
                if self.Dic["CT"] and self.Dic["TD"] and self.Dic["Tp"]:
                    CfgTim = inp
                    TD = float(self.Cr_TD.text())
                    Tp = float(self.Cr_Tp.text())
                    TU = str(Tp - TD - CfgTim)
                    self.Cr_TU.setPlaceholderText(
                        "max. calc. TRampUp: " + TU + "[µs]")
                return

        except ValueError:
            self.Cr_CT.setStyleSheet("border: 1px solid red")
            self.Cr_CT.clear()
            self.Cr_CT.setPlaceholderText("please enter digits only!")

        self.Dic["CT"] = False

#---check FMCW RangeFFT function---#
    def FMCWR_check(self):
        try:
            inp = int(self.Cr_FMCW_R.text())
            R = 2
            x = 1
            while R > 1:
                R = inp/2**x
                x += 1
            if R == 1:
                self.Cr_FMCW_R.setStyleSheet(self.origStyleSheet)
                self.Dic["FMCWR"] = True
            else:
                self.Cr_FMCW_R.setStyleSheet("border: 1px solid orange")
            return

        except ValueError:
            self.Cr_FMCW_R.setStyleSheet("border: 1px solid red")
            self.Cr_FMCW_R.clear()
            self.Cr_FMCW_R.setPlaceholderText("please enter integers only!")

        self.Dic["FMCWR"] = False

#---check FMCW AngFFT function---#
    def FMCWA_check(self):
        try:
            inp = int(self.Cr_FMCW_A.text())
            A = 2
            x = 1
            while A > 1:
                A = inp/2**x
                x += 1
            if A == 1:
                self.Cr_FMCW_A.setStyleSheet(self.origStyleSheet)
                self.Dic["FMCWA"] = True
            else:
                self.Cr_FMCW_A.setStyleSheet("border: 1px solid orange")
            return

        except ValueError:
            self.Cr_FMCW_A.setStyleSheet("border: 1px solid red")
            self.Cr_FMCW_A.clear()
            self.Cr_FMCW_A.setPlaceholderText("please enter intergers only!")

        self.Dic["FMCWA"] = False

#---check FMCW RMin function---#
    def FMCWRm_check(self):
        try:
            inp = float(self.Cr_FMCW_Rm.text())
            if inp >= 0:
                self.Cr_FMCW_Rm.setStyleSheet(self.origStyleSheet)
                self.Dic["FMCWRm"] = True
                return
            else:
                self.Cr_FMCW_Rm.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_FMCW_Rm.setStyleSheet("border: 1px solid red")
            self.Cr_FMCW_Rm.clear()
            self.Cr_FMCW_Rm.setPlaceholderText("please enter digits only!")

        self.Dic["FMCWRm"] = False

#---check FMCW RMax function---#
    def FMCWRM_check(self):
        try:
            inp = float(self.Cr_FMCW_RM.text())
            if inp >= 1:
                self.Cr_FMCW_RM.setStyleSheet(self.origStyleSheet)
                self.Dic["FMCWRM"] = True
                return
            else:
                self.Cr_FMCW_RM.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_FMCW_RM.setStyleSheet("border: 1px solid red")
            self.Cr_FMCW_RM.clear()
            self.Cr_FMCW_RM.setPlaceholderText("please enter digits only!")

        self.Dic["FMCWRM"] = False

#---check Chn1 function---#
    def Chn1_check(self):
        Chn = 1
        self.Chn_check(Chn)

#---check Chn2 function---#
    def Chn2_check(self):
        Chn = 2
        self.Chn_check(Chn)

#---check Chn3 function---#
    def Chn3_check(self):
        Chn = 3
        self.Chn_check(Chn)

#---check delChn function---#
    def Chn_check(self, Chn=None):
        try:
            C1 = int(self.Cr_FMCW_Chn1.value())
            C2 = int(self.Cr_FMCW_Chn2.value())
            C3 = int(self.Cr_FMCW_Chn3.value())

            if Chn == 1:
                if C1 == C2:
                    if (C2+1) != C3 and (C2+1) < 33:
                        self.Cr_FMCW_Chn2.setValue(C2+1)
                    else:
                        self.Cr_FMCW_Chn2.setValue(C2-1)
                elif C1 == C3:
                    if (C3+1) != C2 and (C3+1) < 33:
                        self.Cr_FMCW_Chn3.setValue(C3+1)
                    else:
                        self.Cr_FMCW_Chn3.setValue(C3-1)

            elif Chn == 2:
                if C2 == C1:
                    if (C1+1) != C3 and (C1+1) < 33:
                        self.Cr_FMCW_Chn1.setValue(C1+1)
                    else:
                        self.Cr_FMCW_Chn1.setValue(C1-1)
                elif C2 == C3:
                    if (C3+1) != C1 and (C3+1) < 33:
                        self.Cr_FMCW_Chn3.setValue(C3+1)
                    else:
                        self.Cr_FMCW_Chn3.setValue(C3-1)

            elif Chn == 3:
                if C3 == C1:
                    if (C1+1) != C2 and (C1+1) < 33:
                        self.Cr_FMCW_Chn1.setValue(C1+1)
                    else:
                        self.Cr_FMCW_Chn1.setValue(C1-1)
                elif C3 == C2:
                    if (C2+1) != C1 and (C2+1) < 33:
                        self.Cr_FMCW_Chn2.setValue(C2+1)
                    else:
                        self.Cr_FMCW_Chn2.setValue(C2-1)

        except ValueError:
            pass

#---check FMCW IgnoreSamples function---#
    def FMCWNI_check(self):
        try:
            inp = int(self.Cr_FMCW_NI.value())
            if inp > 0:
                self.Cr_FMCW_NI.setStyleSheet(self.origStyleSheet)
                self.Dic["FMCWNI"] = True
                return
            else:
                self.Cr_FMCW_NI.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_FMCW_NI.setStyleSheet("border: 1px solid red")

        self.Dic["FMCWNI"] = False

#---check RangeDoppler RangeFFT function---#
    def RDR_check(self):
        try:
            inp = int(self.Cr_RD_R.text())
            R = 2
            x = 1
            while R > 1:
                R = inp/2**x
                x += 1
            if R == 1:
                self.Cr_RD_R.setStyleSheet(self.origStyleSheet)
                self.Dic["RDR"] = True
            else:
                self.Cr_RD_R.setStyleSheet("border: 1px solid orange")
            return

        except ValueError:
            self.Cr_RD_R.setStyleSheet("border: 1px solid red")
            self.Cr_RD_R.clear()
            self.Cr_RD_R.setPlaceholderText("please enter integers only!")

        self.Dic["RDR"] = False

#---check RangeDoppler VelFFT function---#
    def RDV_check(self):
        try:
            inp = int(self.Cr_RD_V.text())
            V = 2
            x = 1
            while V > 1:
                V = inp/2**x
                x += 1
            if V == 1:
                self.Cr_RD_V.setStyleSheet(self.origStyleSheet)
                self.Dic["RDV"] = True
            else:
                self.Cr_RD_V.setStyleSheet("border: 1px solid orange")
            return

        except ValueError:
            self.Cr_RD_V.setStyleSheet("border: 1px solid red")
            self.Cr_RD_V.clear()
            self.Cr_RD_V.setPlaceholderText("please enter integers only!")

        self.Dic["RDV"] = False

#---check RangeDoppler RMin function---#
    def RDRm_check(self):
        try:
            inp = float(self.Cr_RD_Rm.text())
            if inp >= 0:
                self.Cr_RD_Rm.setStyleSheet(self.origStyleSheet)
                self.Dic["RDRm"] = True
                return
            else:
                self.Cr_RD_Rm.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_RD_Rm.setStyleSheet("border: 1px solid red")
            self.Cr_RD_Rm.clear()
            self.Cr_RD_Rm.setPlaceholderText("please enter digits only!")

        self.Dic["RDRm"] = False

#---check RangeDoppler RMax function---#
    def RDRM_check(self):
        try:
            inp = float(self.Cr_RD_RM.text())
            if inp >= 1:
                self.Cr_RD_RM.setStyleSheet(self.origStyleSheet)
                self.Dic["RDRM"] = True
                return
            else:
                self.Cr_RD_RM.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_RD_RM.setStyleSheet("border: 1px solid red")
            self.Cr_RD_RM.clear()
            self.Cr_RD_RM.setPlaceholderText("please enter digits only!")

        self.Dic["RDRM"] = False

#---check RangeDoppler IgnoreSamples function---#
    def RDNI_check(self):
        try:
            inp = int(self.Cr_RD_NI.value())
            if inp > 0:
                self.Cr_RD_NI.setStyleSheet(self.origStyleSheet)
                self.Dic["RDNI"] = True
                return
            else:
                self.Cr_RD_NI.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_RD_NI.setStyleSheet("border: 1px solid red")

        self.Dic["RDNI"] = False

#---check RangeProfile NFFT function---#
    def RPN_check(self):
        try:
            inp = int(self.Cr_RP_N.text())
            N = 2
            x = 1
            while N > 1:
                N = inp/2**x
                x += 1
            if N == 1:
                self.Cr_RP_N.setStyleSheet(self.origStyleSheet)
                self.Dic["RPN"] = True
            else:
                self.Cr_RP_N.setStyleSheet("border: 1px solid orange")
            return

        except ValueError:
            self.Cr_RP_N.setStyleSheet("border: 1px solid red")
            self.Cr_RP_N.clear()
            self.Cr_RP_N.setPlaceholderText("please enter integers only!")

        self.Dic["RPN"] = False

#---check RangeProfile RMin function---#
    def RPRm_check(self):
        try:
            inp = float(self.Cr_RP_Rm.text())
            if inp >= 0:
                self.Cr_RP_Rm.setStyleSheet(self.origStyleSheet)
                self.Dic["RPRm"] = True
                return
            else:
                self.Cr_RP_Rm.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_RP_Rm.setStyleSheet("border: 1px solid red")
            self.Cr_RP_Rm.clear()
            self.Cr_RP_Rm.setPlaceholderText("please enter digits only!")

        self.Dic["RPRm"] = False

#---check RangeProfile RMax function---#
    def RPRM_check(self):
        try:
            inp = float(self.Cr_RP_RM.text())
            if inp >= 1:
                self.Cr_RP_RM.setStyleSheet(self.origStyleSheet)
                self.Dic["RPRM"] = True
                return
            else:
                self.Cr_RP_RM.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_RP_RM.setStyleSheet("border: 1px solid red")
            self.Cr_RP_RM.clear()
            self.Cr_RP_RM.setPlaceholderText("please enter digits only!")

        self.Dic["RPRM"] = False

#---check RangeProfile IngoreSamples function---#
    def RPNI_check(self):
        try:
            inp = int(self.Cr_RP_NI.value())
            if inp > 0:
                self.Cr_RP_NI.setStyleSheet(self.origStyleSheet)
                self.Dic["RPNI"] = True
                return
            else:
                self.Cr_RP_NI.setStyleSheet("border: 1px solid red")

        except ValueError:
            self.Cr_RP_NI.setStyleSheet("border: 1px solid red")

        self.Dic["RPNI"] = False

#---Calculate TxPower a.k.a. Pt---#
    def TxPwrCalc(self, Pwr):
        if Pwr > 60:
            Pwr = 60
            print("maximum Power: 60%")
        elif Pwr < 4:
            Pwr = 4
            print("minimum Power: 4%")
        else:
            print("Power set to: " + str(Pwr) + "%")

        TxPwr = np.polyval(self.PP, Pwr)
        return TxPwr

#---ConfigCreator-function---#
    def CFG_CRTR(self):
        self.Dic = {"FS": None, "FSt": None, "TU": None, "TD": None, "TI": None,
                    "Tp": None, "CT": None, "IT": None, "NR": None, "Np": None,
                    "N": None, "TS1": None, "TS2": None, "TS3": None,
                    "TS4": None, "FMCWR": None, "FMCWA": None, "FMCWRm": None,
                    "FMCWRM": None, "Chn1": None, "Chn2": None, "Chn3": None,
                    "FMCWNI": None, "RDR": None, "RDV": None, "RDRm": None,
                    "RDRM": None, "RDNI": None, "RPN": None, "RPRm": None,
                    "RPRM": None, "RPNI": None}

        self.ScCr = QScrollArea()
        self.ScCr.setWidgetResizable(True)

        self.Crtr_Wndw = QWidget()

        self.CrLay = QGridLayout()

        self.Cr_Md_L = QLabel("Measurement Mode")
        self.Cr_Mode = QComboBox()
        self.Cr_Mode.addItems(["FMCW", "RangeDoppler", "RangeProfile"])
        self.Cr_Mode.currentTextChanged.connect(self.CFG_CHNGEMD)

        self.Cr_TXC_L = QLabel("TransmitterChannel")
        self.Cr_TXC = QSpinBox()
        self.Cr_TXC.setRange(1, 4)
        self.Cr_TXC.setPrefix("Tx")

        self.Cr_TXP_L = QLabel("TransmitterPower")
        self.Cr_TXP = QSpinBox()
        self.Cr_TXP.setRange(20, 65)
        self.Cr_TXP.setSuffix("%")

        self.Cr_BCfg = QLabel("BoardConfig:")

        self.Cr_FS_L = QLabel("Frequency @Start [GHz]")
        self.Cr_FS = QLineEdit()
        self.Cr_FS.setPlaceholderText("Range: 70-80 GHz")
        self.Cr_FS.textChanged.connect(self.FS_check)

        self.Cr_FSt_L = QLabel("Frequency @Stop [GHz]")
        self.Cr_FSt = QLineEdit()
        self.Cr_FSt.setPlaceholderText("Range: 70-80 GHz")
        self.Cr_FSt.textChanged.connect(self.FSt_check)

        self.Cr_fc_L = QLabel("centered Freq. fc: ")

        self.Cr_TU_L = QLabel("Time Start2Stop [µs]")
        self.Cr_TU = QLineEdit()
        self.Cr_TU.setPlaceholderText("Range: 1-1000 µs")
        self.Cr_TU.textChanged.connect(self.TU_check)

        self.Cr_TD_L = QLabel("Time Stop2Start [µs]")
        self.Cr_TD = QLineEdit()
        self.Cr_TD.setPlaceholderText("Range: 1-1000 µs")
        self.Cr_TD.textChanged.connect(self.TD_check)

        self.Cr_kf = QLabel("Slope kf [Hz/s]: ")

        self.Cr_Tp_L = QLabel("Time Frame2Frame [µs]")
        self.Cr_Tp = QLineEdit()
        self.Cr_Tp.setPlaceholderText("Range: 1-1000 µs")
        self.Cr_Tp.textChanged.connect(self.Tp_check)

        self.Cr_TI_L = QLabel("Time Sequence2Sequence [s]")
        self.Cr_TI = QLineEdit()
        self.Cr_TI.setPlaceholderText("Range: 0.-5 sec.")
        self.Cr_TI.textChanged.connect(self.TI_check)

        self.Cr_NR_L = QLabel("SequenceRepeats")
        self.Cr_NR = QLineEdit()
        self.Cr_NR.setPlaceholderText("Range: 1-n SequenceRepeats")
        self.Cr_NR.textChanged.connect(self.NR_check)

        self.Cr_Np_L = QLabel("Frames in Sequence")
        self.Cr_Np = QLineEdit()
        self.Cr_Np.setPlaceholderText("Range: 0-256 chirps/frames")
        self.Cr_Np.textChanged.connect(self.Np_check)

        self.Cr_N_L = QLabel("Samples in Frame")
        self.Cr_N = QLineEdit()
        self.Cr_N.setPlaceholderText("Range: 8-3968 samples in steps of 8")
        self.Cr_N.textChanged.connect(self.N_check)

        self.Cr_TS_L = QLabel("Sequence Order")
        self.Cr_TS1 = QSpinBox()
        self.Cr_TS1.setFixedWidth(146)
        self.Cr_TS1.setPrefix("Tx")
        self.Cr_TS1.setRange(1, 4)
        self.Cr_TS1.setValue(1)
        self.Cr_TS1.valueChanged.connect(self.TS1_check)
        self.Cr_TS2 = QSpinBox()
        self.Cr_TS2.setFixedWidth(146)
        self.Cr_TS2.setPrefix("Tx")
        self.Cr_TS2.setRange(1, 4)
        self.Cr_TS2.setValue(2)
        self.Cr_TS2.valueChanged.connect(self.TS2_check)
        self.Cr_TS3 = QSpinBox()
        self.Cr_TS3.setFixedWidth(146)
        self.Cr_TS3.setPrefix("Tx")
        self.Cr_TS3.setRange(1, 4)
        self.Cr_TS3.setValue(3)
        self.Cr_TS3.valueChanged.connect(self.TS3_check)
        self.Cr_TS4 = QSpinBox()
        self.Cr_TS4.setFixedWidth(146)
        self.Cr_TS4.setPrefix("Tx")
        self.Cr_TS4.setRange(1, 4)
        self.Cr_TS4.setValue(4)
        self.Cr_TS4.valueChanged.connect(self.TS4_check)

        self.Cr_IE = QCheckBox("InitEvent")
        self.Cr_IE.setChecked(True)

        self.Cr_IT_L = QLabel("IniTime [µs]")
        self.Cr_IT = QLineEdit()
        self.Cr_IT.setPlaceholderText("orig. value: 5000 µs")
        self.Cr_IT.textChanged.connect(self.IT_check)

        self.Cr_CT_L = QLabel("CfgTime [µs]")
        self.Cr_CT = QLineEdit()
        self.Cr_CT.setPlaceholderText("orig. value: 50 µs")
        self.Cr_CT.textChanged.connect(self.CT_check)

        self.Cr_EE = QCheckBox("ExternalEvent")
        self.Cr_EE.setChecked(False)

        self.Cr_FMCW = QLabel("BeamformingConfig")

        self.Cr_FMCW_R_L = QLabel("RangeFFT")
        self.Cr_FMCW_R = QLineEdit()
        self.Cr_FMCW_R.setPlaceholderText(
            "Range: n over 2 --- orig. value: 10 over 2")
        self.Cr_FMCW_R.textChanged.connect(self.FMCWR_check)

        self.Cr_FMCW_A_L = QLabel("AngleFFT")
        self.Cr_FMCW_A = QLineEdit()
        self.Cr_FMCW_A.setPlaceholderText(
            "Range: n over 2 --- orig. value: 8 over 2")
        self.Cr_FMCW_A.textChanged.connect(self.FMCWA_check)

        self.Cr_FMCW_Abs = QCheckBox("Absolute Values")
        self.Cr_FMCW_Abs.setChecked(True)

        self.Cr_FMCW_Ext = QCheckBox("Extract Range")
        self.Cr_FMCW_Ext.setChecked(True)

        self.Cr_FMCW_Rm_L = QLabel("min. Range")
        self.Cr_FMCW_Rm = QLineEdit()
        self.Cr_FMCW_Rm.setPlaceholderText("Range: 0-n meters")
        self.Cr_FMCW_Rm.textChanged.connect(self.FMCWRm_check)

        self.Cr_FMCW_RM_L = QLabel("max. Range")
        self.Cr_FMCW_RM = QLineEdit()
        self.Cr_FMCW_RM.setPlaceholderText("Range: 1-n meters")
        self.Cr_FMCW_RM.textChanged.connect(self.FMCWRM_check)

        self.Cr_FMCW_Chn_L = QLabel("delete Channels")
        self.Cr_FMCW_Chn1 = QSpinBox()
        self.Cr_FMCW_Chn1.setRange(1, 32)
        self.Cr_FMCW_Chn1.setValue(7)
        self.Cr_FMCW_Chn1.valueChanged.connect(self.Chn1_check)
        self.Cr_FMCW_Chn2 = QSpinBox()
        self.Cr_FMCW_Chn2.setRange(1, 32)
        self.Cr_FMCW_Chn2.setValue(15)
        self.Cr_FMCW_Chn2.valueChanged.connect(self.Chn2_check)
        self.Cr_FMCW_Chn3 = QSpinBox()
        self.Cr_FMCW_Chn3.setRange(1, 32)
        self.Cr_FMCW_Chn3.setValue(31)
        self.Cr_FMCW_Chn3.valueChanged.connect(self.Chn3_check)

        self.Cr_FMCW_NI_L = QLabel("Ignore Samples")
        self.Cr_FMCW_NI = QSpinBox()
        self.Cr_FMCW_NI.setRange(0, 100)
        self.Cr_FMCW_NI.setValue(1)
        self.Cr_FMCW_NI.valueChanged.connect(self.FMCWNI_check)

        self.Cr_FMCW_Re = QCheckBox("RemoveMean")
        self.Cr_FMCW_Re.setChecked(True)

        self.Cr_FMCW_W = QCheckBox("Use DataWindow")
        self.Cr_FMCW_W.setChecked(True)

        self.Cr_FMCW_dB = QCheckBox("Convert to dBV")
        self.Cr_FMCW_dB.setChecked(True)

        self.Cr_RD = QLabel("RangeDopplerConfig")

        self.Cr_RD_R_L = QLabel("RangeFFT")
        self.Cr_RD_R = QLineEdit()
        self.Cr_RD_R.setPlaceholderText(
            "Range: n over 2 --- orig. value: 10 over 2")
        self.Cr_RD_R.textChanged.connect(self.RDR_check)

        self.Cr_RD_V_L = QLabel("VelocityFFT")
        self.Cr_RD_V = QLineEdit()
        self.Cr_RD_V.setPlaceholderText(
            "Range: n over 2 --- orig value: 10 over 2")
        self.Cr_RD_V.textChanged.connect(self.RDV_check)

        self.Cr_RD_Abs = QCheckBox("Absolute Values")
        self.Cr_RD_Abs.setChecked(True)

        self.Cr_RD_Ext = QCheckBox("Extract Range")
        self.Cr_RD_Ext.setChecked(True)

        self.Cr_RD_Rm_L = QLabel("min. Range")
        self.Cr_RD_Rm = QLineEdit()
        self.Cr_RD_Rm.setPlaceholderText("Range: 0-n meters")
        self.Cr_RD_Rm.textChanged.connect(self.RDRm_check)

        self.Cr_RD_RM_L = QLabel("max. Range")
        self.Cr_RD_RM = QLineEdit()
        self.Cr_RD_RM.setPlaceholderText("Range: 1-n meters")
        self.Cr_RD_RM.textChanged.connect(self.RDRM_check)

        self.Cr_RD_Re = QCheckBox("RemoveMean")
        self.Cr_RD_Re.setChecked(True)

        self.Cr_RD_W = QCheckBox("Use DataWindow")
        self.Cr_RD_W.setChecked(True)

        self.Cr_RD_dB = QCheckBox("Convert to dBV")
        self.Cr_RD_dB.setChecked(True)

        self.Cr_RD_NI_L = QLabel("Ignore Samples")
        self.Cr_RD_NI = QSpinBox()
        self.Cr_RD_NI.setRange(0, 100)
        self.Cr_RD_NI.setValue(1)
        self.Cr_RD_NI.valueChanged.connect(self.RDNI_check)

        self.Cr_RP = QLabel("RangeProfileConfig")

        self.Cr_RP_N_L = QLabel("FFT-Size")
        self.Cr_RP_N = QLineEdit()
        self.Cr_RP_N.setPlaceholderText(
            "Range: n over 2 --- orig. value: 12 over 2")
        self.Cr_RP_N.textChanged.connect(self.RPN_check)

        self.Cr_RP_Abs = QCheckBox("Absolute Values")
        self.Cr_RP_Abs.setChecked(True)

        self.Cr_RP_Ext = QCheckBox("Extract Range")
        self.Cr_RP_Ext.setChecked(True)

        self.Cr_RP_Rm_L = QLabel("min. Range")
        self.Cr_RP_Rm = QLineEdit()
        self.Cr_RP_Rm.setPlaceholderText("Range: 0-n meters")
        self.Cr_RP_Rm.textChanged.connect(self.RPRm_check)

        self.Cr_RP_RM_L = QLabel("max. Range")
        self.Cr_RP_RM = QLineEdit()
        self.Cr_RP_RM.setPlaceholderText("Range: 1-n meters")
        self.Cr_RP_RM.textChanged.connect(self.RPRM_check)

        self.Cr_RP_Re = QCheckBox("RemoveMean")
        self.Cr_RP_Re.setChecked(True)

        self.Cr_RP_W = QCheckBox("Use DataWindow")
        self.Cr_RP_W.setChecked(True)

        self.Cr_RP_X = QCheckBox("only Positive Range")
        self.Cr_RP_X.setChecked(True)

        self.Cr_RP_dB = QCheckBox("Convert to dBV")
        self.Cr_RP_dB.setChecked(True)

        self.Cr_RP_NI_L = QLabel("Ignore Samples")
        self.Cr_RP_NI = QSpinBox()
        self.Cr_RP_NI.setRange(0, 100)
        self.Cr_RP_NI.setValue(1)
        self.Cr_RP_NI.valueChanged.connect(self.RPNI_check)

        self.Cr_ok = QPushButton("ok...")
        self.Cr_ok.setToolTip("create ConfigModel")
        self.Cr_ok.clicked.connect(self.CFG_CRTR_STRT)

        # self.CrLay.addWidget(self.Cr_Md_L, 0, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_Mode, 0, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_TXC_L, 1, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_TXC, 1, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_TXP_L, 2, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_TXP, 2, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_BCfg, 3, 0, 1, 2)
        # self.CrLay.addWidget(self.Cr_FS_L, 4, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_FS, 4, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_FSt_L, 5, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_FSt, 5, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_TU_L, 6, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_TU, 6, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_TD_L, 7, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_TD, 7, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_Tp_L, 8, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_Tp, 8, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_TI_L, 9, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_TI, 9, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_NR_L, 10, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_NR, 10, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_Np_L, 11, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_Np, 11, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_N_L, 12, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_N, 12, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_TS_L, 13, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_TS1, 14, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_TS2, 14, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_TS3, 14, 2, 1, 1)
        # self.CrLay.addWidget(self.Cr_TS4, 14, 3, 1, 1)
        # self.CrLay.addWidget(self.Cr_IE, 15, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_IT, 16, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_CT, 17, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_EE, 18, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW, 20, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_R_L, 21, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_R, 21, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_A_L, 22, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_A, 22, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_Abs, 23, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_Ext, 24, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_Rm_L, 25, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_Rm, 25, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_RM_L, 26, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_RM, 26, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_Chn_L, 27, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_Chn1, 28, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_Chn2, 28, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_Chn3, 28, 2, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_NI_L, 29, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_NI, 29, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_Re, 30, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_W, 31, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_FMCW_dB, 32, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_RD, 34, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_RD_R_L, 35, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_RD_R, 35, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_RD_V_L, 36, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_RD_V, 36, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_RD_Abs, 37, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_RD_Ext, 38, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_RD_Rm_L, 39, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_RD_Rm, 39, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_RD_RM_L, 40, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_RD_RM, 40, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_RD_Re, 41, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_RD_W, 42, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_RD_dB, 43, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_RD_NI_L, 44, 0, 1, 1)
        # self.CrLay.addWidget(self.Cr_RD_NI, 44, 1, 1, 1)
        # self.CrLay.addWidget(self.Cr_ok, 57, 2, 1, 1)

        self.CFG_CHNGEMD()

#---ConfigCreator ChangeMode function---#
    def CFG_CHNGEMD(self):
        self.ScCr.close()
        mode = self.Cr_Mode.currentText()
        self.deleteLayout(self.CrLay)

        if mode == "FMCW":
            self.CrLay.addWidget(self.Cr_Md_L, 0, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_Mode, 0, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_TXC_L, 1, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TXC, 1, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_TXP_L, 2, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TXP, 2, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_BCfg, 3, 0, 1, 2)
            self.CrLay.addWidget(self.Cr_FS_L, 4, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_FS, 4, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_fc_L, 4, 3, 2, 1)
            self.CrLay.addWidget(self.Cr_FSt_L, 5, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_FSt, 5, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_kf, 5, 3, 2, 1)
            self.CrLay.addWidget(self.Cr_TU_L, 6, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TU, 6, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_TD_L, 7, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TD, 7, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_Tp_L, 8, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_Tp, 8, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_TI_L, 9, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TI, 9, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_NR_L, 10, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_NR, 10, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_Np_L, 11, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_Np, 11, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_N_L, 12, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_N, 12, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_TS_L, 13, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TS1, 14, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TS2, 14, 1, 1, 1)
            self.CrLay.addWidget(self.Cr_TS3, 14, 2, 1, 1)
            self.CrLay.addWidget(self.Cr_TS4, 14, 3, 1, 1)
            self.CrLay.addWidget(self.Cr_IE, 15, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_IT_L, 16, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_IT, 16, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_CT_L, 17, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_CT, 17, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_EE, 18, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_FMCW, 20, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_FMCW_R_L, 21, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_FMCW_R, 21, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_FMCW_A_L, 22, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_FMCW_A, 22, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_FMCW_Abs, 23, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_FMCW_Ext, 24, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_FMCW_Rm_L, 25, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_FMCW_Rm, 25, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_FMCW_RM_L, 26, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_FMCW_RM, 26, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_FMCW_Chn_L, 27, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_FMCW_Chn1, 27, 1, 1, 1)
            self.CrLay.addWidget(self.Cr_FMCW_Chn2, 27, 2, 1, 1)
            self.CrLay.addWidget(self.Cr_FMCW_Chn3, 27, 3, 1, 1)
            self.CrLay.addWidget(self.Cr_FMCW_NI_L, 29, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_FMCW_NI, 29, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_FMCW_Re, 30, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_FMCW_W, 31, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_FMCW_dB, 32, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_ok, 34, 3, 1, 1)
        elif mode == "RangeDoppler":
            self.CrLay.addWidget(self.Cr_Md_L, 0, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_Mode, 0, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_TXC_L, 1, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TXC, 1, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_TXP_L, 2, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TXP, 2, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_BCfg, 3, 0, 1, 2)
            self.CrLay.addWidget(self.Cr_FS_L, 4, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_FS, 4, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_fc_L, 4, 3, 2, 1)
            self.CrLay.addWidget(self.Cr_FSt_L, 5, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_FSt, 5, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_kf, 5, 3, 2, 1)
            self.CrLay.addWidget(self.Cr_TU_L, 6, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TU, 6, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_TD_L, 7, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TD, 7, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_Tp_L, 8, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_Tp, 8, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_TI_L, 9, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TI, 9, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_NR_L, 10, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_NR, 10, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_Np_L, 11, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_Np, 11, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_N_L, 12, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_N, 12, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_TS_L, 13, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TS1, 14, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TS2, 14, 1, 1, 1)
            self.CrLay.addWidget(self.Cr_TS3, 14, 2, 1, 1)
            self.CrLay.addWidget(self.Cr_TS4, 14, 3, 1, 1)
            self.CrLay.addWidget(self.Cr_IE, 15, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_IT_L, 16, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_IT, 16, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_CT_L, 17, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_CT, 17, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_EE, 18, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RD, 20, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RD_R_L, 21, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RD_R, 21, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_RD_V_L, 22, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RD_V, 22, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_RD_Abs, 23, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RD_Ext, 24, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RD_Rm_L, 25, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RD_Rm, 25, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_RD_RM_L, 26, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RD_RM, 26, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_RD_Re, 27, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RD_W, 28, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RD_dB, 29, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RD_NI_L, 30, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RD_NI, 30, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_ok, 32, 3, 1, 1)
        elif mode == "RangeProfile":
            self.CrLay.addWidget(self.Cr_Md_L, 0, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_Mode, 0, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_TXC_L, 1, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TXC, 1, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_TXP_L, 2, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TXP, 2, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_BCfg, 3, 0, 1, 2)
            self.CrLay.addWidget(self.Cr_FS_L, 4, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_FS, 4, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_fc_L, 4, 3, 2, 1)
            self.CrLay.addWidget(self.Cr_FSt_L, 5, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_FSt, 5, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_kf, 5, 3, 2, 1)
            self.CrLay.addWidget(self.Cr_TU_L, 6, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TU, 6, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_TD_L, 7, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TD, 7, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_Tp_L, 8, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_Tp, 8, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_TI_L, 9, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TI, 9, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_NR_L, 10, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_NR, 10, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_Np_L, 11, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_Np, 11, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_N_L, 12, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_N, 12, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_TS_L, 13, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TS1, 14, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_TS2, 14, 1, 1, 1)
            self.CrLay.addWidget(self.Cr_TS3, 14, 2, 1, 1)
            self.CrLay.addWidget(self.Cr_TS4, 14, 3, 1, 1)
            self.CrLay.addWidget(self.Cr_IE, 15, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_IT_L, 16, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_IT, 16, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_CT_L, 17, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_CT, 17, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_EE, 18, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RP, 20, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RP_N_L, 21, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RP_N, 21, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_RP_Abs, 22, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RP_Ext, 23, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RP_Rm_L, 24, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RP_Rm, 24, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_RP_RM_L, 25, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RP_RM, 25, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_RP_Re, 26, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RP_W, 27, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RP_X, 28, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RP_dB, 29, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RP_NI_L, 30, 0, 1, 1)
            self.CrLay.addWidget(self.Cr_RP_NI, 30, 1, 1, 2)
            self.CrLay.addWidget(self.Cr_ok, 32, 3, 1, 1)
        else:
            self.errmsg("AttributeError!",
                        "Please try to select the mode again!", "c")
            self.ScCr.close()
            self.CFG_CRTR()
            return

        self.Crtr_Wndw.setLayout(self.CrLay)
        self.ScCr.setWindowTitle("ConfigCreator")
        self.ScCr.setWidget(self.Crtr_Wndw)
        self.ScCr.resize(720, 640)
        self.ScCr.show()

#---ConfigCreator Start function---#
    def CFG_CRTR_STRT(self):
        self.ScCr.close()

        mode = self.Cr_Mode.currentText()

        self.TxChn = self.Cr_TXC.value()
        self.TxPwr = self.TxPwrCalc(self.Cr_TXP.value())

        if self.Dic["FS"]:
            self.TCfg["fStrt"] = float(self.Cr_FS.text()) * 1e9
        else:
            self.TCfg["fStrt"] = self.TCfg["fStrt"]
        if self.Dic["FSt"]:
            self.TCfg["fStop"] = float(self.Cr_FSt.text()) * 1e9
        else:
            self.TCfg["fStop"] = self.TCfg["fStop"]
        if self.Dic["TU"]:
            self.TCfg["TRampUp"] = float(self.Cr_TU.text()) * 1e-6
        else:
            self.TCfg["TRampUp"] = self.TCfg["TRampUp"]
        if self.Dic["TD"]:
            self.TCfg["TRampDo"] = float(self.Cr_TD.text()) * 1e-6
        else:
            self.TCfg["TRampDo"] = self.TCfg["TRampDo"]
        if self.Dic["Tp"]:
            self.TCfg["Tp"] = float(self.Cr_Tp.text()) * 1e-6
        else:
            self.TCfg["Tp"] = self.TCfg["Tp"]
        if self.Dic["TI"]:
            self.TCfg["TInt"] = float(self.Cr_TI.text())
        else:
            self.TCfg["TInt"] = self.TCfg["TInt"]
        if self.Dic["NR"]:
            self.TCfg["NrFrms"] = int(self.Cr_NR.text())
        else:
            self.TCfg["NrFrms"] = self.TCfg["NrFrms"]
        if self.Dic["Np"]:
            self.TCfg["Np"] = int(self.Cr_Np.text())
        else:
            self.TCfg["Np"] = self.TCfg["Np"]
        if self.Dic["N"]:
            self.TCfg["N"] = int(self.Cr_N.text())
        else:
            self.TCfg["N"] = self.TCfg["N"]
        if self.Dic["IT"]:
            self.TCfg["IniTim"] = float(self.Cr_IT.text()) * 1e-6
        else:
            self.TCfg["IniTim"] = self.TCfg["IniTim"]
        if self.Dic["CT"]:
            self.TCfg["CfgTim"] = float(self.Cr_CT.text()) * 1e-6
        else:
            self.TCfg["CfgTim"] = self.TCfg["CfgTim"]

        self.TCfg["TxSeq"] = np.array([self.Cr_TS1.value(), self.Cr_TS2.value(),
                                       self.Cr_TS3.value(), self.Cr_TS4.value()])

        if self.Cr_IE.isChecked():
            self.TCfg["IniEve"] = 1
        else:
            self.TCfg["IniEve"] = 0

        if self.Cr_EE.isChecked():
            self.TCfg["ExtEve"] = 1
        else:
            self.TCfg["ExtEve"] = 0

        if mode == "FMCW":
            if self.Dic["FMCWR"]:
                self.TBCfg["RangeFFT"] = int(self.Cr_FMCW_R.text())
            else:
                self.TBCfg["RangeFFT"] = self.TBCfg["RangeFFT"]
            if self.Dic["FMCWA"]:
                self.TBCfg["AngFFT"] = int(self.Cr_FMCW_A.text())
            else:
                self.TBCfg["AngFFT"] = self.TBCfg["AngFFT"]
            if self.Dic["FMCWRm"]:
                self.TBCfg["RMin"] = float(self.Cr_FMCW_Rm.text())
            else:
                self.TBCfg["RMin"] = self.TBCfg["RMin"]
            if self.Dic["FMCWRM"]:
                self.TBCfg["RMax"] = float(self.Cr_FMCW_RM.text())
            else:
                self.TBCfg["RMax"] = self.TBCfg["RMax"]
            if self.Dic["FMCWNI"]:
                self.TBCfg["NIni"] = self.Cr_FMCW_NI.value()
            else:
                self.TBCfg["NIni"] = self.TBCfg["NIni"]

            Chn = np.arange(32)
            Chn = np.delete(Chn, [self.Cr_FMCW_Chn1.value(),
                                  self.Cr_FMCW_Chn2.value(),
                                  self.Cr_FMCW_Chn3.value()])
            self.TBCfg["ChnOrder"] = Chn

            if self.Cr_FMCW_Abs.isChecked():
                self.TBCfg["Abs"] = 1
            else:
                self.TBCfg["Abs"] = 0

            if self.Cr_FMCW_Ext.isChecked():
                self.TBCfg["Ext"] = 1
            else:
                self.TBCfg["Ext"] = 0

            if self.Cr_FMCW_Re.isChecked():
                self.TBCfg["RemoveMean"] = 1
            else:
                self.TBCfg["RemoveMean"] = 0

            if self.Cr_FMCW_W.isChecked():
                self.TBCfg["Window"] = 1
            else:
                self.TBCfg["Window"] = 0

            if self.Cr_FMCW_dB.isChecked():
                self.TBCfg["dB"] = 1
            else:
                self.TBCfg["dB"] = 0

        if mode == "RangeDoppler":
            if self.Dic["RDR"]:
                self.TRCfg["RangeFFT"] = int(self.Cr_RD_R.text())
            else:
                self.TRCfg["RangeFFT"] = self.TRCfg["RangeFFT"]
            if self.Dic["RDV"]:
                self.TRCfg["VelFFT"] = int(self.Cr_RD_V.text())
            else:
                self.TRCfg["VelFFT"] = self.TRCfg["VelFFT"]
            if self.Dic["RDRm"]:
                self.TRCfg["RMin"] = float(self.Cr_RD_Rm.text())
            else:
                self.TRCfg["RMin"] = self.TRCfg["RMin"]
            if self.Dic["RDRM"]:
                self.TRCfg["RMax"] = float(self.Cr_RD_RM.text())
            else:
                self.TRCfg["RMax"] = self.TRCfg["RMax"]
            if self.Dic["RDNI"]:
                self.TRCfg["NIni"] = self.Cr_RD_NI.value()
            else:
                self.TRCfg["NIni"] = self.TRCfg["NIni"]

            if self.Cr_RD_Abs.isChecked():
                self.TRCfg["Abs"] = 1
            else:
                self.TRCfg["Abs"] = 0

            if self.Cr_RD_Ext.isChecked():
                self.TRCfg["Ext"] = 1
            else:
                self.TRCfg["Ext"] = 0

            if self.Cr_RD_Re.isChecked():
                self.TRCfg["RemoveMean"] = 1
            else:
                self.TRCfg["RemoveMean"] = 0

            if self.Cr_RD_W.isChecked():
                self.TRCfg["Window"] = 1
            else:
                self.TRCfg["Window"] = 0

            if self.Cr_RD_dB.isChecked():
                self.TRCfg["dB"] = 1
            else:
                self.TRCfg["dB"] = 0

        if mode == "RangeProfile":
            if self.Dic["RPN"]:
                self.TPCfg["NFFT"] = int(self.Cr_RP_N.text())
            else:
                self.TPCfg["NFFT"] = self.SPCfg["NFFT"]
            if self.Dic["RPRm"]:
                self.TPCfg["RMin"] = float(self.Cr_RP_Rm.text())
            else:
                self.TPCfg["RMin"] = self.SPCfg["RMin"]
            if self.Dic["RPRM"]:
                self.TPCfg["RMax"] = float(self.Cr_RP_RM.text())
            else:
                self.TPCfg["RMax"] = self.SPCfg["RMax"]
            if self.Dic["RPNI"]:
                self.TPCfg["NIni"] = self.Cr_RP_NI.value()
            else:
                self.TPCfg["NIni"] = self.SPCfg["NIni"]

            if self.Cr_RP_Abs.isChecked():
                self.TPCfg["Abs"] = 1
            else:
                self.TPCfg["Abs"] = 0

            if self.Cr_RP_Ext.isChecked():
                self.TPCfg["Ext"] = 1
            else:
                self.TPCfg["Ext"] = 0

            if self.Cr_RP_Re.isChecked():
                self.TPCfg["RemoveMean"] = 1
            else:
                self.TPCfg["RemoveMean"] = 0

            if self.Cr_RP_W.isChecked():
                self.TPCfg["Window"] = 1
            else:
                self.TPCfg["Window"] = 0

            if self.Cr_RP_X.isChecked():
                self.TPCfg["XPos"] = 1
            else:
                self.TPCfg["XPos"] = 0

            if self.Cr_RP_dB.isChecked():
                self.TPCfg["dB"] = 1
            else:
                self.TPCfg["dB"] = 0

        Q = self.errmsg("Config created!", "Config has been saved into the ConfigWindow of the selected MeasurementMode "
                        "and the BoardConfigWindow!\nNo Configs are set yet! To set the Configs go to the ConfigWindow!\n"
                        "Do you wish to open the Windows right now?", "q")

        if Q == 0:
            self.BRD_CFG()
            if mode == "FMCW":
                self.BMF_CFG()
            if mode == "RangeDoppler":
                self.RD_CFG()
            if mode == "RangeProfile":
                self.RP_CFG()
        else:
            return

#---save Config---#
    def CFG_SAVE(self):
        #-------safetyquestion-------#
        Qstn = self.errmsg(
            "Are you sure?", "Should all Configs really be saved to a file?", "q")

#-------check answer-------#
        if Qstn == 0:
            cont = True
        else:
            cont = False

#-------continue or abort-------#
        if not cont:
            self.errmsg("Confirmed!", "Configs have not been saved!", "i")
            return

#-------create Window-------#
        self.Cfg_Save_Wndw = QWidget()
#-------create Title-------#
        self.Cfg_Save_Ttl = QLabel("Enter a saveName for the .config-file:")
#-------create a Input-Line-------#
        self.Cfg_Save_str = QLineEdit()
        self.Cfg_Save_str.setPlaceholderText("for example 'RangeDoppler'")
#-------create a button-------#
        self.Cfg_Save_btn = QPushButton("ok...")
        self.Cfg_Save_btn.setToolTip("create a .config-file")
        self.Cfg_Save_btn.clicked.connect(self.CFG_SAVE_CREATE)
#-------create a Layout and fill-------#
        self.Cfg_Save_Lay = QGridLayout()
        self.Cfg_Save_Lay.addWidget(self.Cfg_Save_Ttl, 0, 0, 1, 2)
        self.Cfg_Save_Lay.addWidget(self.Cfg_Save_str, 1, 0, 1, 2)
        self.Cfg_Save_Lay.addWidget(self.Cfg_Save_btn, 2, 1, 1, 1)
#-------set Window attributes-------#
        self.Cfg_Save_Wndw.setLayout(self.Cfg_Save_Lay)
        self.Cfg_Save_Wndw.setWindowTitle("save Configs")
        self.Cfg_Save_Wndw.resize(256, 128)
        self.Cfg_Save_Wndw.show()

#---create Configsave function---#
    def CFG_SAVE_CREATE(self):
        #-------close Window-------#
        self.Cfg_Save_Wndw.close()
#-------get input-------#
        self.saveName = self.Cfg_Save_str.text()
#-------get saveplace-------#
        self.saveplace = QFileDialog.getExistingDirectory()
#-------check input-------#
        try:
            if len(self.saveName) <= 1:
                raise NameError
            if self.saveplace == "":
                raise NotADirectoryError
#-----------get Configs-----------#
            to_save = {"Board": self.BCfg,
                       "Beam": self.BFCfg,
                       "RangeDoppler": self.RDCfg,
                       "RangeProfile": self.RPCfg,
                       "Mode": "?"}
            if self.CheckNorm.isChecked():
                to_save["Norm"] = 1
                to_save["NVal"] = self.NormBox.value()
            else:
                to_save["Norm"] = 0
                to_save["NVal"] = -200
#-----------create file-----------#
            self.savefull = self.saveplace + "/" + self.saveName + ".config"
            file = open(self.savefull, "w")
            file.write(jsonpickle.dumps(to_save))
            file.close()
            self.errmsg("Success!", "Config-file saved successfully!", "i")
#-------except Errors-------#
        except NameError:
            self.errmsg(
                "NameError!", "Please enter a valid name and try again!", "w")
            self.Cfg_Save_str.clear()
            self.Cfg_Save_Wndw.show()
            return

        except NotADirectoryError:
            self.errmsg("NotADirectoryError!",
                        "Please enter a valid directory and try again!", "w")
            self.CFG_SAVE_CREATE()
            return

#---load config function---#
    def CFG_LOAD(self):
        #-------get file-------#
        self.openfile = QFileDialog.getOpenFileName()[0]
#-------check file-------#
        try:
            if self.openfile == "":
                raise FileNotFoundError
#-----------open file-----------#
            file = open(self.openfile, "r")
            from_save = jsonpickle.loads(file.read())
#-----------assign Configs--------------#
            self.BCfg = dict(from_save["Board"])
            self.BFCfg = dict(from_save["Beam"])
            self.RDCfg = dict(from_save["RangeDoppler"])
            self.RPCfg = dict(from_save["RangeProfile"])
            self.Mode = from_save["Mode"]
            if from_save["Norm"]:
                self.CheckNorm.setChecked(True)
                self.NormBox.setValue(from_save["NVal"])
            else:
                self.CheckNorm.setChecked(False)
                self.NormBox.setValue(from_save["NVal"])
            self.errmsg(
                "Success!", "Successfully loaded Configs from file!", "i")
#-------except Errors-------#
        except FileNotFoundError:
            self.errmsg("FileNotFoundError!",
                        "Could not find file! Please try again!", "w")
            self.CFG_LOAD()
            return

#---Preset-Config-Menu---#
    def CFG_PS(self):
        #-------create menuWindow-------#
        self.PS_Wndw = QWidget()

#-------create a small layout-------#
        self.PS_Layout = QGridLayout()

#-------create Combobox with Presets-------#
        self.PS_CB = QComboBox()
        Presets = ["FMCW", "RangeDoppler", "RangeProfile", "FMCW-RP-Hybrid"]
        self.PS_CB.addItems(Presets)

#-------create a load Button-------#
        self.PS_PshBtn = QPushButton("load...")
        self.PS_PshBtn.setToolTip("load Config-Preset")
        self.PS_PshBtn.clicked.connect(self.CFG_PS_LOAD)
        self.PS_PshBtn.setFixedWidth(50)

#-------fill layout and define Window-------#
        self.PS_Layout.addWidget(self.PS_CB, 0, 0, 1, 2)
        self.PS_Layout.addWidget(self.PS_PshBtn, 1, 1, 1, 1)

        self.PS_Wndw.setLayout(self.PS_Layout)
        self.PS_Wndw.resize(256, 128)
        self.PS_Wndw.setWindowTitle("Preset Configs")
        self.PS_Wndw.show()

#---Preset-load-function---#
    def CFG_PS_LOAD(self):
        #-------get choosen preset-------#
        choosen = self.PS_CB.currentText()

#-------load preset-------#
        if choosen == "FMCW":
            self.BCfg = dict(self.StdCfg)
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

            self.BFCfg = dict(self.SBCfg)
            self.BFCfg["RangeFFT"] = 2**10
            self.BFCfg["AngFFT"] = 2**8
            self.BFCfg["Abs"] = 1
            self.BFCfg["Ext"] = 1
            self.BFCfg["RMin"] = 1
            self.BFCfg["RMax"] = 10
            self.BFCfg["ChnOrder"] = np.array([0, 1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 16, 17,
                                               18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29, 30, 31])

            self.NormBox.setValue(-20)
            self.CheckNorm.setChecked(True)

        elif choosen == "RangeDoppler":
            self.BCfg = dict(self.StdCfg)
            self.BCfg["fStrt"] = 76e9
            self.BCfg["fStop"] = 78e9
            self.BCfg["TRampUp"] = 130-6
            self.BCfg["TRampDo"] = 20e-6
            self.BCfg["TInt"] = 500e-3
            self.BCfg["Tp"] = 400e-6
            self.BCfg["N"] = 256
            self.BCfg["Np"] = 32
            self.BCfg["NrFrms"] = 10

            self.RDCfg = dict(self.SRCfg)
            self.RDCfg["RangeFFT"] = 2**12
            self.RDCfg["VelFFT"] = 2**10
            self.RDCfg["Abs"] = 1
            self.RDCfg["Ext"] = 1
            self.RDCfg["RMin"] = 1
            self.RDCfg["RMax"] = 5
            self.RDCfg["RemoveMean"] = 0

            self.NormBox.setValue(-40)
            self.CheckNorm.setChecked(True)

        elif choosen == "RangeProfile":
            self.BCfg = dict(self.StdCfg)
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

            self.RPCfg = dict(self.SPCfg)
            self.RPCfg["NFFT"] = 2**12
            self.RPCfg["Abs"] = 1
            self.RPCfg["Ext"] = 1
            self.RPCfg["RMin"] = 1
            self.RPCfg["RMax"] = 10

            self.NormBox.setValue(-200)
            self.CheckNorm.setChecked(True)

        elif choosen == "FMCW-RP-Hybrid":
            self.BCfg = dict(self.StdCfg)
            self.BCfg["fStrt"] = 76e9
            self.BCfg["fStop"] = 77e9
            self.BCfg["TRampUp"] = 20e-6
            self.BCfg["TRampDo"] = 1e-6
            self.BCfg["TInt"] = 0.05
            self.BCfg["Tp"] = 80e-6
            self.BCfg["N"] = 800
            self.BCfg["Np"] = 12
            self.BCfg["NrFrms"] = 1000

            self.TCfg = dict(self.BCfg)

            self.BFCfg = dict(self.SBCfg)
            self.BFCfg["RangeFFT"] = 4096
            self.BFCfg["AngFFT"] = 2048

            self.TBCfg = dict(self.BFCfg)

            self.NormBox.setValue(-200)
            self.CheckNorm.setChecked(False)

        else:
            self.errmsg(
                "NameError!", "No Presets found!\nPlease try again!", "c")
            return

        self.errmsg("Preset loaded!",
                    "Successfully loaded Preset: " + choosen, "i")
        self.PS_Wndw.close()

#---Beamforming config function---#
    def BMF_CFG(self):
        #-------Create a new Window-------#
        self.Bmf_Wndw = LockWindow()

#-------Create a list for all Entries-------#
        self.Bmf_Lst = QListWidget()
        self.Bmf_Lst.setFixedWidth(150)
#-------Add all editable options-------#
        Opts = ["RangeFFT", "AngFFT", "Abs", "Ext", 
                "ChnOrder", "NIni", "RemoveMean", "Window", "dB",
                r"_-view all-_"]
        self.Bmf_Vars = Opts.copy()
        self.Bmf_Vars.append("all")
        self.Bmf_Vars.append("clear")
        self.Bmf_Lst.addItems(Opts)
        self.Bmf_Lst.currentItemChanged.connect(self.BMF_CFG_UPDATE)

#-------Create a changeable title-------#
        self.Bmf_Ttl = QLabel("")
        self.Bmf_Ttl.setFixedHeight(50)
        self.Bmf_Ttl.setFont(QtGui.QFont("Times", 20, QtGui.QFont.Bold))

#-------Create a Button to save config-------#
        self.Bmf_Save = QPushButton("save...")
        self.Bmf_Save.setToolTip("save all set options!")
        self.Bmf_Save.clicked.connect(self.BMF_CFG_SAVE)

#-------Create a button to reset all Bmf-Configs-------#
        self.Bmf_Rst = QPushButton("Reset Config...")
        self.Bmf_Rst.setToolTip("Reset Beamforming-Config")
        self.Bmf_Rst.clicked.connect(self.BMF_CFG_RST)

#-------Create Variable-Display-------#
        self.Bmf_Var = QLabel("Variable-Display")

#-------Create original-value-display-------#
        self.Bmf_Orig = QLabel("Orig-Value-Display")

#-------Create a New-Value-Display with check-function-------#
        self.Bmf_New = QLineEdit()
        self.Bmf_New.setPlaceholderText("Enter new value here!")
        self.Bmf_New.textChanged.connect(self.BMF_CFG_CHCK)

#-------Create Pic-Display-------#
        self.Bmf_Pic = QLabel("Pic-Display")

#-------Create active live plot-------#
        self.BmfFig = figure.Figure()
        self.Bmf_Plt = FCA(self.BmfFig)
        self.Bmf_Plt.setFixedSize(480, 300)
        self.BmfFig.subplots_adjust(
            top=0.95, bottom=0.125, left=0.125, right=0.95)
        self.BP = self.BmfFig.add_subplot(111)

#-------Create Explain-Display-------#
        self.Bmf_Exp = QLabel("Explain-Display")

#-------Create Convert-Display-------#
        self.Bmf_Conv = QLabel("Convert-Display")

#-------set viewall Variables-------#
        self.BRFFT = False
        self.BAFFT = False
        self.BAbs  = False
        self.BExt  = False
        self.BRMi  = False
        self.BRMa  = False
        self.BChn  = False
        self.BNIni = False
        self.BRemM = False
        self.BWin  = False
        self.BdB   = False
        self.BFuSc = False

#-------Create a Layout and fill it up-------#
        self.Bmf_Layout = QGridLayout()
        self.Bmf_Layout.addWidget(self.Bmf_Lst, 0, 0, 5, 1, Qt.AlignLeft)
        self.Bmf_Layout.addWidget(self.Bmf_Ttl, 0, 1, 1, 4, Qt.AlignTop)
        self.Bmf_Layout.addWidget(self.Bmf_Var, 1, 1, 1, 1, Qt.AlignLeft)
        self.Bmf_Layout.addWidget(self.Bmf_Orig, 1, 2, 1, 1, Qt.AlignCenter)
        self.Bmf_Layout.addWidget(self.Bmf_New, 1, 3, 1, 1, Qt.AlignCenter)
        self.Bmf_Layout.addWidget(self.Bmf_Conv, 1, 4, 1, 1, Qt.AlignRight)
        self.Bmf_Layout.addWidget(self.Bmf_Plt, 2, 1, 1, 4, Qt.AlignCenter)
        # self.Bmf_Layout.addWidget(self.Bmf_Pic, 2, 1, 1, 4, Qt.AlignCenter)
        self.Bmf_Layout.addWidget(self.Bmf_Exp, 3, 1, 1, 4, Qt.AlignCenter)
        self.Bmf_Layout.addWidget(self.Bmf_Rst, 4, 1, 1, 1, Qt.AlignBottom)
        self.Bmf_Layout.addWidget(self.Bmf_Save, 4, 4, 1, 1, Qt.AlignBottom)

#-------set Window geometry etc.-------#
        self.Bmf_Wndw.setLayout(self.Bmf_Layout)
        self.Bmf_Wndw.resize(720, 640)
        self.Bmf_Wndw.setWindowTitle("Beamforming-Configuration")
        self.Bmf_Wndw.show()

#---Beamforming-Window-update-function---#
    def BMF_CFG_UPDATE(self):
        #-------get current item-------#
        showMe = self.Bmf_Lst.currentItem().text()

#-------check for Lock-------#
        if self.Lock:
            return

#-------clear Input-------#
        self.Bmf_New.clear()

#-------check what to display and show-------#
        if showMe == "RangeFFT":
            self.Bmf_Ttl.setText("RangeFFT - Range Fast Fourier Transform")
            self.Bmf_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SBCfg["RangeFFT"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [const]")
            self.Bmf_Conv.setText("No Convertion!")
            self.Bmf_Exp.setText("This variable defines the window in which the FFT is performed. This means it is only for calculation.\n"
                                 "Calculation works the fastest if this value is 2 by the power of n!\n"
                                 "Increasing this variable means increasing the resolution!")
            self.Bmf_New.setText(str(self.TBCfg["RangeFFT"]))

        elif showMe == "AngFFT":
            self.Bmf_Ttl.setText("AngFFT - Angle Fast Fourier Transform")
            self.Bmf_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SBCfg["AngFFT"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [const]")
            self.Bmf_Conv.setText("No Convertion!")
            self.Bmf_Exp.setText("This variable defines the window in which the FFT is performed. This means it is only for calculation.\n"
                                 "Calculation works the fastest if this value is 2 by the power of n!\n"
                                 "Increasing this variable means increasing the resolution!")
            self.Bmf_New.setText(str(self.TBCfg["AngFFT"]))

        elif showMe == "Abs":
            self.Bmf_Ttl.setText("Abs - Calculated Magnitude Spectrum")
            self.Bmf_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SBCfg["Abs"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [bool]")
            self.Bmf_Conv.setText("Converter: Ready!")
            self.Bmf_Exp.setText("Choose if the absolut values should be used or not!\n"
                                 "This means that the total diffrence is taken. e.g.: abs(6) = 6; abs(-6) = 6; abs(6-1j) = 6")
            self.Bmf_New.setText(str(self.TBCfg["Abs"]))

        elif showMe == "Ext":
            self.Bmf_Ttl.setText("Ext - Extract Range Interval")
            self.Bmf_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SBCfg["Ext"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [bool]")
            self.Bmf_Conv.setText("Converter: Ready")
            self.Bmf_Exp.setText(
                "Choose if you want to take RMin and RMax into account! If set to 0 no Range Interval will get extracted!")
            self.Bmf_New.setText(str(self.TBCfg["Ext"]))

        elif showMe == "RMin":
            self.Bmf_Ttl.setText("RMin - Range Minimum")
            self.Bmf_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SBCfg["RMin"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [m]")
            self.Bmf_Conv.setText("Converter: Ready!")
            self.Bmf_Exp.setText("Defines the minimum Range. Everything in front of this point will get ignored.\nUse this Variable to Scale the y-axis of the plot! "
                                 "This only works if Extract Range Interval is true! -> Ext: " + str(bool(self.TBCfg["Ext"])))
            self.Bmf_New.setText(str(self.TBCfg["RMin"]))

        elif showMe == "RMax":
            self.Bmf_Ttl.setText("RMax - Range Maximum")
            self.Bmf_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SBCfg["RMax"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [m]")
            self.Bmf_Conv.setText("Converter: Ready!")
            self.Bmf_Exp.setText("Defines the maximum Range. Everything behind this point will get ignored.\nUse this Variable to Scale the y-axis of the plot! "
                                 "This only works if Extract Range Interval is true! -> Ext: " + str(bool(self.TBCfg["Ext"])))
            self.Bmf_New.setText(str(self.TBCfg["RMax"]))

        elif showMe == "ChnOrder":
            self.Bmf_Ttl.setText("ChnOrder - Channel-Order")
            self.Bmf_Var.setText("Variable Name:\n"+showMe)
            original = str([7, 15, 23])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [array]")
            self.Bmf_Conv.setText("No Convertion!")
            self.Bmf_Exp.setText(
                "Enter the 3 Channels that should be deleted! Seperation works with ';'! -> 3;17;29")

        elif showMe == "NIni":
            self.Bmf_Ttl.setText("NIni - ignore samples")
            self.Bmf_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SBCfg["NIni"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [const]")
            self.Bmf_Conv.setText("No Conversion!")
            self.Bmf_Exp.setText("This is the number of samples that gets ignored when passing BeamformingUla a Measurement-Frame.\n"
                                 "Originally this value is 1 because the first line of a Measurement-Frame is allways the Channel!")
            self.Bmf_New.setText(str(self.TBCfg["NIni"]))

        elif showMe == "RemoveMean":
            self.Bmf_Ttl.setText("RemoveMean - Remove Mean from Data")
            self.Bmf_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SBCfg["RemoveMean"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [bool]")
            self.Bmf_Conv.setText("Converter: Ready!")
            self.Bmf_Exp.setText("Choose if mean values should be ignored or not! What this does is: get the mean values for all input signals.\n"
                                 "When done getting all values the original data is reduced by them.")
            self.Bmf_New.setText(str(self.TBCfg["RemoveMean"]))

        elif showMe == "Window":
            self.Bmf_Ttl.setText("Window - Lay Window over Data")
            self.Bmf_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SBCfg["Window"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [bool]")
            self.Bmf_Conv.setText("Converter: Read!")
            self.Bmf_Exp.setText("If true, lays a special cost-function over Data/DataShape! To be precise: the cost function consists of a 2D-Window\n"
                                 "which is a Hanning-Window. This means discontinuities at the beginning and end of a sampled signal will get smoothened.")
            self.Bmf_New.setText(str(self.TBCfg["Window"]))

        elif showMe == "dB":
            self.Bmf_Ttl.setText("dB - Returned Data-Scale")
            self.Bmf_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SBCfg["dB"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [bool]")
            self.Bmf_Conv.setText("Converter: Ready!")
            self.Bmf_Exp.setText("Choose between Raw Data and Data as dBV! The diffrence between Raw Data and dBV is the factor 20*log10!\n"
                                 "This means that 20*log10(RawData) = dBV")
            self.Bmf_New.setText(str(self.TBCfg["dB"]))

        elif showMe == "FuSca":
            self.Bmf_Ttl.setText("FuSca - FFT-Scaling-Constant")
            self.Bmf_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SBCfg["FuSca"])
            self.Bmf_Orig.setText("Original Value:\n"+original+" [const]")
            self.Bmf_Conv.setText("No Conversion!")
            self.Bmf_Exp.setText(
                "This is the Data-Scaling-value for post-FFT arrays. This Value is a constant and should not be changed!")
            self.Bmf_New.setText(str(self.TBCfg["FuSca"]))

        elif showMe == r"_-view all-_":
            self.Bmf_Ttl.setText("mixed View")
            self.Bmf_Var.setText("Variable Name:\nOverview")
            self.Bmf_Orig.setText("Original Value:\n-----")
            self.Bmf_Conv.setText("No Conversion!")
            self.Bmf_Exp.setText("Use the Input to add or remove effects! Just enter the Variable Name to toogle options!\n"
                                 "Use the Keywords 'all' and 'clear' to add all Variables or remove them!")

        else:
            self.errmsg("NameError!", "Item '" + showMe + "' not found!", "c")
            self.Bmf_Wndw.close()
            return

#-------show chosen options-------#
        self.Bmf_Wndw.show()

#---check input-function---#
    def BMF_CFG_CHCK(self):
        #-------get current item-------#
        showMe = self.Bmf_Lst.currentItem().text()

#-------get value after change-------#
        value = self.Bmf_New.text()

#-------check value and save&convert if possible-------#
        try:
            if float(value) >= 0:
                if showMe in [1, 2]:
                    new_value = str(float(value) * 1e-3)
                    self.Bmf_Conv.setText(
                        "Converted Value:\n"+new_value+" [km]")
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
                            self.TBCfg["FuSca"] = float(value)
                        else:
                            raise LookupError
                    elif showMe == "NIni":
                        if float(value) >= 0:
                            self.TBCfg["NIni"] = int(value)
                        else:
                            raise LookupError

                elif showMe in ["Abs", "Ext", "dB", "Window", "RemoveMean"]:
                    if float(value) == 0:
                        self.Bmf_Conv.setText(
                            "Converted Value:\nFalse! [bool]")
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

#-------except all possible Errors-------#
        except ValueError:
            if showMe == "ChnOrder":
                Channels = np.arange(32)
                try:
                    n = 0
                    lst = []
                    while n < len(value):
                        if value[n] != ";" and value[n] != " ":
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
                    if len(Chn) == 29:
                        print(Chn)
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
                        if len(Chn) == 29:
                            print(Chn)
                            self.TBCfg["ChnOrder"] = Chn
                    except ValueError:
                        pass

        except LookupError:
            self.Lock = True
            global lock
            lock = self. Lock
            self.Bmf_New.setStyleSheet(
                "border: 3px solid red; background: yellow; color: red")
            self.Bmf_Conv.setText("invalid Value!")
            self.Bmf_Save.setEnabled(False)
            return

        self.Lock = False
        lock = self.Lock
        self.Bmf_New.setStyleSheet(self.origStyleSheet)
        self.Bmf_Save.setEnabled(True)

#-------plot any variable-info--------#
        try:
            self.BP.clear()
            if self.cbar:
                self.bar.remove()
                self.cbar = False

            N = int(self.TCfg["N"])
            fqS = int(self.TCfg["fStrt"])
            fqs = int(self.TCfg["fStop"])
            tU = self.TCfg["TRampUp"]
            R = int(self.TBCfg["RangeFFT"])
            A = int(self.TBCfg["AngFFT"])
            Abs = int(self.TBCfg["Abs"])
            Ext = int(self.TBCfg["Ext"])
            RMa = int(self.TBCfg["RMax"])
            RMi = int(self.TBCfg["RMin"])
            NIni = int(self.TBCfg["NIni"])
            RemM = int(self.TBCfg["RemoveMean"])
            W = int(self.TBCfg["Window"])
            dB = int(self.TBCfg["dB"])
            CO = self.TBCfg["ChnOrder"]
            FS = .25/4096
            CalData = self.CD

            if showMe in ["RangeFFT", "AngFFT"]:
                Rline = np.ones((R, A))
                Nline = np.zeros((N, 32))
                P1 = int((R-N)/2)
                P2 = int((A-32)/2)
                Rline[P1:P1+N, P2:P2+32] = Nline
                im = self.BP.imshow(Rline, origin="lower", aspect="auto")
                self.BP.set_ylabel("samples")
                self.BP.set_xlabel("Channels")
                self.bar = self.BmfFig.colorbar(im, ax=self.BP, ticks=[0, 1])
                self.bar.ax.set_yticklabels(["Raw Data", "FFT Data"])
                self.cbar = True

            if showMe == "Abs":
                ims = self.Bcsv.copy()
                if Abs:
                    ims = abs(ims)
                im = self.BP.imshow(ims, origin="lower", aspect="auto")
                self.BP.set_ylabel("samples/rows of Data-Array")
                self.BP.set_xlabel("Channels/cols of Data-Array")
                self.bar = self.BmfFig.colorbar(im, ax=self.BP)
                self.cbar = True

            if showMe in ["Ext", "RMax", "RMin"]:
                out = np.zeros((RMa+5, 32))
                if Ext:
                    ins = np.ones((RMa-RMi, 32))
                    out[RMi:RMa, :] = ins
                self.BP.imshow(out, origin="lower", aspect="auto")
                self.BP.set_ylabel("Range [m]")
                self.BP.set_xlabel("Channels")

            if showMe == "NIni":
                frame = np.zeros((NIni+25, 32))
                for row in range(NIni+25):
                    frame[row, :] = row
                frame[:NIni, :] = np.amax(frame) + 5
                self.BP.imshow(frame, aspect="auto")
                self.BP.set_ylabel("samples/rows of Data-Array")
                self.BP.set_xlabel("Channels/cols of Data-Array")

            if showMe == "RemoveMean":
                data = self.Bcsv.copy()
                if RemM:
                    mean = np.mean(data, axis=0)
                    mdata = np.tile(mean, (503, 1))
                    data = data - mdata
                im = self.BP.imshow(data, origin="lower", aspect="auto")
                self.BP.set_ylabel("samples/rows of Data-Array")
                self.BP.set_xlabel("Channels/cols of Data-Array")
                self.bar = self.BmfFig.colorbar(im, ax=self.BP)
                self.cbar = True

            if showMe == "Window":
                data = self.Bcsv.copy()
                if W:
                    Win = np.hanning(503)
                    Win2D = np.tile(Win, (32, 1))
                    Win2D = Win2D.transpose()
                    data = data*Win2D
                im = self.BP.imshow(data, origin="lower", aspect="auto")
                self.BP.set_ylabel("samples/rows of Data-Array")
                self.BP.set_xlabel("Channels/cols of Data-Array")
                self.bar = self.BmfFig.colorbar(im, ax=self.BP)
                self.cbar = True

            if showMe == "dB":
                data = self.Bcsv.copy()
                data = abs(data)
                if dB:
                    data = 20*np.log10(data)
                self.BP.imshow(data, origin="lower", aspect="auto")
                self.BP.set_ylabel("samples/rows of Data-Array")
                self.BP.set_xlabel("Channels/cols of Data-Array")

            if showMe in ["ChnOrder", "FuSca"]:
                data = self.Bcsv.copy()
                tray = np.zeros((R, 32))
                P1 = int((R-503)/2)
                tray[P1:P1+503,:] = data
                tray = np.fft.fftshift(tray, axes=0)
                tray = np.fft.fft(tray, R, 0)
                tray = tray/503*FS
                tray = tray[0:int(R/2),:]
                Chn = tray[:,CO]
                Ny = Chn.shape[0]
                Nx = Chn.shape[1]
                CalChn = CalData[CO]
                Win = np.hanning(Nx)
                Scale = sum(Win)
                Win = Win*CalChn
                Win2D = np.tile(Win, (Ny, 1))
                Chn = Win2D*Chn
                jOpt        =   np.zeros((Ny, A), dtype = 'complex_')
                StrtIdx     =   int((A - Nx)/2)
                jOpt[:,StrtIdx:StrtIdx + Nx]    =   Chn
                JOpt        =   np.fft.fft(jOpt, A, 1)/Scale
                JOpt        =   np.fft.fftshift(JOpt, axes = (1))
                JOpt        =   abs(JOpt)
                self.BP.imshow(JOpt, origin="lower", aspect="auto")
                self.BP.set_ylabel("samples after RangeFFT")
                self.BP.set_xlabel("Channels after AngFFT")

            if showMe == r"_-view all-_":
                toogle = str(value)
                if toogle in self.Bmf_Vars:
                    self.Bmf_New.clear()
                    if toogle == "RangeFFT":
                        if self.BRFFT:
                            self.BRFFT = False
                        else:
                            self.BRFFT = True
                    elif toogle == "AngFFT":
                        if self.BAFFT:
                            self.BAFFT = False
                        else:
                            self.BAFFT = True
                    elif toogle == "Abs":
                        if self.BAbs:
                            self.BAbs = False
                        else:
                            self.BAbs = True
                    elif toogle == "Ext":
                        if self.BExt:
                            self.BExt = False
                        else:
                            self.BExt = True
                    elif toogle == "RMin":
                        if self.BRMi:
                            self.BRMi = False
                        else:
                            self.BRMi = True
                    elif toogle == "RMax":
                        if self.BRMa:
                            self.BRMa = False
                        else:
                            self.BRMa = True
                    elif toogle == "ChnOrder":
                        if self.BChn:
                            self.BChn = False
                        else:
                            self.BChn = True
                    elif toogle == "NIni":
                        if self.BNIni:
                            self.BNini = False
                        else:
                            self.BNIni = True
                    elif toogle == "RemoveMean":
                        if self.BRemM:
                            self.BRemM = False
                        else:
                            self.BRemM = True
                    elif toogle == "Window":
                        if self.BWin:
                            self.BWin = False
                        else:
                            self.BWin = True
                    elif toogle == "dB":
                        if self.BdB:
                            self.BdB = False
                        else:
                            self.BdB = True
                    elif toogle == "FuSca":
                        if self.BFuSc:
                            self.BFuSc = False
                        else:
                            self.BFuSc = True
                    elif toogle == "clear":
                        self.BRFFT = False
                        self.BAFFT = False
                        self.BAbs  = False
                        self.BExt  = False
                        self.BRMi  = False
                        self.BRMa  = False
                        self.BChn  = False
                        self.BNIni = False
                        self.BRemM = False
                        self.BWin  = False
                        self.BdB   = False
                        self.BFuSc = False
                    elif toogle == "all":
                        self.BRFFT = True
                        self.BAFFT = True
                        self.BAbs  = True
                        self.BExt  = True
                        self.BRMi  = True
                        self.BRMa  = True
                        self.BChn  = True
                        self.BNIni = True
                        self.BRemM = True
                        self.BWin  = True
                        self.BdB   = True
                        self.BFuSc = True
                    else:
                        self.Bmf_New.setStyleSheet("border: 1px solid red")
                        return
                    self.Bmf_New.setStyleSheet(self.origStyleSheet)

                data = np.array(self.Bcsv.copy())
                if self.BNIni:
                    data = data[NIni:, :]
                Ny = data.shape[0]
                Nx = data.shape[1]
                if self.BRemM:
                    mean = np.mean(data, axis=0)
                    mean = np.tile(mean, (Ny, 1))
                    data = data-mean
                if self.BWin:
                    Win = np.hanning(Ny)
                    Scale = sum(Win)
                    Win2D = np.tile(Win, (Nx, 1))
                    Win2D = Win2D.transpose()
                    data = data*Win2D
                else:
                    Scale = Ny
                if self.BRFFT:
                    cntnr = np.zeros((R, Nx))
                    Strt = int((R-Ny)/2)
                    cntnr[Strt:Strt+Ny, :] = data
                    data = np.fft.fftshift(cntnr, axes=0)
                    data = np.fft.fft(data, R, 0)/Scale*FS
                    data = data[0:int(R/2), :]
                if self.BExt:
                    if self.connected:
                        fsa = self.Board.Get("fs")
                        kf = self.Board.RfGet("kf")
                    else:
                        fsa = 1/(tU/N)
                        kf = (fqs-fqS)/tU
                    fR = np.arange(int(R/2))/R*fsa
                    Range = (fR*self.c0)/(2*kf)
                    Idmin = np.argmin(abs(Range-RMi))
                    Idmax = np.argmin(abs(Range-RMa))
                    data = data[Idmin:Idmax, :]
                XChn = data[:, CO]
                CalChn = CalData[CO]
                if self.BAFFT:
                    Ny = XChn.shape[0]
                    Nx = XChn.shape[1]
                    Win = np.hanning(Nx)
                    Scale = sum(Win)
                    Win = Win*CalChn
                    Win2D = np.tile(Win, (Ny, 1))
                    XChn = XChn*Win2D
                    cntnr = np.zeros((Ny, A), dtype="complex_")
                    Strt = int((A-Nx)/2)
                    cntnr[:,Strt:Strt+Nx] = XChn
                    XChn = np.fft.fft(cntnr, A, 1)/Scale
                    XChn = np.fft.fftshift(XChn, axes=1)
                if self.BAbs:
                    XChn = abs(XChn)
                    if self.BdB:
                        XChn = 20*np.log10(XChn)

                if self.cbar:
                    self.bar.remove()
                    self.cbar = False
                im = self.BP.imshow(XChn, origin="lower", aspect="auto")
                self.BP.set_ylabel("samples")
                self.BP.set_xlabel("Channels")
                self.bar = self.BmfFig.colorbar(im, ax=self.BP)
                self.cbar = True

            self.Bmf_Plt.draw()

        except:
            pass

#---save Beamforming-Config-function---#
    def BMF_CFG_SAVE(self):
        #-------safety-question-------#
        Qstn = self.errmsg(
            "Set Config?", "Are you sure you want to set new Config?\nIf some variables are not set right plotting may not work!", "q")

#-------check answer-------#
        if Qstn == 0:
            cont = True
        else:
            cont = False

#-------continue if answer is yes, else abort-------#
        if cont:
            self.BFCfg = dict(self.TBCfg)
            self.errmsg("Confirmed!", "Config saved successfully!", "i")
            self.Bmf_Wndw.close()
        else:
            self.errmsg(
                "Config not set!", "The User-Config is not set, but still saved in the Window!", "i")

#---Reset Config-Function---#
    def BMF_CFG_RST(self):
        #-------safety-question-------#
        Qstn = self.errmsg(
            "Are you sure?", "If you reset the BeamForming-Config, everything except the standard-Config is lost!\nContinue anyways?", "q")

#-------check answer-------#
        if Qstn == 0:
            cont = True
        else:
            cont = False

#-------continue or abort-------#
        if cont:
            self.BFCfg = dict(self.SBCfg)
            self.TBCfg = dict(self.BFCfg)
            self.errmsg("Confirmed!", "All Configs have been reset!", "i")
        else:
            self.errmsg("Config not reset!",
                        "The Beamforming-Config has not been reset!", "i")

#---RangeDoppler-Config-Function---#
    def RD_CFG(self):
        #-------Create a new Window-------#
        self.RD_Wndw = LockWindow()

#-------Create a List with all changeable config-variables-------#
        self.RD_Lst = QListWidget()
        self.RD_Lst.setFixedWidth(150)

#-------Add names to list-------#
        Opts = ["RangeFFT", "VelFFT", "Abs", "Ext", 
                "RemoveMean", "Window", "dB", "NIni", "_-view all-_"]
        self.RD_Vars = Opts.copy()
        self.RD_Vars.append("all")
        self.RD_Vars.append("clear")
        self.RD_Lst.addItems(Opts)
        self.RD_Lst.currentItemChanged.connect(self.RD_CFG_UPDATE)

#-------Create Title-------#
        self.RD_Ttl = QLabel("")
        self.RD_Ttl.setFixedHeight(50)
        self.RD_Ttl.setFont(QtGui.QFont("Times", 20, QtGui.QFont.Bold))

#-------create a save-Button-------#
        self.RD_Save = QPushButton("save...")
        self.RD_Save.setToolTip("save all set options!")
        self.RD_Save.clicked.connect(self.RD_CFG_SAVE)

#-------create a reset-Button-------#
        self.RD_Rst = QPushButton("Reset Config...")
        self.RD_Rst.setToolTip("Reset RangeDoppler-Config")
        self.RD_Rst.clicked.connect(self.RD_CFG_RST)

#-------create Variabel-Display-------#
        self.RD_Var = QLabel("Variabel-Display")

#-------create original-value-Display-------#
        self.RD_Orig = QLabel("Orig-Value-Display")

#-------create New-Value_Display with check-function-------#
        self.RD_New = QLineEdit()
        self.RD_New.setPlaceholderText("Enter new value here!")
        self.RD_New.textChanged.connect(self.RD_CFG_CHCK)

#-------create Pic-Display-------#
        self.RD_Pic = QLabel("Pic-Display")

#-------create RD-plot-------#
        self.RDFig = figure.Figure()
        self.RD_Plt = FCA(self.RDFig)
        self.RD_Plt.setFixedSize(480, 300)
        self.RDFig.subplots_adjust(
            top=0.95, bottom=0.125, left=0.125, right=0.95)
        self.DP = self.RDFig.add_subplot(111)

#-------create a explain-display-------#
        self.RD_Exp = QLabel("Explain-Display")

#-------create a Convert-Display-------#
        self.RD_Conv = QLabel("Convert-Display")

#-------set viewall Variables-------#
        self.RDRFFT = False
        self.RDVFFT = False
        self.RDAbs  = False
        self.RDExt  = False
        self.RDRMi  = False
        self.RDRMa  = False
        self.RDNIni = False
        self.RDRemM = False
        self.RDWin  = False
        self.RDdB   = False
        self.RDFuSc = False

#-------create a Layout to fill up-------#
        self.RD_Layout = QGridLayout()
        self.RD_Layout.addWidget(self.RD_Lst, 0, 0, 5, 1, Qt.AlignLeft)
        self.RD_Layout.addWidget(self.RD_Ttl, 0, 1, 1, 4, Qt.AlignTop)
        self.RD_Layout.addWidget(self.RD_Var, 1, 1, 1, 1, Qt.AlignLeft)
        self.RD_Layout.addWidget(self.RD_Orig, 1, 2, 1, 1, Qt.AlignCenter)
        self.RD_Layout.addWidget(self.RD_New, 1, 3, 1, 1, Qt.AlignCenter)
        self.RD_Layout.addWidget(self.RD_Conv, 1, 4, 1, 1, Qt.AlignRight)
        # self.RD_Layout.addWidget(self.RD_Pic, 2, 1, 1, 4, Qt.AlignCenter)
        self.RD_Layout.addWidget(self.RD_Plt, 2, 1, 1, 4, Qt.AlignCenter)
        self.RD_Layout.addWidget(self.RD_Exp, 3, 1, 1, 4, Qt.AlignCenter)
        self.RD_Layout.addWidget(self.RD_Rst, 4, 1, 1, 1, Qt.AlignBottom)
        self.RD_Layout.addWidget(self.RD_Save, 4, 4, 1, 1, Qt.AlignBottom)

#-------set Window geometry etc.-------#
        self.RD_Wndw.setLayout(self.RD_Layout)
        self.RD_Wndw.resize(720, 640)
        self.RD_Wndw.setWindowTitle("RangeDoppler-Configuration")
        self.RD_Wndw.show()

#---RangeDopplerConfigWindow-Update-function---#
    def RD_CFG_UPDATE(self):
        #-------get current item-------#
        showMe = self.RD_Lst.currentItem().text()

#-------check for lock-------#
        if self.Lock:
            return

#-------clear input-------#
        self.RD_New.clear()

#-------check what to display and show-------#
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
            self.RD_Exp.setText("Choose if mean values should be ignored or not! What this does is: get the mean values for all input signals.\n"
                                "When done getting all values the original data is reduced by them.")
            self.RD_New.setText(str(self.TRCfg["RemoveMean"]))

        elif showMe == "Abs":
            self.RD_Ttl.setText("Abs - Calculated Magnitude Spectrum")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["Abs"])
            self.RD_Orig.setText("Original Value:\n" + original + " [bool]")
            self.RD_Conv.setText("Converter: Ready!")
            self.RD_Exp.setText("Choose if the absolut values should be used or not!\n"
                                "This means that the total diffrence is taken. e.g.: abs(6) = 6; abs(-6) = 6")
            self.RD_New.setText(str(self.TRCfg["Abs"]))

        elif showMe == "Ext":
            self.RD_Ttl.setText("Ext - Extract Range Interval")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["Ext"])
            self.RD_Orig.setText("Original Value:\n" + original + " [bool]")
            self.RD_Conv.setText("Converter: Ready!")
            self.RD_Exp.setText(
                "Choose if you want to take RMin and RMax into account! If set to 0 no Range Interval will get extracted!")
            self.RD_New.setText(str(self.TRCfg["Ext"]))

        elif showMe == "RMin":
            self.RD_Ttl.setText("RMin - Range Minimum")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["RMin"])
            self.RD_Orig.setText("Original Value:\n" + original + " [m]")
            self.RD_Conv.setText("Converter: Ready!")
            self.RD_Exp.setText("Defines the minimum Range. Everything in front of this point will get ignored.\nUse this Variable to Scale the y-axis of the plot! "
                                "This only works if Extract Range Interval is true! -> Ext: " + str(bool(self.TRCfg["Ext"])))
            self.RD_New.setText(str(self.TRCfg["RMin"]))

        elif showMe == "RMax":
            self.RD_Ttl.setText("RMax - Range Maximum")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["RMax"])
            self.RD_Orig.setText("Original Name:\n" + original + " [m]")
            self.RD_Conv.setText("Converter: Ready!")
            self.RD_Exp.setText("Defines the maximum Range. Everything behind this point will get ignored.\nUse this Variable to Scale the y-axis of the plot! "
                                "This only works if Extract Range Interval is true! -> Ext: " + str(bool(self.TRCfg["Ext"])))
            self.RD_New.setText(str(self.TRCfg["RMax"]))

        elif showMe == "N":
            self.RD_Ttl.setText("N samples - like Board-Config")
            self.RD_Ttl.setText("Variable Name:\n" + showMe)
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
            self.RD_Exp.setText("If true, lays a special cost-function over Data/DataShape! To be precise: the cost function consists of a 2D-Window\n"
                                "which is a Hanning-Window. This means discontinuities at the beginning and end of a sampled signal will get smoothened.")
            self.RD_New.setText(str(self.TRCfg["Window"]))

        elif showMe == "dB":
            self.RD_Ttl.setText("dB - Returned Data-Scale")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["dB"])
            self.RD_Orig.setText("Original Value:\n"+original+" [bool]")
            self.RD_Conv.setText("Converter: Ready!")
            self.RD_Exp.setText("Choose between Raw Data and Data as dBV! The diffrence between Raw Data and dBV is the factor 20*log10!\n"
                                "This means that 20*log10(RawData) = dBV")
            self.RD_New.setText(str(self.TRCfg["dB"]))

        elif showMe == "FuSca":
            self.RD_Ttl.setText("FuSca - FFT-Scaling-Constant")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["FuSca"])
            self.RD_Orig.setText("Original Value:\n"+original+" [const]")
            self.RD_Conv.setText("No Conversion!")
            self.RD_Exp.setText(
                "This is the Data-Scaling-value for post-FFT arrays. This Value is a constant and should not be changed!")
            self.RD_New.setText(str(self.TRCfg["FuSca"]))

        elif showMe == "fc":
            self.RD_Ttl.setText("fc - Frequency Centered")
            self.RD_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SRCfg["fc"])
            self.RD_Orig.setText("Original Value:\n"+original+" [Hz]")
            self.RD_Conv.setText("Converter: Ready!")
            self.RD_Exp.setText(
                "This variable describes the middle of fStrt and fStop!")
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
            self.RD_Exp.setText(
                "array with the threshold values of a Data-array -> Scaled values to dBV!")
            self.RD_New.setText(str(self.TRCfg["ThresdB"]))

        elif showMe == "NIni":
            self.RD_Ttl.setText("NIni - ignore samples")
            self.RD_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SRCfg["NIni"])
            self.RD_Orig.setText("Original Value:\n"+original+" [samples]")
            self.RD_Conv.setText("No Conversion!")
            self.RD_Exp.setText("This is the number of samples that gets ignored when passing RangeDoppler a Measurement-Frame.\n"
                                "Originally this value is 1 because the first line of a Measurement-Frame is allways the Channel!")
            self.RD_New.setText(str(self.TRCfg["NIni"]))

        elif showMe == "_-view all-_":
            self.RD_Ttl.setText("mixed View")
            self.RD_Var.setText("Variable Name:\nOverview")
            self.RD_Orig.setText("Original Value:\n-----")
            self.RD_Conv.setText("No Conversion!")
            self.RD_Exp.setText("Use the Input to add or remove effects! Just enter the Variable Name to toogle options!\n"
                                "Use the Keywords 'all' and 'clear' to add all Variables or remove them!")

        else:
            self.errmsg("NameError!", "Item '" + showMe + "' not found!", "c")
            self.RD_Wndw.close()
            return

#-------show chosen option-------#
        self.RD_Wndw.show()

#---RangeDopplerConfigInput-check-function---#
    def RD_CFG_CHCK(self):
        #-------get current Item-------#
        showMe = self.RD_Lst.currentItem().text()

#-------get value after change-------#
        value = self.RD_New.text()

#-------check value and save&convert if possible-------#
        try:
            if float(value) >= 0:
                if showMe in ["RMax", "RMin"]:
                    new_value = str(float(value) * 10e-3)
                    self.RD_Conv.setText(
                        "Converted Value:\n" + new_value + " [km]")
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

                elif showMe in ["Abs", "Ext", "RemoveMean", "Window", "dB"]:
                    if float(value) == 0:
                        new_value = "False!"
                    elif float(value) == 1:
                        new_value = "True!"
                    else:
                        raise LookupError
                    self.RD_Conv.setText(
                        "Converted Value:\n" + new_value + " [bool]")
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

                elif showMe in ["RangeFFT", "VelFFT", "FuSca", "N", "Np", "NIni"]:
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
                    elif showMe == "NIni":
                        if float(value) >= 0:
                            self.TRCfg["NIni"] = float(value)
                        else:
                            raise LookupError

                elif showMe == "fc":
                    if float(value) > 70e9:
                        self.RD_Conv.setText(
                            "Converted Value:\n" + str(float(value)*1e-9) + " [GHz]")
                        self.TRCfg["fc"] = float(value)
                    else:
                        raise LookupError

                elif showMe == "Tp":
                    if float(value) > 0:
                        self.RD_Conv.setText(
                            "Converted Value:\n" + str(float(value)*1e6) + " [µs]")
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
            self.RD_New.setStyleSheet(
                "border: 3px solid red; background: yellow; color: red")
            self.RD_Conv.setText("Invalid Value!")
            self.RD_Save.setEnabled(False)
            return

        self.Lock = False
        lock = self.Lock
        self.RD_New.setStyleSheet(self.origStyleSheet)
        self.RD_Save.setEnabled(True)

        try:
            self.DP.clear()
            if self.cbar:
                self.bar.remove()
                self.cbar = False

            R = int(self.TRCfg["RangeFFT"])
            V = int(self.TRCfg["VelFFT"])
            Abs = int(self.TRCfg["Abs"])
            Ext = int(self.TRCfg["Ext"])
            RMi = int(self.TRCfg["RMin"])
            RMa = int(self.TRCfg["RMax"])
            ReM = int(self.TRCfg["RemoveMean"])
            Win = int(self.TRCfg["Window"])
            dB = int(self.TRCfg["dB"])
            FS = .25/4096
            NIni = int(self.TRCfg["NIni"])
            Np = int(self.TCfg["Np"])
            N = int(self.TCfg["N"])
            tU = self.TCfg["TRampUp"]

            if showMe in ["RangeFFT", "VelFFT"]:
                out = np.ones((R, V))
                ins = np.zeros((Np, N))
                ins = ins.transpose()
                P1 = int((R-N)/2)
                P2 = int((V-Np)/2)
                out[P1:P1+N, P2:P2+Np] = ins
                im = self.DP.imshow(out, origin="lower", aspect="auto")
                self.DP.set_ylabel("samples")
                self.DP.set_xlabel("chirps")
                self.bar = self.RDFig.colorbar(im, ax=self.DP, ticks=[0, 1])
                self.bar.ax.set_yticklabels(["Raw Data", "FFT Data"])
                self.cbar = True

            if showMe == "Abs":
                data = np.array(self.RDcsv)
                data = data.reshape((32, 128))
                data = data.transpose()
                if Abs:
                    data = abs(data)
                im = self.DP.imshow(data, origin="lower", aspect="auto")
                self.DP.set_ylabel("samples")
                self.DP.set_xlabel("chirps")
                self.bar = self.RDFig.colorbar(im, ax=self.DP)
                self.cbar = True

            if showMe in ["Ext", "RMin", "RMax"]:
                out = np.zeros((RMa+5, 32))
                if Ext:
                    ins = np.ones((RMa-RMi, 32))
                    out[RMi:RMa, :] = ins
                self.DP.imshow(out, origin="lower", aspect="auto")
                self.DP.set_ylabel("Range [m]")
                self.DP.set_xlabel("chirps")

            if showMe == "RemoveMean":
                data = np.array(self.RDcsv)
                data = data.reshape((32, 128))
                data = data.transpose()
                data = data[NIni:, :]
                if ReM:
                    mean = np.mean(data, axis=1)
                    mean = np.tile(mean, (32, 1))
                    data = data - mean.transpose()
                im = self.DP.imshow(data, origin="lower", aspect="auto")
                self.DP.set_ylabel("samples")
                self.DP.set_xlabel("chirps")
                self.bar = self.RDFig.colorbar(im, ax=self.DP)
                self.cbar = True

            if showMe == "Window":
                data = np.array(self.RDcsv)
                data = data.reshape((32, 128))
                data = data.transpose()
                Ny = data.shape[0]
                Nx = data.shape[1]
                if Win:
                    W = np.hanning(Ny)
                    Win2D = np.tile(W, (Nx, 1))
                    Win2D = Win2D.transpose()
                    data = data*Win2D
                im = self.DP.imshow(data, origin="lower", aspect="auto")
                self.DP.set_ylabel("samples")
                self.DP.set_xlabel("chirps")
                self.bar = self.RDFig.colorbar(im, ax=self.DP)
                self.cbar = True

            if showMe == "dB":
                data = np.array(self.RDcsv)
                data = data.reshape((32, 128))
                data = data.transpose()
                data = abs(data)
                if dB:
                    data = 20*np.log10(data)
                im = self.DP.imshow(data, aspect="auto")
                self.DP.set_ylabel("samples")
                self.DP.set_xlabel("chirps")
                self.bar = self.RDFig.colorbar(im, ax=self.DP)
                self.cbar = True

            if showMe == "NIni":
                data = np.array(self.RDcsv)
                data = data.reshape((32, 128))
                data = data.transpose()
                data[:NIni, :] = np.amax(data) + 10
                im = self.DP.imshow(data, origin="lower", aspect="auto")
                self.DP.set_ylabel("samples")
                self.DP.set_xlabel("chirps")
                self.bar = self.RDFig.colorbar(im, ax=self.DP)
                self.cbar=True

            if showMe == "FuSca":
                data = np.array(self.RDcsv)
                data = data.reshape((32, 128))
                data = data.transpose()
                cntnr = np.zeros((R, 32))
                P1 = int((R-128)/2)
                cntnr[P1:P1+128, :] = data
                data = np.fft.fft(cntnr, R, 0)/128*FS
                data = data[0:int(R/2), :]
                data = abs(data)
                im = self.DP.imshow(data, origin="lower", aspect="auto")
                self.DP.set_ylabel("samples after RangeFFT")
                self.DP.set_xlabel("chirps")
                self.bar = self.RDFig.colorbar(im, ax=self.DP)
                self.cbar = True

            if showMe == "_-view all-_":
                toogle = str(value)
                if toogle in self.RD_Vars:
                    self.RD_New.clear()
                    if toogle == "RangeFFT":
                        if self.RDRFFT:
                            self.RDRFFT = False
                        else:
                            self.RDRFFT = True
                    elif toogle == "VelFFT":
                        if self.RDVFFT:
                            self.RDCFFT = False
                        else:
                            self.RDVFFT = True
                    elif toogle == "Abs":
                        if self.RDAbs:
                            self.RDAbs = False
                        else:
                            self.RDAbs = True
                    elif toogle == "Ext":
                        if self.RDExt:
                            self.RDExt = False
                        else:
                            self.RDExt = True
                    elif toogle == "RemoveMean":
                        if self.RDRemM:
                            self.RDRemM = False
                        else:
                            self.RDRemM = True
                    elif toogle == "Window":
                        if self.RDWin:
                            self.RDWin = False
                        else:
                            self.RDWin = True
                    elif toogle == "dB":
                        if self.RDdB:
                            self.RDdB = False
                        else:
                            self.RDdB = True
                    elif toogle == "NIni":
                        if self.RDNIni:
                            self.RDNIni = False
                        else:
                            self.RDNIni = True
                    elif toogle == "clear":
                        self.RDRFFT = False
                        self.RDVFFT = False
                        self.RDAbs  = False
                        self.RDExt  = False
                        self.RDRemM = False
                        self.RDWin  = False
                        self.RDdB   = False
                        self.RDNIni = False
                    elif toogle == "all":
                        self.RDRFFT = True
                        self.RDVFFT = True
                        self.RDAbs  = True
                        self.RDExt  = True
                        self.RDRemM = True
                        self.RDWin  = True
                        self.RDdB   = True
                        self.RDNIni = True
                    else:
                        self.RD_New.setStyleSheet("border: 1px solid red")
                        return
                    self.RD_New.setStyleSheet(self.origStyleSheet)

                data = np.array(self.RDcsv)
                data = data.reshape(32, 128)
                data = data.transpose()
                if self.RDNIni:
                    data = data[NIni:, :]
                Ny = data.shape[0]
                Nx = data.shape[1]
                if self.RDRemM:
                    mean = np.mean(data, axis=1)
                    mean = np.tile(mean, (Nx, 1))
                    mean = mean.transpose()
                    data = data-mean
                if self.RDWin:
                    W = np.hanning(Ny)
                    Scale = sum(W)
                    Win2D = np.tile(W, (Nx, 1))
                    Win2D = Win2D.transpose()
                    data = data*Win2D
                else:
                    Scale = Ny
                if self.RDRFFT:
                    cntnr = np.zeros((R, Nx))
                    P1 = int((R-Ny)/2)
                    cntnr[P1:P1+Ny, :] = data
                    data = np.fft.fft(cntnr, R, 0)/Scale*FS
                    data = data[0:int(R/2), :]
                if self.RDExt:
                    if self.connected:
                        fsa = self.Board.Get("fs")
                        kf = self.Board.RfGet("kf")
                    else:
                        fsa = 1/(tU/N)
                        kf = (self.TCfg["fStop"]-self.TCfg["fStrt"])/self.TCfg["TRampUp"]
                    fR = (np.arange(int(R/2)))/R*fsa
                    Range = (fR*self.c0)/(2*kf)
                    Idmin = np.argmin(abs(Range-RMi))
                    Idmax = np.argmin(abs(Range-RMa))
                    data = data[Idmin:Idmax, :]
                if self.RDVFFT:
                    Ny = data.shape[0]
                    Nx = data.shape[1]
                    Win = np.hanning(Nx)
                    Scale = sum(Win)
                    Win2D = np.tile(Win, (Ny, 1))
                    cntnr = np.zeros((Ny, V), dtype="complex_")
                    P1 = int((V-Nx)/2)
                    cntnr[:, P1:P1+Nx] = data
                    data = np.fft.fft(cntnr, V, 1)/Scale
                    data = np.fft.fftshift(data, axes=1)
                if self.RDAbs:
                    data = abs(data)
                    if self.RDdB:
                        data = 20*np.log10(data)
                if self.cbar:
                    self.bar.remove()
                    self.cbar=False
                im = self.DP.imshow(data, origin="lower", aspect="auto")
                self.DP.set_ylabel("samples")
                self.DP.set_xlabel("chirps")
                self.bar = self.RDFig.colorbar(im, ax=self.DP)
                self.cbar=True

            self.RD_Plt.draw()

        except:
            pass

#---RangeDopplerConfig-save-function---#
    def RD_CFG_SAVE(self):
        #-------safetyquestion-------#
        Qstn = self.errmsg(
            "Set Config?", "Are you sure that you want to set a new Config?\nIf some variables are not set right plotting may not work!", "q")

#-------check answer-------#
        if Qstn == 0:
            cont = True
        else:
            cont = False

#-------continue if yes, abort if no-------#
        if cont:
            self.RDCfg = dict(self.TRCfg)
            self.errmsg("Confirmed!", "Config set successfully!", "i")
            self.RD_Wndw.close()
        else:
            self.errmsg(
                "Config not set!", "The User-Config is not set, but still temporarly saved in the Window!", "i")

#---RangeDopplerConfig-reset-function---#
    def RD_CFG_RST(self):
        #-------safetyquestion-------#
        Qstn = self.errmsg(
            "Are you sure?", "If you reset the RangeDoppler-Config everything except the Standard-Config is lost!\nContinue anyways?", "q")

#-------check answer-------#
        if Qstn == 0:
            cont = True
        else:
            cont = False

#-------continue or abort-------#
        if cont:
            self.RDCfg = dict(self.SRCfg)
            self.TRCfg = dict(self.RDCfg)
            self.errmsg(
                "Confirmed!", "RangeDoppler-Config has been reset!", "i")
        else:
            self.errmsg("Config not reset!",
                        "The RangeDoppler-Config has not been reset!", "i")

#---RangeProfile-Config-Window---#
    def RP_CFG(self):
        #-------Create a new Window-------#
        self.RP_Wndw = LockWindow()

#-------create a List with all changeable config-variables-------#
        self.RP_Lst = QListWidget()
        self.RP_Lst.setFixedWidth(150)

#-------add names to listwidget-------#
        Opts = ["NFFT", "Abs", "Ext", 
                "RemoveMean", "Window", "XPos", "dB", "NIni",
                "_-view all-_"]
        self.RP_Lst.addItems(Opts)
        self.RP_Vars = Opts.copy()
        self.RP_Vars.append("clear")
        self.RP_Vars.append("all")
        self.RP_Lst.currentItemChanged.connect(self.RP_CFG_UPDATE)

#-------create Titel-------#
        self.RP_Ttl = QLabel("")
        self.RP_Ttl.setFixedHeight(50)
        self.RP_Ttl.setFont(QtGui.QFont("Times", 20, QtGui.QFont.Bold))

#-------create a button to save config-------#
        self.RP_Save = QPushButton("save...")
        self.RP_Save.setToolTip("save all set options!")
        self.RP_Save.clicked.connect(self.RP_CFG_SAVE)

#-------create a button to reset all RangeProfile-Configs-------#
        self.RP_Rst = QPushButton("Reset Config...")
        self.RP_Rst.setToolTip("reset RangeProfile-Config!")
        self.RP_Rst.clicked.connect(self.RP_CFG_RST)

#-------create Variabel-Display-------#
        self.RP_Var = QLabel("Variable-Display")

#-------create original-Value-Display-------#
        self.RP_Orig = QLabel("Orig-Value-Display")

#-------New-Value-Display-------#
        self.RP_New = QLineEdit()
        self.RP_New.setPlaceholderText("Enter new value here!")
        self.RP_New.textChanged.connect(self.RP_CFG_CHCK)

#-------create Pic-Display-------#
        self.RP_Pic = QLabel("Pic-Display")

#-------create RP-plot-------#
        self.RPFig = figure.Figure()
        self.RP_Plt = FCA(self.RPFig)
        self.RP_Plt.setFixedSize(480, 300)
        self.RPFig.subplots_adjust(
            top=0.95, bottom=0.15, left=0.15, right=0.90)
        self.RP = self.RPFig.add_subplot(111)

#-------create Explain-Display-------#
        self.RP_Exp = QLabel("Explain-Display")

#-------create Converter-Display-------#
        self.RP_Conv = QLabel("Converter-Dislpay")

#-------assign plot variables------#
        self.RPFFT = False
        self.RPAbs  = False
        self.RPExt  = False
        self.RPRemM = False
        self.RPWin  = False
        self.RPdB   = False
        self.RPNIni = False

#-------create a Layout and fill it up-------#
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
        # self.RP_Layout.addWidget(self.RP_Pic, 2, 1, 1, 4, c)
        self.RP_Layout.addWidget(self.RP_Plt, 2, 1, 1, 4, c)
        self.RP_Layout.addWidget(self.RP_Exp, 3, 1, 1, 4, c)
        self.RP_Layout.addWidget(self.RP_Rst, 4, 1, 1, 1, b)
        self.RP_Layout.addWidget(self.RP_Save, 4, 4, 1, 1, b)

#-------set Windowgeometry etc.-------#
        self.RP_Wndw.setLayout(self.RP_Layout)
        self.RP_Wndw.resize(720, 640)
        self.RP_Wndw.setWindowTitle("RangeProfile-Configuration")
        self.RP_Wndw.show()

#---RangeDoppler-Config-Update-function---#
    def RP_CFG_UPDATE(self):
        #-------get current item-------#
        showMe = self.RP_Lst.currentItem().text()

#-------check for Lock-------#
        if self.Lock:
            return

#-------clear Input-------#
        self.RP_New.clear()

#-------check what to display and show-------#
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
            self.RP_Exp.setText("Choose if the absolut values should be used or not!\n"
                                "This means that the total diffrence is taken. e.g.: abs(6) = 6; abs(-6) = 6")
            self.RP_New.setText(str(self.TPCfg["Abs"]))

        elif showMe == "Ext":
            self.RP_Ttl.setText("Ext - Extract Range Interval")
            self.RP_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SPCfg["Ext"])
            self.RP_Orig.setText("Original Value:\n"+original+" [bool]")
            self.RP_Conv.setText("Converter: Ready!")
            self.RP_Exp.setText(
                "Choose if you want to take RMin and RMax into account! If set to 0 no Range Interval will get extracted!")
            self.RP_New.setText(str(self.TPCfg["Ext"]))

        elif showMe == "RMin":
            self.RP_Ttl.setText("RMin - Range Minimum")
            self.RP_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SPCfg["RMin"])
            self.RP_Orig.setText("Original Value:\n"+original+" [m]")
            self.RP_Conv.setText("Converter: Ready!")
            self.RP_Exp.setText("Defines the minimum Range. Everything in front of this point will get ignored.\nUse this Variable to Scale the y-axis of the plot! "
                                "This only works if Extract Range Interval is true! -> Ext: " + str(bool(self.TPCfg["Ext"])))
            self.RP_New.setText(str(self.TPCfg["RMin"]))

        elif showMe == "RMax":
            self.RP_Ttl.setText("RMax - Range Maximum")
            self.RP_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SPCfg["RMax"])
            self.RP_Orig.setText("Original Value:\n"+original+" [m]")
            self.RP_Conv.setText("Converter: Ready!")
            self.RP_Exp.setText("Defines the maximum Range. Everything behind this point will get ignored.\nUse this Variable to Scale the y-axis of the plot! "
                                "This only works if Extract Range Interval is true! -> Ext: " + str(bool(self.TPCfg["Ext"])))
            self.RP_New.setText(str(self.TPCfg["RMax"]))

        elif showMe == "RemoveMean":
            self.RP_Ttl.setText("RemoveMean - Remove Mean Values")
            self.RP_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SPCfg["RemoveMean"])
            self.RP_Orig.setText("Original Value:\n"+original+" [bool]")
            self.RP_Conv.setText("Converter: Ready!")
            self.RP_Exp.setText("Choose if mean values should be ignored or not! What this does is: get the mean values for all input signals.\n"
                                "When done getting all values the original data is reduced by them.")
            self.RP_New.setText(str(self.TPCfg["RemoveMean"]))

        elif showMe == "Window":
            self.RP_Ttl.setText("Window - Lay Window over Data")
            self.RP_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SPCfg["Window"])
            self.RP_Orig.setText("Original Value:\n"+original+" [bool]")
            self.RP_Conv.setText("Converter: Ready!")
            self.RP_Exp.setText("If true, lays a special cost-function over Data/DataShape! To be precise: the cost function consists of a 2D-Window\n"
                                "which is a Hanning-Window. This means discontinuities at the beginning and end of a sampled signal will get smoothened.")
            self.RP_New.setText(str(self.TPCfg["Window"]))

        elif showMe == "XPos":
            self.RP_Ttl.setText("XPos - only positive RangeProfile")
            self.RP_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SPCfg["XPos"])
            self.RP_Orig.setText("Original Value:\n"+original+" [bool]")
            self.RP_Conv.setText("Converter: Ready!")
            self.RP_Exp.setText("If true, only takes positive RangeProfileValues! The RangeProfileFFT-calculation\nexpands the passed MeasurementData "
                                "in both positive and negative Range.")
            self.RP_New.setText(str(self.TPCfg["XPos"]))

        elif showMe == "dB":
            self.RP_Ttl.setText("dB - Returned Data-Scale")
            self.RP_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SPCfg["dB"])
            self.RP_Orig.setText("Original Value:\n"+original+" [bool]")
            self.RP_Conv.setText("Converter: Ready!")
            self.RP_Exp.setText("Choose between Raw Data and Data as dBV! The diffrence between Raw Data and dBV is the factor 20*log10!\n"
                                "This means that 20*log10(RawData) = dBV")
            self.RP_New.setText(str(self.TPCfg["dB"]))

        elif showMe == "FuSca":
            self.RP_Ttl.setText("FuSca - FFT-Scaling-Constant")
            self.RP_Var.setText("Variable Name:\n" + showMe)
            original = str(self.SPCfg["FuSca"])
            self.RP_Orig.setText("Original Value:\n"+original+" [const]")
            self.RP_Conv.setText("No Conversion!")
            self.RP_Exp.setText(
                "This is the Data-Scaling-value for post-FFT arrays. This Value is a constant and should not be changed!")
            self.RP_New.setText(str(self.TPCfg["FuSca"]))

        elif showMe == "NIni":
            self.RP_Ttl.setText("NIni - ignore samples")
            self.RP_Var.setText("Variable Name:\n"+showMe)
            original = str(self.SPCfg["NIni"])
            self.RP_Orig.setText("Original Value:\n"+original+" [samples]")
            self.RP_Conv.setText("No Conversion!")
            self.RP_Exp.setText("This is the number of samples that gets ignored when passing RangeProfile a Measurement-Frame.\n"
                                "Originally this value is 1 because the first line of a Measurement-Frame is allways the Channel!")
            self.RP_New.setText(str(self.TPCfg["NIni"]))

        elif showMe == "_-view all-_":
            self.RP_Ttl.setText("mixed view")
            self.RP_Var.setText("Variable Name:\nOverview")
            self.RP_Orig.setText("Original Value:\n-----")
            self.RP_Conv.setText("No Conversion")
            self.RP_Exp.setText("Use the Input to add or remove effects! Just enter the Variable Name to toogle options!\n"
                                "Use the Keywords 'all' and 'clear' to add all Variables or remove them!")

        else:
            self.errmsg("NameError!", "Item '" + showMe + "' not found!", "c")
            self.RP_Wndw.close()
            return

#-------show chosen option-------#
        self.RP_Wndw.show()

#---check-input-function---#
    def RP_CFG_CHCK(self):
        #-------get current Item-------#
        showMe = self.RP_Lst.currentItem().text()

#-------get value-------#
        value = self.RP_New.text()

#-------check and save&convert if possible-------#
        try:
            if float(value) >= 0:
                if showMe in ["RMin", "RMax"]:
                    new_value = str(float(value) * 1e-3)
                    self.RP_Conv.setText(
                        "Converted Value:\n" + new_value + " [km]")
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
                    elif showMe == "XPos":
                        self.TPCfg["XPos"] = float(value)
                    elif showMe == "dB":
                        self.TPCfg["dB"] = float(value)
                    else:
                        raise LookupError

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

                elif showMe == "NIni":
                    if int(value) in range(0, int(self.BCfg["N"])):
                        self.TPCfg["NIni"] = int(value)
                    else:
                        raise LookupError

                else:
                    raise ValueError
            else:
                raise ValueError

#-------except all Erros-------#
        except ValueError:
            pass

        except LookupError:
            self.Lock = True
            global lock
            lock = self.Lock
            self.RP_New.setStyleSheet(
                "border: 3px solid red; background: yellow; color: red")
            self.RP_Conv.setText("invalid Value!")
            self.RP_Save.setEnabled(False)
            return

        self.Lock = False
        lock = self.Lock
        self.RP_New.setStyleSheet(self.origStyleSheet)
        self.RP_Save.setEnabled(True)

        try:
            self.RP.clear()

            F = int(self.TPCfg["NFFT"])
            FS = .25/4096
            data = self.RPcsv
            Abs = int(self.TPCfg["Abs"])
            Ext = int(self.TPCfg["Ext"])
            RMi = self.TPCfg["RMin"]
            RMa = self.TPCfg["RMax"]
            ReM = int(self.TPCfg["RemoveMean"])
            W = int(self.TPCfg["Window"])
            XPs = int(self.TPCfg["XPos"])
            dB = int(self.TPCfg["dB"])
            NI = int(self.TPCfg["NIni"])
            tU = self.TCfg["TRampUp"]
            N  = self.TCfg["N"]

            if showMe in ["NFFT", "FuSca"]:
                data = np.array(data)
                # data1 = np.mean(data, axis=1)
                Ny = data.shape[0]
                Nx = data.shape[1]
                cntnr = np.zeros((F, Nx), dtype="complex_")
                P1 = int((F-Ny)/2)
                cntnr[P1:P1+Ny, :] = data
                data = np.fft.fftshift(cntnr, axes=0)
                data = np.fft.fft(data, F, 0)/Ny*FS
                data = abs(data)
                data = np.mean(data, axis=1)
                self.RP.plot(data, c="blue", label="FFT-Data")
                self.RP.set_ylabel("Received Values")
                self.RP.set_xlabel("samples")
                # self.RP.plot(data1, c="cyan", label="Raw-Data")

            elif showMe == "Abs":
                data = np.array(data)
                if Abs:
                    data = abs(data)
                data = np.mean(data, axis=1)
                self.RP.plot(data)
                self.RP.set_ylabel("Received Values")
                self.RP.set_xlabel("samples")

            elif showMe in ["Ext", "RMin", "RMax"]:
                data = np.array(data)
                Ny = data.shape[0]
                Nx = data.shape[1]
                cntnr = np.zeros((F, Nx), dtype="complex_")
                P1 = int((F-Ny)/2)
                cntnr[P1:P1+Ny, :] = data
                data = np.fft.fftshift(cntnr, axes=0)
                data = np.fft.fft(data, F, 0)/Ny*FS
                if Ext:
                    if self.connected:
                        try:
                            fsa = self.Board.Get("fs")
                            kf = self.Board.RfGet("kf")
                        except ZeroDivisionError:
                            kf = (self.TCfg["fStop"] - self.TCfg["fStrt"])/self.TCfg["TRampUp"]
                    else:
                        fsa = 1/(tU/N)
                        kf = (self.TCfg["fStop"] - self.TCfg["fStrt"])/self.TCfg["TRampUp"]
                    if XPs:
                        fR = np.arange(int(F/2))/F*fsa
                    else:
                        fR = np.arange(F)/F*fsa
                    Ra = fR*self.c0/(2*kf)
                    Idmin = np.argmin(abs(Ra-RMi))
                    Idmax = np.argmin(abs(Ra-RMa))
                    data = data[Idmin:Idmax, :]
                data = abs(data)
                data = np.mean(data, axis=1)
                self.RP.plot(data)
                self.RP.set_ylabel("Received Values")
                self.RP.set_xlabel("samples")

            elif showMe == "RemoveMean":
                data = np.array(data)
                if ReM:
                    Ny = data.shape[0]
                    mean = np.mean(data, axis=0)
                    mean = np.tile(mean, (Ny, 1))
                    data = data-mean
                data = np.mean(data, axis=1)
                self.RP.plot(data)
                self.RP.set_ylabel("Received Values")
                self.RP.set_xlabel("samples")

            elif showMe == "Window":
                data = np.array(data)
                if W:
                    Ny = data.shape[0]
                    Nx = data.shape[1]
                    Win = np.hanning(Ny)
                    Win2D = np.tile(Win, (Nx, 1))
                    Win2D = Win2D.transpose()
                    data = data*Win2D
                data = np.mean(data, axis=1)
                self.RP.plot(data)
                self.RP.set_ylabel("Received Values")
                self.RP.set_xlabel("samples")

            elif showMe == "XPos":
                data = np.array(data)
                Ny = data.shape[0]
                Nx = data.shape[1]
                cntnr = np.zeros((F, Nx), dtype="complex_")
                P1 = int((F-Ny)/2)
                cntnr[P1:P1+Ny, :] = data
                data = np.fft.fftshift(cntnr, axes=0)
                data = np.fft.fft(data, F, 0)/Ny*FS
                if XPs:
                    data = data[0:int(F/2), :]
                data = abs(data)
                data = np.mean(data, axis=1)
                self.RP.plot(data)
                self.RP.set_ylabel("Received Values")
                self.RP.set_xlabel("samples")

            elif showMe == "dB":
                data = np.array(data)
                if dB:
                    data = abs(data)
                    data = 20*np.log10(data)
                data = np.mean(data, axis=1)
                self.RP.plot(data)
                self.RP.set_ylabel("dBV")
                self.RP.set_xlabel("samples")

            elif showMe == "NIni":
                data = np.array(data)
                data = data[NI:, :]
                data = np.mean(data, axis=1)
                self.RP.plot(data)
                self.RP.set_ylabel("Received Values")
                self.RP.set_xlabel("samples")

            if showMe == "_-view all-_":
                toogle = str(value)
                if toogle in self.RP_Vars:
                    self.RP_New.clear()
                    if toogle == "NFFT":
                        if self.RPFFT:
                            self.RPFFT = False
                        else:
                            self.RPFFT = True
                    elif toogle == "Abs":
                        if self.RPAbs:
                            self.RPAbs = False
                        else:
                            self.RPAbs = True
                    elif toogle == "Ext":
                        if self.RPExt:
                            self.RPExt = False
                        else:
                            self.RPExt = True
                    elif toogle == "RemoveMean":
                        if self.RPRemM:
                            self.RPRemM = False
                        else:
                            self.RPRemM = True
                    elif toogle == "Window":
                        if self.RPWin:
                            self.RPWin = False
                        else:
                            self.RPWin = True
                    elif toogle == "dB":
                        if self.RPdB:
                            self.RPdB = False
                        else:
                            self.RPdB = True
                    elif toogle == "NIni":
                        if self.RPNIni:
                            self.RPNIni = False
                        else:
                            self.RPNIni = True
                    elif toogle == "clear":
                        self.RPFFT = False
                        self.RPAbs  = False
                        self.RPExt  = False
                        self.RPRemM = False
                        self.RPWin  = False
                        self.RPdB   = False
                        self.RPNIni = False
                    elif toogle == "all":
                        self.RPFFT = True
                        self.RPAbs  = True
                        self.RPExt  = True
                        self.RPRemM = True
                        self.RPWin  = True
                        self.RPdB   = True
                        self.RPNIni = True
                    else:
                        self.RP_New.setStyleSheet("border: 1px solid red")
                        return
                    self.RP_New.setStyleSheet(self.origStyleSheet)

                data= np.array(self.RPcsv)
                if self.RPNIni:
                    data = data[NI:, :]
                Ny = data.shape[0]
                Nx = data.shape[1]
                if self.RPRemM:
                    mean = np.mean(data, axis=0)
                    mean = np.tile(mean, (Ny, 1))
                    data = data-mean
                if self.RPWin:
                    Win = np.hanning(Ny)
                    Scale = sum(Win)
                    Win2D = np.tile(Win, (Nx, 1))
                    Win2D = Win2D.transpose()
                    data = data*Win2D
                else:
                    Scale = Ny
                if self.RPFFT:
                    cntnr = np.zeros((F, Nx), dtype="complex_")
                    P1 = int((F-Ny)/2)
                    cntnr[P1:P1+Ny, :] = data
                    data = np.fft.fftshift(cntnr, axes=0)
                    data = np.fft.fft(data, F, 0)/Scale*FS
                    data = data[0:int(F/2), :]
                if self.RPAbs:
                    data = abs(data)
                    if self.RPdB:
                        data = 20*np.log10(data)
                if self.RPExt:
                    if self.connected:
                        fsa = self.Board.Get("fs")
                        kf = self.Board.RfGet("kf")
                    else:
                        fsa = 1/(tU/N)
                        kf = (self.TCfg["fStop"] - self.TCfg["fStrt"])/self.TCfg["TRampUp"]
                    if XPs:
                        fR = np.arange(int(F/2))/F*fsa
                    else:
                        fR = np.arange(F)/F*fsa
                    Ra = fR*self.c0/(2*kf)
                    Idmin = np.argmin(abs(Ra-RMi))
                    Idmax = np.argmin(abs(Ra-RMa))
                    data = data[Idmin:Idmax, :]
                data = np.mean(data, axis=1)
                self.RP.plot(data)
                if self.RPAbs:
                    if self.RPdB:
                        self.RP.set_ylabel("dBV")
                else:
                    self.RP.set_ylabel("Received Value")
                self.RP.set_xlabel("samples")

            self.RP_Plt.draw()

        except:
            pass

#---save RangeProfile-Config---#
    def RP_CFG_SAVE(self):
        #-------safetyquestion-------#
        Qstn = self.errmsg(
            "Set Config?", "Are you sure you want to set new Config?\nIf some variables are not set right plotting may not work!", "q")

#-------check answer-------#
        if Qstn == 0:
            cont = True
        else:
            cont = False

#-------continue or abort-------#
        if cont:
            self.RPCfg = dict(self.TPCfg)
            self.errmsg("Confirmed!", "Config set successfully!", "i")
            self.RP_Wndw.close()
        else:
            self.errmsg(
                "Config not set!", "The User-defined-Config is not set, but still saved in the Window!", "i")

#---reset RangeProfile-Config---#
    def RP_CFG_RST(self):
        #-------safetyquestion-------#
        Qstn = self.errmsg(
            "Reset Config?", "If you reset the RangeProfile-Config, everything except the standard-Config is lost!\nContinue anyways?", "q")

#-------check answer-------#
        if Qstn == 0:
            cont = True
        else:
            cont = False

#-------continue or abort-------#
        if cont:
            self.RPCfg = dict(self.SPCfg)
            self.TPCfg = dict(self.RPCfg)
            self.errmsg("Confirmed!", "All Configs have been reset!", "i")
        else:
            self.errmsg("Config not reset!",
                        "The RangeDoppler-Config has not been reset!", "i")

#---get-Video-function---#
    def VIDEO(self):
        #-------create a Window-------#
        self.name_Wndw = QWidget()
#-------get Userinput-------#
        self.name_str = QLineEdit()
        self.name_str.setPlaceholderText(
            "for example: 210308_shir_act_FBs014-EPTa")
#-------create Title-------#
        self.name_Ttl = QLabel("Enter VideoName without fileEnding here: ")
#-------create a button-------#
        self.name_btn = QPushButton("ok...")
        self.name_btn.setToolTip("create video")
        self.name_btn.clicked.connect(self.VIDEO_CREATE)
#-------create videoformatoption-------#
        self.name_gif = QRadioButton(".gif")
        self.name_mp4 = QRadioButton(".mp4")
#-------create a Layout and fill it-------#
        self.name_Lay = QGridLayout()
        self.name_Lay.addWidget(self.name_Ttl, 0, 0, 1, 2)
        self.name_Lay.addWidget(self.name_str, 1, 0, 1, 2)
        self.name_Lay.addWidget(self.name_gif, 2, 0, 1, 1)
        self.name_Lay.addWidget(self.name_mp4, 2, 1, 1, 1)
        self.name_Lay.addWidget(self.name_btn, 3, 1, 1, 1)
#-------set Window attributes-------#
        self.name_Wndw.setLayout(self.name_Lay)
        self.name_Wndw.setWindowTitle("get Measurment as Video...")
        self.name_Wndw.resize(256, 128)
        self.name_Wndw.show()

#---create-Video-function---#
    def VIDEO_CREATE(self):
        #-------close Window-------#
        self.name_Wndw.close()
        try:
            #-----------check input-----------#
            self.videoname = self.name_str.text()
            if len(self.videoname) < 1:
                raise NameError

            self.saveplace = QFileDialog.getExistingDirectory()

            self.savefull = self.saveplace + "/" + self.videoname

            if self.name_gif.isChecked():
                self.savefull = self.savefull + ".gif"
            elif self.name_mp4.isChecked():
                self.savefull = self.savefull + ".mp4"
            else:
                raise TypeError

            images = []
            for image in glob.glob("vc/*.png"):
                images.append(imageio.imread(image))
            imageio.mimsave(self.savefull, images)

            self.errmsg("Video created!", "Creation of Video succesfull!", "i")

            for image in glob.glob("vc/*.png"):
                os.remove(image)

        except NameError:
            self.errmsg(
                "NameError!", "Please try again and enter a valid Name!", "w")
            self.VIDEO()
            return

        except IndexError:
            self.errmsg(
                "IndexError!", "VideoCache is empty!\nStart a new Measurement and try again!", "c")
            return

        except TypeError:
            self.errmsg("TypeError!", "Please select a Videoformat!", "w")
            self.VIDEO()
            return

#---get Data function---#
    def DATA(self):
        #-------create a Window-------#
        self.data_Wndw = QWidget()
#-------get User Input-------#
        self.data_str = QLineEdit()
        self.data_str.setPlaceholderText(
            "for example: 210308_shir_act_FBl011-C2V75")
#-------get Title-------#
        self.data_Ttl = QLabel("Enter a fileName without fileEnding here:")
#-------create a button-------#
        self.data_btn = QPushButton("ok...")
        self.data_btn.setToolTip("create a file with data")
        self.data_btn.clicked.connect(self.DATA_CREATE)
#-------create a Layout and fill it-------#
        self.data_Lay = QGridLayout()
        self.data_Lay.addWidget(self.data_Ttl, 0, 0, 1, 2)
        self.data_Lay.addWidget(self.data_str, 1, 0, 1, 2)
        self.data_Lay.addWidget(self.data_btn, 2, 1, 1, 1)
#-------set Window attributes-------#
        self.data_Wndw.setLayout(self.data_Lay)
        self.data_Wndw.setWindowTitle("get Measurement as Dataframe...")
        self.data_Wndw.resize(256, 128)
        self.data_Wndw.show()

#---create Data-function---#
    def DATA_CREATE(self):
        #-------close Window-------#
        self.data_Wndw.close()
        try:
            #-----------check input-----------#
            self.dataname = self.data_str.text()
            if len(self.dataname) < 1:
                raise NameError

            DF = pd.DataFrame(self.AllData)

            self.saveplace = QFileDialog.getExistingDirectory()

            self.savefull = self.saveplace + "/" + self.dataname + ".csv"

            DF.to_csv(self.savefull, sep=";", decimal=",")

            self.errmsg("Data exported!",
                        "Data export to .csv successful!", "i")

        except NameError:
            self.errmsg(
                "NameError!", "Please try again and enter a valid Name!", "w")
            self.DATA()

        except AttributeError:
            self.errmsg(
                "AttributeError!", "There is no data that could be exported!\nPlease start measurement and try again!", "c")

#---report-function---#
    def REPORT(self):
        #-------get saveplace-------#
        saveplace = QFileDialog.getExistingDirectory()
#-------check saveplace-------#
        try:
            if saveplace == "":
                raise NotADirectoryError
#-----------create base savename-----------#
            savename = ttime.strftime("rep_%Y%m%d_%H-%M-%S_RadartoolReport")
#-----------create saveplace link-----------#
            saveplace = saveplace + "/" + savename
#-----------check saveplace existence-----------#
            if not os.path.exists(saveplace):
                os.makedirs(saveplace)
#-----------create saveplace links-----------#
            datasave = saveplace + "/" + savename + ".csv"
            vidsave = saveplace + "/" + savename + ".gif"
            cfgsave = saveplace + "/" + savename + ".config"
#-----------create DataFrame-----------#
            DF = pd.DataFrame(self.AllData)
            DF.to_csv(datasave, sep=";", decimal=",")
#-----------create video-----------#
            images = []
            try:
                for image in glob.glob("vc/*.png"):
                    images.append(imageio.imread(image))
                imageio.mimsave(vidsave, images)
            except:
                self.errmsg("ImageError!", "Could not create gif/.mp4!", "w")
#-----------create saveconfig-----------#
            to_save = {"Board": self.BCfg,
                       "Beam": self.BFCfg,
                       "RangeDoppler": self.RDCfg,
                       "RangeProfile": self.RPCfg}
            if self.FMCW:
                to_save["Mode"] = "FMCW"
            elif self.RD:
                to_save["Mode"] = "RD"
            elif self.RP:
                to_save["Mode"] = "RP"
            else:
                to_save["Mode"] = "RCS"

            if self.CheckNorm.isChecked():
                to_save["Norm"] = 1
                to_save["NVal"] = self.NormBox.value()
            else:
                to_save["Norm"] = 0
                to_save["NVal"] = -200

            DF = pd.DataFrame(index=range(int(self.MaxTab.rowCount())))
            DF["Measurement/timedelta"] = "None"
            DF["SequenceRepeat"] = "None"
            DF["max. dBV"] = "None"
            for col in range(int(self.MaxTab.columnCount())):
                for row in range(int(self.MaxTab.rowCount())):
                    DF.iat[row, col] = self.MaxTab.itemAt(col, row).text()
            to_save["MaxTab"] = DF

            file = open(cfgsave, "w")
            file.write(jsonpickle.dumps(to_save))
            file.close()
#-----------succesmessage-----------#
            self.errmsg("Success!", "Succesfully created report!", "i")

#-------except Errors-------#
        except NotADirectoryError:
            Qstn = self.errmsg("NotADirectoryError!",
                               "Directory not valid! Try again?", "q")
            if Qstn == 0:
                self.REPORT()
            else:
                return

#---reload Report csv function---#
    def REPORT_REPCSV(self):
        #-------control center------#
        if self.rep_rep == 0:
            self.Rep_Ctrl = QWidget()
            self.Rep_Ctrl_Ttl = QLabel("Simulation Controlcenter")
            self.Rep_Ctrl_Ttl.setFont(QtGui.QFont("Times", 12))
            self.Rep_Ctrl_rep = QPushButton("repeat...")
            self.Rep_Ctrl_rep.setToolTip("restart the simulation")
            self.Rep_Ctrl_rep.clicked.connect(self.REPORT_REPCSV_REP)
            self.Rep_Ctrl_ps = QPushButton("stop....")
            self.Rep_Ctrl_ps.setToolTip("Pause Simulation")
            self.Rep_Ctrl_ps.clicked.connect(self.REPORT_REPCSV_STP)
            self.Rep_Ctrl_spdl = QLabel("Pause [s]:")
            self.Rep_Ctrl_spd = QDoubleSpinBox()
            self.Rep_Ctrl_spd.setRange(0.0, 2.0)
            self.Rep_Ctrl_spd.setSingleStep(0.1)
            self.Rep_Ctrl_qt = QPushButton("quit Simulation")
            self.Rep_Ctrl_qt.setToolTip(
                "quit the Simulation and hide Controlcenter")
            self.Rep_Ctrl_qt.clicked.connect(self.REPORT_REPCSV_QUIT)
            self.Rep_Ctrl_Lay = QGridLayout()
            self.Rep_Ctrl_Lay.addWidget(self.Rep_Ctrl_Ttl, 0, 0, 1, 2)
            self.Rep_Ctrl_Lay.addWidget(self.Rep_Ctrl_rep, 1, 0, 1, 1)
            self.Rep_Ctrl_Lay.addWidget(self.Rep_Ctrl_ps, 1, 1, 1, 1)
            self.Rep_Ctrl_Lay.addWidget(self.Rep_Ctrl_spdl, 2, 0, 1, 1)
            self.Rep_Ctrl_Lay.addWidget(self.Rep_Ctrl_spd, 2, 1, 1, 1)
            self.Rep_Ctrl_Lay.addWidget(self.Rep_Ctrl_qt, 3, 0, 1, 2)
            self.Rep_Ctrl.setLayout(self.Rep_Ctrl_Lay)
            self.MWLayout.addWidget(self.Rep_Ctrl, 11, 0, 1, 2)
            self.ccc = self.MWLayout.count() - 1

#-----------clear figure------------#
            self.FGR_CLR()
#-----------get report-----------#
            Qstn = self.errmsg(
                "Report?", "Do you want to select a report (select a folder)?", "q")
            if Qstn == 0:
                report = QFileDialog.getExistingDirectory()
            else:
                filename = QFileDialog.getOpenFileName()[0]
                report = 0
#-----------check report-----------#
            if report == "":
                Qstn = self.errmsg("NotADirectoryError!",
                                   "Path to Report not valid!\nTry again?", "q")
                if Qstn == 0:
                    self.REPORT_REPCSV()
                else:
                    self.REPORT_REPCSV_QUIT()
                    return
#---------------get config---------------#
            if report == 0:
                configpath = filename[:-3] + "config"
            else:
                configpath = report + "/" + report[-37:] + ".config"
            try:
                file = open(configpath, "r")
            except FileNotFoundError:
                self.errmsg("FileNotFoundError!", "Did not find the recommended .config file next to "
                            "the .csv!\nMake sure both files are next to each other and try again!",
                            "c")
                self.REPORT_REPCSV_QUIT()
                return
            from_save = jsonpickle.loads(file.read())
            self.BCfg = dict(from_save["Board"])
            self.BFCfg = dict(from_save["Beam"])
            self.RDCfg = dict(from_save["RangeDoppler"])
            self.RPCfg = dict(from_save["RangeProfile"])
            self.mode = from_save["Mode"]
            self.Norm = from_save["Norm"]
            if self.Norm:
                self.CheckNorm.setChecked(True)
            self.NVal = from_save["NVal"]
            self.NormBox.setValue(self.NVal)
#-----------get measurementdata-----------#
            if report == 0:
                datapath = filename
            else:
                datapath = report + "/" + report[-37:] + ".csv"
            self.MeasData = pd.read_csv(datapath, sep=";", decimal=",")
            self.MeasData = np.array(self.MeasData)
#-----------create plot-----------#
            self.plt = self.figure.add_subplot(111)
#-----------simulate measurement-----------#
            self.Proc = RadarProc.RadarProc()
        if self.mode == "FMCW":
            self.Proc.CfgBeamformingUla(self.BFCfg)
            self.PData = np.zeros((int(self.BCfg["N"]), int(32)))
            self.JRan = self.Proc.GetBeamformingUla("Range")
            lRan = len(self.JRan)
            self.ARan = np.zeros(lRan)
            self.ARan[:lRan] = self.JRan
            self.ARan[-1] = np.ediff1d(self.JRan)[-1] + self.JRan[-1]
            self.JAng = self.Proc.GetBeamformingUla("AngFreqNorm")
            lAng = len(self.JAng)
            self.JAng = np.arange(int(lAng/2)*-1, int(lAng/2))
            self.AAng = np.zeros(lAng)
            self.AAng[:lAng] = self.JAng
            self.AAng[-1] = np.ediff1d(self.JAng)[-1] + self.JAng[-1]
            self.MaxTab.clearContents()
            self.MaxTab.setRowCount(1)
            self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                0, QTableWidgetItem("FMCW"))
            self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                1, QTableWidgetItem(str(self.BCfg["NrFrms"])))
            self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                2, QTableWidgetItem("<-- total"))
            start = ttime.time()
            for MeasIdx in range(int(self.BCfg["NrFrms"])):
                Data = self.MeasData[:, MeasIdx*8:(MeasIdx+1)*8]
                Id = Data[1, 0]
                if Id == 1:
                    self.PData[2:, 0:8] = Data[2:, :]
                    self.plt.clear()
                if Id == 2:
                    self.PData[2:, 8:16] = Data[2:, :]
                if Id == 3:
                    self.PData[2:, 16:24] = Data[2:, :]
                if Id == 4:
                    self.PData[2:, 24:32] = Data[2:, :]
                    self.JOpt = self.Proc.BeamformingUla(self.PData)
                    JMax = np.amax(self.JOpt)
                    delta = ttime.time() - start
                    self.MaxTab.setRowCount(self.MaxTab.rowCount() + 1)
                    self.MaxTab.setItem(
                        (self.MaxTab.rowCount()-1), 0, QTableWidgetItem(str(delta)[:-3]))
                    self.MaxTab.setItem(
                        (self.MaxTab.rowCount()-1), 1, QTableWidgetItem(str(MeasIdx)))
                    self.MaxTab.setItem(
                        (self.MaxTab.rowCount()-1), 2, QTableWidgetItem(str(JMax)))
                    if self.Norm:
                        self.JNorm = self.JOpt - JMax
                        self.JNorm[self.JNorm < self.NVal] = self.NVal
                    else:
                        self.JNorm = self.JOpt
                    self.plt.pcolormesh(
                        self.AAng, self.ARan, self.JNorm, shading="auto")
                    self.plt.set_xlabel("Angle [deg]")
                    self.plt.set_ylabel("Range [m]")
                    self.plt.set_ylim(self.BFCfg["RMin"], self.BFCfg["RMax"])
                    self.canvas.draw()
                    if self.endloop:
                        break
                    QApplication.processEvents()
                    ttime.sleep(self.Rep_Ctrl_spd.value())

        if self.mode == "RD":
            self.Proc.CfgRangeDoppler(self.RDCfg)
            self.JRan = self.Proc.GetRangeDoppler("Range")
            lRan = len(self.JRan)
            self.ARan = np.zeros(lRan)
            self.ARan[:lRan] = self.JRan
            self.ARan[-1] = np.ediff1d(self.JRan)[-1] + self.JRan[-1]
            self.JVel = self.Proc.GetRangeDoppler("Vel")
            lVel = len(self.JVel)
            self.AVel = np.zeros(lVel)
            self.AVel[:lVel] = self.JVel
            self.AVel[-1] = np.ediff1d(self.JVel)[-1] + self.JVel[-1]
            self.MaxTab.clearContents()
            self.MaxTab.setRowCount(1)
            self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                0, QTableWidgetItem("RangeDoppler"))
            self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                1, QTableWidgetItem(str(self.BCfg["NrFrms"])))
            self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                2, QTableWidgetItem("<-- total"))
            start = ttime.time()
            for MeasIdx in range(int(self.BCfg["NrFrms"])):
                Data = self.MeasData[:, MeasIdx]
                RD = self.Proc.RangeDoppler(Data)
                RDMax = np.amax(RD)
                delta = ttime.time() - start
                self.MaxTab.setRowCount(self.MaxTab.rowCount() + 1)
                self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                    0, QTableWidgetItem(str(delta)[:-3]))
                self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                    1, QTableWidgetItem(str(MeasIdx)))
                self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                    2, QTableWidgetItem(str(RDMax)))
                if self.Norm:
                    RDNorm = RD - RDMax
                    RDNorm[RDNorm < self.NVal] = self.NVal
                else:
                    RDNorm = RD
                self.plt.pcolormesh(self.AVel, self.ARan,
                                    RDNorm, shading="auto")
                self.plt.set_xlabel("Velocity [deg/sec]")
                self.plt.set_ylabel("Range [m]")
                self.plt.set_ylim(self.RDCfg["RMin"], self.RDCfg["RMax"])
                self.canvas.draw()
                if self.endloop:
                    break
                QApplication.processEvents()
                ttime.sleep(self.Rep_Ctrl_spd.value())

        if self.mode == "RP":
            self.Proc.CfgRangeProfile(self.RPCfg)
            self.RanSca = self.Proc.GetRangeProfile("Range")
            self.PData = np.zeros((int(self.BCfg["N"]), int(32)))
            self.MaxTab.clearContents()
            self.MaxTab.setRowCount(1)
            self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                0, QTableWidgetItem("RangeProfile"))
            self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                1, QTableWidgetItem(str(self.BCfg["NrFrms"])))
            self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                2, QTableWidgetItem("<-- total"))
            start = ttime.time()
            for MeasIdx in range(int(self.BCfg["NrFrms"])):
                Data = self.MeasData[:, MeasIdx*8:(MeasIdx+1)*8]
                Id = Data[1, 0]
                self.plt.clear()
                if Id == 1:
                    self.PData[2:, 0:8] = Data[2:, :]
                if Id == 2:
                    self.PData[2:, 8:16] = Data[2:, :]
                if Id == 3:
                    self.PData[2:, 16:24] = Data[2:, :]
                if Id == 4:
                    self.PData[2:, 24:32] = Data[2:, :]
                RP = self.Proc.RangeProfile(self.PData)
                RPMax = np.amax(RP)
                delta = ttime.time() - start
                self.MaxTab.setRowCount(self.MaxTab.rowCount() + 1)
                self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                    0, QTableWidgetItem(str(delta)[:-3]))
                self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                    1, QTableWidgetItem(str(MeasIdx)))
                self.MaxTab.setItem((self.MaxTab.rowCount()-1),
                                    2, QTableWidgetItem(str(RPMax)))
                if self.Norm:
                    RP = pd.DataFrame(RP)
                    RP = RP.mean(axis=1)
                    RP.loc[RP < self.NVal] = self.NVal
                self.plt.plot(self.RanSca, RP)
                self.plt.set_xlabel("Range [m]")
                self.plt.set_ylabel("dB")
                self.plt.set_ylim(-200, 0)
                self.canvas.draw()
                if self.endloop:
                    return
                QApplication.processEvents()
                ttime.sleep(self.Rep_Ctrl_spd.value())

        self.rep_rep = 0
        if self.endloop:
            self.endloop = False
            return
        Qstn = self.errmsg(
            "Completed!", "Simulation completed without Errors!\nRestart Simulation?", "q")
        if Qstn == 0:
            self.REPORT_REPCSV_REP()
        else:
            return

#---repeat simulation function---#
    def REPORT_REPCSV_REP(self):
        self.rep_rep = 1
        self.REPORT_REPCSV()

#---quit simulation-function---#
    def REPORT_REPCSV_QUIT(self):
        #-------find widget and delete it-------#
        try:
            item = self.MWLayout.itemAt(self.ccc)
            widget = item.widget()
            widget.setParent(None)
        except AttributeError:
            pass
#-------clear figure-------#
        self.FGR_CLR()
#-------end while-loop if still running-------#
        self.endloop = True

#---stop simulation function---#
    def REPORT_REPCSV_STP(self):
        self.Rep_Ctrl_ps.disconnect()
        self.Rep_Ctrl_ps.setText("start")
        self.Rep_Ctrl_ps.clicked.connect(self.REPORT_REPCSV_CNTN)
        self.pause = True
        while self.pause:
            QApplication.processEvents()

    def REPORT_REPCSV_CNTN(self):
        self.pause = False
        self.Rep_Ctrl_ps.disconnect()
        self.Rep_Ctrl_ps.setText("stop")
        self.Rep_Ctrl_ps.clicked.connect(self.REPORT_REPCSV_STP)

#---reload Report function---#
    def REPORT_RELOAD(self):
        #-------clear Figure-------#
        self.FGR_CLR()
#-------create Window-------#
        self.Rep_Wndw = QWidget()
#-------create Controls-------#
        self.movie_strt_stp = QPushButton("||>")
        self.movie_strt_stp.setToolTip("Start/Stop")
        self.movie_strt_stp.clicked.connect(self.MV_ST)
        self.movie_nxt = QPushButton(">>")
        self.movie_nxt.setToolTip("next Frame")
        self.movie_nxt.clicked.connect(self.MV_N)
        self.movie_bck = QPushButton("<<")
        self.movie_bck.setToolTip("previous Frame")
        self.movie_bck.clicked.connect(self.MV_B)
        self.movie_rstrt = QPushButton("#")
        self.movie_rstrt.setToolTip("Stop at beginning")
        self.movie_rstrt.clicked.connect(self.MV_RS)
#-------create Title-------#
        self.Rep_Ttl = QLabel()
        self.Rep_Ttl.setFont(QtGui.QFont("Times", 16, QtGui.QFont.Bold))
#-------create FrameCounter-------#
        self.Rep_count = QLabel()
#-------create speedslider------#
        self.SLSP = QSlider(Qt.Horizontal)
        self.SLSP.setValue(99)
        self.SLSP.valueChanged.connect(self.MV_SC)
        self.SLSPL = QLabel("Speed:")
#-------create timeslider-------#
        self.SLT = QSlider(Qt.Horizontal)
        self.SLT.setValue(99)
        self.SLT.valueChanged.connect(self.MV_TC)
        self.SLTL = QLabel("Time:")
#-------get Report-------#
        Qstn = self.errmsg(
            "Report?", "Do you want to load a report (select a folder)?", "q")
        if Qstn == 0:
            report = QFileDialog.getExistingDirectory()
            self.Rep_Ttl.setText(os.path.basename(report))
        else:
            fileName = QFileDialog.getOpenFileName()[0]
            self.Rep_Ttl.setText(os.path.basename(fileName))
            report = 0
#-------check link-------#
        try:
            if report == "":
                raise FileNotFoundError
#-----------get gif-----------#
            if report == 0:
                vidname = fileName
            else:
                vidname = report + "/" + report[-37:] + ".gif"
            self.video = QtGui.QMovie(vidname)
            self.video.frameChanged.connect(self.MV_UPDT)
#-----------check Video----------#
            if not self.video.isValid():
                raise ImportError
#-----------update count-----------#
            self.maxcount = self.video.frameCount()
            self.actcount = self.video.currentFrameNumber()
            self.Rep_count.setText(
                "Frame: " + str(self.actcount) + "/" + str(self.maxcount))
#-----------set video to label-----------#
            self.viddisp = QLabel()
            self.viddisp.setMovie(self.video)
            self.viddisp.show()
            self.video.start()
            self.video.stop()
#-----------create layout and fill-----------#
            self.Rep_Lay = QGridLayout()
            self.Rep_Lay.addWidget(self.Rep_Ttl, 0, 0, 1, 5)
            self.Rep_Lay.addWidget(self.viddisp, 1, 0, 3, 5)
            self.Rep_Lay.addWidget(self.SLTL, 5, 0, 1, 1)
            self.Rep_Lay.addWidget(self.SLT, 5, 1, 1, 4)
            self.Rep_Lay.addWidget(self.movie_strt_stp, 6, 2, 1, 1)
            self.Rep_Lay.addWidget(self.movie_rstrt, 6, 1, 1, 1)
            self.Rep_Lay.addWidget(self.movie_bck, 6, 0, 1, 1)
            self.Rep_Lay.addWidget(self.movie_nxt, 6, 3, 1, 1)
            self.Rep_Lay.addWidget(self.Rep_count, 6, 4, 1, 1)
            self.Rep_Lay.addWidget(self.SLSPL, 7, 0, 1, 1)
            self.Rep_Lay.addWidget(self.SLSP, 7, 1, 1, 4)
#-----------set window attributes-----------#
            self.Rep_Wndw.setLayout(self.Rep_Lay)
            self.Rep_Wndw.setWindowTitle("Reloaded Report:")
            self.Rep_Wndw.resize(1080, 640)
            self.Rep_Wndw.show()

#-------except Errors-------#
        except FileNotFoundError:
            Qstn = self.errmsg(
                "FileNotFoundError!", "No reports found to reload! Try to load again?", "q")
            if Qstn == 0:
                self.REPORT_RELOAD()
            else:
                return

        except ImportError:
            self.errmsg("ImportError!", "Videoformat is not readable!", "c")
            return

#---movie start/stop function---#
    def MV_ST(self):
        if self.video.MovieState() == 1:
            self.video.setPaused(False)
        elif self.video.MovieState() == 0:
            self.video.start()
        else:
            self.video.setPaused(True)

#---movie next Frame function---#
    def MV_N(self):
        if self.video.MovieState() != 1:
            self.video.setPaused(True)
        self.video.jumpToNextFrame()

#---movie previous Frame function---#
    def MV_B(self):
        if self.video.MovieState() != 1:
            self.video.setPaused(True)
        self.video.jumpToFrame(int(self.video.currentFrameNumber() - 1))

#---movie restart function---#
    def MV_RS(self):
        self.video.stop()

#---movie frameconter update function---#
    def MV_UPDT(self):
        self.maxcount = self.video.frameCount()
        self.actcount = self.video.currentFrameNumber()
        self.Rep_count.setText(
            "Frame: " + str(self.actcount) + "/" + str(self.maxcount))
        self.SLT.setValue(self.actcount)

#---movie speed changed function---#
    def MV_SC(self):
        self.video.setSpeed(self.SLSP.value())

#---movie time changed function---#
    def MV_TC(self):
        self.video.jumpToFrame(self.SLT.value())

#---Get-Lock-Function---#
    def GET_LCK():
        global lock
        return lock


# Create Lockable QWidget #
class LockWindow(QWidget):
    #---redefine closeEvent actions and decide if closeable or not---#
    def closeEvent(self, event):
        if MainWindow.GET_LCK():
            event.ignore()
        else:
            super(LockWindow, self).closeEvent(event)


# start QApplication if __name__=="__main__" #
if __name__ == "__main__":
    Wndw = MainWindow()
    Wndw.show()
    sys.exit(app.exec_())
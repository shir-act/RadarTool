import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import Mimo77L
import RadarProc
from scipy.ndimage.filters import gaussian_filter
from PyQt5.QtWidgets import QApplication as App

mpl.style.use("seaborn-whitegrid")

def print_INFO():
    print("\n---------------------------MIMO RF INFO-----------------------------\n")
    print("TxPositions:")
    print(Brd.RfGet("TxPosn"))
    print("RxPositions:")
    print(Brd.RfGet("RxPosn"))
    print("ChnDelay:")
    print(Brd.RfGet("ChnDelay"))
    print("Bandwidth:")
    print(str(Brd.RfGet("B")*1e-9) + ("GHz"))
    print("kf a.k.a. UpSlope:")
    print(Brd.RfGet("kf"))
    print("kfDo a.k.a. DownSlope:")
    print(Brd.RfGet("kfDo"))
    print("fc a.k.a. centered frequency")
    print(Brd.RfGet("fc"))
    print("\n---------------------------BOARD STATUS-----------------------------\n")
    print(Brd.BrdDispSts())
    print("\n---------------------------RF DISP CFG------------------------------\n")
    print(Brd.RfDispCfg())
    print("\n---------------------------RADARBOOK INFO---------------------------\n")
    print("MIMO Name:")
    print(Brd.Get("Name"))
    print("")
    print("Samples:")
    print(Brd.Get("N"))
    print("")
    print("CIC Stages:")
    print(Brd.Get("CicStages"))
    print("")
    print("CIC Delay:")
    print(Brd.Get("CicDelay"))
    print("")
    print("CIC Reduction:")
    print(Brd.Get("CicR"))
    print("")
    print("Clock divider:")
    print(Brd.Get("ClkDiv"))
    print("")
    print("total Frames:")
    print(Brd.Get("NrFrms"))
    print("")
    print("freq. ADC:")
    print(Brd.Get("fAdc"))
    print("")
    print("sampling frequency:")
    print(Brd.Get("fs"))
    print("")
    print("ADC Channels:")
    print(Brd.Get("AdcChn"))
    print("")
    print("ADC Gain:")
    print(Brd.Get("AdcGaindB"))
    print("")
    print("Nr. of Channels:")
    print(Brd.Get("NrChn"))
    print("")
    print("N*Multiplier:")
    print(Brd.Get("NMult"))
    print("")
    print("ADC Impendance:")
    print(Brd.Get("AdcImp"))
    print("")
    print("Scale Constant FuSca:")
    print(Brd.Get("FuSca"))
    print("")
    print("\n---------------------------CIC INFO---------------------------------\n")
    Brd.DispCic()
    print("\n---------------------------RF STATUS--------------------------------\n")
    print(Brd.BrdDispRfSts())
    print("\n---------------------------BOARD SOFTWARE VERSION-------------------\n")
    print(Brd.BrdGetSwVers())
    print("\n---------------------------BOARD INFORMATION------------------------\n")
    Brd.BrdDispInf()
    print("\n---------------------------CALIBRATIONDATA INFORMATION--------------\n")
    Brd.BrdDispCalInf()
    print("\n---------------------------MMP CONFIG-------------------------------\n")
    # Brd.Fpga_DispMmpCfg()
    print("NONE")
    print("\n---------------------------SOFTWARE CONFIG--------------------------\n")
    # print(Brd.Fpga_GetSwCfgString())
    print("NONE")
    print("\n---------------------------PRINT INFO DONE--------------------------\n")
    print("--------------------------------------------------------------------")
    print("--------------------------------------------------------------------")
    print("____________________________________________________________________")

# arrFFT = pd.read_csv("C:/Users/shir/Desktop/MDT_FFT.csv")
# RanFFT = np.array(arrFFT.index)
# arrFFT = np.array(arrFFT)
# arrFFT = arrFFT[:,:-1]
# arrFFT = arrFFT[:,[0, 2, 3, 4, 5, 6, 7, 8]]

Brd = Mimo77L.Mimo77L("PNet", "192.168.1.1")
Proc = RadarProc.RadarProc()

# Brd.BrdRst()
Brd.BrdPwrEna()

Brd.Set('Fifo', 'On')
Brd.Set('NrChn', 4)
Brd.Set('ClkDiv', 1)
Brd.Set("CicEna")
Brd.Set('CicStages', 4)
Brd.Set('CicDelay', 8)
Brd.Set('CicR', 8)
Brd.Set("ClkSrc", 1)
Brd.Set("AdcImp", 100100)
Brd.Set("AdcChn", 4)
Brd.Set("AdcGain", 16)

dCfg = {}
dCfg["fStrt"] = _fSt = 76e9
dCfg["fStop"] = _fSp = 77e9
dCfg["TRampUp"] = _tSt = 256e-6
dCfg["TRampDo"] = _tSp = 10e-6
dCfg["Tp"] = _tp = 316e-6
dCfg["TInt"] = _tInt = 0.075
dCfg["N"] = _N = 640
dCfg["Np"] = _Np = 1
dCfg["NrFrms"] = _NrFrms = 100

CalData = Brd.BrdGetCalData({"Mask":1, "Len":72})
Ref = CalData[33]
RefDist = Ref.imag
RefRCS = Ref.real
Brd.RfMeas("ExtTrigUp", dCfg)

SPCfg = {}
SPCfg["fs"] = _fs = Brd.Get("fs")
SPCfg["kf"] = _kf = Brd.RfGet("kf")
SPCfg["NFFT"] = 2048
SPCfg["Abs"] = 1
SPCfg["Ext"] = 1
SPCfg["RMin"] = 1
SPCfg["RMax"] = 10
SPCfg["RemoveMean"] = 1
SPCfg["Window"] = 1
SPCfg["XPos"] = 1
SPCfg["dB"] = 1
SPCfg["NIni"] = 1
SPCfg["FuSca"] = _FuSca = Brd.Get("FuSca")

# CFAR = {}
# CFAR["Lz"] = 1
# CFAR["Lb"] = 1
# CFAR["La"] = 1
# CFAR["Hz"] = 1
# CFAR["Hb"] = 1
# CFAR["Ha"] = 1

dRCfg = {}
dRCfg["NFFT"] = _RFFT = 2048
dRCfg["AngFFT"] = _AFFT = 128
dRCfg["fs"] = _fs
dRCfg["kf"] = _kf
dRCfg["fc"] = _fc = Brd.RfGet("fc")
dRCfg["FuSca"] = _FuSca
dRCfg["CalData"] = CalData
dRCfg["TxPwr"] = _TxPwr = 60
dRCfg["RMin"] = 1
dRCfg["RMax"] = 10

Brd.RfTxEna(4, _TxPwr)

Proc.CfgRangeProfile(SPCfg)
# Proc.CfgRangeProfileCfar(CFAR)
# R = Proc.GetRangeProfile("Range")
Proc.RCSCfg(dRCfg)

v0, sm0, loc, drop = Proc.RCS2dBV(RefRCS, RefDist)

fig2 = plt.figure(2)
fig = plt.figure(1)
try:
    ax2 = fig2.get_axes()[0]
    ax = fig.get_axes()[0]
except:
    ax2 = fig2.add_subplot()
    ax = fig.add_subplot()
# print_INFO()

for ID in range(_NrFrms):
    ax.clear()
    ax2.clear()
    Data = Brd.BrdGetData()
    RP = Proc.RangeProfile(Data)
    # RPCfar = Proc.RangeProfileCfar(Data, "Thres")
    dBsm, dBV, Range = Proc.RCSRP(Data, Dmode="full")
    # dBsm = dBsm - dBsm[loc,:] + dBsm0
    # dBV = dBV - dBV[loc, :] + dBV0
    ax.plot(Range, dBsm)
    ax2.plot(Range, dBV)
    # RPsm, _RPV, _RPRan = Proc.RCSRP(RP, "dBV")
    # Cfarsm, CfarV, CfarR = Proc.RCSRP(RPCfar, "dBV")
    # norm = np.mean(dBV, axis=1)
    # std = np.std(dBsm)
    # gaus = gaussian_filter(dBsm, sigma=1.5, truncate=4, mode="mirror")
    # gaus = np.mean(gaus, axis=1)
    # plt.plot(_Range, np.mean(dBsm, axis=1), c="r")
    # plt.plot(_Range, np.mean(RPsm, axis=1), c="g")
    # plt.plot(Range, gaus, c="g")
    # plt.plot(R, np.mean(RP, axis=1), c="blue", marker="x")
    # plt.plot(R, np.mean(RPCfar, axis=1), c="orange", marker="x")
    # plt.plot(RanRCS, np.max(arrRCS, axis=1), c="green")
    fig.canvas.draw_idle()
    fig2.canvas.draw_idle()
    App.processEvents()

Brd.BrdPwrDi()
Brd.BrdRst()
    
#LÖSUNG:
#       dBV+dBsm0-dBdrop
#       v*sm0/drop

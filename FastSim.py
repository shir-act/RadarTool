import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QFileDialog as QFD
from PyQt5.QtWidgets import QApplication as QA
import RadarProc
import jsonpickle as jp
import time

Pc = RadarProc.RadarProc()

file = QFD.getExistingDirectory()
csv = file + file[-38:] + ".csv"
cpath = csv[:-3] + "config"

df = np.array(pd.read_csv(csv, sep=";", decimal=","))
df = df[2:, 1:]

cfg = open(cpath, "r")
cfg = jp.loads(cfg.read())
print(cfg["Mode"])
if cfg["Mode"] != "RP":
    print("not possible!")
else:
    print("loading...")

BCfg = cfg["Board"]
RPCfg = cfg["RangeProfile"]
f0 = BCfg["fStrt"]
f1 = BCfg["fStop"]
N = BCfg["N"]
Frms = BCfg["NrFrms"]
t01 = BCfg["TRampUp"]
TxPwr = BCfg["TxPwr"]
fs = RPCfg["fs"]
kf = RPCfg["kf"]
RMin = RPCfg["RMin"]
RMax = RPCfg["RMax"]
#CalData = RPCfg["CalData"]

dRCfg = {}
dRCfg["NFFT"] = 2048
dRCfg["AFFT"] = 128
dRCfg["fs"] = fs
dRCfg["kf"] = kf
dRCfg["fc"] = (f0+f1)/2
dRCfg["FuSca"] = 0.25/4096
#dRCfg["CalData"] = CalData
dRCfg["TxPwr"] = TxPwr
dRCfg["RMin"] = RMin
dRCfg["RMax"] = RMax
Pc.RCSCfg(dRCfg)

mpl.style.use("seaborn-whitegrid")

fig = plt.figure(1)
fig.clf()
axx = fig.add_subplot()
tax = fig.add_axes([0.225, 0.15, 0.6, 0.03])
tslide = mpl.widgets.Slider(tax, "NrFrms", 0, Frms-1, valstep=1)
bax = fig.add_axes([0.75, 0.2, 0.1, 0.1])
pb = mpl.widgets.Button(bax, "||>")

NrChn = df.shape[1]/Frms

def update(val):
    Id = tslide.val
    s0 = int(Id*NrChn)
    s1 = int(s0+NrChn)
    Data = df[:,s0:s1]
    axx.clear()
    dBsm, dBV, Range = Pc.RCSRP(Data)
    axx.plot(Range, dBsm)
    axx.set_xlabel("Range [m]")
    axx.set_ylabel("dBsm")
    axx.set_xlim(RMin-0.5, RMax+0.5)
    axx.set_ylim(-100, 20)
    axx.grid(True, "both")
    plt.draw()
tslide.on_changed(update)

def play(mouse_event):
    if tslide.val == Frms-1:
        tslide.set_val(0)
    for Id in range(int(tslide.val), int(Frms)):
        tslide.set_val(Id)
        s0 = int(Id*NrChn)
        s1 = int(s0+NrChn)
        Data = df[:,s0:s1]
        axx.clear()
        dBsm, dBV, Range = Pc.RCSRP(Data)
        axx.plot(Range, dBsm)
        axx.set_xlabel("Range [m]")
        axx.set_ylabel("dBsm")
        axx.set_xlim(RMin-0.5, RMax+0.5)
        axx.set_ylim(-100, 20)
        axx.grid(True, "both")
        plt.pause(0.075)
pb.on_clicked(play)

def jump(Frm):
    Id = Frm
    tslide.set_val(Id)
    s0 = int(Id*NrChn)
    s1 = int(s0+NrChn)
    Data = df[:,s0:s1]
    axx.clear()
    dBsm, dBV, Range = Pc.RCSRP(Data)
    axx.plot(Range, dBsm)
    axx.set_xlabel("Range [m]")
    axx.set_ylabel("dBsm")
    axx.set_xlim(RMin-0.5, RMax+0.5)
    axx.set_ylim(-100, 20)
    axx.grid(True, "both")
    plt.draw()

print("ready!")
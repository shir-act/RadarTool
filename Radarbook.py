# Radarbook.py -- Radarbook class
#
# Copyright (C) 2015-11 Inras GmbH Haderer Andreas
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

# Version 1.0.1
#
# Version 2.0.0
#   - Derived from connection class
# Version 2.0.1
#   - Correct for interger indizes in array assignments
# Version 2.1.0
#   - Tested with RadServe 2.6.4
# Version 2.1.1
#   - get extension size
# Version 2.1.2
#     Allow setting device index in constructor
# Version 2.1.3
#     Correct error in Fpga_GetCalData
#     Correct error in Fpga_StoreCalTable
# Version 3.0.0
# Usb Cy_Clr Fifo: Requires a new firmware version

import  sys
import  os
import  socket
import  struct
import  numpy as np
import  SeqTrig as SeqTrig
import  Connection as Connection

class Radarbook(Connection.Connection):
    """ Radarbook class object:C
        (c) Haderer Andreas Inras GmbH

        Communication and access of Radarbook device with TCPIP Connection
    """
    def __init__(self, stConType='RadServe', stIpAdr='192.168.1.1', devIdx=0):
        super(Radarbook, self).__init__(stConType, stIpAdr, devIdx)

        self.HUid           =   0                               # Hardware UID of radarbook
        self.SUid           =   0                               # Software UID of radarbook FPGA framework
        self.SVers          =   0
        self.ReportToFile   =   0
        self.stFileName     =   "Cmd.log"
        self.DictModuleId   =   {   11: "AD7622    ",   12: "PiPoAv",       13: "SaCon",
                                    14: "Cic1      ",   15: "AD7991",       16: "RefC",
                                    17: "AD5660    ",   18: "AltSpi",       19: "USpi",
                                    20: "MCP2515   ",   21: "MT29F4G08",    22: "FArmSpi",
                                    23: "FArmMem   ",   24: "AD8283DatInt", 25: "AD8283",
                                    26: "AD9512    ",   27: "SFtdi",        28: "TimUnit",
                                    29: "AltTim    ",   30: "AltOut",       31: "AltIn",
                                    32: "VersContr ",   33: "Cmd",          34: "FrameGen",
                                    35: "BGT24     ",   36: "HFtdi",        37: "FArmSysMon",
                                    38: "SysChn    ",   39: "Hmc703e",      40: "FrmCtrl",
                                    41: "SeqTrig   ",   42: "BLX",          43: "RCC",
                                    44: "ChnMap6   ",   47: "AD5160",       48: "FArmHPPwr",
                                    49: "SRamFifo  ",   54: "ICTA",         57: "ZCFilt",
                                    58: "TarList   ",   59: "DPA",          60: "ChnMap8",
                                    61: "FrmCtrl8  ",   62: "KorTim",       63: "RDMap",
                                    64: "AFE5801DatInt",65: "FArmWDG",      67: "ArArmPwr",
                                    68: "USpi8     ",   69: "AD9517_4",     72: "AFE5801",
                                    77: "USpiF     ",   78: "USpi16F",      79: "IFRX"}
        # define Brd constants
        self.DefBrdConst()

        self.Name                   =   "Radarbook"
        self.Usb_Timeout            =   0

        #------------------------------------------------------------------
        # Configure Sampling
        #------------------------------------------------------------------
        self.Rad_N                  =   1248
        self.Rad_NMult              =   1
        self.Rad_Rst                =   1
        #self.Rad_NrFrms             =   20000000
        self.Rad_ClkDiv             =   1

        self.Rad_SampCfg_Nr         =   1248-1
        self.Rad_SampCfg_Rst        =   1

        self.Rad_MaskChn            =   2**8-1
        self.Rad_MaskChnEna         =   2**8-1
        self.Rad_MaskChnRst         =   0

        self.Rad_NrChn              =   8
        self.Rad_FrmSiz             =   1

        #------------------------------------------------------------------
        # Configure Cic filter
        #------------------------------------------------------------------
        self.Rad_CicCfg_FiltSel     =   2**8-1                                          # Select Cic filters
        self.Rad_CicCfg_CombDel     =   0                                               # Comb delay
        self.Rad_CicCfg_OutSel      =   0                                               # Output select
        self.Rad_CicCfg_SampPhs     =   0                                               # Sampling phase
        self.Rad_CicCfg_SampRed     =   1                                               # Sampling rate reduction
        self.Rad_CicCfg_RegCtrl     =   int('0x800',0) + int('0x400',0) + int('0x1',0)  # Cic filter control register

        #------------------------------------------------------------------
        # Configure AD8283
        #------------------------------------------------------------------
        self.Rad_AdcCfg_AdcSel      =   3                                               # ADC Select
        self.Rad_AdcCfg_FiltCtrl    =   int('0x00',0)                                   # ADC Filter control
        self.Rad_AdcCfg_GainCtrl    =   int('0x02',0)                                   # ADC Gain control
        self.Rad_AdcCfg_ChCtrl      =   int('0x06',0)                                   # ADC Channel select
        self.Rad_AdcCfg_ImpCtrl     =   int('0x01',0)                                   # ADC Impedance control
        self.Rad_AdcCfg_DivCtrl     =   1                                               # Clock divider value
        self.Rad_AdcCfg_ClkCtrl     =   1                                               # 1: Use clock from the baseband board; 0 use clock from frontend

        #------------------------------------------------------------------
        # Configure Frame Control MMP
        #------------------------------------------------------------------
        self.Rad_FrmCtrlCfg_ChnSel                  =   2**8 - 1                                            # Select Channels to be configured
        self.Rad_FrmCtrlCfg_Rst                     =   1                                                   # Reset MMP
        self.Rad_FrmCtrlCfg_RegChnCtrl              =   int('0x2',0) + int('0x8',0) + int('0x10',0)         # Channel control register

        #------------------------------------------------------------------
        # Configure Signal Processing
        #------------------------------------------------------------------
        self.Rad_PipeCfg_Ctrl                       =   3 + 16
        self.Rad_PipeCfg_SyncnFifoNr                =   0
        self.Rad_PipeCfg_SyncnFrmNr                 =   0
        self.Rad_PipeCfg_SyncnSeqNr                 =   0
        self.Rad_PipeCfg_SyncnDelay                 =   0

        self.Rad_FUsbCfg_Mask                       =   1
        self.Rad_FUsbCfg_ChnEna                     =   255
        self.Rad_FUsbCfg_DatSiz                     =   1024
        self.Rad_FUsbCfg_WaitLev                    =   1024 + 512

        #------------------------------------------------------------------
        # Configure Signal Processing
        #------------------------------------------------------------------
        self.Rad_SigProcCfg_Ena                     =   1
        self.Rad_SigProcCfg_Rst                     =   1

        self.Rad_SRamFifoCfg_Mask                   =   1
        self.Rad_SRamFifoCfg_Bypass                 =   0
        self.Rad_SRamFifoCfg_Rst                    =   1
        self.Rad_SRamFifoCfg_ChnMask                =   self.Rad_MaskChn

        self.SeqCfg                                 =   { "Mask" : 1}


        fSeqTrig        =   80e6/self.Rad_ClkDiv
        objSeqTrig      =   SeqTrig.SeqTrig(fSeqTrig)
        self.SeqCfg     =   objSeqTrig.ContUnifM1(1e-3)
        self.Set('NrChn',8)

    def __str__(self):
        return "Radarbook " + " (" + self.stIpAdr + ", " + str(self.PortNr) + ") " + self.Sts

    def __del__(self):
        pass

    def Set(self, stVal, *varargin):
        #   @function       Set
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Set Parameters of Radarbook Baseboard
        #   @paramin[in]    stSelect: String to select parameter to change
        #
        #                   Known stSelect Parameter Strings:
        #                       DebugInf:       Debug Level (>10 Debug Information is output)
        #                           ->          Debug Level number 0 - ...
        #                       Name:           Name of Board
        #                           ->          string containing desired name
        #                       N:              Number of Samples
        #                           ->          Value with number of samples
        #                       CicDi:          Disable CIC filters
        #                       CicEna:         Enable CIC filters
        #                       CicStages:      Number of stages of CIC filter
        #                           ->          Value 1 - 4
        #                       CicDelay:       Comb delay of CIC filter
        #                           ->          Comb delay: 2,4,8,16 are supported values
        #                       CicR:           Sample rate reduction values of CIC filter
        #                           ->          Sample rate reduction 1- ...
        #                       ClkDiv:         AD9512 Clock Divider
        #                           ->          Clock divider value 1 - 32
        #                       NrFrms:         Number of frames to sample
        #                           ->          Value containing number of frames
        #                       ClkSrc:         Clock Source
        #                           ->          0: Clock from frontend; 1 (default) from baseboard
        #                       AdcImp:         Impdeance of AD8283
        #                           ->          < 100.1k Set to 200E; > 100.1k set to 200k
        #                       NrChn:          Number of channels for processing and dat transfer
        #                           ->          1 to 12
        #                       Fifo:           SRamFifo: Enable or Disable Fifo
        #                           ->          On or Off
        #                       AdcChn:         Set number of ADC channels
        #                           ->          2 - 6
        #                       NMult:          Combine multiple frames for data transfer (Transfer size: N*NMult)
        #                           ->          integer value 1 ..
        #                       AdcGain:
        #                           ->
        if stVal == 'DebugInf':
            if len(varargin) > 0:
                self.DebugInf    =   varargin[0]
        elif stVal == 'Name':
            if len(varargin) > 0:
                if isinstance(varargin[0], str):
                    self.Name       =   varargin[0]
                    self.ConSetConfig(stVal, varargin[0], 'STRING')
        elif stVal == 'N':
            if len(varargin) > 0:
                Val         =   varargin[0]
                Val         =   np.floor(Val)
                Val         =   np.ceil(Val/8)*8
                self.Rad_N  =   Val
                self.ConSetConfig(stVal, int(Val), 'INT')
        elif stVal == 'Samples':
            if len(varargin) > 0:
                Val         =   varargin[0]
                Val         =   np.floor(Val)
                Val         =   np.ceil(Val/8)*8
                self.Rad_N  =   Val
                self.ConSetConfig(stVal, int(Val), 'INT')
        elif stVal  == 'CicDi':
            self.Rad_CicCfg_SampRed      =       1
            self.Rad_CicCfg_RegCtrl      =       self.cCIC1_REG_CONTROL_BYPASS + self.cCIC1_REG_CONTROL_EN
            self.ConSetConfig(stVal, 'false', 'STRING');
        elif stVal  == 'CicEna':
            self.Rad_CicCfg_SampRed      =       1
            self.Rad_CicCfg_RegCtrl      =       self.cCIC1_REG_CONTROL_EN + self.cCIC1_REG_CONTROL_RSTCNTREOP  + self.cCIC1_REG_CONTROL_RSTFILTEOP
            self.ConSetConfig(stVal, 'true', 'STRING');
        elif stVal == 'CicStages':
            if len(varargin) > 0:
                Val             =   np.floor(varargin[0] - 1)
                if Val > 3:
                    Val     = 3
                if Val < 0:
                   Val      = 0
                self.Rad_CicCfg_OutSel      =   Val
                self.ConSetConfig(stVal, int(Val), 'INT')
        elif stVal ==  'CicDelay':
            if len(varargin) > 0:
                Val         =   varargin[0]
                Val         =   np.floor(np.log2(Val)-1)
                if Val > 3:
                    Val     = 3
                if Val < 0:
                    Val     = 0
                self.Rad_CicCfg_CombDel     =   Val
                self.ConSetConfig(stVal, Val, 'DOUBLE');
        elif stVal ==  'CicR':
            if len(varargin) > 0:
                Val         =   np.floor(varargin[0])
                if Val > 2**10:
                    Val     = 2**10
                if Val < 1:
                    Val     = 1
                self.Rad_CicCfg_SampRed     =   Val
                self.ConSetConfig(stVal, Val, 'DOUBLE');
        elif stVal ==  'ClkDiv':
            if len(varargin) > 0:
                Val         =   np.floor(varargin[0])
                if Val > 32:
                    Val     =   32
                if Val < 1:
                    Val     =   1
                if Val > 1:
                    Val     =   np.floor(Val/2)*2
                self.Rad_AdcCfg_DivCtrl     =   Val
                self.Rad_ClkDiv             =   Val
                self.ConSetConfig(stVal, Val, 'DOUBLE');
        elif stVal ==  'ClkSrc':
            if len(varargin) > 0:
                Val         =   np.floor(varargin[0])
                Val         =   Val % 2
                self.Rad_AdcCfg_ClkCtrl     =     Val
                self.ConSetConfig(stVal, Val, 'DOUBLE');
        elif stVal ==  'AdcImp':
            if len(varargin) > 0:
                Val         =   np.floor(varargin[0]);
                if Val < (200 + 200e3)/2:
                    self.Rad_AdcCfg_ImpCtrl     =   self.cAD8283_REG_CHIMP_200E
                else:
                    self.Rad_AdcCfg_ImpCtrl     =   self.AD8283_REG_CHIMP_200K
                self.ConSetConfig(stVal, Val, 'DOUBLE');
        elif stVal ==  'NrFrms':
            if len(varargin) > 0:
                NrFrms      =   np.floor(varargin[0])
                if NrFrms < 1:
                    NrFrms  =   1
                if NrFrms > 2**31:
                    NrFrms  =   2**31
                    print('Limit Number of Frames')
                self.Rad_NrFrms  =   NrFrms
                self.cNumPackets =   NrFrms
                #self.ConSetConfig(stVal, int(NrFrms), 'INT')
        elif stVal ==  'NrChn':
            if len(varargin) > 0:
                NrChn       =   np.floor(varargin[0])
                if NrChn < 1:
                    NrChn   =   1
                if NrChn > 12:
                    NrChn   =   12
                print('Set NrChn to: ', NrChn)
                Mask12                      =   2**12 - 1
                Mask                        =   2**NrChn - 1
                self.Rad_MaskChn            =   Mask
                self.Rad_MaskChnEna         =   Mask
                self.Rad_MaskChnRst         =   Mask12 - Mask
                self.Rad_FrmCtrlCfg_ChnSel  =   Mask
                self.Rad_CicCfg_FiltSel     =   Mask
                self.Rad_FUsbCfg_ChnEna     =   Mask
                self.Rad_NrChn              =   NrChn
                self.Rad_SRamFifoCfg_ChnMask=   Mask
                self.ConSetConfig(stVal, int(NrChn), 'INT');
        elif stVal ==  'Fifo':
            if len(varargin) > 0:
                stFifo          =   varargin[0]
                if isinstance(stFifo, str):
                    ValSet  =   0;
                    if stFifo == 'On':
                        self.Rad_SRamFifoCfg_Bypass     =   0
                        ValSet      =   1
                        self.ConSetConfig(stVal, stFifo, 'STRING');
                    if stFifo == 'Off':
                        self.Rad_SRamFifoCfg_Bypass     =   1
                        ValSet      =   1
                        self.ConSetConfig(stVal, stFifo, 'STRING');
                    if ValSet < 1:
                        print('Set Fifo: Value not known')
        elif stVal ==  'AdcChn':
            if len(varargin) > 0:
                NrChn   =   varargin[0]
                if NrChn < 2:
                    NrChn   =   2
                if NrChn > 6:
                    NrChn   =   6
                self.Rad_AdcCfg_ChCtrl      =   self.cAD8283_REG_MUXCNTRL_AB + (NrChn-2)*2
                self.ConSetConfig(stVal, int(NrChn), 'INT');
        elif stVal ==  'NMult':
            if len(varargin) > 0:
                NMult       =   varargin[0]
                if NMult < 1:
                    NMult   =   1
                if NMult*self.Rad_N >= 4096:
                    NMult   =   1
                self.Rad_NMult       =   NMult
                self.ConSetConfig(stVal, int(NMult), 'INT');
        elif stVal ==  'AdcGain':
            if len(varargin) > 0:
                Gain        =   varargin[0];
                if Gain ==  16:
                        self.Rad_AdcCfg_GainCtrl     =   self.cAD8283_REG_GAIN_16
                        self.FuSca                   =   0.25/4096
                        self.AdcGaindB               =   16
                elif Gain == 22:
                        self.Rad_AdcCfg_GainCtrl     =   self.cAD8283_REG_GAIN_22
                        self.FuSca                   =   0.125/4096
                        self.AdcGaindB               =   22
                elif Gain == 28:
                        self.Rad_AdcCfg_GainCtrl     =   self.cAD8283_REG_GAIN_28
                        self.FuSca                   =   0.0625/4096
                        self.AdcGaindB               =   28
                elif Gain == 34:
                        self.Rad_AdcCfg_GainCtrl     =   self.cAD8283_REG_GAIN_34
                        self.FuSca                   =   0.03125/4096
                        self.AdcGaindB               =   34
                else:
                    pass
                self.ConSetConfig(stVal, Gain, 'DOUBLE');
        elif stVal == 'UsbTimeout':
            if len(varargin) > 0:
                Timeout         =   np.floor(varargin[0])
                if Timeout < 500:
                    Timeout   =   1000
                self.Usb_Timeout  =   Timeout
        elif stVal == 'UsbCfgTimeout':
            if len(varargin) > 1:
                Timeout             =   np.floor(varargin[1])
                self.ConSetCfgTimeout(Timeout)
        elif stVal == 'FrmSiz':
            if len(varargin) > 0:
                self.Rad_FrmSiz     =   np.floor(varargin[0])

            self.ConSetConfig(stVal, np.floor(varargin[0]), 'INT');

        elif stVal == 'SampleRateDuringFileStream':
            if len(varargin) > 0:
                self.ConSetConfig(stVal, varargin[0]);

        elif stVal == 'Comment':
            if len(varargin) > 0:
                self.ConSetConfig(stVal, varargin[0], 'STRING');

        else:
            print('Parameter not known')

    def Get(self, stVal):
        #   @function       Get
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Get Parameters of Radarbook Baseboard
        #   @paramin[in]    stSelect: String to select parameter to change
        #
        #                   Known stSelect Parameter Strings:
        #                       DebugInf:       Debug Level (>10 Debug Information is output)
        #                       Name:           Name of Board
        #                       N:              Number of Samples
        #                       CicStages:      Number of stages of CIC filter
        #                       CicDelay:       Comb delay of CIC filter
        #                       CicR:           Sample rate reduction values of CIC filter
        #                       ClkDiv:         AD9512 Clock Divider
        #                       NrFrms:         Number of frames to sample
        #                       fAdc:           AD8283 Sampling Clock
        #                       fs:             Sampling frequency after CIC filter
        #                       AdcChn:         Number of enabled ADC Channels for a single AD8283
        #                       AdcImp:         Adc Impedance
        #                       NMult:          Multi frame processing
        #   @return         Requested value

        if isinstance(stVal, str):
            if stVal == 'DebugInf':
                Ret     =   self.DebugInf
            elif stVal == 'Name':
                Ret     =   self.Name
            elif stVal == 'N':
                if self.cType == 'RadServe' and self.cReplay > -1:
                    Ret = self.ConGet('N', 'INT');
                    self.Rad_N = Ret;
                else:
                    Ret     =   self.Rad_N
            elif stVal == 'Samples':
                if self.cType == 'RadServe' and self.cReplay > -1:
                    Ret = self.ConGet('N', 'INT');
                    self.Rad_N = Ret;
                else:
                    Ret     =   self.Rad_N
            elif stVal == 'CicStages':
                Ret     =   self.Rad_CicCfg_OutSel + 1
            elif stVal == 'CicDelay':
                Ret     =   2**(self.Rad_CicCfg_CombDel + 1)
            elif stVal == 'CicR':
                Ret     =   self.Rad_CicCfg_SampRed
            elif stVal == 'ClkDiv':
                Ret     =   self.Rad_ClkDiv
            elif stVal == 'NrFrms':
                Ret     =   self.Rad_NrFrms
            elif stVal == 'fAdc':
                Ret     =   80e6/self.Rad_ClkDiv
            elif stVal == 'fs':
                R           =   self.Rad_CicCfg_SampRed
                NrAdcChn    =   self.GetAdcChn()
                Ret         =   80.0e6/self.Rad_ClkDiv
                Ret         =   (Ret/R)/NrAdcChn
            elif stVal == 'AdcChn':
                Ret         =   self.GetAdcChn()
            elif stVal == 'AdcGaindB':
                Ret         =   self.AdcGaindB
            elif stVal == 'AdcGain':
                Ret         =   10**(self.AdcGaindB/20)
            elif stVal == 'NrChn':
                if self.cType == 'RadServe' and self.cReplay > -1:
                    Ret = self.ConGet(stVal, 'INT');
                    self.Rad_NrChn = Ret;
                else:
                    Ret         =   self.Rad_NrChn
            elif stVal == 'NMult':
                Ret         =   self.Rad_NMult
            elif stVal == 'AdcImp':
                Ret         =   self.GetAdcImp()
            elif stVal == 'FuSca':
                if self.Rad_AdcCfg_GainCtrl     ==   self.cAD8283_REG_GAIN_16:
                    self.FuSca                   =   0.25/4096
                elif self.Rad_AdcCfg_GainCtrl     ==   self.cAD8283_REG_GAIN_22:
                    self.FuSca                   =   0.125/4096
                elif self.Rad_AdcCfg_GainCtrl     ==   self.cAD8283_REG_GAIN_28:
                    self.FuSca                   =   0.0625/4096
                else:
                    self.FuSca                   =   0.03125/4096
                Ret         =   self.FuSca

            elif stVal == 'FileSize':
                if self.cType == 'RadServe' and self.cReplay > -1:
                    Ret = self.ConGet(stVal, 'DOUBLE');
            elif stVal == 'ExtensionSize':
                if self.cType == 'RadServe' and self.cReplay > -1:
                    Ret = self.ConGet(stVal, 'DOUBLE');

            else:
                print('Parameter not known')
                Ret         =   -1

        return Ret

    def     ConGet(self, Key, Type):
        if self.cType == 'RadServe':
            return self.ConGetConfig(Key, Type)
        else:
            return 0;

    def SetFileParam(self, stKey, Val, DataType='STRING'):
        if isinstance(stKey,str):
            self.ConSetConfig(stKey, Val, DataType);
        else:
            print('Key is not of type string');

    def GetFileParam(self, stKey, stType):
        if isinstance(stKey,str):
            return self.ConGetConfig(stKey, stType);
        else:
            print('Key is not of type string');
            return [];

    def Prnt(self, stVal):
        #   @function       Prnt
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Prints Parameters of Radarbook Baseboard to Matlab Command Window
        #   @paramin[in]    stSelect: String to select parameter to change
        #
        #                   Known stSelect Parameter Strings:
        #                       Name:           Name of Board
        #                       N:              Number of Samples
        #                       fAdc:           AD8283 Sampling Clock
        #                       fs:             Sampling frequency after CIC filter
        #   @return         Requested value
        if isinstance(stVal, str):
            if stVal == 'Name':
                print(' Prnt: Name: ', self.Name)
            elif stVal == 'N':
                print(' Prnt: N: ', self.Rad_N, 'Samples')
            elif stVal == 'Samples':
                print(' Prnt: N: ', self.Rad_N, 'Samples')
            elif stVal == 'fAdc':
                print(' Prnt: fAdc: ', 80e6/self.Rad_ClkDiv/1e6, ' MHz')
            elif stVal == 'fs':
                R           =   self.Rad_CicCfg_SampRed
                NrAdcChn    =   self.GetAdcChn()
                fs          =   80e6/self.Rad_ClkDiv/R/NrAdcChn
                print(' Prnt: fs: ', (fs/1e3), ' kHz')
            else:
                print('Parameter not known')
        else:
            print('stVal is no string')

    def DispCic(self):
        #   @function       DispCic
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Disp Configuration of CIC filters in Matlab Command window

        if np.floor(self.Rad_CicCfg_RegCtrl/self.cCIC1_REG_CONTROL_BYPASS) > 0:
            print(' ', self.Name, ': CIC disabled')
        else:
            print(' ', self.Name, ': CIC enabled')
        print('  Delay:   ',(2**(self.Rad_CicCfg_CombDel+1)))
        print('  Stages:  ',(self.Rad_CicCfg_OutSel+1))
        print('  R:       ',(self.Rad_CicCfg_SampRed))
        print(' ')


    def BrdSetCal(self, dCfg):
        #   @function       BrdSetCal
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Set Calibration Cfg and Calibration Data
        self.Fpga_SetCalCfg(dCfg)
        self.Fpga_SetCalData(dCfg)

    def BrdGetCalData(self, dCfg):
        #   @function       BrdGetCalData
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Get Calibration Data
        Ret             =   self.Fpga_GetCalData(dCfg)
        Ret             =   self.Cal2Num(Ret)
        dCfg["Type"]    =   0
        if dCfg["Type"] == 0:
            CplxData    =   Ret[::2] + 1j*Ret[1::2]
        else:
            CplxData    =   -1

        return CplxData

    def BrdRst(self):
        #   @function       BrdRst
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Reset Baseboard: Function calls Fpga_SeqTrigRst() and Fpga_MimoSeqRst()
        #                   -> FPGA Timing units are put into reset: No Sampling is triggered
        self.Fpga_SeqTrigRst(self.SeqCfg["Mask"])
        Ret     =   self.Fpga_MimoSeqRst()
        return Ret

    def BrdPwrEna(self):
        #   @function       BrdPwrEna
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Enable all power supplies for RF frontend
        dPwrCfg     =   {   "IntEna"        : self.cPWR_INT_ON,
                            "RfEna"         : self.cPWR_RF_ON
                        }
        Ret         =   self.Fpga_SetRfPwr(dPwrCfg)
        return  Ret

    def BrdPwrDi(self):
        #   @function       BrdPwrDi
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Disable all power supplies for RF frontend
        dPwrCfg     =   {   "IntEna"        : self.cPWR_INT_OFF,
                            "RfEna"         : self.cPWR_RF_OFF
                        }
        Ret         =   self.Fpga_SetRfPwr(dPwrCfg)
        return  Ret

    def BrdDispRfSts(self):
        #   @function       BrdDispRfSts
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Display Status of RF board
        Ret         =   self.Fpga_DispRfChipSts(1)
        return Ret

    def RcsCornerCube(self, fc, aCorner):
        #   @file        RefCornerCube.m
        #   @author      Andreas Haderer
        #   @date        2014-05-05
        #   @brief       Calcuate RCS of corner cube, aCorner: length of connecting edge
        c0          =   3e8
        Lambdac     =   c0/fc
        Rcs         =   4*np.pi*aCorner**4/(3*Lambdac**2)
        return      Rcs

    def BrdDispSwVers(self):
        #   @function       BrdDispSwVers
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Disp software version of the board
        self.Fpga_DispSwCfg()

    def BrdGetSwVers(self):
        #   @function       BrdGetSwVers
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Disp FPGA Configuration
        Vers        =   self.Fpga_GetSwVers()
        dRet        =   {
                            "SwPatch"   :   -1,
                            "SwMin"     :   -1,
                            "SwMaj"     :   -1,
                            "SUid"      :   -1,
                            "HUid"      :   -1
                        }
        if Vers[0]:
            Vers    =   Vers[1]
            dRet["SwPatch"]     =   Vers[0] % (2**8)
            TmpVal              =   np.floor(Vers[0]/(2**8))
            dRet["SwMin"]       =   TmpVal % (2**8)
            dRet["SwMaj"]       =   np.floor(TmpVal/(2**8))
            dRet["SUid"]        =   Vers[1]
            dRet["HUid"]        =   Vers[2]
        else:
            print('No version information available');

        return dRet

    def BrdDispInf(self):
        #   @function       BrdDispInf
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Display Board Information
        Ret     =   self.Fpga_DispBrdInf()
        return Ret

    def BrdDispCalInf(self, *varargin):
        #   @function       BrdDispCalInf
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Disp calibration information
        if len(varargin) > 0:
            dCfg        =   varargin[0]
        else:
            dCfg        =   {
                                "Mask"    :   1
                            }
        print(' ')
        print('-------------------------------------------------------------------')
        print('Calibration Table Information')
        Val     =   self.Fpga_GetCalCfg(dCfg)
        if Val[0] == True:
            Val     =   Val[1];
            if len(Val) > 2:
                print('Type              = ',Val[0])
                print('Date              = ',Val[1])
                print('Rev               = ',self.RevStr(Val[2]))
        print('-------------------------------------------------------------------');

    def BrdSampIni(self):
        #   @function       BrdSampIni
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Function initializes baseboard (ADC, CIC, FrmCtrl, SRamFifo)
        if (int(self.DebugInf) & 8) > 0:
            print('BrdSampIni')
        dAdcCfg                     =   {
                                            "AdcSel"    :   0
                                        }
        dAdcCfg["AdcSel"]           =   self.Rad_AdcCfg_AdcSel                          # ADC Select
        dAdcCfg["FiltCtrl"]         =   self.Rad_AdcCfg_FiltCtrl                        # ADC Filter control
        dAdcCfg["GainCtrl"]         =   self.Rad_AdcCfg_GainCtrl                        # ADC Gain control
        dAdcCfg["ChCtrl"]           =   self.Rad_AdcCfg_ChCtrl                          # ADC Channel select
        dAdcCfg["ImpCtrl"]          =   self.Rad_AdcCfg_ImpCtrl                         # ADC Impedance control
        dAdcCfg["DivCtrl"]          =   self.Rad_AdcCfg_DivCtrl                         # Clock divider value
        dAdcCfg["ClkCtrl"]          =   self.Rad_AdcCfg_ClkCtrl                         # 1: Use clock from the baseband board; 0 use clock from frontend

        dFrmCtrlCfg                 =   {
                                            "ChnSel"    :   0
                                        }
        dFrmCtrlCfg["ChnSel"]       =   self.Rad_FrmCtrlCfg_ChnSel                      # Select Channels to be configured
        dFrmCtrlCfg["Rst"]          =   self.Rad_FrmCtrlCfg_Rst                         # Reset MMP
        dFrmCtrlCfg["RegChnCtrl"]   =   self.Rad_FrmCtrlCfg_RegChnCtrl                  # Channel control register


        dCicCfg                     =   {
                                            "FiltSel"    :   0
                                        }
        dCicCfg["FiltSel"]          =   self.Rad_CicCfg_FiltSel                         # Select Cic filters
        dCicCfg["CombDel"]          =   self.Rad_CicCfg_CombDel                         # Comb delay
        dCicCfg["OutSel"]           =   self.Rad_CicCfg_OutSel                          # Output select
        dCicCfg["SampPhs"]          =   self.Rad_CicCfg_SampPhs                         # Sampling phase
        dCicCfg["SampRed"]          =   self.Rad_CicCfg_SampRed                         # Sampling rate reduction
        dCicCfg["RegCtrl"]          =   self.Rad_CicCfg_RegCtrl                         # Cic filter control register

        dSigProcCfg                 =   {
                                            "Ena"    :   0
                                        }

        dSigProcCfg["Ena"]          =   1                                               # Enable/Disable SigProc
        dSigProcCfg["Rst"]          =   1                                               # Reset SigProc

        self.Fpga_SetAdc(dAdcCfg)                                                       # Adc and Clock control
        self.Fpga_SetFrmCtrl(dFrmCtrlCfg)                                               # Data transmission control
        self.Fpga_SetCic(dCicCfg)                                                       # Cic filters
        self.Fpga_SetSigProc(dSigProcCfg)

    def BrdAccessData(self):
        #   @function       BrdAccessData
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Function initializes board and starts Sampling
        #                   TCPIP: Initialize ARM Module
        #                   Usb: Clear SRamFifo and initialize FUsb MMP; -> remove data from Cypress slave fifos until a timeout occurs
        #
        if self.cType == 'Usb' or self.cType == 'RadServe':
            if (int(self.DebugInf) & 8) > 0:
                print('Access Data')

            #--------------------------------------------------------------
            # Configure SRamFifo
            #--------------------------------------------------------------
            dSRamFifoCfg        =   {
                                        "Mask"      :   self.Rad_SRamFifoCfg_Mask,
                                        "Bypass"    :   self.Rad_SRamFifoCfg_Bypass,
                                        "Rst"       :   self.Rad_SRamFifoCfg_Rst,
                                        "ChnMask"   :   self.Rad_SRamFifoCfg_ChnMask
                                    }

            # Calculate Number of Samples to
            Cmp2                =   int(self.cFRMCTRL_REG_CH0CTRL_FRMCNTRENA + self.cFRMCTRL_REG_CH0CTRL_SOFTID)
            Cmp1                =   int(self.cFRMCTRL_REG_CH0CTRL_FRMCNTRENA)

            if (int(self.Rad_FrmCtrlCfg_RegChnCtrl) & Cmp2) == Cmp2:
                Samp    =   self.Rad_N - 2
            elif (int(self.Rad_FrmCtrlCfg_RegChnCtrl) & Cmp1) == Cmp1:
                Samp    =   self.Rad_N - 1
            else:
                Cmp1    =   self.cFRMCTRL_REG_CH0CTRL_SOFTID
                if (int(self.Rad_FrmCtrlCfg_RegChnCtrl) & Cmp1) == Cmp1:
                    Samp    =   self.Rad_N - 1
                else:
                    Samp    =   self.Rad_N

            dSampCfg            =   {
                                        "Nr"        :   Samp,
                                        "Rst"       :   1
                                    }
            self.Fpga_SetSamp(dSampCfg)

            #--------------------------------------------------------------
            # Configure FUsb Interface
            #--------------------------------------------------------------
            dFUsbCfg            =   {
                                        "Mask"      :     self.Rad_FUsbCfg_Mask,
                                        "ChnEna"    :     self.Rad_FUsbCfg_ChnEna,
                                        "DatSiz"    :     self.Rad_N*self.Rad_NMult,
                                        "WaitLev"   :     4096 - 128
                                    }

            #--------------------------------------------------------------
            # Configure Frame Control
            #--------------------------------------------------------------
            dFrmCtrlCfg         =   {
                                        "ChnSel"              :   self.Rad_FrmCtrlCfg_ChnSel,                     # Select Channels to be configured
                                        "Rst"                 :   self.Rad_FrmCtrlCfg_Rst,                        # Reset MMP
                                        "RegChnCtrl"          :   self.Rad_FrmCtrlCfg_RegChnCtrl                  # Channel control register
                                    }

            #----------------------------------------------------------
            # Start Sampling: Reset framecounter, and start sequence
            #----------------------------------------------------------
            self.Fpga_SetFrmCtrl(dFrmCtrlCfg)
            self.Fpga_SetSRamFifo(dSRamFifoCfg)
            self.Fpga_SetFUsb(dFUsbCfg);
			# self.ConClrFifo()
			# Cy_ClrFifo needs RDL_Fx3B16_R-2-0-0 Firmware image
            self.Cy_ClrFifo()

        else:
            if (int(self.DebugInf) & 8) > 0:
                print("Access Data")

            #--------------------------------------------------------------
            # Configure SRamFifo
            #--------------------------------------------------------------
            dSRamFifoCfg        =   {
                                        "Mask"      :   self.Rad_SRamFifoCfg_Mask,
                                        "Bypass"    :   self.Rad_SRamFifoCfg_Bypass,
                                        "Rst"       :   self.Rad_SRamFifoCfg_Rst,
                                        "ChnMask"   :   self.Rad_SRamFifoCfg_ChnMask
                                    }

            # Calculate Number of Samples to
            Cmp2                =   int(self.cFRMCTRL_REG_CH0CTRL_FRMCNTRENA + self.cFRMCTRL_REG_CH0CTRL_SOFTID)
            Cmp1                =   int(self.cFRMCTRL_REG_CH0CTRL_FRMCNTRENA)

            if (int(self.Rad_FrmCtrlCfg_RegChnCtrl) & Cmp2) == Cmp2:
                Samp    =   self.Rad_N - 2
            elif (int(self.Rad_FrmCtrlCfg_RegChnCtrl) & Cmp1) == Cmp1:
                Samp    =   self.Rad_N - 1
            else:
                Cmp1    =   self.cFRMCTRL_REG_CH0CTRL_SOFTID
                if (int(self.Rad_FrmCtrlCfg_RegChnCtrl) & Cmp1) == Cmp1:
                    Samp    =   self.Rad_N - 1
                else:
                    Samp    =   self.Rad_N

            dSampCfg            =   {
                                        "Nr"        :   Samp,
                                        "Rst"       :   1
                                    }
            self.Fpga_SetSamp(dSampCfg)

            #--------------------------------------------------------------
            # Configure FArmMem Channels
            #--------------------------------------------------------------
            dMemChnCfgEna       =   {
                                        "Chn"            :   self.Rad_MaskChnEna,                   # Channel select Mask
                                        "Ctrl"           :   7,                                     # Channel control register
                                        "FrmSiz"         :   self.Rad_N*self.Rad_NMult,
                                        "WaitLev"        :   4096 - 128                             # Frame wait level
                                    }
            # Channels in reset state
            dMemChnCfgRst       =   {
                                        "Chn"            :   self.Rad_MaskChnRst,                   # Channel select
                                        "Ctrl"           :   1,                                     # Channel control register
                                        "FrmSiz"         :   self.Rad_N*self.Rad_NMult,
                                        "WaitLev"        :   4096 - 128,                            # Frame wait level
                                    }


            MemChnEna           =   dMemChnCfgEna["Chn"]                                            # Enable channels
            MemChnCtrl          =   5                                                               # RoEoP and ClrFlgs

            #--------------------------------------------------------------
            # Configure Data Pipe
            #--------------------------------------------------------------
            dPipeCfg            =   {
                                        "Ctrl"                :   self.Rad_PipeCfg_Ctrl,
                                        "SyncnFifoNr"         :   self.Rad_PipeCfg_SyncnFifoNr,
                                        "SyncnFrmNr"          :   self.Rad_PipeCfg_SyncnFrmNr,
                                        "SyncnSeqNr"          :   self.Rad_PipeCfg_SyncnSeqNr,
                                        "SyncnDelay"          :   self.Rad_PipeCfg_SyncnDelay
                                    }
            #--------------------------------------------------------------
            # Configure Frame Control
            #--------------------------------------------------------------
            dFrmCtrlCfg         =   {
                                        "ChnSel"              :   self.Rad_FrmCtrlCfg_ChnSel,                     # Select Channels to be configured
                                        "Rst"                 :   self.Rad_FrmCtrlCfg_Rst,                        # Reset MMP
                                        "RegChnCtrl"          :   self.Rad_FrmCtrlCfg_RegChnCtrl                  # Channel control register
                                    }
            if self.hConDat > -1:
                self.CloseTcpipDataCom()
                print('Close data port')
                self.Arm_OpenDataPort(self.cDataPort)
                self.hConDat    =   self.OpenTcpIpDatCom(self.cIpAddr, self.cDataPort)
            else:
                self.Arm_OpenDataPort(self.cDataPort)
                self.hConDat    =   self.OpenTcpIpDatCom(self.cIpAddr, self.cDataPort)


            #----------------------------------------------------------
            # Configure Data Interface FArmMem,
            #   (1) Rst Fifos, clear data in fifos
            #   (2) Enable Fifos
            #----------------------------------------------------------
            self.Arm_SetMemChnEna( 0, 0)
            self.Arm_SetMemChnCfg(dMemChnCfgRst)
            self.Arm_SetMemChnCfg(dMemChnCfgEna);
            self.Arm_SetOutPipe(dPipeCfg)
            self.Arm_SetTcpIpFrms(1,self.Rad_NrFrms)

            #----------------------------------------------------------
            # Start Sampling: Reset framecounter, and start sequence
            #----------------------------------------------------------
            self.Fpga_SetFrmCtrl(dFrmCtrlCfg)
            self.Fpga_SetSRamFifo(dSRamFifoCfg)
            self.Arm_SetMemChnEna(MemChnEna, MemChnCtrl)

    def BrdSampStrt(self):
        #   @function       BrdSampStrt
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Start sampling: Load timing unit and execute trigger signal to start timing
        self.Fpga_SeqTrigLoad(self.SeqCfg["Mask"], self.SeqCfg["Ctrl"], self.SeqCfg["ChnEna"])
        self.Fpga_SeqTrigEve(self.SeqCfg["Mask"])

    # DOXYGEN ------------------------------------------------------
    #> @brief Generate trigger event for timing unit
    #>
    #> This method generates a trigger signal for the timing unit in the FPGA (SeqTrig)
    def     BrdSampTrig(self):
        self.Fpga_SeqTrigEve(self.SeqCfg["Mask"]);

    def BrdGetData(self, *varargin):
        #   @function       BrdGetData
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Get Measurement Data (Sampled IF signals)
        #   @param[in]      NrPack: Number of consecutive frames to read (only in USB Mode supported)
        #   @return         Data: 2D Array containing measurement data (Col1 -> Chn1, Col2 -> Chn2, etc)
        self.Rad_NrChn = int(self.Rad_NrChn);
        self.Rad_N = int(self.Rad_N);
        if self.cType == 'Usb':
            #TODO
            pass
        elif self.cType == 'RadServe':
            if len(varargin) > 0:
                NrPack  =   int(varargin[0])
            else:
                NrPack  =   1
            #----------------------------------------------------------
            # Open Data Port
            #----------------------------------------------------------
            if self.hConDat < 0:
                self.ConSetTimeout(self.Usb_Timeout)
                self.GetDataPort()

            UsbData             =   self.ConGetData(NrPack*self.Rad_NrChn*self.Rad_N)
            Data                =   np.zeros((self.Rad_N*NrPack,self.Rad_NrChn))
            for Idx in range(0, NrPack):
                IdxStrt         =   int((Idx)*self.Rad_NrChn*self.Rad_N)
                IdxStop         =   int((Idx+1)*self.Rad_NrChn*self.Rad_N)
                Data1           =   UsbData[IdxStrt:IdxStop]
                Data1           =   Data1.reshape((self.Rad_NrChn,self.Rad_N)).transpose()
                Data1[1:,:]     =   Data1[1:,:]/16
                Data[(Idx)*self.Rad_N:(Idx+1)*self.Rad_N,:]       =   Data1

        else:
            if self.hConDat > -1:
                if len(varargin) > 0:
                    NrPack          =   int(varargin[0])
                else:
                    NrPack          =   int(1)
                Data                =   np.zeros((int(self.Rad_N*NrPack*self.Rad_NMult), int(self.Rad_NrChn)))
                for Idx in range(0,NrPack):
                    ArmData             =   self.Arm_ReadFrm(self.Rad_MaskChnEna)
                    DataSiz             =   ArmData.shape
                    if (DataSiz[0] == self.Rad_N*self.Rad_NMult) and (DataSiz[1] == self.Rad_NrChn):
                        if len(ArmData) > 1:
                            FrmCntr         =   ArmData[0,:]
                            ArmData         =   ArmData/16
                            ArmData[0,:]    =   FrmCntr

                        Data[int((Idx)*self.Rad_N*self.Rad_NMult):int((Idx+1)*self.Rad_N*self.Rad_NMult),:] = ArmData
            else:
                Data            =   -1

        return Data



    def BrdGetFrm(self, *varargin):
        #   @function       BrdGetData
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Get Measurement Data (Sampled IF signals)
        #   @param[in]      NrPack: Number of consecutive frames to read (only in USB Mode supported)
        #   @return         Data: 2D Array containing measurement data (Col1 -> Chn1, Col2 -> Chn2, etc)
        if self.cType == 'Usb':
            #TODO
            pass
        else:
            if self.hConDat > -1:
                Frm     =   np.zeros((int(self.Rad_FrmSiz*self.Rad_N),int(self.Rad_NrChn)))
                for Idx in range(0,int(self.Rad_FrmSiz)):
                    Data            =   self.Arm_ReadFrm(self.Rad_MaskChnEna)
                    Frm[int(Idx*self.Rad_N):int((Idx+1)*self.Rad_N),:]   =   Data
                if len(Data) > 1:
                    FrmCntr         =   Frm[0,:]
                    Frm             =   Frm/16
                    Frm[0,:]        =   FrmCntr

            else:
                Frm            =   -1

        return Frm

    def BrdSetTimCont(self, stSel, *varargin):
        #   @function       BrdSetTimCont
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Close connections for data transfer
        #   @param[in]      stSel: String to select predefined timing
        #                   ContUnifM1: Continuous uniform timing with single measurement phase: only ADC is triggered
        #                               This timing can be used to test the sampling chain.
        #                               @param[in]: Repetition interval; measurements are triggered with the selected period
        fSeqTrig        =   80e6/self.Rad_ClkDiv

        if stSel == 'ContUnifM1':
            objSeqTrig          =   SeqTrig.SeqTrig(fSeqTrig)
            if len(varargin) > 0:
                self.SeqCfg     =   objSeqTrig.ContUnifM1(varargin[0])
                Ini             =   1;
        elif stSel == 'ContUnifM1PWPT':
            objSeqTrig          =   SeqTrig.SeqTrig(fSeqTrig)
            if len(varargin) > 2:
                self.SeqCfg     =   objSeqTrig.ContUnifM1PWPT(varargin[0],varargin[1], varargin[2])
                Ini             =   1;
        elif stSel == 'ContUnifMx':
            objSeqTrig          =   SeqTrig.SeqTrig(fSeqTrig)
            if len(varargin) > 2:
                print('Set ContUnifMx')
                self.SeqCfg     =   objSeqTrig.ContUnifMx(varargin[0], varargin[1], varargin[2])
                Ini             =   1
            else:
                Ini             =   0
                print('Duration must be specified')
        elif stSel == 'RccSegUnifM1':
            objSeqTrig          =   SeqTrig.SeqTrig(fSeqTrig)
            if len(varargin) > 1:
                self.SeqCfg     =   objSeqTrig.RccSeqContUnifM1(varargin[0], varargin[1])
                Ini             =   1;
            else:
                Ini             =   0;
                print('Parameters must be specified')
        elif stSel == 'RccSegUnifM1PW':
            objSeqTrig          =   SeqTrig.SeqTrig(fSeqTrig)
            if len(varargin) > 2:
                self.SeqCfg     =   objSeqTrig.RccSeqContUnifM1PW(varargin[0], varargin[1], varargin[2])
                Ini             =   1;
            else:
                Ini             =   0;
                print('Parameters must be specified')
        elif stSel == 'RccSegUnifMx':
            objSeqTrig          =   SeqTrig.SeqTrig(fSeqTrig)
            if len(varargin) > 3:
                # RccSeqContUnifMx(self, Tp, TCfg, TWait, Np):
                self.SeqCfg     =   objSeqTrig.RccSeqContUnifMx(varargin[0], varargin[1], varargin[2], varargin[3])
                Ini             =   1;
            else:
                Ini             =   0;
                print('Parameters must be specified')
        elif stSel == 'RccSegUnifMxPW':
            objSeqTrig          =   SeqTrig.SeqTrig(fSeqTrig)
            if len(varargin) > 4:
                # RccSeqContUnifMx(self, Tp, TCfg, TWait, Np):
                self.SeqCfg     =   objSeqTrig.RccSeqContUnifMxPW(varargin[0], varargin[1], varargin[2], varargin[3], varargin[4])
                Ini             =   1;
            else:
                Ini             =   0;
                print('Parameters must be specified')
        elif stSel == 'RccSegUnifMTxPaCon':
            objSeqTrig          =   SeqTrig.SeqTrig(fSeqTrig)
            if len(varargin) > 3:
                self.SeqCfg     =   objSeqTrig.RccSeqContUnifMTxPaCon(varargin[0], varargin[1], varargin[2], varargin[3])
                Ini             =   1
            else:
                Ini             =   0
                print('Parameters must be specified')
        elif stSel == 'RccSegUnifM1_RccMs':
            objSeqTrig          =   SeqTrig.SeqTrig(fSeqTrig);
            if len(varargin) > 1:
                self.SeqCfg     =   objSeqTrig.RccSeqContUnifM1_RccMs(varargin[0], varargin[1]);
                Ini             =   1
            else:
                Ini             =   0
                print('Parameters must be specified')
        else:
            Ini             =   0
            print('Duration must be specified')



        if Ini > 0:
            self.Fpga_SeqTrigRst(self.SeqCfg["Mask"]);
            NSeq        =   len(self.SeqCfg["Seq"]);
            if self.DebugInf > 0:
                print('Run SeqTrig: ', NSeq, ' Entries')
            Tmp     =   self.SeqCfg["Seq"]
            for Idx in range (0, NSeq):
                self.Fpga_SeqTrigCfgSeq(self.SeqCfg["Mask"], Idx, self.SeqCfg["Seq"][Idx])

    def Fpga_SetAdc(self, *varargin):
        #   @file           Fpga_SetAdc.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Configure AD8283 ADC and Sampling clock for AD8283 with AD9512
        #                   For a detailed description refer to the manual of AD8283
        #   @paramin[in]    AdcCfg Configuration Structure
        #                   Supported Fields:
        #                       AdcSel:         Bitmask to select AD8283
        #                       FiltCtrl:       Anti-aliasing filter control
        #                       GainCtrl:       ADC gain control
        #                       ChCtrl:         ADC channel control
        #                       ImpCtrl:        ADC input impedance control
        #                       DivCtrl:        Clock divider control of AD9512
        #                       ClkCtrl:        Sampling clock control (0 Frontend, 1 Baseband)
        if (int(self.DebugInf) & 8) > 0:
            print('Fpga_SetAdc')
        if len(varargin) > 0:
            dAdcCfg     =       varargin[0]
            if not ('AdcSel' in dAdcCfg):
                dAdcCfg["AdcSel"]           =   self.Rad_AdcCfg_AdcSel
            else:
                self.Rad_AdcCfg_AdcSel      =   dAdcCfg["AdcSel"]
            if not ('FiltCtrl' in dAdcCfg):
                dAdcCfg["FiltCtrl"]         =   self.Rad_AdcCfg_FiltCtrl
            else:
                self.Rad_AdcCfg_FiltCtrl    =   dAdcCfg["FiltCtrl"]
            if not ('GainCtrl' in dAdcCfg):
                dAdcCfg["GainCtrl"]         =   self.Rad_AdcCfg_GainCtrl
            else:
                self.Rad_AdcCfg_GainCtrl    =   dAdcCfg["GainCtrl"]
            if not ('ChCtrl' in dAdcCfg):
                dAdcCfg["ChCtrl"]           =   self.Rad_AdcCfg_ChCtrl
            else:
                self.Rad_AdcCfg_ChCtrl      =   dAdcCfg["ChCtrl"]
            if not ('ImpCtrl' in dAdcCfg):
                dAdcCfg["ImpCtrl"]          =   self.Rad_AdcCfg_ImpCtrl
            else:
                self.Rad_AdcCfg_ImpCtrl     =   dAdcCfg["ImpCtrl"]
            if not ('DivCtrl' in dAdcCfg):
                dAdcCfg["DivCtrl"]          =   self.Rad_AdcCfg_DivCtrl
            else:
                self.Rad_AdcCfg_DivCtrl     =   dAdcCfg["DivCtrl"]
            if not ('ClkCtrl' in dAdcCfg):
                dAdcCfg["ClkCtrl"]          =   self.Rad_AdcCfg_ClkCtrl
            else:
                self.Rad_AdcCfg_ClkCtrl     =   dAdcCfg["ClkCtrl"]
        else:
            dAdcCfg         =       {
                                        "AdcSel"        :   self.Rad_AdcCfg_AdcSel,             # ADC Select
                                        "FiltCtrl"      :   self.Rad_AdcCfg_FiltCtrl,           # ADC Filter control
                                        "GainCtrl"      :   self.Rad_AdcCfg_GainCtrl,           # ADC Gain control
                                        "ChCtrl"        :   self.Rad_AdcCfg_ChCtrl,             # ADC Channel select
                                        "ImpCtrl"       :   self.Rad_AdcCfg_ImpCtrl,            # ADC Impedance control
                                        "DivCtrl"       :   self.Rad_AdcCfg_DivCtrl,            # Clock divider value
                                        "ClkCtrl"       :   self.Rad_AdcCfg_ClkCtrl             # 1: Use clock from the baseband board; 0 use clock from frontend
                                    }

        Cod             =   int('0x9010',0)
        FpgaCmd         =   np.zeros(7, dtype='uint32')
        FpgaCmd[0]      =   dAdcCfg["AdcSel"]
        FpgaCmd[1]      =   dAdcCfg["FiltCtrl"]
        FpgaCmd[2]      =   dAdcCfg["GainCtrl"]
        FpgaCmd[3]      =   dAdcCfg["ChCtrl"]
        FpgaCmd[4]      =   dAdcCfg["ImpCtrl"]
        FpgaCmd[5]      =   dAdcCfg["DivCtrl"]
        FpgaCmd[6]      =   dAdcCfg["ClkCtrl"]
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SetAdc Cfg:", FpgaCmd)
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SetAdc Ret:", Ret)
        return      Ret

    def Fpga_SetFrmCtrl(self, *varargin):
        #   @function           Fpga_SetFrmCtrl
        #   @author             Haderer Andreas (HaAn)
        #   @datestr            2013-12-28
        #   @brief              Configure Frame Control MMP
        #                       The Frame Control block is used to number the measurements or to output a test signal. For a detailed description
        #                       of the MMP refer to the user manual.
        #   @paramin[in]    FrmCtrlCfg Configuration Structure (optional)
        #                   Supported Fields:
        #                       ChnSel:         Bitmask to select the channels; channels can be configured with different setting
        #                       Rst:            Reset MMP: 1 -> resets all counters (FrmCntr is set to zero)
        #                       RegChnCtrl:     Set Channel control register
        if len(varargin) > 0:
            dFrmCtrlCfg     =   varargin[0]
            if not ('ChnSel' in dFrmCtrlCfg):
                dFrmCtrlCfg["ChnSel"]           =   self.Rad_FrmCtrlCfg_ChnSel
            else:
                self.Rad_FrmCtrlCfg_ChnSel      =   dFrmCtrlCfg["ChnSel"]
            if not ('Rst' in dFrmCtrlCfg):
                dFrmCtrlCfg["Rst"]              =   self.Rad_FrmCtrlCfg_Rst
            else:
                self.Rad_FrmCtrlCfg_Rst         =   dFrmCtrlCfg["Rst"]
            if not('RegChnCtrl' in dFrmCtrlCfg):
                dFrmCtrlCfg["RegChnCtrl"]       =   self.Rad_FrmCtrlCfg_RegChnCtrl
            else:
                self.Rad_FrmCtrlCfg_RegChnCtrl  =   dFrmCtrlCfg["RegChnCtrl"]
        else:
            dFrmCtrlCfg             =   {
                                            ["ChnSel"]      :   self.Rad_FrmCtrlCfg_ChnSel,
                                            ["Rst"]         :   self.Rad_FrmCtrlCfg_Rst,
                                            ["RegChnCtrl"]  :   self.Rad_FrmCtrlCfg_RegChnCtrl
                                        }

        Cod             =   int('0x9012',0);
        FpgaCmd         =   np.zeros(3, dtype='uint32')
        FpgaCmd[0]      =   dFrmCtrlCfg["ChnSel"]
        FpgaCmd[1]      =   dFrmCtrlCfg["Rst"]
        FpgaCmd[2]      =   dFrmCtrlCfg["RegChnCtrl"]
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SetFrmCtrl Cfg:", FpgaCmd)
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SetFrmCtrl Ret:", Ret)
        return     Ret

    def Fpga_SetCic(self, *varargin):
        #   @function            Fpga_SetCic
        #   @author             Haderer Andreas (HaAn)
        #   @datestr            2013-12-28
        #   @brief              Configure Cic filters
        #                       Configure CIC filters with data structure
        #   @paramin[in]    Cic1Cfg Configuration Structure
        #                   Supported Fields:
        #                       FiltSel:         Bitmask to select filter
        #                       CombDelay:       Register value for CombDelay (0,1,2,3) -> (2,4,8,16)
        #                       OutSel:          Output selection (0,1,2,3) -> (1,2,3,4)
        #                       SampPhs:         Sampling Phase (0 - R-1)
        #                       SampRed:         Sampling rate reduction
        #                       RegCtrl:         Control register
        if len(varargin) > 0:
            dCicCfg      =   varargin[0]
            if not ('FiltSel' in dCicCfg):
                dCicCfg["FiltSel"]          =   self.Rad_CicCfg_FiltSel
            else:
                self.Rad_CicCfg_FiltSel     =   dCicCfg["FiltSel"]
            if not ('CombDel' in dCicCfg):
                dCicCfg["CombDel"]          =   self.Rad_CicCfg_CombDel
            else:
                self.Rad_CicCfg_CombDel     =   dCicCfg["CombDel"]
            if not ('OutSel' in dCicCfg):
                dCicCfg["OutSel"]           =   self.Rad_CicCfg_OutSel
            else:
                self.Rad_CicCfg_OutSel      =   dCicCfg["OutSel"]
            if not ('SampPhs' in dCicCfg):
                dCicCfg["SampPhs"]          =   self.Rad_CicCfg_SampPhs
            else:
                self.Rad_CicCfg_SampPhs     =   dCicCfg["SampPhs"]
            if not ('SampRed' in dCicCfg):
                dCicCfg["SampRed"]          =   self.Rad_CicCfg_SampRed
            else:
                self.Rad_CicCfg_SampRed     =   dCicCfg["SampRed"]
            if not ('RegCtrl' in dCicCfg):
                dCicCfg["RegCtrl"]          =   self.Rad_CicCfg_RegCtrl
            else:
                self.Rad_CicCfg_RegCtrl     =   dCicCfg["RegCtrl"]
        else:
            dCicCfg             =   {
                                        "FiltSel"   :   self.Rad_CicCfg_FiltSel,
                                        "CombDel"   :   self.Rad_CicCfg_CombDel,
                                        "OutSel"    :   self.Rad_CicCfg_OutSel,
                                        "SampPhs"   :   self.Rad_CicCfg_SampPhs,
                                        "SampRed"   :   self.Rad_CicCfg_SampRed,
                                        "RegCtrl"   :   self.Rad_CicCfg_RegCtrl
                                    }
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SetCic Cfg:", dCicCfg)
        Cod             =   int('0x9101',0)
        FpgaCmd         =   np.zeros(6, dtype='uint32')
        FpgaCmd[0]      =   dCicCfg["FiltSel"]
        FpgaCmd[1]      =   dCicCfg["CombDel"]
        FpgaCmd[2]      =   dCicCfg["OutSel"]
        FpgaCmd[3]      =   dCicCfg["SampPhs"]
        FpgaCmd[4]      =   dCicCfg["SampRed"]
        FpgaCmd[5]      =   dCicCfg["RegCtrl"]
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SetCic Ret:", Ret)

        return  Ret

    def Fpga_SetFUsb(self, *varargin):
        if len(varargin) > 0:
            dFUsbCfg         =   varargin[0]
            if not ('Mask' in dFUsbCfg):
                dFUsbCfg["Mask"]            =   self.Rad_FUsbCfg_Mask
            else:
                self.Rad_FUsbCfg_Mask       =   dFUsbCfg["Mask"]

            if not ('ChnEna' in dFUsbCfg):
                dFUsbCfg["ChnEna"]          =   self.Rad_FUsbCfg_ChnEna
            else:
                self.Rad_FUsbCfg_ChnEna     =   dFUsbCfg["ChnEna"]

            if not ('DatSiz' in dFUsbCfg):
                dFUsbCfg["DatSiz"]          =   self.Rad_FUsbCfg_DatSiz
            else:
                self.Rad_FUsbCfg_DatSiz     =   dFUsbCfg["DatSiz"]

            if not ('WaitLev' in dFUsbCfg):
                dFUsbCfg["WaitLev"]         =   self.Rad_FUsbCfg_WaitLev
            else:
                self.Rad_FUsbCfg_WaitLev    =   dFUsbCfg["WaitLev"]
        else:
            dFUsbCfg["Mask"]                =   self.Rad_FUsbCfg_Mask;
            dFUsbCfg["ChnEna"]              =   self.Rad_FUsbCfg_ChnEna;
            dFUsbCfg["DatSiz"]              =   self.Rad_FUsbCfg_DatSiz;
            dFUsbCfg["WaitLev"]             =   self.Rad_FUsbCfg_WaitLev;

        Cod         =   int('0x910F',0)
        FpgaCmd     =   np.zeros(5, dtype='uint32')
        FpgaCmd[0]  =   dFUsbCfg["Mask"]
        FpgaCmd[1]  =   2
        FpgaCmd[2]  =   dFUsbCfg["ChnEna"]
        FpgaCmd[3]  =   dFUsbCfg["DatSiz"]
        FpgaCmd[4]  =   dFUsbCfg["WaitLev"]
        Ret         =   self.CmdSend(0,Cod,FpgaCmd);
        Ret         =   self.CmdRecv();

    def Fpga_SetSigProc(self, *varargin):
        #   @function       Fpga_SetSigProc
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Enable Disable FPGA Signal Processing; Only required if framework includes signal processing capabilities
        #   @paramin[in]    SigProcCfg Configuration Structure (optional)
        #                   Supported Fields:
        #                       Ena:            Enable signal processing chain
        #                       Rst:            Reset signal processing chain (0 or 1)
        if len(varargin) > 0:
            dSigProcCfg     =   varargin[0]
            if not ('Ena' in dSigProcCfg):
                dSigProcCfg["Ena"]          =   self.Rad_SigProcCfg_Ena
            else:
                self.Rad_SigProcCfg_Ena     =   dSigProcCfg["Ena"]
            if not ('Rst' in dSigProcCfg):
                dSigProcCfg["Rst"]          =   self.Rad_SigProcCfg_Rst
            else:
                self.Rad_SigProcCfg_Rst     =   dSigProcCfg["Rst"]
        else:
            dSigProcCfg         =   {
                                        "Ena"      :    self.Rad_SigProcCfg_Ena,
                                        "Rst"      :    self.Rad_SigProcCfg_Rst
                                    }
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SetSigProc Cfg", dSigProcCfg)
        Cod             =   int('0x9011',0)
        FpgaCmd         =   np.zeros(2, dtype='uint32')
        FpgaCmd[0]      =   dSigProcCfg["Ena"]
        FpgaCmd[1]      =   dSigProcCfg["Rst"]
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SetSigProc Ret", Ret)
        return      Ret

    def Fpga_SetSamp(self, *varargin):
        #   @function       Fpga_SetSamp
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Set mumber of samples for ADC (FPGA Framework)
        #                   The specified value defines the size of the data frames on the streaming interface after the ADC
        #   @paramin[in]    SampCfg Configuration Structure
        #                   Supported Fields:
        #                       Nr:             Number of ADC samples
        #                       Rst:            Reset data interface (0 or 1)
        if len(varargin) > 0:
            dSampCfg    =   varargin[0]
            if not ('Nr' in dSampCfg):
                dSampCfg["Nr"]          =   self.Rad_N
                self.Rad_SampCfg_Nr     =   self.Rad_N
            if not ('Rst' in dSampCfg):
                dSampCfg["Rst"]         =   self.Rad_Rst
                self.Rad_SampCfg_Rst    =   self.Rad_Rst
        else:
            dSampCfg        =   {
                                    "Nr"        :   self.Rad_SampCfg_Nr,
                                    "Rst"       :   self.Rad_SampCfg_Rst
                                }

        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SetSamp Cfg", dSampCfg)

        Cod             =   int('0x9102',0)
        FpgaCmd         =   np.zeros(2,dtype='uint32')
        FpgaCmd[0]      =   dSampCfg["Nr"]
        FpgaCmd[1]      =   dSampCfg["Rst"]
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SetSamp Ret", Ret)

        return  Ret

    def Fpga_SetSRamFifo(self, *varargin):
        #   @function       Fpga_SetSRamFifo.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Configure SRamFifo
        #   @param[in]      SRamFifoCfg: Configuration structure (optional)
        #                   Supported Fields:
        #                       Mask:            Bitmask to select SRAM
        #                       Bypass:          1: Disable Fifo -> input is copied to output without storing values to Fifo
        #                       Rst:             1: Reset Fifo -> Clear all content stored in the fifo: -> ring buffer is cleared
        if len(varargin) > 0:
            dSRamFifoCfg        =   varargin[0]
            if not ('Mask' in dSRamFifoCfg):
                dSRamFifoCfg["Mask"]        =   self.Rad_SRamFifoCfg_Mask
            else:
                self.Rad_SRamFifoCfg_Mask   =   dSRamFifoCfg["Mask"]
            if not ('Bypass' in dSRamFifoCfg):
                dSRamFifoCfg["Bypass"]      =   self.Rad_SRamFifoCfg_Bypass
            else:
                self.Rad_SRamFifoCfg_Bypass =   dSRamFifoCfg["Bypass"]
            if not('Rst' in dSRamFifoCfg):
                dSRamFifoCfg["Rst"]         =   self.Rad_SRamFifoCfg_Rst
            else:
                self.Rad_SRamFifoCfg_Rst    =   dSRamFifoCfg["Rst"]
            if not('ChnMask' in dSRamFifoCfg):
                dSRamFifoCfg["ChnMask"]     =   self.Rad_SRamFifoCfg_ChnMask
            else:
                self.Rad_SRamFifoCfg_ChnMask=   dSRamFifoCfg["ChnMask"]
        else:
            dSRamFifoCfg        =   {
                                        ["Mask"]        :   self.Rad_SRamFifoCfg_Mask,
                                        ["Bypass"]      :   self.Rad_SRamFifoCfg_Bypass,
                                        ["Rst"]         :   self.Rad_SRamFifoCfg_Rst,
                                        ["ChnMask"]     :   self.Rad_SRamFifoCfg_ChnMask
                                    }

        Cod             =   int('0x910E',0)
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SetSRamFifo Cfg:", dSRamFifoCfg)

        FpgaCmd         =   np.zeros(5,dtype='uint32')
        FpgaCmd[0]      =   dSRamFifoCfg["Mask"]
        FpgaCmd[1]      =   3
        FpgaCmd[2]      =   dSRamFifoCfg["Bypass"]
        FpgaCmd[3]      =   dSRamFifoCfg["Rst"]
        FpgaCmd[4]      =   dSRamFifoCfg["ChnMask"]

        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SetSRamFifo Ret:", Ret)
        return  Ret

    def Fpga_MimoRstSequencer(self):
        #   @function       Fpga_MimoRstSequencer
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Reset Mimo sequencer; clear all entries in the table
        FpgaCmd         =   np.zeros(1,dtype='uint32')
        Cod             =   int('0x9212',0)
        FpgaCmd[0]      =   1
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_MimoRstSequencer Ret:", Ret)
        return  Ret


    def Fpga_GetMonIfAna(self):
        #   @function    Fpga_GetMonIfAna
        #   @author      Haderer Andreas (HaAn)
        #   @date        2013-12-01
        #   @brief       Get Values of IfMonitoring Signals
        #   @return      Array with values of the Monitoring channels
        FpgaCmd         =   np.zeros(1,dtype='uint32')
        Cod             =   int('0x9020',0)
        FpgaCmd[0]      =   1
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_GetMonIfAna Ret:", Ret)
        return  Ret

    def Fpga_MimoSeqNrEntries(self, NrEntries):
        #   @function       Fpga_MimoSeqNrEntries
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Set number of cycles in sequencer
        #   @param[in]      NrEntries: number of entries (measurement cycles)
        FpgaCmd         =   np.zeros(2,dtype='uint32')
        Cod             =   int('0x9212',0)
        FpgaCmd[0]      =   2
        FpgaCmd[1]      =   NrEntries
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_MimoSeqNrEntries Ret:", Ret)
        return  Ret

    def Fpga_MimoSeqSetMod(self, Mod):
        #   @function       Fpga_MimoSeqSetMod.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Set operational mode for sequencer
        FpgaCmd         =   np.zeros(2,dtype='uint32')
        Cod             =   int('0x9212',0)
        FpgaCmd[0]      =   0
        FpgaCmd[1]      =   Mod
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_MimoSeqSetMod Ret:", Ret)
        return  Ret

    def Fpga_MimoSeqSetCrocRegs(self, SeqNr, Data):
        #   @function       Fpga_MimoSeqSetCrocRegs
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Set RCC1010 registers for Mimo sequencer
        #   @param[in]      SeqNr: selects the measurement cycle
        #   @param[in]      Data: Array with values programmed to the RCC1010 at the begin of the measurement cycle
        #                   Commonly the values for the processing call with external trigger input are programmed
        if len(Data) > 28:
            Data        =   Data[0:28]

        FpgaCmd         =   np.zeros(2 + len(Data),dtype='uint32')
        Cod             =   int('0x9212',0)
        FpgaCmd[0]      =   4
        FpgaCmd[1]      =   SeqNr
        FpgaCmd[2:]     =   Data
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_MimoSeqSetCrocRegs Ret:", Ret)
        return  Ret

    def Fpga_MimoSeqSetChnRegs(self, Chn, SeqNr, Data):
        #   @function       Fpga_MimoSeqSetChnRegs
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Set Registers of Mimo sequencer; a channel can be connected to a transceiver; and in the initialization phase the values
        #                   are programmed to the device. (Commonly the data values are programmed over an SPI interface to configure the measurements, e.g. activate antennas)
        #   @param[in]      Chn: Selected sequencer channel
        #   @param[in]      SeqNr: Index of sequence
        #   @param[in]      Data: Array with values programmed over the selected channel
        if len(Data) > 28:
            Data        =   Data[0:28]
        FpgaCmd         =   np.zeros(3 + len(Data),dtype='uint32')
        Cod             =   int('0x9212',0)
        FpgaCmd[0]      =   3
        FpgaCmd[1]      =   Chn
        FpgaCmd[2]      =   SeqNr
        FpgaCmd[3:]     =   Data
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_MimoSeqSetChnRegs Ret:", Ret)
        return  Ret

    def Fpga_SetRfPwr(self, dCfg):
        #   @function       Fpga_SetRfPwr
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Set power control of FArmHP board
        FpgaCmd         =   np.zeros(2,dtype='uint32')
        Cod             =   int('0x9015',0)
        if "IntEna" in dCfg:
            FpgaCmd[0]      =   dCfg["IntEna"]
        else:
            FpgaCmd[0]      =   0
        if "RfEna" in dCfg:
            FpgaCmd[1]      =   dCfg["RfEna"]
        else:
            FpgaCmd[1]      =   0
        Ret                 =   self.CmdSend(0, Cod, FpgaCmd)
        Ret                 =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SetRfPwr Ret:", Ret)
        return Ret

    def Fpga_DispRfChipSts(self, Mask):
        #   @file           Fpga_DispRfChipSt.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Disp Status of Rf frontend and rf chips (chipid)
        print(' ')
        print('-------------------------------------------------------------------')
        print('RF Board Configuration')
        Val     =   self.Fpga_GetRfChipSts(Mask)
        if Val[0] == True:
            Val     =   Val[1]
            if len(Val) > 2:
                if Val[0] == 100:
                    print('MIMO-77-TX4RX8')
                    print('RF UID            =  %x' % Val[0])
                    print('RF RevNr          = ', self.RevStr(Val[1]))
                    print('RF SerialNr       =  %x' % Val[2])
                    print('RF Date           = ', Val[3])
                    print('RF Startup        = ', Val[4])
                    print('--------------------')
                    print('RCC               =  %x' % (Val[5]*2**16 + Val[6]))
                    print('DPA1              =  %x' % (Val[7]*2**16 + Val[8]))
                    print('DPA2              =  %x' % (Val[9]*2**16 + Val[10]))
                    print('DPA3              =  %x' % (Val[11]*2**16 + Val[12]))
                    print('MRX1              =  %x' % (Val[13]*2**16 + Val[14]))
                    print('MRX2              =  %x' % (Val[15]*2**16 + Val[16]))
                elif Val[0] == 101:
                    print('KOR-77-TX2RX8: Old')
                    print('RF UID            = ', Val[0])
                    print('RCC               = ', Val[1], Val[2])
                    print('DPA1              = ', Val[3], Val[4])
                    print('DPA2              = ', Val[5], Val[6])
                    print('MRX1              = ', Val[7], Val[8])
                    print('MRX2              = ', Val[9], Val[10])
                elif Val[0] == 102:
                    print('KOR-77-TX2RX8: New')
                    print('RF UID            = ', Val[0])
                    print('RF RevNr          = ', self.RevStr(Val[1]))
                    print('RF SerialNr       = ', Val[2])
                    print('RF Date           = ', Val[3])
                    print('RF Startup        = ', Val[4])
                    print('--------------------')
                    print('RCC               = ', Val[5], Val[6])
                    print('DPA1              = ', Val[7], Val[8])
                    print('MRX1              = ', Val[9], Val[10])
                    print('MRX2              = ', Val[11], Val[12])
                elif Val[0] == 200:
                    print('MIMO-24-TX2RX8 ADF')
                    print('RF UID            = ', Val[0])
                    print('RF RevNr          = ', self.RevStr(Val[1]))
                    print('RF SerialNr       = ', Val[2])
                    print('RF Date           = ', Val[3])
                    print('RF Startup        = ', Val[4])
                elif Val[0] == 201:
                    print('MIMO-24-TX2RX8 ADF')
                    print('RF UID            = ', Val[0])
                    print('RF RevNr          = ', self.RevStr(Val[1]))
                    print('RF SerialNr       = ', Val[2])
                    print('RF Date           = ', Val[3])
                    print('RF Startup        = ', Val[4])
                else:
                    print('BrdInf');
                    print('RF UID            = ', Val[0])
                    print('RF RevNr          = ', self.RevStr(Val[1]))
                    print('RF SerialNr       = ', Val[2])
                    print('RF Date           = ', Val[3])
                    print('RF Startup        = ', Val[4])
        else:
            print('No status information available')

        print('-------------------------------------------------------------------')

    def Fpga_SeqTrigCfgSeq(self, Mask, SeqNr, dSeq):
        #   @file           Fpga_SeqTrigCfgSeq.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Configure sequence of SeqTrig MMP
        FpgaCmd         =   np.zeros(19,dtype='uint32')
        Cod             =   int('0x9213',0)
        FpgaCmd[0]      =   Mask
        FpgaCmd[1]      =   2
        FpgaCmd[2]      =   SeqNr
        FpgaCmd[3]      =   dSeq["CntrCtrl"]
        FpgaCmd[4]      =   dSeq["CntrPerd"]
        FpgaCmd[5]      =   dSeq["NextAdr"]
        FpgaCmd[6]      =   dSeq["SeqId"]
        FpgaCmd[7]      =   dSeq["Chn0Tim0"]
        FpgaCmd[8]      =   dSeq["Chn0Tim1"]
        FpgaCmd[9]      =   dSeq["Chn0Cfg"]
        FpgaCmd[10]     =   dSeq["Chn1Tim0"]
        FpgaCmd[11]     =   dSeq["Chn1Tim1"]
        FpgaCmd[12]     =   dSeq["Chn1Cfg"]
        FpgaCmd[13]     =   dSeq["Chn2Tim0"]
        FpgaCmd[14]     =   dSeq["Chn2Tim1"]
        FpgaCmd[15]     =   dSeq["Chn2Cfg"]
        FpgaCmd[16]     =   dSeq["Chn3Tim0"]
        FpgaCmd[17]     =   dSeq["Chn3Tim1"]
        FpgaCmd[18]     =   dSeq["Chn3Cfg"]
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SeqTrigCfgSeq: ", dSeq)
        Ret             =   self.CmdSend(0, Cod, FpgaCmd);
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SeqTrigCfgSeq Ret:", Ret)
        return Ret

    def Fpga_GetBrdInf(self):
        #   @file           Fpga_GetBrdInf.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Get Board Information (Read Monitoring Signals)
        FpgaCmd         =   np.zeros(1,dtype='uint32')
        Cod             =   int('0x9013',0)
        FpgaCmd[0]      =   0
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_GetBrdInf Ret:", Ret)
        return  Ret

    def Fpga_SeqTrigLoad(self, Mask, RegCtrl, RegChnEna):
        #   @file           Fpga_SeqTrigLoad.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Load seqtrig with configuration
        FpgaCmd         =   np.zeros(4,dtype='uint32')
        Cod             =   int('0x9213',0)
        FpgaCmd[0]      =   Mask
        FpgaCmd[1]      =   3
        FpgaCmd[2]      =   RegCtrl
        FpgaCmd[3]      =   RegChnEna
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SeqTrigLoad Cfg:", FpgaCmd)

        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()

        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SeqTrigLoad Ret:", Ret)
        return  Ret

    def Fpga_SeqTrigEve(self, Mask):
        #   @file           Fpga_SeqTrigEve.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Trigger event for Mimo sequencer
        FpgaCmd         =   np.zeros(2,dtype='uint32')
        Cod             =   int('0x9213',0)
        FpgaCmd[0]      =   Mask
        FpgaCmd[1]      =   4
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SeqTrigEve Ret:", Ret)
        return  Ret

    def Fpga_SeqTrigGetCntr(self, Mask, Clr):
        #   @file           Fpga_SeqTrigGetCntr
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Get number of counter events: Event is generated if HOLD flag is set in SeqTrig Unit
        #                   This function can be used to stop the timing on a defined hold point
        #   @param[in]      Mask: Bitmask to select the SeqTrig Unit in the FPGA framework; if only one unit is present set to 1
        #   @param[in]      Clr: Clear counter; If set greater than 0, then the counter is cleared after the read operation
        #   @return         Counter Value: Value of the sequence counter in the SeqTrig MMP
        FpgaCmd         =   np.zeros(4,dtype='uint32')
        Cod             =   int('0x9213',0)
        FpgaCmd[0]      =   Mask
        FpgaCmd[1]      =   5
        FpgaCmd[2]      =   4
        FpgaCmd[3]      =   Clr
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SeqTrigEve Ret:", Ret)
        return  Ret

    def Fpga_SeqTrigSetHold(self, Mask):
        #   @file           Fpga_SeqTrigSetHold.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Set hold condition; In this case the timing is stopped at the next hold point;
        #                   Use the HOLD flag to define a Hold point in the SeqTrig timing; If no hold point is defined, then the function has no effect
        #   @param[in]      Mask: Bitmask to select the SeqTrig Unit in the FPGA framework; if only one unit is present set to 1
        FpgaCmd         =   np.zeros(3,dtype='uint32')
        Cod             =   int('0x9213',0)
        FpgaCmd[0]      =   Mask
        FpgaCmd[1]      =   5
        FpgaCmd[2]      =   1
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SeqTrigEve Ret:", Ret)
        return  Ret

    def Fpga_SeqTrigClrHold(self, Mask):
        #   @file           Fpga_SeqTrigClrHold.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Clr Hold condition; If the SeqTrig is waiting at a hold point, than the clear continues timing again
        #   @param[in]      Mask: Bitmask to select the SeqTrig Unit in the FPGA framework; if only one unit is present set to 1
        FpgaCmd         =   np.zeros(3,dtype='uint32')
        Cod             =   int('0x9213',0)
        FpgaCmd[0]      =   Mask
        FpgaCmd[1]      =   5
        FpgaCmd[2]      =   2
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SeqTrigEve Ret:", Ret)
        return  Ret

    def Fpga_SeqTrigGetHold(self, Mask):
        #   @function       Fpga_SeqTrigGetHold
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Get hold condition: Check if SeqTrig is in hold
        #   @param[in]      Mask: Bitmask to select the SeqTrig Unit in the FPGA framework; if only one unit is present set to 1
        #   @return         Hold: Hold flag of MMP; 1 if MMP is in hold; 0 if MMP is running (hold condition is not reached jet, or no hold point is set in the timing)
        FpgaCmd         =   np.zeros(3,dtype='uint32')
        Cod             =   int('0x9213',0)
        FpgaCmd[0]      =   Mask
        FpgaCmd[1]      =   5
        FpgaCmd[2]      =   3
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SeqTrigEve Ret:", Ret)
        return  Ret

        # function [HUid SUid SwVers]       =     Fpga_GetSwCfg(obj);
        # %   @function       Fpga_GetSwCfg
        # %   @author         Haderer Andreas (HaAn)
        # %   @date           2013-12-01
        # %   @brief          Disp FPGA Configuration
        #     Vers            =   obj.Fpga_GetSwVers();
        #     SwVers.SwPatch  =   mod(Vers(1),2^8);
        #     Vers(1)         =   floor(Vers(1)/2^8);
        #     SwVers.SwMin    =   mod(Vers(1),2^8);
        #     SwVers.SwMaj    =   floor(Vers(1)/2^8);

        #     SUid            =   Vers(2);
        #     HUid            =   Vers(3);
        # end

    def Fpga_SeqTrigRst(self, Mask):
        #   @function       Fpga_SeqTrigRst
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Reset SeqTrig and stop current sequence
        #   @param[in]      Mask: Bitmask to select trig unit (in general 1, if only a single is present)
        FpgaCmd         =   np.zeros(2,dtype='uint32')
        Cod             =   int('0x9213',0)
        FpgaCmd[0]      =   Mask
        FpgaCmd[1]      =   1
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SeqTrigRst Ret:", Ret)

        return  Ret

    def Fpga_MimoSeqRst(self):
        #   @function       Fpga_MimoSeqRst
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Reset Mimo sequencer: Clears all entries in the configuration table of MIMO sequencer
        FpgaCmd         =   np.zeros(2,dtype='uint32')
        Cod             =   int('0x9212',0)
        FpgaCmd[0]      =   1
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_MimoSeqRst Ret:", Ret)

        return  Ret

    def Fpga_DispSwCfg(self):
        #   @function       Fpga_DispSwCfg
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Disp FPGA Configuration
        print(' ');
        print('-------------------------------------------------------------------');
        print('FPGA Software UID');
        Data        =   self.Fpga_GetSwVers()
        if len(Data) > 2:
            Tmp         =   Data[0]
            SwPatch     =   Tmp % 2**8
            Tmp         =   np.floor(Tmp/2**8)
            SwMin       =   Tmp % 2**8
            SwMaj       =   np.floor(Tmp/2**8)
            print(' Sw-Rev: ',int(SwMaj),'-',int(SwMin),'-',int(SwPatch))
            print(' Sw-UID: ',int(Data[1]))
            print(' Hw-UID: ',int(Data[2]))
        else:
            print('No version information available')
        print('-------------------------------------------------------------------');

    def Fpga_GetSwVers(self):
        #   @function       Fpga_GetSwVers
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Get Fpga Software framework version number
        FpgaCmd         =   np.zeros(1,dtype='uint32')
        Cod             =   int('0x900E',0)
        FpgaCmd[0]      =   0
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        return  Ret

    def Fpga_DispMmpCfg(self):
        #   @function       Fpga_DispMmpCfg
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Disp FPGA Configuration
        self.MmpList        =   []
        self.stMmpList      =   "MMP List:\n"
        RxData              =   self.Fpga_GetMmpList()
        if len(RxData) > 0:
            NrMmp           =   RxData[0]
            print("Nr Mmp: " + str(NrMmp))
            for Idx in range(0, NrMmp):
                VersData    =   self.Fpga_GetMmpVers(Idx)
                # Format output string
                if len(VersData) > 0:
                    if (VersData[0] in self.DictModuleId):
                        stMmpVers   =   "MMP ID: " + str(VersData[0]) + " " + self.DictModuleId[VersData[0]] + " | "
                        stMmpVers   +=  "Sw-Vers " + str(VersData[1]) + "-" + str(VersData[2]) + "-" + str(VersData[3])
                    else:
                        stMmpVers   =   "MMP ID: " + str(VersData[0]) + " unknown"
                    print(str(stMmpVers))
                else:
                    print("Error Fpga_GetMmpVers")

                self.MmpList.append(VersData)
        else:
            print("Error Fpga_DispMmpCfg")

        print("MmpList read")
        return self.MmpList

    def Fpga_SetCalCfg(self, dCfg):
        #   @function       Fpga_SetCalCfg
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Set Calibration Cfg
        FpgaCmd         =   np.zeros(5, dtype='uint32')
        Cod             =   int('0x901F',0)
        if not ('Type' in dCfg):
            dCfg["Type"]    =   0

        FpgaCmd[0]      =   dCfg["Mask"]
        FpgaCmd[1]      =   2
        FpgaCmd[2]      =   dCfg["Type"]
        FpgaCmd[3]      =   dCfg["RevNr"]
        FpgaCmd[4]      =   dCfg["DateNr"]
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SetCalCfg Ret:", Ret)
        return Ret

    def Fpga_GetCalCfg(self, dCfg):
        #   @function       Fpga_GetCalCfg
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Get Calibration Cfg
        FpgaCmd         =   np.zeros(2,dtype='uint32')
        Cod             =   int('0x901F',0)
        FpgaCmd[0]      =   dCfg["Mask"]
        FpgaCmd[1]      =   4
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_GetCalCfg Ret:", Ret)
        return Ret

    def Fpga_GetCalData(self, dCfg):
        #   @function       Fpga_GetCalData
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Get Calibration Cfg
        N           =   dCfg["Len"]
        StrtIdx     =   1
        Data        =   np.zeros(int(N), dtype='int32')
        while(StrtIdx < N):
            if (StrtIdx + 24) < N:
                Len         =   24
            else:
                Len         =   N - StrtIdx + 1
            FpgaCmd         =   np.zeros(4, dtype='uint32')
            Cod             =   int('0x901F',0)
            FpgaCmd[0]      =   dCfg["Mask"]
            FpgaCmd[1]      =   5
            FpgaCmd[2]      =   StrtIdx
            FpgaCmd[3]      =   Len
            Ret             =   self.CmdSend(0, Cod, FpgaCmd)
            Ret             =   self.CmdRecv()
            Data[StrtIdx-1:StrtIdx+int(Len)-1]       =   Ret
            StrtIdx         =   StrtIdx + Len

        return Data

    def Fpga_SetCalData(self, dCfg):
        #   @function       Fpga_SetCalData
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Set Calibration Data
        Data            =   dCfg["Data"]

        StoreData       =   np.zeros((len(Data),2))
        StoreData[:,0]  =   np.array(np.real(Data)*2**24, dtype='int32')
        StoreData[:,1]  =   np.array(np.imag(Data)*2**24, dtype='int32')
        Data            =   StoreData.flatten(1)

        N               =   len(Data)
        StrtIdx         =   1
        while(StrtIdx < N):
            Cod             =   int('0x901F',0)
            if (StrtIdx + 24) < N:
                TmpData     =   Data[StrtIdx-1:StrtIdx + 24 - 1]
                Len         =   24
            else:
                TmpData     =   Data[StrtIdx-1:]
                Len         =   N - StrtIdx + 1

            FpgaCmd         =   np.zeros(Len + 4, dtype='uint32')
            FpgaCmd[0]      =   dCfg["Mask"]
            FpgaCmd[1]      =   3
            FpgaCmd[2]      =   StrtIdx
            FpgaCmd[3]      =   Len
            FpgaCmd[4:]     =   TmpData
            if (int(self.DebugInf) & 8) > 0:
                print("Fpga_SetCalData Cfg:", dCfg)

            Ret             =   self.CmdSend(0, Cod, FpgaCmd)
            Ret             =   self.CmdRecv()
            if (int(self.DebugInf) & 8) > 0:
                print("Fpga_SetCalData Ret:", Ret)
            StrtIdx         =   StrtIdx + Len

    def Fpga_GetRfChipSts(self, Mask):
        #   @function       Fpga_GetRfChipSts.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Get RfUId and Chip ID of RF chips
        FpgaCmd         =   np.zeros(2,dtype='uint32')
        Cod             =   int('0x901A',0)
        FpgaCmd[0]      =   Mask
        FpgaCmd[1]      =   1
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_GetRfChipSts Ret:", Ret)
        return Ret

    def Fpga_StoreCalTable(self, dCfg):
        #   @function       Fpga_StoreCalTable
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Store Calibration Data to EEPROM
        FpgaCmd         =   np.zeros(4,dtype='uint32')
        Cod             =   int('0x901F',0)
        if not ('Table' in dCfg):
            dCfg["Table"]   =   0
        if not ('Type' in dCfg):
            dCfg["Type"]    =   0

        FpgaCmd[0]      =   dCfg["Mask"]
        FpgaCmd[1]      =   1
        FpgaCmd[2]      =   dCfg["Type"]
        FpgaCmd[3]      =   dCfg["Table"]
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_StoreCalTable Ret:", Ret)
        return Ret

    def Fpga_SetUSpiData(self, dUSpiCfg, Regs):
        #   (c) Andreas Haderer
        #   @file           Fpga_SetUSpiData
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Transmit data over USPI interface
        #   @param[in]      USpiCfg configuration structure for USP interface
        #                   Fields:     Mask:   device selection mask
        #                               Chn:    channel for data transmission
        #   @param[in]      Regs:       Data words to be transmitted
        Regs        =   Regs.flatten(1)
        if (len(Regs) > 28):
            Regs    =   Regs[0:28];

        FpgaCmd         =   np.zeros(3 + len(Regs), dtype='uint32')
        Cod             =   int('0x9017',0)
        FpgaCmd[0]      =   dUSpiCfg["Mask"]
        FpgaCmd[1]      =   1
        FpgaCmd[2]      =   dUSpiCfg["Chn"]
        FpgaCmd[3:]     =   Regs
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SetUSpiData Ret:", Ret)
        return Ret

    def Fpga_SetUSpi8Data(self, dUSpiCfg, Regs):
        #   @function       Fpga_SetUSpi8Data
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Programm Registers over USPI8 Interface
        Regs            =   Regs.flatten(1)
        if (len(Regs) > 28):
            Regs        =   Regs[0:28]
        FpgaCmd         =   np.zeros(3 + len(Regs), dtype='uint32')
        Cod             =   int('0x9018',0)
        FpgaCmd[0]      =   dUSpiCfg["Mask"]
        FpgaCmd[1]      =   1
        FpgaCmd[2]      =   dUSpiCfg["Chn"]
        FpgaCmd[3:]     =   Regs
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SetUSpi8Data Ret:", Ret)
        return Ret

    def Fpga_SetUSpi8DataExt(self, dUSpiCfg, Regs):
        #   @function       Fpga_SetUSpi8DataExt
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Programm Registers over USPI8 Interface
        Regs            =   Regs.flattend(1)
        if (len(Regs) > 28):
            Regs    =   Regs[0:28]
        FpgaCmd         =   np.zeros(3 + len(Regs), dtype='uint32')
        Cod             =   int('0x9018',0)
        FpgaCmd[0]      =   dUSpiCfg["Mask"]
        FpgaCmd[1]      =   2
        FpgaCmd[2]      =   dUSpiCfg["Chn"]
        FpgaCmd[3:]     =   Regs
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SetUSpi8DataExt Ret:", Ret)
        return Ret

    def Fpga_SetUSpi8Cfg(self, dUSpiCfg):
        #   @function       Fpga_SetUSpi8Cfg
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Set configuration of USPI8 block
        Cod             =   int('0x9018',0)
        FpgaCmd         =   np.zeros(18, dtype='uint32')
        FpgaCmd[0]      =   dUSpiCfg["Mask"]
        FpgaCmd[1]      =   3
        FpgaCmd[2]      =   dUSpiCfg["Cfg0"]
        FpgaCmd[3]      =   dUSpiCfg["ClkDiv0"]
        FpgaCmd[4]      =   dUSpiCfg["Cfg1"]
        FpgaCmd[5]      =   dUSpiCfg["ClkDiv1"]
        FpgaCmd[6]      =   dUSpiCfg["Cfg2"]
        FpgaCmd[7]      =   dUSpiCfg["ClkDiv2"]
        FpgaCmd[8]      =   dUSpiCfg["Cfg3"]
        FpgaCmd[9]      =   dUSpiCfg["ClkDiv3"]
        FpgaCmd[10]     =   dUSpiCfg["Cfg4"]
        FpgaCmd[11]     =   dUSpiCfg["ClkDiv4"]
        FpgaCmd[12]     =   dUSpiCfg["Cfg5"]
        FpgaCmd[13]     =   dUSpiCfg["ClkDiv5"]
        FpgaCmd[14]     =   dUSpiCfg["Cfg6"]
        FpgaCmd[15]     =   dUSpiCfg["ClkDiv6"]
        FpgaCmd[16]     =   dUSpiCfg["Cfg7"]
        FpgaCmd[17]     =   dUSpiCfg["ClkDiv7"]
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Fpga_SetUSpi8Cfg Ret:", Ret)
        return Ret


    def Arm_GetAppSts(self):
        #   @function       Arm_GetAppSts
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Get Status of ARM application
        ArmCmd          =   np.ones(1,dtype='uint32')
        Cod             =   int("0x6008", 0)
        Ret             =   self.CmdSend(0, Cod, ArmCmd)
        Ret             =   self.CmdRecv()
        return Ret

    def Arm_StrtApp(self):
        #   @function       Arm_StrtApp
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Start application
        ArmCmd          =   np.ones(1,dtype='uint32')
        Cod             =   int("0x6004", 0)
        Ret             =   self.CmdSend(0, Cod, ArmCmd)
        Ret             =   self.CmdRecv()
        return Ret

    def Arm_OpenDataPort(self, Port):
        #   @file           Arm_OpenDataPort.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Open TcpIp data server on ARM processor
        FpgaCmd         =   np.zeros(2,dtype='uint32')
        Cod             =   int('0x7F10',0)
        FpgaCmd[0]      =   1
        FpgaCmd[1]      =   Port
        Ret             =   self.CmdSend(0,Cod,FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Arm_OpenDataPort Ret:", Ret)
        return Ret

    def Arm_SetMemChnEna(self, MemChnEna, MemChnCtrl):
        #   @file           Arm_SetMemChnEna.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Configure number of FArmMem channels
        FpgaCmd         =   np.zeros(2,dtype='uint32')
        Cod             =   int('0x7F02',0)
        FpgaCmd[0]      =   MemChnEna
        FpgaCmd[1]      =   MemChnCtrl
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Arm_SetMemChnEna: Ret", Ret)

        return Ret

    def Arm_SetMemChnCfg(self, dMemChnCfg):
        #   @file           Arm_SetMemChnCfg.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Configure FArmMem channel
        FpgaCmd         =   np.zeros(4,dtype='uint32')
        Cod             =   int('0x7F01',0)
        FpgaCmd[0]      =   dMemChnCfg["Chn"]
        FpgaCmd[1]      =   dMemChnCfg["Ctrl"]
        FpgaCmd[2]      =   dMemChnCfg["FrmSiz"]
        FpgaCmd[3]      =   dMemChnCfg["WaitLev"]
        if (int(self.DebugInf) & 8) > 0:
            print("Arm_SetMemChnCfg Cfg", dMemChnCfg)
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        if (int(self.DebugInf) & 8) > 0:
            print("Arm_SetMemChnCfg Ret", Ret)
        return Ret

    def Arm_SetOutPipe(self, dPipeCfg):
        #   @file           Arm_SetOutPipe.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Configure Output Pipe
        FpgaCmd         =   np.zeros(5,dtype='uint32')
        Cod             =   int('0x7F03',0)
        FpgaCmd[0]      =   dPipeCfg["Ctrl"]
        FpgaCmd[1]      =   dPipeCfg["SyncnFifoNr"]
        FpgaCmd[2]      =   dPipeCfg["SyncnFrmNr"]
        FpgaCmd[3]      =   dPipeCfg["SyncnSeqNr"]
        FpgaCmd[4]      =   dPipeCfg["SyncnDelay"]
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        return Ret

    def Arm_SetTcpIpFrms(self, Ena, Frms):
        #   @file           Arm_SetTcpIpFrms.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Set number of TcpIp frames to be transmitted
        FpgaCmd         =   np.zeros(2,dtype='uint32')
        Cod             =   int('0x7F11',0)
        if Ena > 0:
            self.Rad_ActFrms     =   Frms
        else:
            self.Rad_ActFrms     =   0
        FpgaCmd[0]      =   Ena
        FpgaCmd[1]      =   Frms
        Ret             =   self.CmdSend(0, Cod, FpgaCmd)
        Ret             =   self.CmdRecv()
        return Ret

    def Arm_ReadFrm(self, MemChnEna):
        #   @file        Arm_ReadFrm.m
        #   @author      Haderer Andreas (HaAn)
        #   @date        2013-12-01
        #   @brief       Read frame form enabled mem channels
        Data        =   np.zeros((int(self.Rad_N*self.Rad_NMult), int(self.Rad_NrChn)), dtype='int16')
        while (MemChnEna > 0):
            if self.Rad_ActFrms > 0:
                if  self.cRadDatSocket:
                    try:
                        RxBytes     =   self.cRadDatSocket.recv(4)
                    except Exception:
                        print("Error in Arm_ReadFrm recv: Exception raised")
                        return  -1*np.ones(1,dtype="int16")

                    Header          =   np.fromstring(RxBytes, dtype="uint32")
                    LenFrm          =   Header[0] % 2**16
                    Chn             =   Header[0] // 2**16
                    MemChnEna       =   MemChnEna - 2**(Chn)

                    if LenFrm > 0:
                        try:
                            RxBytes         =   self.cRadDatSocket.recv(2*LenFrm)
                        except Exception:
                            print("Error in Arm_ReadFrm recv: Exception raised")
                            return -1

                        while len(RxBytes) < (2*LenFrm):
                            LenData     =   len(RxBytes)
                            RxBytes     =   RxBytes + self.cRadDatSocket.recv(2*LenFrm - LenData)

                        Res                 =   np.fromstring(RxBytes, dtype="int16")
                        Data[:,Chn]         =   Res
                        self.Rad_ActFrms    =   self.Rad_ActFrms - 1;
                    else:
                        Data            =   -1*np.ones(1,dtype="int16")

                else:
                    print("Error: RadDatSocket is false")
                    return -1*np.ones(1,dtype="int16")

            else:
                print('Error: Number of Frames!')
                MemChnEna           =   0;

        return  Data

    def Fpga_GetMmpList(self):
        #  @function       Fpga_GetMmpList.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Get Number of Listed MMPs
        FpgaCmd         =   np.zeros(1,dtype='uint32')
        CmdCod          =   int("0x900F", 0)
        RxData          =   self.CmdSend(0, CmdCod, FpgaCmd)
        RxData          =   self.CmdRecv()
        return RxData

    def Fpga_GetMmpVers(self, MmpIdx):
        #   @function       Fpga_GetMmpVers.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-28
        #   @brief          Get Vers Info of MMP selected by Nr
        FpgaCmd         =   np.zeros(2,dtype='uint32')
        FpgaCmd[0]      =   1                           # Sub cmd get mmp vers
        FpgaCmd[1]      =   MmpIdx                      # MMP index
        CmdCod          =   int("0x900F", 0)
        RxData          =   self.CmdSend(0, CmdCod,FpgaCmd)
        RxData          =   self.CmdRecv()
        return RxData

    def Fpga_DispBrdInf(self):
        #   @function       Fpga_DispBrdInf
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Disp Board Information (Board Monitoring Signals, Temp and Input voltage)
        print(' ')
        print('-------------------------------------------------------------------')
        print('Board Information')
        Val             =   self.Fpga_GetBrdInf()
        Ret             =   -1
        if len(Val) > 3:
            FPGABRDINF_LM94022_U20      =   2.365
            FPGABRDINF_LM94022_SCA      =   (-1.0/0.0136)
            Temp1                       =   Val[0]/256*3.3
            Temp1                       =   (Temp1 - FPGABRDINF_LM94022_U20)*FPGABRDINF_LM94022_SCA + 20
            ISup                        =   Val[1]/256*3.3*2/(50e-3*20)
            VSup                        =   Val[2]/256*3.3*14.3117
            Temp2                       =   Val[3]/256*3.3
            Temp2                       =   (Temp2 - FPGABRDINF_LM94022_U20)*FPGABRDINF_LM94022_SCA + 20
            print('Temp1 (AD8283)       = ', (Temp1),' °')
            print('Temp2 (Sup)          = ', (Temp2),' °')
            print('VSup (Sup)           = ', (VSup),' V')
            print('ISup (Sup)           = ', (ISup),' A')

            Ret         =   np.zeros(4,dtype='float')
            Ret[0]      =   Temp1;
            Ret[1]      =   Temp2;
            Ret[2]      =   VSup;
            Ret[3]      =   ISup;
        else:
            print('Board does not respond!')

        print('-------------------------------------------------------------------')
        return  Ret

    def RevStr(self, Val):
        #   @function    RevStr
        #   @author      Haderer Andreas (HaAn)
        #   @date        2013-12-01
        #   @brief       Convert revision number ot revision string (Maj.Min.Patch)
        RevMaj  =   int(np.floor(Val/2**16))
        RevMin  =   int(np.floor(Val/2**8) % 2**8)
        RevPat  =   int(Val % 2**8)
        stRev   =   str(RevMaj) + '.' + str(RevMin) + '.' + str(RevPat)
        return stRev

    def Fpga_GetSwCfg(self):
        Result      =   self.Fpga_GetSwVers()
        Result      =   ((self.SVers % 256),)
        Dummy       =   self.SVers // 256
        Result      +=  ((Dummy//256),)
        Dummy       =   Dummy // 256
        Result      +=  ((Dummy,))

        return      Result

    def Fpga_GetSwCfgString(self):
        Result      =   self.Fpga_GetSwCfg()
        return      "SwVers: " + str(Result[2]) + "-" + str(Result[1]) + "-" + str(Result[0])

    def GetAdcChn(self, *varargin):
        #   @function    GetAdcChn
        #   @author      Haderer Andreas (HaAn)
        #   @date        2013-12-01
        #   @brief       Return nr of configured channels for a single AD8283
        #   @param[in]   AdcCfg (optional): If no parameter is provided, then the field of the obj is analyzed
        #                Required field:
        #                   ChCtrl          Channel control register of ADC
        Nr          =   0
        if len(varargin) > 0:
            dAdcCfg     =   varargin[0]
            if 'ChCtrl' in dAdcCfg:
                if dAdcCfg["ChCtrl"] == self.cAD8283_REG_MUXCNTRL_AB:
                    Nr  =   2
                elif dAdcCfg["ChCtrl"] == self.cAD8283_REG_MUXCNTRL_ABC:
                    Nr  =   3
                elif dAdcCfg["ChCtrl"] ==  self.cAD8283_REG_MUXCNTRL_ABCD:
                        Nr  =   4;
                elif dAdcCfg["ChCtrl"] ==  self.cAD8283_REG_MUXCNTRL_ABCDE:
                        Nr  =   5;
                elif dAdcCfg["ChCtrl"] ==  self.cAD8283_REG_MUXCNTRL_ABCDEF:
                        Nr  =   6;
                else:
                    print('ADC Cfg: Error channel setting!')
                    Nr  =   -1
            else:
                print('ADC Cfg: ChCtrl field missing!')
        else:
            if self.Rad_AdcCfg_ChCtrl == self.cAD8283_REG_MUXCNTRL_AB:
                Nr  =   2
            elif self.Rad_AdcCfg_ChCtrl ==  self.cAD8283_REG_MUXCNTRL_ABC:
                Nr  =   3
            elif self.Rad_AdcCfg_ChCtrl ==  self.cAD8283_REG_MUXCNTRL_ABCD:
                Nr  =   4
            elif self.Rad_AdcCfg_ChCtrl ==  self.cAD8283_REG_MUXCNTRL_ABCDE:
                Nr  =   5
            elif self.Rad_AdcCfg_ChCtrl ==  self.cAD8283_REG_MUXCNTRL_ABCDEF:
                Nr  =   6;
            else:
                print('ADC Cfg: Error channel setting!')
                Nr  =   -1;
        return Nr

    def GetAdcImp(self, *varargin):
        #   @function    GetAdcImp
        #   @author      Haderer Andreas (HaAn)
        #   @date        2013-12-01
        #   @brief       Return AD8283 Input Impedance
        #   @param[in]   AdcCfg (optional): If no parameter is provided, then the field of the obj is analyzed
        #                Required field:
        #                   ImpCtrl          Channel impedance control register of ADC

        Imp         =   0
        if len(varargin) > 0:
            dAdcCfg  =   varargin[0]
            if 'ImpCtrl' in dAdcCfg:
                if dAdcCfg["ChCtrl"] == self.cAD8283_REG_CHIMP_200E:
                    Imp     =   200
                elif dAdcCfg["ChCtrl"] == self.cAD8283_REG_CHIMP_200K:
                    Imp     =   200e3
                else:
                    print('ADC Cfg: Error impedance setting!')
                    Imp     =   -1
            else:
                print('ADC Cfg: ImpCtrl field missing!')
        else:
            if self.Rad_AdcCfg_ImpCtrl == self.cAD8283_REG_CHIMP_200E:
                Imp     =   200
            elif self.Rad_AdcCfg_ImpCtrl == self.cAD8283_REG_CHIMP_200K:
                Imp     =   200e3
            else:
                print('ADC Cfg: Error impedance setting!')
                Imp     =   -1
        return Imp

    def     Cy_ClrFifo(self):
        Cod         =   int('0x9001', 0)
        FpgaCmd     =   [0]
        Ret         =   self.CmdSend(0, Cod, FpgaCmd)
        Ret         =   self.CmdRecv()
        return Ret

    def     Cy_GerVers(self):
        Cod         =   int('0x9000', 0)
        FpgaCmd     =   [0]
        Ret         =   self.CmdSend(0, Cod, FpgaCmd)
        Ret         =   self.CmdRecv()
        return Ret

    def Num2Cal(self, Val):
        #   @function       Num2Cal
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Convert calibration number to s8.24 number format
        #   @param[in]      Double array with cal
        #   @return         S8.24 values for eeprom
        # if isreal(Val)
        #     Val         =   round(Val*2^24);
        #     Idcs        =   find(Val < 0);
        #     Val(Idcs)   =   Val(Idcs) + 2^32;
        #     Cal         =   Val;
        # else
        #     Val1        =   round(real(Val)*2^24);
        #     Idcs        =   find(Val1 < 0);
        #     Val1(Idcs)  =   Val1(Idcs) + 2^32;
        #     CalReal     =   Val1;
        #     Val1        =   round(imag(Val)*2^24);
        #     Idcs        =   find(Val1 < 0);
        #     Val1(Idcs)  =   Val1(Idcs) + 2^32;
        #     CalImag     =   Val1;
        #     Cal         =   CalReal + i.*CalImag;
        if np.isreal(Val).all:
            Cal                     =   np.array(Val*2**24, dtype="int32")
        else:
            pass

        return Cal

    def Cal2Num(self, Cal):
        #   @function       Cal2Num
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Convert calibration data eeprom number format s8.24 to double
        #   @param[in]      Cal data (S8.24 integer values)
        #   @return         cal data as double
        Ret         =   Cal/2**24

        return Ret

    def DefBrdConst(self):
        #--------------------------------------------------------------------------
        # AD8283
        #--------------------------------------------------------------------------
        self.cAD8283_REG_GAIN_16            =   int("0x02", 0)          # Total input gain 16 dB
        self.cAD8283_REG_GAIN_22            =   int("0x03", 0)          # Total input gain 22 dB
        self.cAD8283_REG_GAIN_28            =   int("0x04", 0)          # Total input gain 28 dB
        self.cAD8283_REG_GAIN_34            =   int("0x05", 0)          # Total input gain 34 dB
        self.cAD8283_REG_CHIN_FREQ_13_4     =   int("0x00", 0)          # Cut-off frequency 1.3*1/4*fs */
        self.cAD8283_REG_CHIN_FREQ_12_4     =   int("0x10", 0)          # Cut-off frequency 1.2*1/4*fs */
        self.cAD8283_REG_CHIN_FREQ_11_4     =   int("0x20", 0)          # Cut-off frequency 1.1*1/4*fs */
        self.cAD8283_REG_CHIN_FREQ_09_4     =   int("0x40", 0)          # Cut-off frequency 0.9*1/4*fs */
        self.cAD8283_REG_CHIN_FREQ_08_4     =   int("0x50", 0)          # Cut-off frequency 0.8*1/4*fs */
        self.cAD8283_REG_CHIN_FREQ_07_4     =   int("0x60", 0)          # Cut-off frequency 0.7*1/4*fs */
        self.cAD8283_REG_CHIN_FREQ_13_3     =   int("0x80", 0)          # Cut-off frequency 1.3*1/3*fs */
        self.cAD8283_REG_CHIN_FREQ_12_3     =   int("0x90", 0)          # Cut-off frequency 1.2*1/3*fs */
        self.cAD8283_REG_CHIN_FREQ_11_3     =   int("0xA0", 0)          # Cut-off frequency 1.1*1/3*fs */
        self.cAD8283_REG_CHIN_FREQ_10_3     =   int("0xB0", 0)          # Cut-off frequency 1.0*1/3*fs */
        self.cAD8283_REG_CHIN_FREQ_09_3     =   int("0xC0", 0)          # Cut-off frequency 0.9*1/3*fs */
        self.cAD8283_REG_CHIN_FREQ_08_3     =   int("0xD0", 0)          # Cut-off frequency 0.8*1/3*fs */
        self.cAD8283_REG_CHIN_FREQ_07_3     =   int("0xE0", 0)          # Cut-off frequency 0.7*1/3*fs */
        self.cAD8283_REG_CHIMP_200E         =   int("0x00", 0)          # Select input impedance 200 Ohm*/
        self.cAD8283_REG_CHIMP_200K         =   int("0x01", 0)          # Select input impedance 200k Ohm */
        self.cAD8283_REG_MUXCNTRL_A         =   int("0x00", 0)          # Turn on channel A Dsync is not active */
        self.cAD8283_REG_MUXCNTRL_AUX       =   int("0x01", 0)          # Turn on channel AUX  DSync is not active*/
        self.cAD8283_REG_MUXCNTRL_AB        =   int("0x02", 0)          # Turn on channel A and B */
        self.cAD8283_REG_MUXCNTRL_AAUX      =   int("0x03", 0)          # Turn on channel A and Aux */
        self.cAD8283_REG_MUXCNTRL_ABC       =   int("0x04", 0)          # Turn on channel A, B and C */
        self.cAD8283_REG_MUXCNTRL_ABAUX     =   int("0x05", 0)          # Turn on channel A, B and AUX */
        self.cAD8283_REG_MUXCNTRL_ABCD      =   int("0x06", 0)          # Turn on channel A, B, C and D */
        self.cAD8283_REG_MUXCNTRL_ABCAUX    =   int("0x07", 0)          # Turn on channel A, B, C and AUX */
        self.cAD8283_REG_MUXCNTRL_ABCDE     =   int("0x08", 0)          # Turn on channel A, B, C, D and E */
        self.cAD8283_REG_MUXCNTRL_ABCDAUX   =   int("0x09", 0)          # Turn on channel A, B, C, D and AUX */
        self.cAD8283_REG_MUXCNTRL_ABCDEF    =   int("0x0A", 0)          # Turn on channel A, B, C, D, E and F */
        self.cAD8283_REG_MUXCNTRL_ABCDEAUX  =   int("0x0B", 0)          # Turn on channel A, B, C, D, E and AUX */
        self.cAD8283_REG_MUXCNTRL_CHPWON    =   int("0x40", 0)          # Turn on inactive channels */
        #--------------------------------------------------------------------------
        # HMC703: Modes of operation
        #--------------------------------------------------------------------------
        self.cHMC703_REG_SDCFG_MOD_FRAC         =       0
        self.cHMC703_REG_SDCFG_MOD_INT          =       1
        self.cHMC703_REG_SDCFG_MOD_RAMP_1WAY    =       5
        self.cHMC703_REG_SDCFG_MOD_RAMP_2WAY    =       6
        self.cHMC703_REG_SDCFG_MOD_RAMP_CONT    =       7
        #--------------------------------------------------------------------------
        # Cic1 MMP: Control Register Bit Masks
        #--------------------------------------------------------------------------
        self.cCIC1_REG_CONTROL_EN               =   int("0x1", 0)       # Enable MMP*/
        self.cCIC1_REG_CONTROL_RST              =   int("0x2", 0)       # Reset the filter chain*/
        self.cCIC1_REG_CONTROL_RSTCNTRSOP       =   int("0x100", 0)     # Reset sample cntr on SoP signal*/
        self.cCIC1_REG_CONTROL_RSTFILTSOP       =   int("0x200", 0)     # Reset filter on SoP signal*/
        self.cCIC1_REG_CONTROL_RSTCNTREOP       =   int("0x400", 0)     # Reset sample cntr on EoP signal*/
        self.cCIC1_REG_CONTROL_RSTFILTEOP       =   int("0x800", 0)     # Reset filter on EoP signal*/
        self.cCIC1_REG_CONTROL_BYPASS           =   int("0x10000", 0)   # Bypass Cic filter */
        #--------------------------------------------------------------------------
        # FrmCtrl MMP: Channel Control Register Bit Masks
        #--------------------------------------------------------------------------
        self.cFRMCTRL_REG_CH0CTRL_TESTENA       =   int("0x1", 0)       # test mode enable*/
        self.cFRMCTRL_REG_CH0CTRL_FRMCNTRENA    =   int("0x2", 0)       # frame counter enable*/
        self.cFRMCTRL_REG_CH0CTRL_PADENA        =   int("0x4", 0)       # frame padding enable*/
        self.cFRMCTRL_REG_CH0CTRL_WAITENA       =   int("0x8", 0)       # wait enable*/
        self.cFRMCTRL_REG_CH0CTRL_GLOBWAITENA   =   int("0x10", 0)      # global wait signal enable (or of all channels)*/
        self.cFRMCTRL_REG_CH0CTRL_SOFTID        =   int("0x100", 0)     # frame identification number set by software
        #--------------------------------------------------------------------------
        # ChnMap6 MMP: Channel Control Register Bit Masks
        #--------------------------------------------------------------------------
        self.cCHNMAP6_REG_CTRL_IRQENA           =   int("0x1", 0)       # Enable interrupt*/
        self.cCHNMAP6_REG_CTRL_CHN0ENA          =   int("0x10", 0)      # Enable channel 0, has no effect for output*/
        self.cCHNMAP6_REG_CTRL_CHN1ENA          =   int("0x20", 0)      # Enable channel 1, has no effect for output*/
        self.cCHNMAP6_REG_CTRL_CHN2ENA          =   int("0x40", 0)      # Enable channel 2, has no effect for output*/
        self.cCHNMAP6_REG_CTRL_CHN3ENA          =   int("0x80", 0)      # Enable channel 3, has no effect for output*/
        self.cCHNMAP6_REG_CTRL_CHN4ENA          =   int("0x100", 0)     # Enable channel 4, has no effect for output*/
        self.cCHNMAP6_REG_CTRL_CHN5ENA          =   int("0x200", 0)     # Enable channel 5, has no effect for output*/
        self.cCHNMAP6_REG_CHN0CTRL_OUTSEL0      =   int("0x1", 0)       # Channel 0 output select 0*/
        self.cHNMAP6_REG_CHN0CTRL_OUTSEL1       =   int("0x2", 0)       # Channel 0 output select 1*/
        self.cCHNMAP6_REG_CHN1CTRL_OUTSEL0      =   int("0x1", 0)       # Channel 1 output select 0*/
        self.cCHNMAP6_REG_CHN1CTRL_OUTSEL1      =   int("0x2", 0)       # Channel 1 output select 1*/
        self.cCHNMAP6_REG_CHN2CTRL_OUTSEL0      =   int("0x1", 0)       # Channel 2 output select 0*/
        self.cCHNMAP6_REG_CHN2CTRL_OUTSEL1      =   int("0x2", 0)       # Channel 2 output select 1*/
        #--------------------------------------------------------------------------
        # ZCFilt MMP:
        #--------------------------------------------------------------------------
        self.cZCFILT_REG_CONTROL_RST            =   int("0x1", 0)       # Reset MMP*/
        self.cZCFILT_REG_CONTROL_BYPASS         =   int("0x2", 0)       # Reset the filter chain*/
        self.cZCFILT_REG_CONTROL_OUT0           =   int("0x10", 0)      # output control 0*/
        self.cZCFILT_REG_CONTROL_OUT1           =   int("0x20", 0)      # output control 1*/
        self.cZCFILT_REG_CONTROL_UPD0           =   int("0x40", 0)      # update control 0*/
        self.cZCFILT_REG_CONTROL_UPD1           =   int("0x80", 0)      # update control 1*/
        #--------------------------------------------------------------------------
        # SeqTrig MMP: Configure Timing of Sequence Trigger
        #--------------------------------------------------------------------------
        self.cSEQTRIG_REG_CTRL_RST                      =   int("0x1", 0)       # Rst MMP*/
        self.cSEQTRIG_REG_CTRL_CH0ENA                   =   int("0x10", 0)      # Enable output channel 0*/
        self.cSEQTRIG_REG_CTRL_CH1ENA                   =   int("0x20", 0)      # Enable output channel 1*/
        self.cSEQTRIG_REG_CTRL_CH2ENA                   =   int("0x40", 0)      # Enable output channel 2*/
        self.cSEQTRIG_REG_CTRL_CH3ENA                   =   int("0x80", 0)      # Enable output channel 3*/
        self.cSEQTRIG_REG_CTRL_IRQ0ENA                  =   int("0x100", 0)     # Enable channel 0 sys irq*/
        self.cSEQTRIG_REG_CTRL_IRQ1ENA                  =   int("0x200", 0)     # Enable channel 1 sys irq*/
        self.cSEQTRIG_REG_CTRL_IRQ2ENA                  =   int("0x400", 0)     # Enable channel 2 sys irq*/
        self.cSEQTRIG_REG_CTRL_IRQ3ENA                  =   int("0x800", 0)     # Enable channel 3 sys irq*/
        self.cSEQTRIG_MEM_SEQ_CNTRCTRL_ENA              =   int("0x1", 0)           # sequence counter enable */
        self.cSEQTRIG_MEM_SEQ_CNTRCTRL_SYNCN            =   int("0x2", 0)           # sequence counter syncn enable */
        self.cSEQTRIG_MEM_SEQ_CNTRCTRL_EXTEVE           =   int("0x4", 0)           # sequence counter external trigger for sequence update */
        self.cSEQTRIG_MEM_SEQ_CNTRCTRL_ADRSELENA        =   int("0x8", 0)           # sequence address select enable */
        self.cSEQTRIG_MEM_SEQ_CNTRCTRL_ADRSELMOD        =   int("0x10", 0)          # address update mode (1 single shoot, 0 continuous) */
        self.cSEQTRIG_MEM_SEQ_CNTRCTRL_RELOAD           =   int("0x20", 0)          # Reload counter */
        self.cSEQTRIG_MEM_SEQ_CNTRCTRL_CHN0_INTVALENA   =   int("0x100", 0)         # interval enable for chn0 (Chn0Trig = 1 for Tim0 < t <= Tim1) */
        self.cSEQTRIG_MEM_SEQ_CNTRCTRL_CHN1_INTVALENA   =   int("0x200", 0)         # interval enable for chn0 (Chn1Trig = 1 for Tim0 < t <= Tim1) */
        self.cSEQTRIG_MEM_SEQ_CNTRCTRL_CHN2_INTVALENA   =   int("0x400", 0)         # interval enable for chn0 (Chn2Trig = 1 for Tim0 < t <= Tim1) */
        self.cSEQTRIG_MEM_SEQ_CNTRCTRL_CHN3_INTVALENA   =   int("0x800", 0)         # interval enable for chn0 (Chn3Trig = 1 for Tim0 < t <= Tim1) */
        self.cSEQTRIG_MEM_SEQ_CHNTIM_ENA                =   int("0x80000000", 0)    # channel tim enable */
        #--------------------------------------------------------------------------
        # FUsb Configuration
        #--------------------------------------------------------------------------
        self.Rad_FUsbCfg_Mask                      =   int(1)
        self.Rad_FUsbCfg_ChnEna                    =   int(255)
        self.Rad_FUsbCfg_DatSiz                    =   int(1024)
        self.Rad_FUsbCfg_WaitLev                   =   int(1024 + 512)
        #--------------------------------------------------------------------------
        # Constants for power supply
        #--------------------------------------------------------------------------
        self.cPWR_INT_P1_ON         =   1
        self.cPWR_INT_P2_ON         =   2
        self.cPWR_INT_P3_ON         =   4
        self.cPWR_INT_ON            =   7
        self.cPWR_INT_OFF           =   0

        self.cPWR_RF_P1_ON          =   1
        self.cPWR_RF_P2_ON          =   2
        self.cPWR_RF_P3_ON          =   4
        self.cPWR_RF_ON             =   7
        self.cPWR_RF_OFF            =   0



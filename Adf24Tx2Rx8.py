# ADF24Tx2RX8 -- Class for 24-GHz Radar
#
# Copyright (C) 2015-11 Inras GmbH Haderer Andreas
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.
#import  src.cmd_modules.Radarbook   as Radarbook
import  Radarbook   as Radarbook
import  SeqTrig     as SeqTrig
import  DevAdf5904  as DevAdf5904
import  DevAdf5901  as DevAdf5901
import  DevAdf4159  as DevAdf4159
import numpy as np

class Adf24Tx2Rx8(Radarbook.Radarbook):

    def __init__(self, stConType, stIpAdr):
        super(Adf24Tx2Rx8, self).__init__(stConType, stIpAdr)

        #>  Object of first receiver (DevAdf5904 class object)
        self.Adf_Rx1                =   [];
        #>  Object of second receiver (DevAdf5904 clas object)
        self.Adf_Rx2                =   [];
        #>  Object of transmitter (DevAdf5901 class object)
        self.Adf_Tx                 =   [];
        #>  Object of transmitter Pll (DevAdf4159 class object)
        self.Adf_Pll                    =   [];

        self.Rf_USpiCfg_Mask            =   1;
        self.Rf_USpiCfg_Pll_Chn         =   0;
        self.Rf_USpiCfg_Tx_Chn          =   1;
        self.Rf_USpiCfg_Rx1_Chn         =   2;
        self.Rf_USpiCfg_Rx2_Chn         =   3;

        self.Rf_Adf5904_FreqStrt        =   24.125e9;
        self.Rf_Adf5904_RefDiv          =   1;
        self.Rf_Adf5904_SysClk          =   80e6;

        self.Rf_fStrt                   =   76e9;
        self.Rf_fStop                   =   77e9;
        self.Rf_TRampUp                 =   256e-6;
        self.Rf_TRampDo                 =   256e-6;

        self.Rf_VcoDiv                  =   2;

        self.stRfVers                   =   '2.0.1';

        objSeqTrig                      =   SeqTrig.SeqTrig(80e6);
        self.SeqCfg                     =   objSeqTrig.ContUnifM1(1e-3);

        # Initialize Receiver
        dUSpiCfg                        =   dict()
        dUSpiCfg                        =   {   "Mask"          : self.Rf_USpiCfg_Mask,
                                                "Chn"           : self.Rf_USpiCfg_Rx1_Chn
                                            }
        self.Adf_Rx1                    =   DevAdf5904.DevAdf5904(self, dUSpiCfg)

        dUSpiCfg                        =   dict()
        dUSpiCfg                        =   {   "Mask"          : self.Rf_USpiCfg_Mask,
                                                "Chn"           : self.Rf_USpiCfg_Rx2_Chn
                                            }
        self.Adf_Rx2                    =   DevAdf5904.DevAdf5904(self, dUSpiCfg)
        dUSpiCfg                        =   dict()
        dUSpiCfg                        =   {   "Mask"          : self.Rf_USpiCfg_Mask,
                                                "Chn"           : self.Rf_USpiCfg_Tx_Chn
                                            }

        self.Adf_Tx                     =   DevAdf5901.DevAdf5901(self, dUSpiCfg);

        dUSpiCfg                        =   dict()
        dUSpiCfg                        =   {   "Mask"          : self.Rf_USpiCfg_Mask,
                                                "Chn"           : self.Rf_USpiCfg_Pll_Chn
                                            }
        self.Adf_Pll                    =   DevAdf4159.DevAdf4159(self, dUSpiCfg)


    # DOXYGEN ------------------------------------------------------
    #> @brief Get Version information of Adf24Tx2Rx8 class
    #>
    #> Get version of class
    #>      - Version string is returned as string
    #>
    #> @return  Returns the version string of the class (e.g. 0.5.0)
    def     RfGetVers(self):
        return obj.stRfVers

    def     RfGetChipSts(self):
        lChip   =   list()
        Val     =   self.Fpga_GetRfChipSts(1)
        print(Val)
        if Val[0] == True:
            Val     =   Val[1]
            if len(Val) > 2:
                if Val[0] == 202:
                    lChip.append(('Adf4159 PLL', 'No chip information available'))
                    lChip.append(('Adf5901 TX', 'No chip information available'))
                    lChip.append(('Adf5904 RX1', 'No chip information available'))
                    lChip.append(('Adf5904 RX2', 'No chip information available'))
        return lChip

    # DOXYGEN ------------------------------------------------------
    #> @brief Set attribute of class object
    #>
    #> Sets different attributes of the class object
    #>
    #> @param[in]     stSel: String to select attribute
    #>
    #> @param[in]     Val: value of the attribute (optional); can be a string or a number
    #>
    #> Supported parameters
    #>              - Currently no set parameter supported
    def RfSet(self, *varargin):
        if len(varargin) > 0:
            stVal   =   varargin[0]

    # DOXYGEN ------------------------------------------------------
    #> @brief Get attribute of class object
    #>
    #> Reads back different attributs of the object
    #>
    #> @param[in]   stSel: String to select attribute
    #>
    #> @return      Val: value of the attribute (optional); can be a string or a number
    #>
    #> Supported parameters
    #>      -   <span style="color: #ff9900;"> 'TxPosn': </span> Array containing positions of Tx antennas
    #>      -   <span style="color: #ff9900;"> 'RxPosn': </span> Array containing positions of Rx antennas
    #>      -   <span style="color: #ff9900;"> 'ChnDelay': </span> Channel delay of receive channels
    def RfGet(self, *varargin):
        if len(varargin) > 0:
            stVal       = varargin[0]
            if stVal == 'TxPosn':
                Ret     =   np.zeros(2)
                Ret[0]  =   0
                Ret[1]  =   9.325e-3
                return Ret
            elif stVal == 'RxPosn':
                Ret     =   np.arange(8)
                Ret     =   Ret*6.2170e-3 + 24.798e-3
                return Ret
            elif stVal == 'ChnDelay':
                # Ret     =   [0, 1, 2, 3, 2, 3, 0, 1].';
                Ret     =   np.zeros(8)
                Ret[1]  =   1
                Ret[2]  =   2
                Ret[3]  =   3
                Ret[4]  =   2
                Ret[5]  =   3
                Ret[6]  =   0
                Ret[7]  =   1
                return  Ret
            elif stVal == 'B':
                Ret     =   (self.Rf_fStop - self.Rf_fStrt)
                return  Ret
            elif stVal == 'kf':
                Ret     =   (self.Rf_fStop - self.Rf_fStrt)/self.Rf_TRampUp
                return  Ret
            elif stVal == 'kfUp':
                Ret     =   (self.Rf_fStop - self.Rf_fStrt)/self.Rf_TRampUp
                return  Ret
            elif stVal == 'kfDo':
                Ret     =   (self.Rf_fStop - self.Rf_fStrt)/self.Rf_TRampDo
                return  Ret
            elif stVal == 'fc':
                Ret     =   (self.Rf_fStop + self.Rf_fStrt)/2
                return  Ret
        return -1

    # DOXYGEN ------------------------------------------------------
    #> @brief Enable all receive channels
    #>
    #> Enables all receive channels of frontend
    #>
    #>
    #> @note: This command calls the Adf4904 objects Adf_Rx1 and Adf_Rx2 without altering the class settings
    #>        In the default configuration all Rx channels are enabled. The configuration of the objects can be changed before
    #>        calling the RxEna command.
    #>
    #> @code
    #> CfgRx1.Rx1      =   0;
    #> Brd.Adf_Rx1.SetCfg(CfgRx1);
    #> CfgRx2.All      =   0;
    #> Brd.Adf_Rx2.SetCfg(CfgRx2);
    #> @endcode
    #>  In the above example Chn1 of receiver 1 is disabled and all channels of receiver Rx2 are disabled
    def     RfRxEna(self):
        self.RfAdf5904Ini(1);
        self.RfAdf5904Ini(2);

    # DOXYGEN ------------------------------------------------------
    #> @brief Configure receivers
    #>
    #> Configures selected receivers
    #>
    #> @param[in]   Mask: select receiver: 1 receiver 1; 2 receiver 2
    #>
    def     RfAdf5904Ini(self, Mask):
        if Mask == 1:
            self.Adf_Rx1.Ini();
            if self.DebugInf > 10:
                print('Rf Initialize Rx1 (ADF5904)')
        elif Mask == 2:
            self.Adf_Rx2.Ini();
            if self.DebugInf > 10:
                print('Rf Initialize Rx2 (ADF5904)')

        else:
            pass

    # DOXYGEN ------------------------------------------------------
    #> @brief Configure registers of receiver
    #>
    #> Configures registers of receivers
    #>
    #> @param[in]   Mask: select receiver: 1 receiver 1; 2 receiver 2
    #>
    #> @param[in]   Data: register values
    #>
    #> @note Function is obsolete in class version >= 1.0.0: use function Adf_Rx1.SetRegs() and Adf_Rx2.SetRegs() to configure receiver
    def     RfAdf5904SetRegs(self, Mask, Data):
        if Mask == 1:
            self.Adf_Rx1.SetRegs(Data)
            if self.DebugInf > 10:
                print('Rf Initialize Rx1 (ADF5904)')
        elif Mask == 2:
            self.Adf_Rx2.SetRegs(Data);
            if self.DebugInf > 10:
                print('Rf Initialize Rx2 (ADF5904)')
        else:
            pass

    # DOXYGEN ------------------------------------------------------
    #> @brief Configure registers of transmitter
    #>
    #> Configures registers of transmitter
    #>
    #> @param[in]   Mask: select receiver: 1 transmitter 1
    #>
    #> @param[in]   Data: register values
    #>
    #> @note Function is obsolete in class version >= 1.0.0: use function Adf_Tx.SetRegs() to configure transmitter
    def     RfAdf5901SetRegs(self, Mask, Data):
        if Mask == 1:
            self.Adf_Tx.SetRegs(Data);


    # DOXYGEN ------------------------------------------------------
    #> @brief Configure registers of PLL
    #>
    #> Configures registers of PLL
    #>
    #> @param[in]   Mask: select receiver: 1 transmitter 1
    #>
    #> @param[in]   Data: register values
    #>
    #> @note Function is obsolete in class version >= 1.0.0: use function Adf_Pll.SetRegs() to configure PLL
    def     RfAdf4159SetRegs(self, Mask, Data):
        Data                =   Data.flatten(1)

        dUSpiCfg["Mask"]    =   self.Rf_USpiCfg_Mask
        dUSpiCfg["Chn"]     =   self.Rf_USpiCfg_Pll_Chn
        Ret                 =   self.Fpga_SetUSpiData(dUSpiCfg, Data);
        return Ret

    # DOXYGEN -------------------------------------------------
    #> @brief Displays status of frontend in Matlab command window
    #>
    #> Display status of frontend in Matlab command window
    def     BrdDispSts(self):
        self.BrdDispInf()
        self.Fpga_DispRfChipSts(1)

    # DOXYGEN ------------------------------------------------------
    #> @brief Enable transmitter
    #>
    #> Configures TX device
    #>
    #> @param[in]   TxChn
    #>                  - 0: off
    #>                  - 1: Transmitter 1 on
    #>                  - 2: Transmitter 2 on
    #> @param[in]   TxPwr: Power register setting 0 - 256; only 0 to 100 has effect
    #>
    #>
    def     RfTxEna(self, TxChn, TxPwr):
        TxChn       =   (TxChn % 3)
        TxPwr       =   (TxPwr % 2**8)
        if self.DebugInf > 10:
            stOut   =   "Rf Initialize Tx (ADF5901): Chn: " + str(TxChn) + " | Pwr: " + str(TxPwr)
            print(stOut)
        dCfg            =   dict()
        dCfg["TxChn"]   =   TxChn
        dCfg["TxPwr"]   =   TxPwr
        self.Adf_Tx.SetCfg(dCfg)
        self.Adf_Tx.Ini()


    def     RfMeas(self, *varargin):

        ErrCod      =   0
        if len(varargin) > 1:
            stMod       =   varargin[0]

            if stMod == 'ExtTrigUp':
                print('Simple Measurement Mode: ExtTrigUp')
                dCfg            =   varargin[1]

                if not ('fStrt' in dCfg):
                    print('RfMeas: fStrt not specified!')
                    ErrCod      =   -1
                if not ('fStop' in dCfg):
                    print('RfMeas: fStop not specified!')
                    ErrCod      =   -1
                if not ('TRampUp' in dCfg):
                    print('RfMeas: TRampUp not specified!')
                    ErrCod      =   -1
                if not ('NrFrms' in dCfg):
                    print('RfMeas: NrFrms not specified!')
                    ErrCod      =   -1
                if not ('N' in dCfg):
                    print('RfMeas: N not specified!')
                    ErrCod      =   -1
                if not ('TInt' in dCfg):
                    print('RfMeas: TInt not specified!')
                    ErrCod      =   -1

                dCfg                =   self.ChkMeasCfg(dCfg);

                self.Rf_fStrt       =   dCfg["fStrt"]
                self.Rf_fStop       =   dCfg["fStop"]
                self.Rf_TRampUp     =   dCfg["TRampUp"]


                if 'SynthesizerCfg' in dCfg:
                    if dCfg["SynthesizerCfg"] > 0:
                        # Configure ADF4159 PLL
                        dCfgAdf4951                 =   dict()
                        dCfgAdf4951["fStrt"]        =   dCfg["fStrt"]
                        dCfgAdf4951["fStop"]        =   dCfg["fStop"]
                        dCfgAdf4951["TRampUp"]      =   dCfg["TRampUp"]
                        self.RfAdf4159Ini(dCfgAdf4951);
                else:
                    # Configure ADF4159 PLL
                    dCfgAdf4951                     =   dict()
                    dCfgAdf4951["fStrt"]            =   dCfg["fStrt"]
                    dCfgAdf4951["fStop"]            =   dCfg["fStop"]
                    dCfgAdf4951["TRampUp"]          =   dCfg["TRampUp"]
                    self.RfAdf4159Ini(dCfgAdf4951);

                CicIni  =   True
                if CicIni in dCfg:
                    if CicIni > 0:
                        CicIni  =   True
                    else:
                        CicIni  =   False


                self.Set('NrFrms', 8*dCfg["NrFrms"])
                # Calculate Sampling Rate
                N       =   dCfg["N"];
                Ts      =   dCfg["TRampUp"]/N

                if CicIni:
                    fs      =   1/Ts
                    Div     =   np.floor(20e6/fs)

                    if Div < 1:
                        Div     =   1
                    self.CfgCicFilt(Div)
                    self.Set('ClkDiv', 1)
                else:
                    fs      =   self.Get('fs')
                    Ts      =   1/fs
                    Div     =   self.Get('Div')

                self.Set('N', N)

                self.Rad_FrmCtrlCfg_RegChnCtrl   =   self.cFRMCTRL_REG_CH0CTRL_FRMCNTRENA + self.cFRMCTRL_REG_CH0CTRL_WAITENA + self.cFRMCTRL_REG_CH0CTRL_GLOBWAITENA
                self.BrdSampIni()

                MeasTim         =   dCfg["TInt"]

                IniEve          =   1
                if 'IniEve' in dCfg:
                    IniEve      =   dCfg["IniEve"]

                IniTim          =   2e-3
                if 'IniTim' in dCfg:
                    IniTim  =   dCfg["IniTim"]

                MeasEve         =   0
                if 'ExtEve' in dCfg:
                    MeasEve     =   dCfg["ExtEve"]
                    if dCfg["ExtEve"] > 0:
                        MeasTim     =   dCfg["TRampUp"] + 100e-6

                # Parameters that are used for Doppler processing
                MeasTrigPll         =   1
                IniTrigPll          =   0
                if 'MeasTrigPll' in dCfg:
                    MeasTrigPll     =   dCfg["MeasTrigPll"]
                if 'IniTrigPll' in dCfg:
                    TIniPll         =   dCfg["IniTrigPll"]

                TimCfg                  =   dict()
                TimCfg["IniEve"]        =   IniEve;                         #   Use ExtEve after Ini phase
                TimCfg["IniTim"]        =   IniTim;                         #   Duration of Ini phase in us
                TimCfg["IniTrigPll"]    =   IniTrigPll;                     #   Trigger PLL in init phase
                TimCfg["MeasEve"]       =   MeasEve;                        #   Use ExtEve after meas phase
                TimCfg["MeasTim"]       =   MeasTim;
                TimCfg["MeasTrigPll"]   =   MeasTrigPll;                    #
                self.BrdSetTim_M1PW(TimCfg);

                if 'Strt' in dCfg:
                    if dCfg["Strt"] > 0:
                        self.BrdAccessData()
                        self.BrdSampStrt()
                else:
                    self.BrdAccessData()
                    self.BrdSampStrt()

            elif stMod == 'ExtTrigUpNp':
                print('Simple Measurement Mode Range ContUnifMx')
                dCfg                =   varargin[1]

                if not ('fStrt' in dCfg):
                    print('RfMeas: fStrt not specified!')
                    ErrCod      =   -1

                if not ('fStop' in dCfg):
                    print('RfMeas: fStop not specified!')
                    ErrCod      =   -1

                if not ('TRampUp' in dCfg):
                    print('RfMeas: TRampUp not specified!')
                    ErrCod      =   -1

                if not ('NrFrms' in dCfg):
                    print('RfMeas: NrFrms not specified!')
                    ErrCod      =   -1

                if not ('N' in dCfg):
                    print('RfMeas: N not specified!')
                    ErrCod      =   -1

                if not ('TInt' in dCfg):
                    print('RfMeas: TInt not specified!')
                    ErrCod      =   -1

                if not ('Np' in dCfg):
                    print('RfMeas: TInt not specified!')
                    ErrCod      =   -1

                dCfg            =   self.ChkMeasCfg(dCfg)

                self.Rf_fStrt       =   dCfg["fStrt"]
                self.Rf_fStop       =   dCfg["fStop"]
                self.Rf_TRampUp     =   dCfg["TRampUp"]

                if 'SynthesizerCfg' in dCfg:
                    if dCfg["SynthesizerCfg"] > 0:
                        # Configure ADF4159 PLL
                        dCfgAdf4951             =   dict()
                        dCfgAdf4951["fStrt"]    =   dCfg["fStrt"]
                        dCfgAdf4951["fStop"]    =   dCfg["fStop"]
                        dCfgAdf4951["TRampUp"]  =   dCfg["TRampUp"]
                        self.RfAdf4159Ini(dCfgAdf4951);
                else:
                    # Configure ADF4159 PLL
                    dCfgAdf4951             =   dict()
                    dCfgAdf4951["fStrt"]    =   dCfg["fStrt"]
                    dCfgAdf4951["fStop"]    =   dCfg["fStop"]
                    dCfgAdf4951["TRampUp"]  =   dCfg["TRampUp"]
                    self.RfAdf4159Ini(dCfgAdf4951);



                CicIni  =   True
                if CicIni in dCfg:
                    if CicIni > 0:
                        CicIni  =   True
                    else:
                        CicIni  =   False

                self.Set('NrFrms', 8*dCfg["NrFrms"]*dCfg["Np"])
                N       =   dCfg["N"];

                if CicIni:
                    # Calculate Sampling Rate
                    Ts      =   dCfg["TRampUp"]/N
                    fs      =   1/Ts
                    Div     =   np.floor(20e6/fs)
                    if Div < 1:
                        Div     = 1
                    # Configure CIC Filter
                    self.CfgCicFilt(Div)
                    self.Set('ClkDiv',1);
                else:
                    fs      =   self.Get('fs')
                    Ts      =   1/fs
                    Div     =   self.Get('ClkDiv')

                self.Set('N', N);


                TWait   =   dCfg["TInt"] - (dCfg["Tp"]*dCfg["Np"])
                if TWait < 1e-3:
                    TWait   =   1e-3

                self.Rad_FrmCtrlCfg_RegChnCtrl   =   self.cFRMCTRL_REG_CH0CTRL_FRMCNTRENA + self.cFRMCTRL_REG_CH0CTRL_WAITENA + self.cFRMCTRL_REG_CH0CTRL_GLOBWAITENA
                self.BrdSampIni()

                IniEve          =   1
                if 'IniEve' in dCfg:
                    IniEve      =   dCfg["IniEve"]

                IniTim          =   2e-3;
                if 'IniTim' in dCfg:
                    IniTim      =   dCfg["IniTim"]

                WaitEve         =   0;
                if 'ExtEve' in dCfg:
                    WaitEve     =   dCfg["ExtEve"]
                    if dCfg["ExtEve"] > 0:
                        TWait       =   0.1e-3
                TimCfg          =   dict()

                TimCfg["IniEve"]    =   IniEve                              #   Use ExtEve after Ini phase
                TimCfg["IniTim"]    =   IniTim                              #   Duration of Ini phase in us
                TimCfg["MeasTim"]   =   dCfg["Tp"]
                TimCfg["MeasNp"]    =   dCfg["Np"]
                TimCfg["WaitEve"]   =   WaitEve
                TimCfg["WaitTim"]   =   TWait

                self.BrdSetTim_MxPW(TimCfg);

                if 'Strt' in dCfg:
                    if dCfg["Strt"] > 0:
                        self.BrdAccessData()
                        self.BrdSampStrt()
                else:
                    self.BrdAccessData()
                    self.BrdSampStrt()

        return ErrCod


    # DOXYGEN ------------------------------------------------------
    #> @brief Reset frontend
    #>
    #> Reset frontend; Disables and enabled supply to reset frontend
    #>
    def     RfRst(self):
        self.BrdPwrDi()
        self.BrdPwrEna()

    # DOXYGEN ------------------------------------------------------
    #> @brief Initialize PLL with selected configuration
    #>
    #> Configures PLL
    #>
    #> @param[in]   Cfg: structure with PLL configuration
    #>      -   <span style="color: #ff9900;"> 'fStrt': </span> Start frequency in Hz
    #>      -   <span style="color: #ff9900;"> 'fStrt': </span> Stop frequency in Hz
    #>      -   <span style="color: #ff9900;"> 'TRampUp': </span> Upchirp duration in s
    #>
    #> %> @note Function is obsolete in class version >= 1.0.0: use function Adf_Pll.SetCfg() and Adf_Pll.Ini()
    def     RfAdf4159Ini(self, Cfg):
        self.Adf_Pll.SetCfg(Cfg);
        self.Adf_Pll.Ini();

    def     BrdSetTim_M1PW(self, dCfg):

            fSeqTrig                =   80e6/self.Rad_ClkDiv;
            Seq                     =   SeqTrig.SeqTrig(fSeqTrig);

            print('BrdSetTim_M1PW')
            SeqTrigCfg              =   dict()
            SeqTrigCfg["Mask"]      =   1
            SeqTrigCfg["Ctrl"]      =   Seq.SEQTRIG_REG_CTRL_IRQ2ENA                                    # Enable interrupt event on channel 2
            SeqTrigCfg["ChnEna"]    =   Seq.SEQTRIG_REG_CTRL_CH0ENA + Seq.SEQTRIG_REG_CTRL_CH1ENA

            # Phase 0: Ini with dummy frame: (caSeq, 'RccCfg', TCfg, Adr, TxChn(Idx)-1);
            if dCfg["IniTrigPll"] > 0:
                if dCfg["IniEve"] > 0:
                    lSeq                        =   Seq.IniSeq('IniExtTrig', dCfg["IniTim"])
                else:
                    lSeq                        =   Seq.IniSeq('IniTrig', dCfg["IniTim"])
            else:
                if dCfg["IniEve"] > 0:
                    lSeq                        =   Seq.IniSeq('IniExt', dCfg["IniTim"])
                else:
                    lSeq                        =   Seq.IniSeq('Ini', dCfg["IniTim"])

            # Phase 1: Meas
            if dCfg["MeasTrigPll"] > 0:
                if dCfg["MeasEve"] > 0:
                    lSeq                        =   Seq.AddSeq(lSeq,'RccMeasWait', dCfg["MeasTim"], 1, 0)
                else:
                    lSeq                        =   Seq.AddSeq(lSeq,'RccMeas', dCfg["MeasTim"], 1, 0)
            else:
                if dCfg["MeasEve"] > 0:
                    lSeq                        =   Seq.AddSeq(lSeq,'MeasWait', dCfg["MeasTim"], 1, 0)
                else:
                    lSeq                        =   Seq.AddSeq(lSeq,'Meas', dCfg["MeasTim"], 1, 0)
            SeqTrigCfg["Seq"]               =   lSeq

            self.SeqCfg                     =   SeqTrigCfg

            self.Fpga_SeqTrigRst(self.SeqCfg["Mask"]);
            NSeq        =   len(self.SeqCfg["Seq"]);
            if self.DebugInf > 0:
                print('Run SeqTrig: ', NSeq, ' Entries')
            Tmp     =   self.SeqCfg["Seq"]
            for Idx in range (0, NSeq):
                self.Fpga_SeqTrigCfgSeq(self.SeqCfg["Mask"], Idx, self.SeqCfg["Seq"][Idx])


    def     BrdSetTim_MxPW(self, dCfg):

        fSeqTrig                        =   80e6/self.Rad_ClkDiv
        Seq                             =   SeqTrig.SeqTrig(fSeqTrig)

        print('BrdSetTim_MxPW')

        SeqTrigCfg                      =   dict()
        SeqTrigCfg["Mask"]              =   1
        SeqTrigCfg["Ctrl"]              =   Seq.SEQTRIG_REG_CTRL_IRQ2ENA;                       # Enable interrupt event on channel 2
        SeqTrigCfg["ChnEna"]            =   Seq.SEQTRIG_REG_CTRL_CH0ENA + Seq.SEQTRIG_REG_CTRL_CH1ENA;

        # Phase 0: Ini with dummy frame: (caSeq, 'RccCfg', TCfg, Adr, TxChn(Idx)-1);
        if dCfg["IniEve"] > 0:
            lSeq                        =   Seq.IniSeq('IniExt', dCfg["IniTim"])
        else:
            lSeq                        =   Seq.IniSeq('Ini', dCfg["IniTim"])
        # Phase 2: Meas
        lSeq                            =   Seq.AddSeq(lSeq,'RccMeasN', dCfg["MeasTim"], 1, 2, dCfg["MeasNp"], 0)
        if dCfg["WaitEve"] > 0:
            lSeq                        =   Seq.AddSeq(lSeq,'WaitEve', dCfg["WaitTim"], 1, 0)
        else:
            lSeq                        =   Seq.AddSeq(lSeq,'Wait', dCfg["WaitTim"], 1, 0)
        SeqTrigCfg["Seq"]               =   lSeq;

        self.SeqCfg                     =   SeqTrigCfg;

        self.Fpga_SeqTrigRst(self.SeqCfg["Mask"]);
        NSeq        =   len(self.SeqCfg["Seq"]);
        if self.DebugInf > 0:
            print('Run SeqTrig: ', NSeq, ' Entries')
        Tmp     =   self.SeqCfg["Seq"]
        for Idx in range (0, NSeq):
            self.Fpga_SeqTrigCfgSeq(self.SeqCfg["Mask"], Idx, self.SeqCfg["Seq"][Idx])


    # DOXYGEN ------------------------------------------------------
    #> @brief Configure CIC filter for clock divider
    #>
    #> Configure CIC filter: Filter transfer function is adjusted to sampling rate divider
    #>
    #> @param[in] Div:
    def     CfgCicFilt(self, Div):
        if Div >= 16:
            self.Set('CicEna')
            self.Set('CicR',Div)
            self.Set('CicDelay',16)
            self.Set('CicStages',4)
        elif Div >= 8:
            self.Set('CicEna')
            self.Set('CicR',Div)
            self.Set('CicDelay',8)
            self.Set('CicStages',4)
        elif Div >= 4:
            self.Set('CicEna')
            self.Set('CicR',Div)
            self.Set('CicDelay',4)
            self.Set('CicStages',4)
        elif Div >= 2:
            self.Set('CicEna')
            self.Set('CicR',Div)
            self.Set('CicDelay',2)
            self.Set('CicStages',4)
        else:
            self.Set('CicDi')


    # DOXYGEN ------------------------------------------------------
    #> @brief Check measurement configuration
    #>
    #> Check measurement configuration structure
    #>
    #> @param[in] Cfg:
    def     ChkMeasCfg(self, dCfg):

        if 'IniEve' in dCfg:
            IniEve  =   np.floor(dCfg["IniEve"])
            IniEve  =   (IniEve % 2)
            if IniEve != dCfg["IniEve"]:
                print("Adf24Tx2Rx8: IniEve set to ", IniEve)
            dCfg["IniEve"]  =   IniEve;

        if 'ExtEve' in dCfg:
            ExtEve  =   np.floor(dCfg["ExtEve"])
            ExtEve  =   (ExtEve % 2)
            if ExtEve != dCfg["ExtEve"]:
                print("AdfTx2Rx8: ExtEve set to ", ExtEve)
            dCfg["ExtEve"]      =   ExtEve

        if 'N' in dCfg:
            N   =   np.ceil(dCfg["N"]/8)*8
            if (N != dCfg["N"]):
                print("AdfTx2Rx8: N must be a mulitple of 8 -> Set N to ", N)
            if N > 4096 - 128:
                N   =   4096 - 128
                print("AdfTx2Rx8: N to large -> Set N to ", N)
            dCfg["N"]   =   N
            if  N < 8:
                N   =   8
                print("AdfTx2Rx8: N to small -> Set N to ", N)

        # Check number of repetitions: standard timing modes can only can be used with 256 repttions
        # Np must be greater or equal to 1 and less or equal than 256
        if 'Np' in dCfg:
            Np  =   np.ceil(dCfg["Np"])
            if Np < 1:
                Np  =   1
            if Np > 256:
                Np  =   256

            if Np != dCfg["Np"]:
                print("AdfTx2Rx8: Np -> Set Np to ", Np)
            dCfg["Np"]   =   Np

        # Check number of frames: at least one frame must be measured
        if 'NrFrms' in dCfg:
            dCfg["NrFrms"]  =   np.ceil(dCfg["NrFrms"])
            if dCfg["NrFrms"] < 1:
                dCfg["NrFrms"]  =   1
                print("AdfTx2Rx8: NrFrms < 1 -> Set to 1")


        # Initialization time (used to generate dummy frame and reset signal processing chain and data interface)
        if 'IniTim' in dCfg:
            IniEve  =   1
            if 'IniEve' in dCfg:
                IniEve      =   dCfg["IniEve"]
            # If external event is programmed after init, a too long ini time can result that the event is missed
            if (IniEve > 0) and (dCfg["IniTim"] > 5e-3):
                print("Adf24Tx2Rx8: Trigger Event could be missed (Meas does not start)")

        # Tx Field: SeqTrig MMP < 2.0.0 support 16 entries in the sequence table:
        if 'TxSeq' in dCfg:
            TxSeq   =   dCfg["TxSeq"]
            TxSeq   =   TxSeq.flatten(1)
            NSeq    =   len(TxSeq)
            if NSeq > 16:
                print("Adf24Tx2Rx8: TxSeq to long -> limit to 16")
                TxSeq   =   TxSeq[0:16]
            if NSeq < 1:
                TxSeq   =   0
                print("Adf24Tx2Rx8: TxSeq empty -> Set to 0")
            dCfg["TxSeq"]   =   TxSeq
        return dCfg
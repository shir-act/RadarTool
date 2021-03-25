# Mimo77 -- Class for 77-GHz Radar with Waveguide transition
#
# Copyright (C) 2015-11 Inras GmbH Haderer Andreas
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

# Version 1.0.1
#     Allow setting device index in constructor

# Version 1.1.1
# Correct disabling of interrupts

# Version 1.1.2
# Add CfgTim + 5 us to avaoid miss of trigger signal

#Version  1.1.3
# Automatically set timeout for USB (required for Windows)
# Set number of frames to 0 (RadServe transmits)

import  Radarbook as Radarbook
import  sys
import  numpy     as np
import  SeqTrig   as SeqTrig

# DOXYGEN ------------------------------------------------------
#> @brief Class constructor
#>
#> Construct a class object to connect to the baseband board with Mimo77 frontend.
#>
#> @param[in]     stConType: Connection Type (string)
#>          -   <span style="color: #ff9900;"> 'PNet': </span>: TCP/IP stack with Mex file
#>          -   <span style="color: #ff9900;"> 'Usb': </span>: USB connection
#>          -   <span style="color: #ff9900;"> Tcp': </span>: Matlab TCP/IP stack requires instrumentation and control toolbox
#>
#> @param[in]     stIPAddr: IPAddress of Board '192.168.1.1' (string optional)
#>
#> @return  Returns a object of the class with the desired connection settings
#>
#> e.g. with PNet TCP/IP functions
#>   @code
#>   Brd =   Mimo77L('PNet','192.168.1.1')
#>   @endcode
#> e.g. with Matlab TCP/IP functions (requires instrumentation toolbox)
#>   @code
#>   Brd =   Mimo77L('Tcp','192.168.1.1')
#>   @endcode
#> e.g. with UsbAny driver and USB module
#>   @code
#>   Brd =   Mimo77L('Usb')
#>   @endcode
#>  Version 1.0.1
#>  Correct number of frames
#>  Version 1.0.2
#   - Enable with Connection class
#   - Add set act ramp parameters
#>  Version 1.1.0
#   - Set number of frams for RadServe



class Mimo77L(Radarbook.Radarbook):
    """ Mimo77 class object:
        (c) Haderer Andreas Inras GmbH
    """

    def __init__(self, stConType, stIpAdr, devIdx=0):
        super(Mimo77L, self).__init__(stConType, stIpAdr, devIdx)

        #>  Start frequency
        self.Rf_fStrt           =   0
        #>  Stop frequency
        self.Rf_fStop           =   0
        #>  Upchirp duration
        self.Rf_TRampUp         =   0
        #> Downchirp duration
        self.Rf_TRampDo         =   0

        self.Rf_Rpn7720_Pwr     =   32

        self.stRfVers           =   "1.1.2"

        self.Rf_RccCfg_Mask     =   1

        # Initialize SeqTrig Cfg structure
        objSeqTrig              =       SeqTrig.SeqTrig(80e6);
        self.SeqCfg             =       objSeqTrig.ContUnifM1(1e-3);

        self.Set('NrChn', 8)

    # DOXYGEN ------------------------------------------------------
    #> @brief Get Version information of frontend class
    #>
    #> Get version of class
    #>      - Version string is returned as string
    #>
    #> @return  Returns the version string of the class (e.g. 0.5.0)
    def     RfGetVers(self):
        return  self.stRfVers

    # DOXYGEN -------------------------------------------------
    #> @brief Displays version information in Matlab command window
    #>
    #> Display version of class in Matlab command window
    def RfDispVers(self):
        print("Mimo77L Class Version: ",self.stRfVers)


    def RfSet(self, *varargin):
        if len(varargin):
            if isinstance(varargin[0], str):
                stSel   =   varargin[0]
                if stSel == 'TxPwrAll':
                    self.Rf_Rpn7720_Pwr     =   varargin[1] % 64
            elif isinstance(varargin[0], dict):
                print("Mimo77::RfSet dict")
                pass
            else:
                print("Mimo77::RfSet parameter not recognized")

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
    #>      -   <span style="color: #ff9900;"> 'TxPosn': </span> Positions of transmit anntennas in m <br>
    #>      -   <span style="color: #ff9900;"> 'RxPosn': </span> Positions of receive antennas in m <br>
    #>      -   <span style="color: #ff9900;"> 'ChnDelay': </span> Channel delay shifts<br>
    #>      -   <span style="color: #ff9900;"> 'B': </span> bandwidth of frequency chirp <br>
    #>      -   <span style="color: #ff9900;"> 'kf': </span>  Slope of frequency ramp
    #>      -   <span style="color: #ff9900;"> 'kfUp': </span> Slope of frequency ramp upchirp <br>
    #>      -   <span style="color: #ff9900;"> 'kfDo': </span> Slope of frequency ramp downchirp <br>
    #>      -   <span style="color: #ff9900;"> 'fc': </span> Center frequency <br>
    #>
    #> e.g. Read Tx-Positions
    #>   @code
    #>      Brd =   Mimo77L('PNet','192.168.1.1')
    #>
    #>      Brd.RfGet('TxPosn')
    #>
    #>   @endcode
    def RfGet(self, *varargin):
        if len(varargin) > 0:
            stVal       = varargin[0]
            if stVal == 'TxPosn':
                Ret     =   np.arange(4)
                Ret     =   Ret*13.636e-3 + 25.614e-3
                return Ret
            elif stVal == 'RxPosn':
                Ret     =   np.arange(8)
                Ret     =   Ret*1.948e-3
                return Ret
            elif stVal == 'ChnDelay':
                Ret     =   np.zeros(8)
                Ret[0]  =   0
                Ret[1]  =   1
                Ret[2]  =   2
                Ret[3]  =   3
                Ret[4]  =   0
                Ret[5]  =   1
                Ret[6]  =   2
                Ret[7]  =   3
                return  Ret
            elif stVal == 'B':
                Ret     =   (self.Rf_fStop - self.Rf_fStrt)
                return  Ret
            elif stVal == 'kf':
                print("kf: ", self.Rf_fStop, self.Rf_fStrt, self.Rf_TRampUp)
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
    #> @brief Enable Receive chips
    #>
    #> Function is not used in L-class; receivers are enabled by
    #> default; configuration of receiver is performed in FPGA
    #>
    def RfRxEna(self):
        pass
        # Not used in L-class; receivers are enabled by default
        # Function is only implemented for compatibility with MIMO77 scripts

    # DOXYGEN ------------------------------------------------------
    #> @brief Enable transmit antenna static
    #>
    #> Set static setup for tx antenna and power
    #>
    #> @param[in] TxChn: Transmit antenna to activate 0-4; 0->all off
    #>
    #> @param[in] TxPwr: Output power setting 0..63 (register setting for tranmitter)
    #>                  - 63 maximum output power
    def RfTxEna(self, TxChn, TxPwr):
        TxChn   =   TxChn % 5
        TxPwr   =   TxPwr % 64
        self.Fpga_Mimo77RfTxEna(TxChn, TxPwr)

    # DOXYGEN ------------------------------------------------------
    #> @brief Display status of board
    #>
    #> Function is used to display status of the board
    #>
    def BrdDispSts(self):
        self.BrdDispInf()
        self.Fpga_DispRfChipSts(1)


    # DOXYGEN ------------------------------------------------------
    #> @brief RfMeasurement modes
    #>
    #> Set timing and ramp configuration for the mode
    #>
    #> @param[in] stSel: String to select predefined mode
    #>
    #> @param[in] Cfg: Structure to configure measurement mode
    #>      -   <span style="color: #ff9900;"> 'ExtTrigUp': </span> FMCW measurement mode with uniform timing <br>
    #>          -   Cfg.fStrt       Start frequency in Hz (mandatory)
    #>          -   Cfg.fStop       Stop frequency in Hz (mandatory)
    #>          -   Cfg.TRampUp     Upchirp ramp duration (mandatory)
    #>          -   Cfg.TRampDo     Downchirp ramp duration (mandatory)
    #>          -   Cfg.NrFrms      Number of measured Upchirps (mandatory)
    #>          -   Cfg.N           Desired number of samples N (mandatory)
    #>          -   Cfg.IniEve      Enable disable trigger event after start phase: (default 1)
    #>                              If set to 0, measurement is started automatically
    #>                              If set to 1, Fpga_SeqTrigExtEve starts the measurement
    #>          -   Cfg.IniTim      Time duration of ini phase in s (default 2ms)
    #>                              Can be helpful to delay measurements if initialization takes longer (e.g large USB data frames)
    #>          -   Cfg.CfgTim      Duration for reconfiguration of PLL (default 50us)
    #>          -   Cfg.ExtEve      Wait for external event after measurement frame (default 0)
    #>                              If set to 1, Fpga_SeqTrigExtEve must be called to initiate next measurement
    #>          -   Cfg.Start       Enable disable start of timing in FPGA
    #>
    #>      -   <span style="color: #ff9900;"> 'ExtTrigUpNp': </span> FMCW measurement mode with NP uniform chirps (sequence) <br>
    #>          -   Cfg.fStrt       Start frequency in Hz (mandatory)
    #>          -   Cfg.fStop       Stop frequency in Hz (mandatory)
    #>          -   Cfg.TRampUp     Upchirp ramp duration (mandatory)
    #>          -   Cfg.TRampDo     Downchirp ramp duration (mandatory)
    #>          -   Cfg.NrFrms      Number of sequences (one sequence consists of Np chirps) (mandatory)
    #>          -   Cfg.N           Desired number of samples N (mandatory)
    #>          -   Cfg.Np          Number of subsequent frames Np (mandatory)
    #>          -   Cfg.Tp          Chirp repetition interval (mandatory)
    #>          -   Cfg.TInt        Interval between adjacent sequencies
    #>          -   Cfg.IniEve      Enable disable trigger event after start phase: (default 1)
    #>                              If set to 0, measurement is started automatically
    #>                              If set to 1, Fpga_SeqTrigExtEve starts the measurement
    #>          -   Cfg.IniTim      Time duration of ini phase in s (default 2ms)
    #>                              Can be helpful to delay measurements if initialization takes longer (e.g large USB data frames)
    #>          -   Cfg.CfgTim      Duration for reconfiguration of PLL (default 50us)
    #>          -   Cfg.ExtEve      Wait for external event after a sequence (default 0)
    #>                              If set to 1, Fpga_SeqTrigExtEve must be called to initiate next measurement sequence (Np frames)
    #>          -   Cfg.Start       Enable disable start of timing in FPGA
    #>      -   <span style="color: #ff9900;"> 'ExtTrigUp_TxSeq': </span> FMCW measurement mode with Tx sequence (sequence) <br>
    #>          -   Cfg.fStrt       Start frequency in Hz (mandatory)
    #>          -   Cfg.fStop       Stop frequency in Hz (mandatory)
    #>          -   Cfg.TRampUp     Upchirp ramp duration (mandatory)
    #>          -   Cfg.TRampDo     Downchirp ramp duration (mandatory)
    #>          -   Cfg.NrFrms      Number of sequences (one sequence consists of Np x (Nrentries in TxSeq) chirps) (mandatory)
    #>          -   Cfg.N           Desired number of samples N (mandatory)
    #>          -   Cfg.Np          Number of subsequent frames Np (mandatory)
    #>          -   Cfg.Tp          Chirp repetition interval (mandatory)
    #>          -   Cfg.TxSeq       Tx activation sequence; Array with activation sequence (0-4)
    #>          -   Cfg.TInt        Interval between adjacent sequencies
    #>          -   Cfg.IniEve      Enable disable trigger event after start phase: (default 1)
    #>                              If set to 0, measurement is started automatically
    #>                              If set to 1, Fpga_SeqTrigExtEve starts the measurement
    #>          -   Cfg.IniTim      Time duration of ini phase in s (default 2ms)
    #>                              Can be helpful to delay measurements if initialization takes longer (e.g large USB data frames)
    #>          -   Cfg.CfgTim      Duration for reconfiguration of PLL (default 50us)
    #>          -   Cfg.ExtEve      Wait for external event after a sequence (default 0)
    #>                              If set to 1, Fpga_SeqTrigExtEve must be called to initiate next measurement sequence (Np frames)
    #>          -   Cfg.Start       Enable disable start of timing in FPGA
    def RfMeas(self, *varargin):

        if len(varargin) > 1:
            stMod       =   varargin[0]

            if stMod == "ExtTrigUp":
                # Measurement mode with external trigger
                print("Measurement Mode: ExtTrigUp");

                dCfg             =   varargin[1];

                if  not isinstance(dCfg, dict):
                    print("fatal error", file=sys.stderr)
                    return -1

                if not ('fStrt' in dCfg):
                    print("RfMeas: fStrt not specified!", file=sys.stderr)
                if not ('fStop' in dCfg):
                    print("RfMeas: fStop not specified!", file = sys.stderr)
                if not ('TRampUp' in dCfg):
                    print("RfMeas: TRampUp not specified!", file = sys.stderr)
                if not ('TRampDo' in dCfg):
                    print("RfMeas: TRampDo not specified!", file = sys.stderr)
                if not ('NrFrms' in dCfg):
                    print("RfMeas: NrFrms not specified!", file = sys.stderr)
                if not ('N' in dCfg):
                    print("RfMeas: N not specified!", file = sys.stderr)
                if not ('TInt' in dCfg):
                    print("RfMeas: TInt not specified!", file = sys.stderr)

                print('Check Meas Data')
                dCfg    =   self.ChkMeasCfg(dCfg)

                dCfg["Tx1"]         =   int("11001111", 2)
                dCfg["Tx2"]         =   int("11001111", 2)
                dCfg["Tx3"]         =   int("11001111", 2)
                dCfg["SeqEntr"]     =   1

                # Initialize RCC1010 and External processing call
                self.Fpga_Rcc1010Ini(1, dCfg)

                # Store ramp configuration
                self.Rf_fStrt       =   dCfg["fStrt"]
                self.Rf_fStop       =   dCfg["fStop"]
                self.Rf_TRampUp     =   dCfg["TRampUp"]
                self.Rf_TRampDo     =   dCfg["TRampDo"]

                NrChn               =   self.Get("NrChn")
                self.Set("NrFrms", NrChn*dCfg["NrFrms"])
                self.cNumPackets    =   0

                # Calculate Sampling Rate
                N       =   dCfg["N"]
                Ts      =   dCfg["TRampUp"]/N
                fs      =   1/Ts
                Div     =   np.floor(20e6/fs)
                if Div < 1:
                    Div     = 1

                self.CfgCicFilt(Div)

                self.Set("N", N)
                self.Set("ClkDiv",1)

                # Enable frame counter
                self.Rad_FrmCtrlCfg_RegChnCtrl  =   self.cFRMCTRL_REG_CH0CTRL_FRMCNTRENA + self.cFRMCTRL_REG_CH0CTRL_WAITENA + self.cFRMCTRL_REG_CH0CTRL_GLOBWAITENA;
                self.BrdSampIni()

                # Programm Timing to Board: Nios is used to initialize
                # pattern
                IniEve          =   1
                if ("IniEve" in dCfg):
                    IniEve      =   dCfg["IniEve"]
                IniTim          =   2e-3
                if ("IniTim" in dCfg):
                    IniTim      =   dCfg["IniTim"]
                CfgTim          =   30e-6;
                if ("CfgTim" in dCfg):
                    CfgTim      =   dCfg["CfgTim"]
                MeasEve         =   0
                if ("ExtEve" in dCfg):
                    MeasEve     =   dCfg["ExtEve"]

                dTimCfg             =   dict()
                dTimCfg["IniEve"]   =   IniEve                          #   Use ExtEve after Ini phase
                dTimCfg["IniTim"]   =   IniTim*1e6                      #   Duration of Ini phase in us
                dTimCfg["CfgTim"]   =   CfgTim*1e6                      #   Configuration: Configure RCC for ExtTrig
                dTimCfg["MeasEve"]  =   MeasEve                         #   Use ExtEve after meas phase
                dTimCfg["MeasTim"]  =   dCfg["TInt"]*1e6 - dTimCfg["CfgTim"]

                # Implement check timing funtion
                self.Fpga_SetTimRccM1PW(dTimCfg);

                TimOut                      =   (IniTim + self.cUsbNrTx*self.cMult*dCfg['TInt'] + 2)*1000
                self.Set('UsbTimeout', TimOut)

                self.SeqCfg['Ctrl'] =   0;                              # disable interrupts

                if ("Strt" in dCfg):
                    if dCfg["Strt"] > 0:
                        self.BrdAccessData()
                        self.BrdSampStrt()
                else:
                    self.BrdAccessData()
                    self.BrdSampStrt()

                print("Configuration finished")

            elif stMod == "ExtTrigUpNp":

                print("Measurement Mode: ExtTrigUpNp")

                dCfg             =   varargin[1];

                if not isinstance(dCfg, dict):
                    print("fatal error", file=sys.stderr)
                    return -1

                if not ('fStrt' in dCfg):
                    print("RfMeas: fStrt not specified!", file=sys.stderr)
                if not ('fStop' in dCfg):
                    print("RfMeas: fStop not specified!", file = sys.stderr)
                if not ('TRampUp' in dCfg):
                    print("RfMeas: TRampUp not specified!", file = sys.stderr)
                if not ('TRampDo' in dCfg):
                    print("RfMeas: TRampDo not specified!", file = sys.stderr)
                if not ('NrFrms' in dCfg):
                    print("RfMeas: NrFrms not specified!", file = sys.stderr)
                if not ('N' in dCfg):
                    print("RfMeas: N not specified!", file = sys.stderr)
                if not ('TInt' in dCfg):
                    print("RfMeas: TInt not specified!", file = sys.stderr)
                if not ('Tp' in dCfg):
                    print("RfMeas: Tp not specified!", file = sys.stderr)
                if not ('Np' in dCfg):
                    print("RfMeas: Np not specified!", file = sys.stderr)

                dCfg    =   self.ChkMeasCfg(dCfg)

                dCfg["Tx1"]         =   int("11001111", 2)
                dCfg["Tx2"]         =   int("11001111", 2)
                dCfg["Tx3"]         =   int("11001111", 2)
                dCfg["SeqEntr"]     =   1

                # Initialize RCC1010 and External processing call
                self.Fpga_Rcc1010Ini(1, dCfg)

                self.Rf_fStrt       =   dCfg["fStrt"]
                self.Rf_fStop       =   dCfg["fStop"]
                self.Rf_TRampUp     =   dCfg["TRampUp"]
                self.Rf_TRampDo     =   dCfg["TRampDo"]



                NrChn   =   self.Get("NrChn")
                self.Set("NrFrms", NrChn*dCfg["NrFrms"]*dCfg["Np"])
                self.cNumPackets    =   0

                # Calculate Sampling Rate
                N       =   dCfg["N"]
                Ts      =   dCfg["TRampUp"]/N
                fs      =   1/Ts
                Div     =   np.floor(20e6/fs)
                if Div < 1:
                    Div     = 1;

                # Configure CIC Filter
                self.CfgCicFilt(Div)

                self.Set("N", N)
                self.Set("ClkDiv",1)

                # Configure Timing
                TWait       =   dCfg["TInt"] - (dCfg["Tp"]*dCfg["Np"])
                if TWait < 1e-3:
                    TWait = 1e-3
                    print("Mimo77L: Wait time to short -> Set TWait to : ", TWait)

                self.Rad_FrmCtrlCfg_RegChnCtrl   =   self.cFRMCTRL_REG_CH0CTRL_FRMCNTRENA + self.cFRMCTRL_REG_CH0CTRL_WAITENA + self.cFRMCTRL_REG_CH0CTRL_GLOBWAITENA;
                self.BrdSampIni()

                # Programm Timing to Board: Nios is used to initialize
                # pattern
                IniEve          =   1
                if ("IniEve" in dCfg):
                    IniEve      =   dCfg["IniEve"]
                IniTim          =   2e-3;
                if ("IniTim" in dCfg):
                    IniTim      =   dCfg["IniTim"]
                CfgTim          =   30e-6;
                if ("CfgTim" in dCfg):
                    CfgTim      =   dCfg["CfgTim"]
                WaitEve         =   0
                if ("ExtEve" in dCfg):
                    WaitEve     =   dCfg["ExtEve"]

                dTimCfg             =   dict()
                dTimCfg["IniEve"]   =   IniEve                      #   Use ExtEve after Ini phase
                dTimCfg["IniTim"]   =   IniTim*1e6                  #   Duration of Ini phase in us
                dTimCfg["CfgTim"]   =   CfgTim*1e6                  #   Configuration: Configure RCC for ExtTrig
                dTimCfg["MeasTim"]  =   dCfg["Tp"]*1e6 - dTimCfg["CfgTim"]
                dTimCfg["MeasNp"]   =   dCfg["Np"]
                dTimCfg["WaitEve"]  =   WaitEve
                dTimCfg["WaitTim"]  =   TWait*1e6

                self.Fpga_SetTimRccMxPW(dTimCfg);
                TimOut                      =   (IniTim + self.cUsbNrTx*self.cMult*dCfg['TInt'] + 2)*1000
                self.Set('UsbTimeout', TimOut)

                self.SeqCfg['Ctrl'] =   0;                          # disable interrupts

                if ("Start" in dCfg):
                    if dCfg["Start"] > 0:
                        self.BrdAccessData()
                        self.BrdSampStrt()
                else:
                    self.BrdAccessData()
                    self.BrdSampStrt()

            elif stMod == "ExtTrigUp_TxSeq":
                print("Measurement Mode: ExtTrigUp_TxSeq")


                dCfg             =   varargin[1];

                if not isinstance(dCfg, dict):
                    print("Fatal error in Cfg structure", file=sys.stderr)
                    return -1

                if not ('fStrt' in dCfg):
                    print("RfMeas: fStrt not specified!", file=sys.stderr)
                if not ('fStop' in dCfg):
                    print("RfMeas: fStop not specified!", file = sys.stderr)
                if not ('TRampUp' in dCfg):
                    print("RfMeas: TRampUp not specified!", file = sys.stderr)
                if not ('TRampDo' in dCfg):
                    print("RfMeas: TRampDo not specified!", file = sys.stderr)
                if not ('NrFrms' in dCfg):
                    print("RfMeas: NrFrms not specified!", file = sys.stderr)
                if not ('N' in dCfg):
                    print("RfMeas: N not specified!", file = sys.stderr)
                if not ('TInt' in dCfg):
                    print("RfMeas: TInt not specified!", file = sys.stderr)
                if not ('Tp' in dCfg):
                    print("RfMeas: Tp not specified!", file = sys.stderr)
                if not ('Np' in dCfg):
                    print("RfMeas: Np not specified!", file = sys.stderr)

                dCfg                =   self.ChkMeasCfg(dCfg)

                dCfg["Tx1"]         =   int("11001111", 2)
                dCfg["Tx2"]         =   int("11001111", 2)
                dCfg["Tx3"]         =   int("11001111", 2)
                dCfg["SeqEntr"]     =   5
                dCfg["TxPwr"]       =   self.Rf_Rpn7720_Pwr

                # Initialize RCC1010
                self.Fpga_Rcc1010Ini(2, dCfg)

                self.Rf_fStrt       =   dCfg["fStrt"]
                self.Rf_fStop       =   dCfg["fStop"]
                self.Rf_TRampUp     =   dCfg["TRampUp"]
                self.Rf_TRampDo     =   dCfg["TRampDo"]

                TxSeq               =   dCfg["TxSeq"]
                NEntr               =   len(TxSeq)
                NrChn   =   self.Get("NrChn")

                self.Set("NrFrms", NrChn*dCfg["NrFrms"]*NEntr*dCfg["Np"])
                self.cNumPackets    =   0

                # Calculate Sampling Rate
                N       =   dCfg["N"]
                Ts      =   dCfg["TRampUp"]/N
                fs      =   1/Ts
                Div     =   np.floor(20e6/fs)
                if Div < 1:
                    Div     = 1

                # Configure CIC Filter
                self.CfgCicFilt(Div)

                self.Set("N", N)
                self.Set("ClkDiv",1)


                # Enabel SoftID: to number frames with TXSeq entry
                self.Rad_FrmCtrlCfg_RegChnCtrl   =   self.cFRMCTRL_REG_CH0CTRL_FRMCNTRENA + self.cFRMCTRL_REG_CH0CTRL_WAITENA + self.cFRMCTRL_REG_CH0CTRL_GLOBWAITENA + self.cFRMCTRL_REG_CH0CTRL_SOFTID;
                self.BrdSampIni()

                ExtEve  =   0
                if ("ExtEve" in dCfg):
                    if dCfg["ExtEve"] > 0:
                        ExtEve  =   1

                TxSeqVal        =   self.ConvToSeqWord(TxSeq)

                IniEve          =   1
                if "IniEve" in dCfg:
                    IniEve      =   dCfg["IniEve"]
                IniTim          =   2e-3
                if "IniTim" in dCfg:
                    IniTim      =   dCfg["IniTim"]
                CfgTim          =   30e-6
                if ("CfgTim" in dCfg):
                    CfgTim      =   dCfg["CfgTim"]
                WaitEve         =   0
                if ("ExtEve" in dCfg):
                    WaitEve     =   dCfg["ExtEve"]
                # Check the timing in this mode
                CfgTim          =   dCfg["Tp"] - (dCfg["TRampUp"] + dCfg["TRampDo"] + 5e-6)
                if (CfgTim < 30e-6):
                    CfgTim      =   30e-6
                    dCfg["Tp"]  =   (dCfg["TRampUp"] + dCfg["TRampDo"] + CfgTim)
                    print("Mimo77L: Configuration time to short -> Set Tp to : ", dCfg["Tp"])
                WaitTim         =   dCfg["TInt"] - dCfg["Tp"]*NEntr*dCfg["Np"]
                if WaitTim < 1e-3:
                    WaitTim     =   1e-3;
                    print("Mimo77L: Wait time to short -> Set WaitTim to : ", WaitTim)

                dTimCfg             =   dict()
                dTimCfg["IniEve"]   =   IniEve                      #   Use ExtEve after Ini phase
                dTimCfg["IniTim"]   =   IniTim*1e6                  #   Duration of Ini phase in us
                dTimCfg["CfgTim"]   =   CfgTim*1e6                  #   Configuration: Configure RCC for ExtTrig
                dTimCfg["MeasTim"]  =   dCfg["Tp"]*1e6 - dTimCfg["CfgTim"]
                dTimCfg["MeasNp"]   =   dCfg["Np"]
                dTimCfg["WaitEve"]  =   ExtEve
                dTimCfg["WaitTim"]  =   WaitTim*1e6
                dTimCfg["NTx"]      =   NEntr
                dTimCfg["TxSeq1"]   =   TxSeqVal[0]
                dTimCfg["TxSeq2"]   =   TxSeqVal[1]


                TimOut                      =   (IniTim + self.cUsbNrTx*self.cMult*dCfg['TInt'] + 2)*1000
                self.Set('UsbTimeout', TimOut)

                self.Fpga_SetTimRccMxPaconPW(dTimCfg);

                self.SeqCfg['Ctrl'] =   0;                          # disable interrupts

                if ("Strt" in dCfg):
                    if dCfg["Strt"] > 0:
                        self.BrdAccessData()
                        self.BrdSampStrt()
                else:
                    self.BrdAccessData()
                    self.BrdSampStrt()
            else:
                print("Measurement mode not known")


    # DOXYGEN ------------------------------------------------------
    #> @brief Display last chirp configuration
    #>
    def RfDispCfg(self):
        print("Rf Cfg")
        print("  fStrt:   %d GHz ", (self.Rf_fStrt/1e9))
        print("  fStop:   %d GHz ", (self.Rf_fStop/1e9))
        print("  TUp  :   %d us ", (self.Rf_TRampUp/1e-6))
        print("  TDown:   %d us ", (self.Rf_TRampDo/1e-6))

    # DOXYGEN ------------------------------------------------------
    #> @brief Set Timing RCCM1PW
    #>
    #> Chirp sequence
    #>      (1) Ini phase with dummy frame to reset sampling chain
    #>      (2) Cfg phase: configure RCC
    #>      (3) Meas phase: trigger RCC and measure frame
    #>      Seq: 1[|]2->3[|]2->3[|]->2->3 ....
    #
    #> @param[in] Cfg: configuration structure
    #>              - IniEve: enable external event at end of ini phase
    #>              - IniTim: duration of initialization phase (us)
    #>              - CfgTim: duration of configuration phase (us)
    #>              - MeasEve: enable external event at end of meas
    #>                phase
    #>              - MeasTim: duration of measurement phase
    def Fpga_SetTimRccM1PW(self, dCfg):

        CmdCod      =   int("0x9402", 0);
        FpgaCmd     =   np.array([1, 1, dCfg["IniEve"], dCfg["IniTim"], dCfg["CfgTim"], dCfg["MeasEve"], dCfg["MeasTim"]], dtype='uint32')

        Ret         =   self.CmdSend(0, CmdCod,FpgaCmd);
        Ret         =   self.CmdRecv();
        return      Ret

    #> @brief Set Timing SetTim RccMxPaconPW
    #>
    #> Uniform timing with configuration phase for RCC:
    #>      (1) Ini phase with dummy frame to reset sampling chain
    #>      (2) Cfg phase: configure RCC
    #>      (3) Meas phase: trigger RCC and measure frame with
    #>          automatic number of repetitions
    #>      (4) Wait phase
    #>      Seq: 1[|] {2->3}(Np) -> 4[|] {2->3}(Np) -> 4[|] ...
    #> @param[in] Cfg: configuration structure
    #>              - IniEve: enable external event at end of ini phase
    #>              - IniTim: duration of initialization phase (us)
    #>              - CfgTim: duration of configuration phase (us)
    #>              - MeasTim: duration of measurement phase (us)
    #>              - MeasNp: Number of repetitions <= 256
    #>              - WaitEve: enable external event at end of wait
    #>              - WaitTim: duration of wait phase in us
    def Fpga_SetTimRccMxPW(self, dCfg):

        CmdCod      =   int("0x9402", 0)
        FpgaCmd     =   np.zeros(9, )
        FpgaCmd     =   np.array([1, 2, dCfg["IniEve"], dCfg["IniTim"], dCfg["CfgTim"], dCfg["MeasTim"], dCfg["MeasNp"], dCfg["WaitEve"], dCfg["WaitTim"]], dtype='uint32');

        Ret         =   self.CmdSend(0, CmdCod,FpgaCmd);
        Ret         =   self.CmdRecv();
        return      Ret


    # DOXYGEN ------------------------------------------------------
    #> @brief Set Timing RCCMxPW
    #>
    #> Chirp sequence with different antenna activation
    #>      (1) Ini phase with dummy frame to reset sampling chain
    #>      (2) Cfg phase: configure RCC
    #>      (3_1) Meas phase: trigger RCC and measure frame with
    #>          first antenna activation
    #>      (3_2) Meas phase: trigger RCC and measure frame with
    #>          first antenna activation
    #>      (3_n) Meas phase: trigger RCC and measure frame with
    #>          first antenna activation
    #>      (4) Wait phase
    #>      Seq: 1[|] {2->3_1->2->3_2-> ... -> 2->3_n}(Np) -> 4[|] {2->3_1->2->3_2-> ... -> 2->3_n}(Np) -> 4[|] ...
    #> @param[in] Cfg: configuration structure
    #>              - IniEve: enable external event at end of ini phase
    #>              - IniTim: duration of initialization phase (us)
    #>              - CfgTim: duration of configuration phase (us)
    #>              - MeasTim: duration of measurement phase (us)
    #>              - MeasNp: Number of repetitions <= 256
    #>              - WaitEve: enable external event at end of wait
    #>              - WaitTim: duration of wait phase in us
    #>              - NTx: Number of antenna activations
    #>              - TxSeq1: data containing activation sequence
    #>              - TxSeq2: data containing activation sequence
    def     Fpga_SetTimRccMxPaconPW(self, dCfg):
        CmdCod      =   int("0x9402", 0)
        FpgaCmd     =   np.array([1, 3, dCfg["IniEve"], dCfg["IniTim"],
                                    dCfg["CfgTim"], dCfg["MeasTim"], dCfg["MeasNp"], dCfg["WaitEve"],
                                    dCfg["WaitTim"], dCfg["NTx"], dCfg["TxSeq1"], dCfg["TxSeq2"]], dtype='uint32')

        Ret         =   self.CmdSend(0, CmdCod,FpgaCmd);
        Ret         =   self.CmdRecv();
        return      Ret

    # DOXYGEN ------------------------------------------------------
    #> @brief Initialize RCC1010
    #>
    #> Programm Ramp configuration to RCC and performe calibration
    #>
    #> @param[in] SmartSel: Select initialization
    #> @param[in] Cfg:
    def     Fpga_Rcc1010Ini(self, SmartSel, dCfg):
        CmdCod      =   int("0x9401", 0)
        if (SmartSel == 1):
            FpgaCmd     =   np.array([1, 1, 1, round(dCfg["fStrt"]/1e9 * 2**24), round(dCfg["fStop"]/1e9 * 2**24),
                                            round(dCfg["TRampUp"]/1e-6 * 2**16), round(dCfg["TRampDo"]/1e-6 * 2**16),
                                            dCfg["Tx1"], dCfg["Tx2"], dCfg["Tx3"], dCfg["SeqEntr"]], dtype='uint32')
        else:
            FpgaCmd     =   np.array([1, 2, 1, round(dCfg["fStrt"]/1e9 * 2**24), round(dCfg["fStop"]/1e9 * 2**24),
                                            round(dCfg["TRampUp"]/1e-6 * 2**16), round(dCfg["TRampDo"]/1e-6 * 2**16),
                                            dCfg["Tx1"], dCfg["Tx2"], dCfg["Tx3"], dCfg["SeqEntr"], dCfg["TxPwr"]], dtype='uint32')

        Ret         =   self.CmdSend(0, CmdCod,FpgaCmd);
        Ret         =   self.CmdRecv();
        return      Ret


    def    RfRst(self):
        self.Fpga_SetRccRst(self.Rf_RccCfg_Mask, 2)

    # DOXYGEN ------------------------------------------------------
    #> @brief Reset RCC1010
    #>
    #> Reset RCC1010 delete actual config; make sure that timing unit
    #> is switched off
    #>
    #> @param[in] Mask: Bitmask of RCC1010
    #>
    #> @param[in] Rst:
    #>              - 0 pull low (permanently), Reset is low actice
    #>              - 1 set high (permanently)
    #>              - 2 pulled low and released again
    def     Fpga_SetRccRst(self, Mask, Rst):
        CmdCod      =   int("0x9402", 0)

        FpgaCmd     =   np.zeros(2, dtype='uint32')
        FpgaCmd     =   np.array([Mask, Rst])

        Ret         =   self.CmdSend(0, CmdCod,FpgaCmd);
        Ret         =   self.CmdRecv();
        return      Ret

    # DOXYGEN ------------------------------------------------------
    #> @brief Set static tx configuration
    #>
    #> Static activation of transmitter
    #>
    #> @param[in] TxChn:
    #>              - 0: all antennas off
    #>              - 1-4: activate antenna
    #> @param[in] TxPwr: tx power setting
    #>              - 0-63 transmit power setting
    def     Fpga_Mimo77RfTxEna(self, TxChn, TxPwr):
        CmdCod      =   int("0x9400", 0)

        FpgaCmd     =   np.array([1, 1 ,TxChn, TxPwr], dtype='uint32');

        Ret         =   self.CmdSend(0, CmdCod,FpgaCmd);
        Ret         =   self.CmdRecv();
        return      Ret

    # DOXYGEN ------------------------------------------------------
    #> @brief Convert activation sequence to data words
    #>
    #> Static activation of transmitter; four bit are used for a single sequence;
    #> a maximum of 16 sequences is supported
    #>
    #> @param[in] TxSeq:
    #> @return  TxSeq1, TxSeq2: coded activation sequence
    def ConvToSeqWord(self, TxSeq):
        TxSeq1  =   0
        TxSeq2  =   0
        Shift1  =   1
        Shift2  =   1
        for Idx in range(0,len(TxSeq)):
            if Idx <= 8:
                TxSeq1  =   TxSeq1 + (TxSeq[Idx] % 16)*Shift1
                Shift1  =   Shift1*16
            else:
                TxSeq2  =   TxSeq2 + (TxSeq[Idx] % 16)*Shift2
                Shift2  =   Shift2*16

        Ret     =   np.array([TxSeq1, TxSeq2], dtype='uint32')
        return  Ret

    # DOXYGEN ------------------------------------------------------
    #> @brief Configure CIC filter for clock divider
    #>
    #> Configure CIC filter: Filter transfer function is adjusted to sampling rate divider
    #>
    #> @param[in] Div:
    def CfgCicFilt(self, Div):
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
    def ChkMeasCfg(self, dCfg):

        if ("IniEve" in dCfg):
            IniEve  =   np.floor(dCfg["IniEve"])
            IniEve  =   (IniEve % 2)
            if IniEve != dCfg["IniEve"]:
                print("Mimo77L: IniEve set to ", IniEve)
            dCfg["IniEve"]  =   IniEve

        if ("ExtEve" in dCfg):
            ExtEve  =   np.floor(dCfg["ExtEve"])
            ExtEve  =   (ExtEve % 2)
            if ExtEve != dCfg["ExtEve"]:
                print("Mimo77L: ExtEve set to ", ExtEve)
            dCfg["ExtEve"]  =   ExtEve

        if ("N" in dCfg):
            N   =   np.ceil(dCfg["N"]/8)*8
            if (N != dCfg["N"]):
                print("Mimo77L: N must be a mulitple of 8 -> Set N to ", N)
            if (N > 4096 - 128):
                N   =   4096 - 128
                print("Mimo77L: N to large -> Set N to ", N)
            dCfg["N"]   =   N;
            if  N < 8:
                N   =   8
                print("Mimo77L: N to small -> Set N to ",N)



        # Check number of repetitions: standard timing modes can only can be used with 256 repttions
        # Np must be greater or equal to 1 and less or equal than 256
        if ("Np" in dCfg):
            Np  =   np.ceil(dCfg["Np"])
            if Np < 1:
                Np  =   1
            if Np > 256:
                Np  =   256
            if Np != dCfg["Np"]:
                print("Mimo77L: Np -> Set Np to ", Np)
            dCfg["Np"]  =   Np

        # Check number of frames: at least one frame must be measured
        if ("NrFrms" in dCfg):
            dCfg["NrFrms"]  =   np.ceil(dCfg["NrFrms"])
            if dCfg["NrFrms"] < 1:
                dCfg["NrFrms"]  =   1
                print("Mimo77L: NrFrms < 1 -> Set to 1")

        # Initialization time (used to generate dummy frame and reset signal processing chain and data interface)
        if ("IniTim" in dCfg):
            IniEve  =   1
            if ("IniEve" in dCfg):
                IniEve      =   dCfg["IniEve"]

            # If external event is programmed after init, a too long ini time can result that the event is missed
            if (IniEve > 0) and (dCfg["IniTim"] > 5e-3):
                print("Mimo77L: Trigger Event could be missed (Meas does not start)")


        # Tx Field: SeqTrig MMP < 2.0.0 support 16 entries in the sequence table:
        if ("TxSeq" in dCfg):
            TxSeq   =   dCfg["TxSeq"]
            NSeq    =   len(TxSeq)
            if NSeq > 16:
                print("Mimo77L: TxSeq to long -> limit to 16")
                TxSeq   =   TxSeq[0:16];
            if NSeq < 1:
                TxSeq   =   0
                print("Mimo77L: TxSeq empty -> Set to 0")
            dCfg["TxSeq"]   =   TxSeq;

        return dCfg

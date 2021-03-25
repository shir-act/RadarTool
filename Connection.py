"""This module contains the classes and methods for communication to the RadarLog
   """
# Version 1.0.0
#     Supports RadServe for Radarbook and RadarLog
#     Supports PNet for Radarbook with ARM module

# Version 1.0.1
#     Correct  return value

# Version 1.0.2
# 	  RDL: Added functions from RadarLog
#	  RDL: Get file params by type (with arrays)
#     RDL: Bufsize unified
#     RBK: OpenTcpIpDatCom used in all functions requiring a connection to the dataport
#     RBK: Added function ConSetDatSockTimeout to allow setting of socket timeout for slow measurements

# Version 1.0.3
#     RDL: Use OpenTcpIpDatCom in all functions requiring a connection to DataPort
#     RDL: Added ConSetDatSockTimeout to allow setting the socket timeout for slow measurements
#     RBK: SetFileParam with Strings is working

# Version 1.0.4
#     RDL: Handle double-responses from RadServe
#     RBK: Allow setting device index in constructor

# Version 1.0.5
#     Set max number of simultaneously queued USB transfers
#     Merged class (Radarbook/Radarlog)

# Version 1.0.6
#     Add Parameters to OpenExtensionPort
#     Created PollClosed functions for DataPort, Replay, File

# Version 1.0.7
#     Add function to set usb config timeout

#Version 2.0.0

import  os
import  sys
import  ctypes
import  socket
import  matplotlib.pyplot as plt
import  numpy as np
#import matplotlib.pyplot as plt

class Connection():

    ## Constructor
    def __init__(self, stConType='Usb', stIpAdr='127.0.0.1', devIdx=0):
        self.cType              =   stConType
        self.cIpAddr            =   stIpAdr
        self.cCfgPort           =   8000
        self.cDataPort          =   6000
        self.DebugInf           =   1

        self.cDataOpened        =   -1
        self.cReplay            =   -1
        self.cReplayExt         =   -1
        self.cExtSize           =   0

        self.cOpened            =   -1
        self.cResponseOk        =   1
        self.cResponseMsg       =   2
        self.cResponseInt       =   3
        self.cResponseData      =   4
        self.cResponseDouble    =   5
        self.cArmCmdBegin       =   int('0x6000', 0)
        self.cArmCmdEnd         =   int('0x7FFF', 0)
        self.cFpgaCmdBegin      =   int('0x9000', 0)
        self.cFpgaCmdEnd        =   int('0xAFFF', 0)

        self.cBufSiz            =   256

        self.hCon               =   -1
        self.hConDat            =   -1
        self.hConDatTimeout     =    4
        self.cPortOpen          =   -1
        self.cPortNum           =   0

        self.hConVideo          =  -1
        self.cVideoPort         = 6001
        self.cVideoPortOpen     = -1
        self.cVideoCols         = 0
        self.cVideoRows         = 0
        self.cVideoChn          = 0
        self.cVideoRate         = 0
        self.cVideoSize         = 0
        self.cVideoFrames       = 0

        self.cMult              =   32
        self.cDataPortKeepAlive =   False
        self.cNumPackets         = 0

        self.cUsbNrTx           = 24

        self.cCfgTimeout       =  100
        self.cTimeout           =   -1
        self.ConNew             =   0

        if (devIdx > 0):
            self.SetIndex(devIdx);

    ## Destructor
    def __del__(self):
        # Delete handles if exist
        print('Delete class connection')
        if self.cType == 'RadServe':
            if self.hConDat > 0:
                self.cRadDatSocket.close();
                self.hConDat = -1;
            if self.hConVideo > 0:
                self.cRadVideoSocket.close();
                self.hConVideo = -1;

            self.PollDataPortClosed();
            self.PollFileClosed();
            self.PollReplayClosed();

            if self.hCon > 0:
                self.cRadSocket.close()
                self.hCon   =   -1

    #-------------- cmd functions --------------
    # DOXYGEN ------------------------------------------------------
    #> @brief Build command send to the Radar system
    #>
    #>
    #> @param[in]     Ack: acknowledge flag
    #>
    #> @param[in]     CmdCod: Command code
    #>
    #> @param[in]     Data: Data values
    #>
    def CmdBuild(self, Ack, CmdCod, Data):
        LenData     =   len(Data) + 1
        TxData      =   np.zeros(LenData,dtype= 'uint32')
        TxData[0]   =   (2**24)*Ack + (2**16)*LenData + CmdCod
        TxData[1:]  =   np.uint32(Data)
        return TxData

    # DOXYGEN ------------------------------------------------------
    #> @brief Send command to device
    #>
    #>
    #> @param[in]     Ack: acknowledge flag
    #>
    #> @param[in]     CmdCod: Command code
    #>
    #> @param[in]     Data: Data values
    #>
    def CmdSend(self, Ack, Cod, Data, Open=1):
        #   @function    CmdSend
        #   @author      Haderer Andreas (HaAn)
        #   @date        2013-12-01
        #   @brief       Transmit command to ARM processor

        Cmd             =   self.CmdBuild(Ack,Cod,Data)
        #print("Cmd: ", Cmd)
        Ret             =   []
        if self.cType == 'Usb':
            CmdBytes        =   self.ToUint8(Cmd)
            TxData          =   0
            if self.hCon > -1:
                TxData      =   1
                self.ConNew =   0
            else:
                Dev         =   self.UsbOpen()
                if Dev > 0:
                    self.hCon       =   0
                    TxData          =   1
                    self.ConNew     =   1

            if TxData > 0:
                self.USBnAny('send', np.uint8(CmdBytes), 'uart')

        elif self.cType == 'PNet':
            TxData                  =   0
            if self.hCon > -1:
                TxData              =   1
                self.ConNew         =   0
            else:
                self.hCon       =   self.OpenTcpipCom(self.cIpAddr, self.cCfgPort)
                if self.hCon > -1:
                    TxData          =   1
                    self.ConNew     =   1
            if TxData > 0:
                try:
                    self.cRadSocket.sendall(Cmd)
                except socket.timeout:
                    TxData      =   -1
                    print("Socket timed out")
                except socket.error:
                    TxData      =   -1
                    print("error")
                finally:
                    pass

        elif self.cType == 'RadServe':
            if self.hCon == -1:
                self.hCon       =   self.OpenTcpipCom(self.cIpAddr, self.cCfgPort)
                self.hCon
                if self.hCon == -1:
                    print('Couldn''t connect to RadServe');

            if self.cOpened == -1 and Open == 1:
                # send command to open device on RadServe
                CmdOpen         =   self.CmdBuild(0, int('0x6120',0), [1])
                try:
                    self.cRadSocket.sendall(CmdOpen)
                except socket.timeout:
                    TxData      =   -1
                    print("Socket timed out")
                except socket.error:
                    TxData      =   -1
                    print("error")
                finally:
                    pass
                Ret             =   self.CmdRecv()
                self.cOpened    = 1

            try:
                self.cRadSocket.sendall(Cmd)
            except socket.timeout:
                TxData      =   -1
                print("Socket timed out")
            except socket.error:
                TxData      =   -1
                print("error")
            finally:
                pass

        return Ret

    #   @function       CmdRecv
    #   @author         Haderer Andreas (HaAn)
    #   @date           2013-12-01
    #   @brief          Receive response from baseboard
    def CmdRecv(self, dispError = True):
        Ret         =   []
        if self.cType == 'Usb':
            TxData          =   0
            if self.hCon > -1:
                TxData      =   1
            else:
                print('REC: USB Connection closed previously')
            if TxData > 0:
                RLen        =   self.USBnAny('recv32', np.int32(128), 'uart');
                Header      =   np.double(RLen(1));
                Len         =   np.floor((Header/2**16) % 256)
                if Len < 32:
                    Ret     =   np.double(RLen[1:Len])
                else:
                    Ret         =   1
            if self.ConNew > 0:
                self.UsbClose()
        elif self.cType == 'PNet':
            TxData          =   0
            if self.hCon > -1:
                TxData      =   1
            else:
                print('REC: TCPIP Connection closed previously')
            if TxData > 0:
                #----------------------------------------------------------
                # Read response
                #----------------------------------------------------------
                try:
                    # Receive data from the server and shut down
                    RxBytes         =   self.cRadSocket.recv(4)
                    RxData          =   np.fromstring(RxBytes, dtype='uint32')
                    LenRxData       =   RxData[0]//(2**16)
                    RxBytes         =   self.cRadSocket.recv((LenRxData-1)*4)
                    if len(RxBytes) == ((LenRxData-1)*4):
                        Data        =   np.zeros(LenRxData-1,dtype ='uint32')
                        Data        =   np.fromstring(RxBytes, dtype="uint32")
                        Ret         =   Data
                    else:
                        Ret         =   []
                        print("len(RxBytes) wrong: %d != %d" % (len(RxBytes), (LenRxData-1)*4))
                except socket.timeout:
                    Ret             =   []
                    print("socket timed out")
                except socket.error:
                    Ret             =   []
                finally:
                    if self.ConNew > 0:
                        self.CloseTcpipCom()

        elif self.cType == 'RadServe':
            #print("Cmd Recv RadServe: ", self.hCon)
            if self.hCon > -1:
                Len         =   self.cRadSocket.recv(4)
                Len         =   np.fromstring(Len, dtype='uint32')
                Type        =   Len % 2**16
                Len         =   np.floor(Len/2**16)
                Err         =   0
                if (Len > 1024):
                    Err     =   1
                    Len     =   Len - 1024
                Len         =   Len - 1

                #print("Len: ", Len, "Err: ", Err, "Type:", Type)
                if (Err > 0) and (Len > 0):
                    #print("If first")
                    Ret     =   self.cRadSocket.recv(int(4*Len[0]))
                    if (dispError):
                        print(Ret.decode('ASCII'));
                    Ret     =   Ret.decode('ASCII')
                    #Ret     =   -1
                elif ((((self.cArmCmdBegin <= Type) and (Type <= self.cArmCmdEnd)) or ((self.cFpgaCmdBegin <= Type) and (Type <= self.cFpgaCmdEnd)) ) and (Len > 0)):
                    #print("Elff 1")
                    Ret     =   self.cRadSocket.recv(int(4*Len[0]))
                    Ret     =   np.fromstring(Ret, dtype='uint32')
                elif (Err == 0) and (Type == self.cResponseMsg) and (Len > 0):
                    # handle non error case - TODO !
                    Ret     =   self.cRadSocket.recv(int(4*Len[0]))
                    if (dispError):
                        print(Ret.decode('ASCII'));
                    Ret     =   Ret.decode('ASCII');
                elif (Err == 0) and (Type == self.cResponseOk):
                    Ret     =   0
                elif (Err == 0) and (Type == self.cResponseDouble):
                    Ret     = self.cRadSocket.recv(int(4*Len[0]));
                    Ret     = np.fromstring(Ret, dtype='double');
                elif (Err == 0) and (Type == self.cResponseInt):
                    Ret     =   self.cRadSocket.recv(int(4*Len[0]))
                    Ret     =   np.fromstring(Ret, dtype='uint32')
                elif (Err == 0) and (Type == self.cResponseData):
                    if (Len > 0):
                        Ret     =   self.cRadSocket.recv(4*int(Len))
                        Ret     =   np.fromstring(Ret, dtype='uint32')
                    else:
                        Ret =   []
                else:
                    Ret     =   0
        return Ret

    #------------- Open/Close functions ---------
    # DOXYGEN ------------------------------------------------------
    #> @brief Open connection for the different types of communication
    #>
    #> Opens communication and set hCon parameter if opened
    #>
    def     ConOpen(self):
        if self.cType == 'Usb':
            if self.hCon > -1:
                self.UsbClose()
                self.UsbOpen()
            else:
                self.UsbOpen()
        elif self.cType == 'PNet':
            if self.hCon > -1:
                self.CloseTcpipCom();
                self.OpenTcpipCom(self.cIpAddr, self.cCfgPort)
            else:
                self.OpenTcpipCom(self.cIpAddr, self.cCfgPort)
        elif self.cType == 'RadServe':
            if self.hCon == -1:
                self.OpenTcpipCom(self.cIpAddr, self.cCfgPort);

    def     ConClose(self):
        if self.cType == 'Usb':
            self.UsbClose()
        elif self.cType == 'PNet':
            if self.hCon > -1:
                print('Close connection to ',self.Name)
                self.CloseTcpipCom()
                self.hCon       =   -1
        elif self.cType == 'RadServe':
            if self.hCon > -1:
                self.CloseTcpipCom()
                self.hCon = -1

    def     ConCloseData(self):
        if self.cType == 'Usb':
            self.UsbClose();
        elif self.cType == 'RadServe':
            self.ConCloseDataPort()
        else:
            if self.hConDat > -1:
                print('Close Data connection to ',self.Name)
                self.CloseTcpipDataCom();
                self.hConDat     =   -1;

    def     UsbOpen(self):
        if self.hCon > -1:
            self.UsbClose();
        Dev             =   self.USBnAny('open')
        self.hCon       =   1
        self.hConDat    =   1
        if self.DebugInf > 10:
            print('USB device pointer: ', Dev)

    def     UsbClose(self):
        if self.hCon > -1:
            self.USBnAny('close')
            self.hConDat        =   -1
            self.hCon           =   -1

    # DOXYGEN ------------------------------------------------------
    #> @brief Open TCPIP connection
    #>
    #> Open TCPIP connection
    #>
    #> @param[in]     IpAdr: IP address
    #>
    #> @param[in]     Port: Port number of connection
    #>
    def     OpenTcpipCom(self, IpAdr, Port):
        hCon    =   -1
        if (self.cType == 'PNet') or (self.cType == 'RadServe'):
            try:
                self.cRadSocket         =   socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.cRadSocket.settimeout(4)
                self.cRadSocket.connect((IpAdr, Port))
                hCon            =   1
            except socket.timeout:
                hCon            =   -1
                print("Socket timed out")
            except socket.error:
                hCon            =   -1
                print("error")
            finally:
                pass
        return hCon

    def     CloseTcpipCom(self):
        if self.cType == 'PNet':
            # Use Pnet functions
            if self.hCon > -1:
                self.cRadSocket.close()
                self.hCon   =   -1

    def OpenTcpIpDatCom(self, IpAdr, Port):
        #   @function       OpenTcpipCom.m
        #   @author         Haderer Andreas (HaAn)
        #   @date           2013-12-01
        #   @brief          Open TCPIP connection at given address and port number
        #   @param[in]      IpAdr:  String containing valid IP address; string is not checked
        #   @param[in]      Port:   Port number of connection
        #   @return         tcpCon: Handle to TCP connection
        try:
            self.cRadDatSocket          =   socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.cRadDatSocket.settimeout(self.hConDatTimeout)
            self.cRadDatSocket.connect((IpAdr, Port))
            hConDat            =   1
        except socket.timeout:
            hConDat            =   -1
            print("Socket timed out")
        except socket.error:
            hConDat            =   -1
            print("error")
        finally:
            pass

        return hConDat

    def     CloseTcpipDataCom(self):
        if ((self.cType == 'PNet') or (self.cType == 'RadServe')):
            if self.hConDat > 0:
                self.cRadDatSocket.close()
                self.hConDat     =   -1

    def     OpenTcpIpVideoCom(self, IpAdr, Port):
        if ((self.cType == 'RadServe') and (self.hConVideo == -1)):
            # Use Pnet functions
            #disp('TCP/IP with PNet functions');
            #disp(['Con:', num2str(Port)]);
            try:
                self.cRadVideoSocket  =   socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.cRadVideoSocket.settimeout(None) # receive complete video frame at once
                self.cRadVideoSocket.connect((IpAdr, Port))
                hConVideo        =   1
            except socket.timeout:
                hConVideo        =   -1
                print("Socket timed out")
            except socket.error:
                hConVideo        =   -1
                print("error")
            finally:
                pass
            return hConVideo;

    def     CloseTcpipVideoCom(self):
        if self.hConVideo > -1:
            self.cRadVideoSocket.close()
            hConVideo = -1;

    # ----- file functions --------------
    def     CreateFile(self, stName, Max=-1):
        Len         =   (len(stName) % 4)
        for Idx in range (0, 4-Len):
            stName  =   stName + ' '
        Data        =   np.zeros(int(3 + len(stName)/4 + 1), dtype='uint32')
        Data[0]     =   np.uint32(self.cBufSiz)
        Data[1]     =   np.uint32(self.cMult)
        Data[2]     =   np.uint32(len(stName))
        Data[3:-1]  =   np.fromstring(stName,dtype='uint32')
        Data[int(3+len(stName)/4)]  =   np.uint32(self.cUsbNrTx)
        # create file
        Ret         =   self.CmdSend(0, int('0x6150',0), Data);
        Ret         =   self.CmdRecv();
        Data        =   np.zeros(2,dtype='uint32')
        Data[0]     =   0
        if (Max != -1):
          Data[1]   = np.uint32(Max);
        else:
          Data[1]     =   np.uint32(self.cNumPackets)
        # write file
        Ret         =   self.CmdSend(0, int('0x6151',0), Data)
        Ret         =   self.CmdRecv()

    def     StopFile(self):
        Data        =   np.zeros(1, dtype='uint32')
        Ret         =   self.CmdSend(0, int('0x6152',0), Data)
        Ret         =   self.CmdRecv()
        return Ret

    def     CloseFile(self):
        Data        =   np.zeros(1, dtype='uint32')
        Ret         =   self.CmdSend(0, int('0x6153',0), Data)
        Ret         =   self.CmdRecv()

        self.PollFileClosed();

    def     PollFileClosed(self):
        Ret = 1;
        # poll file closed?
        while (Ret == 1):
            Ret = self.CmdSend(0, int('0x6158',0), np.zeros(1, dtype='uint32'));
            Ret = self.CmdRecv();

    def     ReplayFile(self, stName, FrameIdx=1, WithVideo=0):
        Len         =   (len(stName) % 4)
        for Idx in range (0, 4-Len):
            stName  =   stName + ' '
        Data        =   np.zeros(int(3 + len(stName)/4), dtype='uint32')
        Data[0]     =   np.uint32(self.cMult)
        Data[1]     =   np.uint32(FrameIdx)-1
        Data[2]     =   np.uint32(len(stName))
        Data[3:]    =   np.fromstring(stName,dtype='uint32')
        Ret         =   self.CmdSend(0, int('0x6154',0), Data, 0);
        Port        =   self.CmdRecv();
        if Port > 0:
            self.cPortOpen = 1;
            self.cPortNum = Port;
        else:
            quit();
        if (WithVideo != 0):
            Ret  = self.CmdSend(0, int('0x6157',0), [], 0)
            Ret  = self.CmdRecv();
            if (len(Ret) == 7):
                self.cVideoPort = Ret[0]
                self.cVideoCols = Ret[1]
                self.cVideoRows = Ret[2]
                self.cVideoChn  = Ret[3]
                self.cVideoRate = Ret[5]
                self.cVideoSize = Ret[1]*Ret[2]*Ret[3]
                self.cVideoFrames = Ret[6]
                self.cVideoPort = Ret[0]
                self.cVideoPortOpen = 1
        if Port > 0:
            if self.hConDat == -1:
                # Use Pnet functions
                #disp('TCP/IP with PNet functions');
                #disp(['Con:', num2str(Port)]);
                self.hConDat = self.OpenTcpIpDatCom(self.cIpAddr, Port);
                if self.hConDat == 1:
                    self.cReplay = 1;
        if (WithVideo != 0) and (len(Ret) == 7):
            # Use Pnet functions
            #disp('TCP/IP with PNet functions');
            #disp(['Con:', num2str(Port)]);
            self.hConVideo = self.OpenTcpIpVideoCom(self.cIpAddr, self.cVideoPort);

    def     StopReplayFile(self):
        if self.cReplay > -1:
            Data = [];
            Ret  =   self.CmdSend(0, int('0x6155',0), Data, 0)
            Ret  =   self.CmdRecv()

            self.PollReplayClosed();
        self.cReplay = -1;

        self.CloseTcpipVideoCom();
        self.CloseTcpipDataCom();

    def     PollReplayClosed(self):
        Ret = 1;
        while (Ret == 1):
            Ret = self.CmdSend(0, int('0x6159',0), np.zeros(1, dtype='uint32'), 0)
            Ret = self.CmdRecv();

    def     CreateFileExtension(self, stName, Selection=0, AddRaw=0, SplitChn=0): #, Parameters=[]):
        Len         =   (len(stName) % 4)
        for Idx in range (0, 4-Len):
            stName  =   stName + ' '

        Parameters = [];
        Data        =   np.zeros(int(9 + len(stName)/4 + len(Parameters)*2 + 1), dtype='uint32')
        Data[0]     =   np.uint32(self.cBufSiz)
        Data[1]     =   np.uint32(self.cMult)
        Data[2]     =   np.uint32(len(stName))
        Data[3:int(3+len(stName)/4)]    = np.fromstring(stName,dtype='uint32')
        Data[int(3+len(stName)/4)]      = np.uint32(Selection);
        Data[int(3+len(stName)/4+1)]    = np.uint32(AddRaw);
        Data[int(3+len(stName)/4+2)]    = np.uint32(SplitChn);
        Data[int(3+len(stName)/4+3)]    = np.uint32(self.cNumPackets);

        if (len(Parameters) > 0):
            ParamCorr = [self.cUsbNrTx];
            ParamCorr.extend(Parameters);

            Data[int(3+len(stName)/4+4)] = np.uint32(len(ParamCorr));
            ParamStr                     = np.array(ParamCorr, dtype="float32").tostring();
            print(int(8+len(stName)/4));
            print(int(8 + len(stName)/4 + len(ParamCorr)*2 + 1 + 1));
            Data[int(8+len(stName)/4):int(8 + len(stName)/4 + len(ParamCorr)*2 + 1 + 1)] = np.fromstring(ParamStr, dtype="uint32");
        else:
            Data[int(3+len(stName)/4+4)] = np.uint32(0);
            Data[int(len(Data)-1)]       = np.uint32(self.cUsbNrTx)

        # create file
        Ret         =   self.CmdSend(0, int('0x615A',0), Data);
        Ret         =   self.CmdRecv();

    def     CloseFileExtension(self):
        Data        =   np.zeros(1, dtype='uint32')
        Ret         =   self.CmdSend(0, int('0x615B',0), Data)
        Ret         =   self.CmdRecv()

        Ret = 1;
        # poll file closed?
        while (Ret == 1):
            Ret = self.CmdSend(0, int('0x615C',0), Data);
            Ret = self.CmdRecv();

    def     ReplayFileExtension(self, stName, FrameIdx=1, WithVideo=0):
        Len         =   (len(stName) % 4)
        for Idx in range (0, 4-Len):
            stName  =   stName + ' '
        Data        =   np.zeros(int(2 + len(stName)/4), dtype='uint32')
        Data[0]     =   np.uint32(FrameIdx)-1
        Data[1]     =   np.uint32(len(stName))
        Data[2:]    =   np.fromstring(stName,dtype='uint32')
        Ret         =   self.CmdSend(0, int('0x615D',0), Data, 0); # replay file ext
        Ret         =   self.CmdRecv(); # Ret = Port, Single Packet Size
        if (len(Ret) == 2):
            Port = Ret[0];
            self.cExtSize   = Ret[1];
            if Port > 0:
                self.cPortOpen = 1;
                self.cPortNum = Port;
            if (WithVideo != 0):
                Ret  = self.CmdSend(0, int('0x6157',0), [], 0)
                Ret  = self.CmdRecv();
                if (len(Ret) == 7):
                    self.cVideoPort = Ret[0]
                    self.cVideoCols = Ret[1]
                    self.cVideoRows = Ret[2]
                    self.cVideoChn  = Ret[3]
                    self.cVideoRate = Ret[5]
                    self.cVideoSize = Ret[1]*Ret[2]*Ret[3]
                    self.cVideoFrames = Ret[6]
                    self.cVideoPort = Ret[0]
                    self.cVideoPortOpen = 1
            if Port > 0 and self.cExtSize > 0:
                if self.hConDat == -1:
                    # Use Pnet functions
                    #disp('TCP/IP with PNet functions');
                    #disp(['Con:', num2str(Port)]);
                    self.hConDat = self.OpenTcpIpDatCom(self.cIpAddr, Port);
                    if self.hConDat == 1:
                        self.cReplay        = 1;
                        self.cReplayExt     = 1;
            if (WithVideo != 0) and (len(Ret) == 7):
                # Use Pnet functions
                #disp('TCP/IP with PNet functions');
                #disp(['Con:', num2str(Port)]);
                self.hConVideo = self.OpenTcpIpVideoCom(self.cIpAddr, self.cVideoPort);
        else:
            quit();

    def     StopReplayFileExtension(self):
        if self.cReplay > -1:
            Data = [];
            Ret  =   self.CmdSend(0, int('0x615E',0), Data, 0)
            Ret  =   self.CmdRecv()

            Ret = 1;
            while (Ret == 1):
                Ret = self.CmdSend(0, int('0x615F',0), Data, 0)
                Ret = self.CmdRecv();
        self.cReplay = -1;
        self.cReplayExt = -1;

        self.CloseTcpipVideoCom();
        self.CloseTcpipDataCom();
    # ----- end of file functions --------------

    # ----- data port functions --------------
    def     GetDataPort(self):
        if self.cPortOpen == -1:
            Data        =   np.zeros(6, dtype='uint32')
            Data[1]     =   np.uint32(self.cBufSiz)
            Data[2]     =   np.uint32(self.cMult)
            Data[3]     =   np.uint32(self.cNumPackets)
            Data[4]     =   np.uint32(self.cDataPortKeepAlive)
            Data[5]     =   np.uint32(self.cUsbNrTx)
            Ret         =   self.CmdSend(0, int('0x6130', 0), Data)
            Port        =   self.CmdRecv()
            if Port != -1:
                self.cPortOpen  =   1
                self.cPortNum   =   Port
                if self.hConDat == -1:
                    self.hConDat = self.OpenTcpIpDatCom(self.cIpAddr, Port);
                    self.cDataOpened = 1;

    def     CloseDataPort(self):
        if self.cDataOpened > -1 and self.cPortOpen == 1:
            Data    =   np.zeros(1, dtype='uint32')
            Ret     =   self.CmdSend(0, int('0x6131',0), Data)
            Ret     =   self.CmdRecv()
            if Ret == 0:
                self.cPortOpen = -1;
                self.cDataOpened = -1;

            self.PollDataPortClosed();

        self.CloseTcpipDataCom()

    def     PollDataPortClosed(self):
        Ret = 1;
        # poll dataport closed?
        while (Ret == 1):
            Ret = self.CmdSend(0, int('0x6132',0), np.zeros(1, dtype='uint32'));
            Ret = self.CmdRecv();

    def     RestartDataPort(self, NumPackets=0):
        if self.cPortOpen > -1:
            Data        =   np.zeros(2, dtype='uint32')
            if (NumPackets == 0):
                Data[1] = np.uint32(self.cNumPackets);
            else:
                Data[1]     =   np.uint32(NumPackets);
            Ret         =   self.CmdSend(0, int('0x6136', 0), Data)
            Ret         =   self.CmdRecv()

    def     GetExtensionPort(self, Selection=0, Parameters=[]):
        Cmd     = int('0x6133', 0)

        if self.cPortOpen == -1:
            Data        =   np.zeros(8 + len(Parameters)*2, dtype='uint32')
            Data[1]     =   np.uint32(self.cBufSiz)
            Data[2]     =   np.uint32(self.cMult)
            Data[3]     =   np.uint32(self.cNumPackets)
            Data[4]     =   np.uint32(Selection)
            Data[5]     =   np.uint32(self.cDataPortKeepAlive)
            Data[6]     =   np.uint32(len(Parameters))
            ParamStr    =   np.array(Parameters, dtype=np.float).tostring();
            Data[7:int(7 + len(Parameters)*2)] = np.fromstring(ParamStr, dtype="uint32");
            Data[int(len(Data)-1)] =   np.uint32(self.cUsbNrTx)

            Ret         =   self.CmdSend(0, Cmd, Data)
            Ret         =   self.CmdRecv() # Ret = Port, Single Packet Size
            if len(Ret) == 2:
                Port = Ret[0];
                self.cExtSize = Ret[1];
                if Port > 0 and self.cExtSize > 0:
                    self.cPortOpen  =   1
                    self.cPortNum   =   Ret[0];
                    if self.hConDat == -1:
                        self.hConDat = self.OpenTcpIpDatCom(self.cIpAddr, Port);
                        if self.hConDat == 1:
                            self.cDataOpened = 1;

    def     CloseExtensionPort(self):
        if self.cDataOpened > -1 and self.cPortOpen == 1:
            Data    =   np.zeros(1, dtype='uint32')
            Ret     =   self.CmdSend(0, int('0x6134',0), Data)
            Ret     =   self.CmdRecv()
            if Ret == 0:
                self.cPortOpen = -1;
                self.cDataOpened = -1;

            Ret = 1;
            # poll extensionport closed?
            while (Ret == 1):
                Ret = self.CmdSend(0, int('0x6135',0), np.zeros(1, dtype='uint32'));
                Ret = self.CmdRecv();

        self.CloseTcpipDataCom()
    # ----- end of data port functions --------------

    # ----- stream functions --------------
    def     CreateStream(self, Mult):
        Data        =   np.zeros(2, dtype='uint32')
        Data[0]     =   0
        Data[1]     =   np.uint32(Mult)
        # create stream cmd
        [Ret]       =   self.CmdSend(0, int('0x6160',0), Data)
        [Ret]       =   self.CmdRecv()

        # start stream cmd
        Data        =   np.zeros(2, dtype='uint32')
        Data[0]     =   0
        Data[1]     =   np.uint32(Mult)
        [Ret]       =   self.CmdSend(0, int('0x6161', 0), Data)
        [Ret]       =   self.CmdRecv()

    def     StopStream(self):
        Data        =   np.zeros(1, dtype='uint32')
        [Ret]       =   self.CmdSend(0,int('0x6162', 0), Data)
        [Ret]       =   self.CmdRecv()

    def     CloseStream(self):
        Data        =   np.zeros(1, dtype='uint32')
        [Ret]       =   self.CmdSend(0, int('0x6163', 0), Data)
        [Ret]       =   self.CmdRecv()
        # poll stream closed
    # ----- end of stream functions --------------

    def     SetIndex(self, Idx):
        Data        =   np.zeros(1, dtype='uint32')
        Data[0]     =   np.uint32(Idx)
        [Ret]       =   self.CmdSend(0, int('0x6113', 0), Data, 0);
        [Ret]       =   self.CmdRecv()

    def     ConClrFifo(self):
        Data        =   np.zeros(1,dtype='uint32')
        Ret         =   self.CmdSend(0, int('0x612B',0), Data)
        Ret         =   self.CmdRecv()

    def 	ConSetFileParam(self, stName, Val, DataType='STRING'):
       self.ConSetConfig(stName, Val, DataType);
    def     ConSetConfig(self, stName, Val, DataType='STRING'):
        if  self.cType == 'RadServe':
            Len    =   len(stName) % 4;
            if (Len != 0):
                for Idx in range(0,(4-Len)):
                    stName = stName + ' ';
            Name = np.fromstring(stName, dtype='uint32');

            if (DataType.upper() == 'INT' or isinstance(Val, int)):
                Data = np.zeros(4 + len(Name));
                Data[1] = 1; # type
                Data[2] = np.uint32(len(stName));
                for Idx in range(0,len(Name)):
                    Data[3 + Idx] = Name[Idx];
                Data[3 + len(Name)] = Val;
            elif (DataType.upper() == 'DOUBLE' or isinstance(Val, float)):
                Data = np.zeros(5 + len(Name));
                Data[1] = 2; # type
                Data[2] = np.uint32(len(stName));
                for Idx in range(0,len(Name)):
                    Data[3 + Idx] = Name[Idx];
                valArray = np.array(Val, dtype=np.float).tostring();
                Data[int(3 + len(Name)):int(3 + len(Name) + 2)] = np.fromstring(valArray, dtype=np.uint32);
            elif (DataType.upper() == 'ARRAY32'):
                print('LEN: ', len(Val));
                Data = np.zeros(4 + len(Val) + len(Name));
                Data[1] = 3; # type
                Data[2] = np.uint32(len(stName));
                for Idx in range(0,len(Name)):
                    Data[3 + Idx] = Name[Idx];
                Data[int(3 + len(Name))] = np.uint32(len(Val)); # len of array
                for Idx in range(0,len(Val)):
                    Data[int(4 + len(Name) + Idx)] = np.uint32(Val[Idx]);
                    print('idx: ', Idx);
            elif (DataType.upper() == 'ARRAY64'):
                print('LEN: ', len(Val));
                Data = np.zeros(4 + len(Val)*2 + len(Name));
                Data[1] = 4; # type
                Data[2] = np.uint32(len(stName));
                for Idx in range(0,len(Name)):
                    Data[3 + Idx] = Name[Idx];
                Data[int(3 + len(Name))] = np.uint32(len(Val)); # len of array
                valArray = Val.tostring();
                Data[int(4 + len(Name)):int(4 + len(Name) + len(Val)*2)] = np.fromstring(Val, dtype=np.uint32);
            else:
                Len    =   len(Val) % 4;
                stVal = Val;
                if (Len != 0):
                    for Idx in range(0,(4 - int(Len))):
                        stVal = stVal + ' ';
                Value = np.fromstring(stVal, dtype='uint32');
                Data = np.zeros(3 + len(Name) + len(Value));
                Data[1] = 0; # type
                Data[2] = np.uint32(len(stName));
                for Idx in range(0,len(Name)):
                    Data[3 + Idx] = Name[Idx];
                for Idx in range(0,len(Value)):
                    Data[3 + len(Name) + Idx] = Value[Idx];
            Ret         =   self.CmdSend(0,int('0x612A',0),Data)
            Ret         =   self.CmdRecv()

    def     ConGetConfig(self, Key, DataType):
        if self.cType == 'RadServe':
            Len         =   (len(Key) % 4)
            for Idx in range (0, 4-Len):
                Key  =   Key + ' '

            Data        =   np.zeros(int(1 + len(Key)/4), dtype='uint32')
            if DataType == 'INT':
                Data[0] = 1
            elif DataType == 'DOUBLE':
                Data[0] = 2
            elif DataType == 'ARRAY32':
                Data[0] = 3
            elif DataType == 'ARRAY64':
                Data[0] = 4
            elif DataType == 'STRING':
                Data[0] = 0
            else:
                Data[0] = 5

            Data[1:]    =   np.fromstring(Key,dtype='uint32')
            Ret         =   self.CmdSend(0, int('0x6156',0), Data, 0);
            Ret         =   self.CmdRecv(DataType != 'STRING');

            if DataType == 'ARRAY64':
                Ret     =   np.fromstring(Ret, dtype='uint64')
            return Ret;

    def     ConSetTimeout(self, Val):
        if (Val != self.cTimeout) and (Val > 0):
            if self.cType == 'Usb':
                self.cTimeout   =   Val
                self.USBnAny('timeout', np.int32(self.cTimeout))
            elif self.cType == 'RadServe':
                if (Val != self.cTimeout):
                    Data = np.zeros(2, 'uint32');
                    Data[1] = Val;
                    self.CmdSend(0, int('0x6127', 0), Data);
                    self.CmdRecv();
                    self.cTimeout = Val;
                pass

    def     ConSetCfgTimeout(self, Val):
        if (Val != self.cCfgTimeout) and (Val > 0):
            if self.cType == 'RadServe':
                if (Val != self.cCfgTimeout):
                    Data = np.zeros(2, 'uint32');
                    Data[1] = Val;
                    self.CmdSend(0, int('0x6126', 0), Data);
                    self.CmdRecv();
                    self.cCfgTimeout = Val;
                pass

    def     ConSetDatSockTimeout(self, Val):
        if self.cType == 'RadServe':
            self.hConDatTimeout = Val;

    def     ConGetData(self, Len):
        if self.hConDat > -1:
            RxBytes = self.cRadDatSocket.recv(0);
            try:
                # Receive data from the server and shut down
                RxBytes         =   self.cRadDatSocket.recv(int(2*Len))

            except socket.timeout:
                Ret     =   np.zeros(int(Len))
            except socket.error:
                Ret     =   np.zeros(int(Len))
            finally:
                while len(RxBytes) < (2*Len):
                    LenData     =   len(RxBytes)
                    #try: # used for unlimited waiting - not wanted
                    RxBytes     =   RxBytes + self.cRadDatSocket.recv(int(2*Len - LenData))
                    #except socket.timeout:
                    #    continue;
                    #except socket.error:
                    #    Ret = zeros(int(Len))
                Ret             =   np.fromstring(RxBytes, dtype='int16')
                pass
        else:
            Ret     =   np.zeros(int(Len))

        return Ret

    # DOXYGEN ------------------------------------------------------
    #> @brief Display version information of USB mex driver
    #>
    #> Display version information in the Matlab command window
    #>
    def     DispSrvVers(self):
        if self.cType == 'Usb':
            self.USBnAny('version')
        elif self.cType == 'RadServe':
            Ret         =   self.CmdSend(0, int('0x6100',0),[])
            Ret         =   self.CmdRecv()
        print("Cmd DispSrvVers finished")

    def     ListDev(self):
        if self.cType == 'RadServe':
            Ret         =   self.CmdSend(0, int('0x6110',0),[],0)
            Ret         =   self.CmdRecv();

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
    #>      -   <span style="color: #ff9900;"> 'BufSiz': </span> Set buffer size in RadServe <br>
    #>      -   <span style="color: #ff9900;"> 'Mult': </span> Set Packetsize for file streaming  <br>
    #>
    #> e.g. Set BufSiz to 1024
    #>   @code
    #>      Brd =   Radarlog( )
    #>
    #>      Brd.ConSet('BufSiz',1024)
    #>   @endcode
    def     ConSet(self,*varargin):
        if len(varargin) > 0:
            stVal       =   varargin[0]
            if stVal == 'BufSiz':
                if len(varargin) > 1:
                    self.cBufSiz    =   varargin[1]
            elif stVal == 'Mult':
                if len(varargin) > 1:
                    self.cMult      =   varargin[1]
            elif stVal == 'KeepAlive':
                if len(varargin) > 1:
                    self.cDataPortKeepAlive  =   varargin[1]
            elif stVal == 'NumPackets':
                if len(varargin) > 1:
                    self.cNumPackets  =   varargin[1]
            elif stVal == 'UsbNrTx':
                if len(varargin) > 1:
                    self.cUsbNrTx  =   varargin[1]

    def     AddVideo(self, Add):
        if self.cType == 'RadServe':
            Ret         =   self.CmdSend(0, int('0x6101',0),[np.uint32(Add)],0)
            Ret         =   self.CmdRecv();

    def     DispVideo(self, Cnt):
        if (self.hConVideo > 0 and self.cVideoRate != 0):
            if ((Cnt + 1) % self.cVideoRate == 0):
                Len = self.cVideoSize;
                inp = np.zeros(Len, dtype='uint8')
                Idx = 0;

                while (Len > 0):
                    tmp = self.cRadVideoSocket.recv(Len);
                    tmpLen = len(tmp);
                    if (tmpLen == 0):
                        Len = -1;
                    else:
                        inp[Idx:Idx+tmpLen] = np.fromstring(tmp, dtype='uint8');
                        Idx = Idx + tmpLen;
                        Len = Len - tmpLen;

                if (len(inp) == self.cVideoSize):
                    inp = np.reshape(inp, (self.cVideoRows, self.cVideoCols, self.cVideoChn));
                    plt.imshow(inp)
                    return True;

    def     GetVideo(self, Cnt):
        if (self.hConVideo > 0 and self.cVideoRate != 0):
            if ((Cnt + 1) % self.cVideoRate == 0):
                Len = self.cVideoSize;
                inp = np.zeros(Len, dtype='uint8')
                Idx = 0;

                while (Len > 0):
                    tmp = self.cRadVideoSocket.recv(Len);
                    tmpLen = len(tmp);
                    if (tmpLen == 0):
                        Len = -1;
                    else:
                        inp[Idx:Idx+tmpLen] = np.fromstring(tmp, dtype='uint8');
                        Idx = Idx + tmpLen;
                        Len = Len - tmpLen;

                if (len(inp) == self.cVideoSize):
                    inp = np.reshape(inp, (self.cVideoRows, self.cVideoCols, self.cVideoChn));
                    return inp;

# RadarProc.py -- RadarProc class
#
# Copyright (C) 2015-11 Inras GmbH Haderer Andreas
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

import numpy as np

class RadarProc(object):
    """ Radarbook class object:
        (c) Haderer Andreas Inras GmbH
        Communication and access of Radarbook device with TCPIP Connection
    """

    def __init__(self):
        pass
        self.c0                         =   2.99792458e8
        self.fs                         =   -1
        self.kf                         =   -1
        self.FuSca                      =   2/2048

        # Calculate RangeProfile
        self.RangeProfile_RemoveMean    =   1
        self.RangeProfile_Window        =   1
        self.RangeProfile_NIni          =   1
        self.RangeProfile_FFT           =   2**12
        self.RangeProfile_XPos          =   1
        self.RangeProfile_Abs           =   1
        self.RangeProfile_dB            =   1
        self.RangeProfile_Ext           =   0
        self.RangeProfile_RMin          =   0
        self.RangeProfile_RMax          =   0

        #Calculate BeamformingUla
        self.BeamformingUla_RemoveMean  =   1
        self.BeamformingUla_RangeWindow =   1
        self.BeamformingUla_NIni        =   1
        self.BeamformingUla_RangeFFT    =   2**12
        self.BeamformingUla_Ext         =   0
        self.BeamformingUla_RMin        =   1
        self.BeamformingUla_RMax        =   2
        self.BeamformingUla_AngFFT      =   2**10
        self.BeamformingUla_Abs         =   1
        self.BeamformingUla_dB          =   1
        self.BeamformingUla_AngWindow   =   1
        self.BeamformingUla_ChnOrder    =   np.arange(8)
        self.BeamformingUla_CalData     =   np.ones(8)

        #Calculate RangeDoppler
        self.RangeDoppler_RemoveMean        =   1
        self.RangeDoppler_RangeWindow       =   1
        self.RangeDoppler_NIni              =   1
        self.RangeDoppler_RangeFFT          =   2**12
        self.RangeDoppler_Ext               =   0
        self.RangeDoppler_RMin              =   1
        self.RangeDoppler_RMax              =   10
        self.RangeDoppler_VelFFT            =   2**10
        self.RangeDoppler_Abs               =   1
        self.RangeDoppler_dB                =   1
        self.RangeDoppler_VelWindow         =   1
        self.RangeDoppler_N                 =   256
        self.RangeDoppler_Frms              =   32
        self.RangeDoppler_fc                =   0
        self.RangeDoppler_Tp                =   0
        self.RangeDopplerTar_ThresdB        =   0

        self.RangeProfileCfar_Lz            =   int(9)
        self.RangeProfileCfar_Lb            =   int(8)
        self.RangeProfileCfar_La            =   int(8)
        self.RangeProfileCfar_Hz            =   0
        self.RangeProfileCfar_Hb            =   1
        self.RangeProfileCfar_Ha            =   1


        self.BeamformingUlaCfar_RangeLz     =   int(9)
        self.BeamformingUlaCfar_RangeLb     =   int(9)
        self.BeamformingUlaCfar_RangeLa     =   int(9)
        self.BeamformingUlaCfar_RangeHz     =   0
        self.BeamformingUlaCfar_RangeHb     =   1
        self.BeamformingUlaCfar_RangeHa     =   1

        self.BeamformingUlaCfar_AngLz       =   int(9)
        self.BeamformingUlaCfar_AngLb       =   int(9)
        self.BeamformingUlaCfar_AngLa       =   int(9)
        self.BeamformingUlaCfar_AngHz       =   0
        self.BeamformingUlaCfar_AngHb       =   1
        self.BeamformingUlaCfar_AngHa       =   1

    def GetRangeProfile(self, stSel):
        if stSel == 'Range':
            if self.RangeProfile_XPos > 0:
                Freq    =   np.arange(int(self.RangeProfile_FFT/2))/self.RangeProfile_FFT * self.fs
            else:
                Freq    =   np.arange(int(self.RangeProfile_FFT)) /self.RangeProfile_FFT * self.fs
            if self.RangeProfile_Ext > 0:
                Range       =   Freq*self.c0/(2*self.kf)
                IdxMin      =   np.argmin(abs(Range - self.RangeProfile_RMin))
                IdxMax      =   np.argmin(abs(Range - self.RangeProfile_RMax))
                Range       =   Range[IdxMin:IdxMax]
            else:
                Range       =   Freq*self.c0/(2*self.kf)
            return Range
        if stSel == 'Freq':
            if self.RangeProfile_XPos > 0:
                Freq    =   np.arange(int(self.RangeProfile_FFT/2))/self.RangeProfile_FFT * self.fs
            else:
                Freq    =   np.arange(int(self.RangeProfile_FFT)) /self.RangeProfile_FFT * self.fs
            if self.RangeProfile_Ext > 0:
                Range       =   Freq*self.c0/(2*self.kf)
                IdxMin      =   np.argmin(abs(Range - self.RangeProfile_RMin))
                IdxMax      =   np.argmin(abs(Range - self.RangeProfile_RMax))
                Freq        =   Freq[IdxMin:IdxMax]
            return Freq

    def RangeProfile(self, Data):
        #   @function       RangeProfile
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Calculate Range Profile
        #           NIni:           Number of samples to remove
        #           RemoveMean:     Remove mean from channel data
        #           Window:         Use window
        #           NFFT:           FFT size
        #           XPos:           Extract positive range profile only
        #           Abs:            Calculate magnitude spectrum
        #           dB:             Spectrum in dB
        #           FuSca:          Data Scaling constant
        #           RMin:           Minimum Range
        #           RMax:           Maximum Range
        #           Ext:            Extract range interval

        X   =   self.RangeProfileFFT(Data)

        if self.RangeProfile_XPos > 0:
            X       =   X[0:int(self.RangeProfile_FFT/2),:]

        if self.RangeProfile_Abs > 0:
            X       =   abs(X)
            if self.RangeProfile_dB > 0:
                X   =   20*np.log10(X)

        if self.RangeProfile_Ext > 0:
            X       =   X[int(self.RangeProfile_IdxMin):int(self.RangeProfile_IdxMax),:]

        return X

    def RangeProfileFFT(self, Data, *varargin):
        Data    =   Data[self.RangeProfile_NIni:,:]
        Siz     =   Data.shape
        Ny      =   Siz[0]                  # rows
        Nx      =   Siz[1]                  # colums

        if self.RangeProfile_RemoveMean > 0:
            # Remove mean from data
            Tmp     =   np.mean(Data, axis=0)              # mean for all input signals
            mTmp    =   np.tile(Tmp, (Ny, 1))
            Data    =   Data - mTmp

        if self.RangeProfile_Window > 0:
            Win     =   np.hanning(Ny)
            ScaWin  =   sum(Win)
            Win2D   =   np.tile(Win, (Nx, 1))
            Win2D   =   Win2D.transpose()
        else:
            ScaWin  =   Ny
            Win2D   =   np.ones((Ny, Nx))

        Data        =   Data*Win2D
        if len(varargin) > 0:
            # Calculate CFAR
            HCfar   =   np.tile(self.RangeProfileCfar_HCfar, (Nx,1))
            HCfar   =   HCfar.transpose()
            # Calculate symmetric fft
            x           =   np.zeros((int(self.RangeProfile_FFT), Nx),dtype = 'complex_')
            StrtIdx     =   int((self.RangeProfile_FFT - Ny)/2)
            x[StrtIdx:StrtIdx+Ny,:]     =   Data
            x           =   x*HCfar
        else:
            # Calculate symmetric fft
            x           =   np.zeros((int(self.RangeProfile_FFT), Nx),dtype = 'complex_')
            StrtIdx     =   int((self.RangeProfile_FFT - Ny)/2)
            x[StrtIdx:StrtIdx+Ny,:]     =   Data

        x           =   np.fft.fftshift(x, axes = 0)
        X           =   np.fft.fft(x, self.RangeProfile_FFT, 0)/ScaWin*self.FuSca

        return X

    def RangeProfileCfar(self, Data, stSel):

        X   =   self.RangeProfileFFT(Data, 'Cfar')

        if self.RangeProfile_XPos > 0:
            X       =   X[0:int(self.RangeProfile_FFT/2),:]

        if self.RangeProfile_Abs > 0:
            X       =   abs(X)
            if self.RangeProfile_dB > 0:
                X   =   20*np.log10(X)

        if self.RangeProfile_Ext > 0:
            X       =   X[self.RangeProfile_IdxMin:self.RangeProfile_IdxMax,:]


        if stSel == 'Thres':
            return X
        if stSel == 'List':
            RP      =   self.RangeProfile(Data)
            Range   =   self.GetRangeProfile('Range')
            # find values above threshold

            TarMap  =   (RP > X)*np.ones(RP.shape)
            Siz     =   TarMap.shape
            Ny      =   Siz[0]                  # rows
            Nx      =   Siz[1]                  # colums
            TarMap  =   TarMap[1:Ny,:] - TarMap[0:Ny-1,:]
            lTar    =   list()
            for Idx in range(0,Nx):
                lChn    =   list()
                TarMap[0,Idx]       =   0
                TarMap[1,Idx]       =   0
                TarMap[Ny-3,Idx]    =   0
                TarMap[Ny-2,Idx]    =   0
                IdcsPos     =   np.argwhere(TarMap[:,Idx] > 0.1) + 1
                IdcsNeg     =   np.argwhere(TarMap[:,Idx] < -0.1) + 1

                if len(IdcsPos) < len(IdcsNeg):
                    IdcsNeg     =   IdcsNeg[0:len(IdcsPos)]
                if len(IdcsNeg) < len(IdcsPos):
                    IdcsPos     =   IdcsPos[0:len(IdcsNeg)]


                for TarIdx in range(0,len(IdcsPos)):
                    dTar    =   {}
                    if IdcsPos[TarIdx] < IdcsNeg[TarIdx]:
                        MaxIdx          =   np.argmax(RP[IdcsPos[TarIdx]-2:IdcsNeg[TarIdx]+2,Idx]) + IdcsPos[TarIdx]-2

                        dTar["R"]       =   Range[MaxIdx]
                        dTar["Amp"]     =   RP[MaxIdx,Idx]
                        dTar["Bins"]    =   IdcsNeg[TarIdx] - IdcsPos[TarIdx]
                    lChn.append(dTar)

                lTar.append(lChn)


            return lTar

        return X

    def CfgRangeProfileCfar(self, dCfg):
        if 'Lz' in dCfg:
            self.RangeProfileCfar_Lz        =   int(dCfg["Lz"])
            if self.RangeProfileCfar_Lz < 0:
                self.RangeProfileCfar_Lz    =   int(0)
            if (self.RangeProfileCfar_Lz % 2):
                self.RangeProfileCfar_Lz    =   self.RangeProfileCfar_Lz + 1
        if 'Lb' in dCfg:
            self.RangeProfileCfar_Lb        =   int(dCfg["Lb"])
            if self.RangeProfileCfar_Lb < 0:
                self.RangeProfileCfar_Lb    =   int(0)
        if 'La' in dCfg:
            self.RangeProfileCfar_La        =   int(dCfg["La"])
            if self.RangeProfileCfar_La < 0:
                self.RangeProfileCfar_La    =   int(0)
        if 'Hz' in dCfg:
            self.RangeProfileCfar_Hz        =   dCfg["Hz"]
        if 'Hb' in dCfg:
            self.RangeProfileCfar_Hb        =   dCfg["Hb"]
        if 'Ha' in dCfg:
            self.RangeProfileCfar_Ha        =   dCfg["Ha"]

        hCfar               =   np.zeros(self.RangeProfileCfar_Lb + self.RangeProfileCfar_Lz + self.RangeProfileCfar_La)
        Idx1                =   0
        Idx2                =   self.RangeProfileCfar_Lb
        hCfar[Idx1:Idx2]    =   np.ones(self.RangeProfileCfar_Lb)*self.RangeProfileCfar_Hb
        Idx1                =   self.RangeProfileCfar_Lb
        Idx2                =   self.RangeProfileCfar_Lb + self.RangeProfileCfar_Lz
        hCfar[Idx1:Idx2]    =   np.ones(self.RangeProfileCfar_Lz)*self.RangeProfileCfar_Hz
        Idx1                =   Idx2
        Idx2                =   Idx2 + self.RangeProfileCfar_La
        hCfar[Idx1:Idx2]    =   np.ones(self.RangeProfileCfar_La)*self.RangeProfileCfar_Ha

        hCfarPad            =   np.zeros(int(self.RangeProfile_FFT))
        StrtIdx             =   int((self.RangeProfile_FFT - len(hCfar))/2)
        hCfarPad[StrtIdx:StrtIdx + len(hCfar)]     =   hCfar
        hCfarPad            =   np.fft.fftshift(hCfarPad)
        self.RangeProfileCfar_HCfar     =   np.fft.ifft(hCfarPad, self.RangeProfile_FFT)
        self.RangeProfileCfar_HCfar     =   np.fft.fftshift(self.RangeProfileCfar_HCfar)*self.RangeProfile_FFT

        return self.RangeProfileCfar_HCfar

    def CfgRangeProfile(self, dCfg):
        #   @function       CfgRangeProfile
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Calculate Range Profile
        #           NIni:           Number of samples to remove
        #           RemoveMean:     Remove mean from channel data
        #           Window:         Use window
        #           NFFT:           FFT size
        #           XPos:           Extract positive range profile only
        #           Abs:            Calculate magnitude spectrum
        #           dB:             Spectrum in dB
        #           FuSca:          Data Scaling constant
        #           fs:             Sampling frequency
        #           kf:             Chirp rate

        if 'NIni' in dCfg:
            self.RangeProfile_NIni  =   dCfg["NIni"]
            if self.RangeProfile_NIni < 0:
                self.RangeProfile_NIni  =   0
        if 'RemoveMean' in dCfg:
            self.RangeProfile_RemoveMean    =   dCfg["RemoveMean"]
        if 'Window' in dCfg:
            self.RangeProfile_Window        =   dCfg["Window"]
        if 'NFFT' in dCfg:
            self.RangeProfile_FFT           =   dCfg["NFFT"]
            self.RangeProfile_FFT           =   round(self.RangeProfile_FFT/2)*2
        if 'XPos' in dCfg:
            self.RangeProfile_XPos          =   dCfg["XPos"]
        if 'Abs' in dCfg:
            self.RangeProfile_Abs           =   dCfg["Abs"]
        if 'dB' in dCfg:
            self.RangeProfile_dB            =   dCfg["dB"]
        if 'FuSca' in dCfg:
            self.FuSca                      =   dCfg["FuSca"]
        if 'fs' in dCfg:
            self.fs                         =   dCfg["fs"]
        if 'kf' in dCfg:
            self.kf                         =   dCfg["kf"]
        if 'RMin' in dCfg:
            self.RangeProfile_RMin          =   dCfg["RMin"]
        if 'RMax' in dCfg:
            self.RangeProfile_RMax          =   dCfg["RMax"]
        if 'Ext' in dCfg:
            self.RangeProfile_Ext           =   dCfg["Ext"]

        # Update requried parameters
        if self.RangeProfile_XPos > 0:
            Freq    =   np.arange(int(self.RangeProfile_FFT/2))/self.RangeProfile_FFT * self.fs
        else:
            Freq    =   np.arange(int(self.RangeProfile_FFT)) /self.RangeProfile_FFT * self.fs

        if self.RangeProfile_Ext > 0:
            Range       =   Freq*self.c0/(2*self.kf)
            self.RangeProfile_IdxMin      =   np.argmin(abs(Range - self.RangeProfile_RMin))
            self.RangeProfile_IdxMax      =   np.argmin(abs(Range - self.RangeProfile_RMax))

    def RangeDoppler(self, Data):
        #   @function       BeamformingUla
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Calculate DBF Cost function for ULA (Uniform Linear Array)
        #           NIni:           Number of samples to remove
        #           RemoveMean:     Remove mean from channel data
        #           Window:         Use window
        #           NFFT:           FFT size
        #           XPos:           Extract positive range profile only
        #           Abs:            Calculate magnitude spectrum
        #           dB:             Spectrum in dB
        #           FuSca:          Data Scaling constant

        Data    =   Data.reshape(int(self.RangeDoppler_Frms), int(self.RangeDoppler_N))
        Data    =   Data.transpose()
        Data    =   Data[self.RangeDoppler_NIni:,:]

        Siz     =   Data.shape
        Ny      =   Siz[0]                          # rows
        Nx      =   Siz[1]                          # colums

        if self.RangeDoppler_RemoveMean > 0:
            # Remove mean from data
            Tmp     =   np.mean(Data, axis=1)          # mean for all input signals
            mTmp    =   np.tile(Tmp, (Nx, 1))
            Data    =   Data - mTmp.transpose()

        if self.RangeDoppler_RangeWindow > 0:
            Win     =   np.hanning(Ny)
            ScaWin  =   sum(Win)
            Win2D   =   np.tile(Win, (Nx, 1))
            Win2D   =   Win2D.transpose()
            Data    =   Data*Win2D
        else:
            ScaWin  =   Ny

        # Calculate Range FFT
        x           =   np.zeros((int(self.RangeDoppler_RangeFFT), Nx))
        StrtIdx     =   int((self.RangeDoppler_RangeFFT - Ny)/2)
        x[StrtIdx:StrtIdx+Ny,:]     =   Data
        X           =   np.fft.fft(x, int(self.RangeDoppler_RangeFFT), 0)/ScaWin*self.FuSca
        # Extract positive rangebins
        X           =   X[0:int(self.RangeDoppler_RangeFFT/2),:]

        if self.RangeDoppler_Ext > 0:
            X       =   X[self.RangeDoppler_IdxMin:self.RangeDoppler_IdxMax,:]

        # Calculate Angular FFT
        Siz     =   X.shape
        Ny      =   Siz[0]                  # rows
        Nx      =   Siz[1]

        if self.RangeDoppler_VelWindow > 0:
            Win     =   np.hanning(Nx)
            ScaWin  =   sum(Win)
            Win2D   =   np.tile(Win, (Ny,1))
            X       =   X*Win2D
        else:
            ScaWin  =   Nx

        # Use complex array: important for assignment in the next line
        rd          =   np.zeros((Ny, int(self.RangeDoppler_VelFFT)), dtype = 'complex_')
        StrtIdx     =   int((self.RangeDoppler_VelFFT - Nx)/2)
        rd[:,StrtIdx:StrtIdx + Nx]    =   X

        RD        =   np.fft.fft(rd, self.RangeDoppler_VelFFT, 1)/ScaWin
        RD        =   np.fft.fftshift(RD, axes = 1)

        if self.RangeDoppler_Abs > 0:
            RD          =   abs(RD)
            if self.RangeDoppler_dB > 0:
                RD    =   20*np.log10(RD)

        return RD

    def CfgRangeDoppler(self, dCfg):
        if 'NIni' in dCfg:
            self.RangeDoppler_NIni  =   dCfg["NIni"]
            if self.RangeDoppler_NIni < 0:
                self.RangeDoppler_NIni  =   0
        if 'RemoveMean' in dCfg:
            self.RangeDoppler_RemoveMean        =   dCfg["RemoveMean"]
        if 'Window' in dCfg:
            self.RangeDoppler_Window            =   dCfg["Window"]
        if 'RangeFFT' in dCfg:
            self.RangeDoppler_RangeFFT          =   dCfg["RangeFFT"]
            self.RangeDoppler_RangeFFT          =    round(self.RangeDoppler_RangeFFT/2)*2
        if 'VelFFT' in dCfg:
            self.RangeDoppler_VelFFT            =   dCfg["VelFFT"]
            self.RangeDoppler_VelFFT            =    round(self.RangeDoppler_VelFFT/2)*2
        if 'Abs' in dCfg:
            self.RangeDoppler_Abs               =   dCfg["Abs"]
        if 'dB' in dCfg:
            self.RangeDoppler_dB                =   dCfg["dB"]
        if 'FuSca' in dCfg:
            self.FuSca                          =   dCfg["FuSca"]
        if 'fs' in dCfg:
            self.fs                             =   dCfg["fs"]
        if 'kf' in dCfg:
            self.kf                             =   dCfg["kf"]
        if 'RMin' in dCfg:
            self.RangeDoppler_RMin              =   dCfg["RMin"]
        if 'RMax' in dCfg:
            self.RangeDoppler_RMax              =   dCfg["RMax"]
        if 'Ext' in dCfg:
            self.RangeDoppler_Ext               =   dCfg["Ext"]
        if 'N' in dCfg:
            self.RangeDoppler_N                 =   dCfg["N"]
        if 'Frms' in dCfg:
            self.RangeDoppler_Frms              =   dCfg["Frms"]
        if 'fc' in dCfg:
            self.RangeDoppler_fc                =   dCfg["fc"]
        if 'Tp' in dCfg:
            self.RangeDoppler_Tp                =   dCfg["Tp"]
        if 'ThresdB' in dCfg:
            self.RangeDopplerTar_ThresdB        =   dCfg["ThresdB"]

        # Update requried parameters
        Freq    =   np.arange(int(self.RangeDoppler_RangeFFT/2))/self.RangeDoppler_RangeFFT * self.fs

        if self.RangeDoppler_Ext > 0:
            Range       =   Freq*self.c0/(2*self.kf)
            self.RangeDoppler_IdxMin      =   np.argmin(abs(Range - self.RangeDoppler_RMin))
            self.RangeDoppler_IdxMax      =   np.argmin(abs(Range - self.RangeDoppler_RMax))

    def GetRangeDoppler(self, stSel):
        if stSel == 'Range':
            Freq    =   np.arange(int(self.RangeDoppler_RangeFFT/2))/self.RangeDoppler_RangeFFT * self.fs

            if self.RangeDoppler_Ext > 0:
                Range       =   Freq*self.c0/(2*self.kf)
                IdxMin      =   np.argmin(abs(Range - self.RangeDoppler_RMin))
                IdxMax      =   np.argmin(abs(Range - self.RangeDoppler_RMax))
                Range       =   Range[IdxMin:IdxMax]
            else:
                Range       =   Freq*self.c0/(2*self.kf)
            return Range

        if stSel == 'Vel':
            Freq    =   np.linspace(-self.RangeDoppler_VelFFT/2, self.RangeDoppler_VelFFT/2-1, num=int(self.RangeDoppler_VelFFT))/self.RangeDoppler_VelFFT * 1/self.RangeDoppler_Tp
            Vel     =   Freq*self.c0/(2*self.RangeDoppler_fc)
            return Vel

    def BeamformingUlaFFT(self, Data, *varargin):
        #   @function       BeamformingUlaFFT
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Calculate DBF Cost function for ULA (Uniform Linear Array)
        #           NIni:           Number of samples to remove
        #           RemoveMean:     Remove mean from channel data
        #           Window:         Use window
        #           NFFT:           FFT size
        #           XPos:           Extract positive range profile only
        #           Abs:            Calculate magnitude spectrum
        #           dB:             Spectrum in dB
        #           FuSca:          Data Scaling constant

        Data    =   Data[self.BeamformingUla_NIni:, :]
        Siz     =   Data.shape
        Ny      =   Siz[0]                          # rows
        Nx      =   Siz[1]                          # colums

        if self.BeamformingUla_RemoveMean > 0:
            # Remove mean from data
            Tmp     =   np.mean(Data, axis=0)          # mean for all input signals
            mTmp    =   np.tile(Tmp, (Ny, 1))
            Data    =   Data - mTmp

        if self.BeamformingUla_RangeWindow > 0:
            Win     =   np.hanning(Ny)
            ScaWin  =   sum(Win)
            Win2D   =   np.tile(Win, (Nx, 1))
            Win2D   =   Win2D.transpose()
            Data    =   Data*Win2D
        else:
            ScaWin  =   Ny

        if len(varargin) > 0:
            ChnIdx      =   int((self.BeamformingUla_AngFFT - Nx)/2)
            x           =   np.zeros((self.BeamformingUla_RangeFFT , Nx), dtype = 'complex_')
            StrtIdx     =   int((self.BeamformingUla_RangeFFT - Ny)/2)
            x[StrtIdx:StrtIdx+Ny,:]     =   Data*self.HCfar[StrtIdx:StrtIdx+Ny,ChnIdx:ChnIdx + Nx]
        else:
            # Calculate Range FFT
            x           =   np.zeros((int(self.BeamformingUla_RangeFFT), Nx))
            StrtIdx     =   int((self.BeamformingUla_RangeFFT - Ny)/2)
            x[StrtIdx:StrtIdx+Ny,:]     =   Data

        x           =   np.fft.fftshift(x, axes = 0)
        X           =   np.fft.fft(x, self.BeamformingUla_RangeFFT, 0)/ScaWin*self.FuSca
        # Extract positive rangebins
        X           =   X[0:int(self.BeamformingUla_RangeFFT/2),:]

        if self.BeamformingUla_Ext > 0:
            X       =   X[self.BeamformingUla_IdxMin:self.BeamformingUla_IdxMax,:]

        # extract channels according to channel order
        XChn        =   X[:,self.BeamformingUla_ChnOrder]
        CalChn      =   self.BeamformingUla_CalData[self.BeamformingUla_ChnOrder]


        # Calculate Angular FFT
        Siz     =   XChn.shape
        Ny      =   Siz[0]                  # rows
        Nx      =   Siz[1]

        if self.BeamformingUla_AngWindow > 0:
            Win     =   np.hanning(Nx)
            ScaWin  =   sum(Win)
            Win     =   Win*CalChn
            Win2D   =   np.tile(Win, (Ny,1))
            XChn    =   XChn*Win2D
        else:
            ScaWin  =   Nx
            Win2D   =   np.tile(CalChn, (Ny,1))
            XChn    =   XChn*Win2D

        # Use complex array: important for assignment in the next line
        jOpt        =   np.zeros((Ny, int(self.BeamformingUla_AngFFT)), dtype = 'complex_')
        StrtIdx     =   int((self.BeamformingUla_AngFFT - Nx)/2)
        jOpt[:,StrtIdx:StrtIdx + Nx]    =   XChn

        JOpt        =   np.fft.fft(jOpt, self.BeamformingUla_AngFFT, 1)/ScaWin
        JOpt        =   np.fft.fftshift(JOpt, axes = (1))

        return JOpt

    def BeamformingUla(self, Data):
        #   @function       BeamformingUla
        #   @author         Haderer Andreas (HaAn)
        #   @date           2015-07-27
        #   @brief          Calculate DBF Cost function for ULA (Uniform Linear Array)
        #           NIni:           Number of samples to remove
        #           RemoveMean:     Remove mean from channel data
        #           Window:         Use window
        #           NFFT:           FFT size
        #           XPos:           Extract positive range profile only
        #           Abs:            Calculate magnitude spectrum
        #           dB:             Spectrum in dB
        #           FuSca:          Data Scaling constant
        JOpt    =   self.BeamformingUlaFFT(Data)
        if self.BeamformingUla_Abs > 0:
            JOpt        =   abs(JOpt)
            if self.BeamformingUla_dB > 0:
                JOpt    =   20*np.log10(JOpt)

        return JOpt

    def BeamformingUlaCfar(self, Data, stSel):

        JThres      =   self.BeamformingUlaFFT(Data,'Cfar')
        if self.BeamformingUla_Abs > 0:
            JThres        =   abs(JThres)

        if stSel == 'Thres':
            return JThres
        if stSel == 'Tar':
            JOpt    =   self.BeamformingUlaFFT(Data)
            if self.BeamformingUla_Abs > 0:
                JOpt        =   abs(JOpt)
            JTar    =   1*(JOpt > JThres)
            return JTar
        return JThres

    def CfgBeamformingUlaCfar(self, dCfg):
        if 'RangeLz' in dCfg:
            self.BeamformingUlaCfar_RangeLz             =   int(dCfg["RangeLz"])
            if self.BeamformingUlaCfar_RangeLz < 0:
                self.BeamformingUlaCfar_RangeLz         =   int(0)
            if (self.BeamformingUlaCfar_RangeLz % 2) == 0:
                self.BeamformingUlaCfar_RangeLz         =   self.BeamformingUlaCfar_RangeLz + 1
        if 'RangeLb' in dCfg:
            self.BeamformingUlaCfar_RangeLb             =   int(dCfg["RangeLb"])
            if self.BeamformingUlaCfar_RangeLb < 0:
                self.BeamformingUlaCfar_RangeLb         =   int(0)
        if 'RangeLa' in dCfg:
            self.BeamformingUlaCfar_RangeLa             =   int(dCfg["RangeLa"])
            if self.BeamformingUlaCfar_RangeLa < 0:
                self.BeamformingUlaCfar_RangeLa         =   int(0)
        if 'RangeHz' in dCfg:
            self.BeamformingUlaCfar_RangeHz             =   dCfg["RangeHz"]
        if 'RangeHb' in dCfg:
            self.BeamformingUlaCfar_RangeHb             =   dCfg["RangeHb"]
        if 'RangeHa' in dCfg:
            self.BeamformingUlaCfar_RangeHa             =   dCfg["RangeHa"]

        if 'AngLz' in dCfg:
            self.BeamformingUlaCfar_AngLz               =   int(dCfg["AngLz"])
            if self.BeamformingUlaCfar_AngLz < 0:
                self.BeamformingUlaCfar_AngLz           =   int(0)
            if (self.BeamformingUlaCfar_AngLz % 2) == 0:
                self.BeamformingUlaCfar_AngLz           =   self.BeamformingUlaCfar_AngLz + 1
        if 'AngLb' in dCfg:
            self.BeamformingUlaCfar_AngLb               =   int(dCfg["AngLb"])
            if self.BeamformingUlaCfar_AngLb < 0:
                self.BeamformingUlaCfar_AngLb           =   int(0)
        if 'AngLa' in dCfg:
            self.BeamformingUlaCfar_AngLa               =   int(dCfg["AngLa"])
            if self.BeamformingUlaCfar_AngLa < 0:
                self.BeamformingUlaCfar_AngLa           =   int(0)
        if 'AngHz' in dCfg:
            self.BeamformingUlaCfar_AngHz               =   dCfg["AngHz"]
        if 'AngHb' in dCfg:
            self.BeamformingUlaCfar_AngHb               =   dCfg["AngHb"]
        if 'AngHa' in dCfg:
            self.BeamformingUlaCfar_AngHa               =   dCfg["AngHa"]


        hRangeCfar              =   np.zeros(self.BeamformingUlaCfar_RangeLb + self.BeamformingUlaCfar_RangeLz + self.BeamformingUlaCfar_RangeLa)
        Idx1                    =   0
        Idx2                    =   self.BeamformingUlaCfar_RangeLb
        hRangeCfar[Idx1:Idx2]   =   np.ones(self.BeamformingUlaCfar_RangeLb)*self.BeamformingUlaCfar_RangeHb
        Idx1                    =   self.BeamformingUlaCfar_RangeLb
        Idx2                    =   self.BeamformingUlaCfar_RangeLb + self.BeamformingUlaCfar_RangeLz
        hRangeCfar[Idx1:Idx2]   =   np.ones(self.BeamformingUlaCfar_RangeLz)*self.BeamformingUlaCfar_RangeHz
        Idx1                    =   Idx2
        Idx2                    =   Idx2 + self.BeamformingUlaCfar_RangeLa
        hRangeCfar[Idx1:Idx2]   =   np.ones(self.BeamformingUlaCfar_RangeLa)*self.BeamformingUlaCfar_RangeHa

        hAngCfar                =   np.zeros(self.BeamformingUlaCfar_AngLb + self.BeamformingUlaCfar_AngLz + self.BeamformingUlaCfar_AngLa)
        Idx1                    =   0
        Idx2                    =   self.BeamformingUlaCfar_AngLb
        hAngCfar[Idx1:Idx2]     =   np.ones(self.BeamformingUlaCfar_AngLb)*self.BeamformingUlaCfar_AngHb
        Idx1                    =   self.BeamformingUlaCfar_AngLb
        Idx2                    =   self.BeamformingUlaCfar_AngLb + self.BeamformingUlaCfar_AngLz
        hAngCfar[Idx1:Idx2]     =   np.ones(self.BeamformingUlaCfar_AngLz)*self.BeamformingUlaCfar_AngHz
        Idx1                    =   Idx2
        Idx2                    =   Idx2 + self.BeamformingUlaCfar_AngLa
        hAngCfar[Idx1:Idx2]     =   np.ones(self.BeamformingUlaCfar_AngLa)*self.BeamformingUlaCfar_AngHa

        HRangeCfar              =   np.tile(hRangeCfar,(len(hAngCfar), 1))
        HRangeCfar              =   HRangeCfar.transpose();
        HAngCfar                =   np.tile(hAngCfar, (len(hRangeCfar), 1))
        HCfar                   =   HRangeCfar+HAngCfar
        Sca                     =   sum(HCfar)
        HCfar                   =   HCfar/Sca*100


        HCfarPad                =   np.zeros((self.BeamformingUla_RangeFFT, self.BeamformingUla_AngFFT))
        StrtRange               =   int((self.BeamformingUla_RangeFFT - len(hRangeCfar))/2)
        StrtAng                 =   int((self.BeamformingUla_AngFFT - len(hAngCfar))/2)

        HCfarPad[StrtRange:StrtRange+len(hRangeCfar), StrtAng:StrtAng+len(hAngCfar)]    =   HCfar
        HCfarPad                =   np.fft.fftshift(HCfarPad, axes = 0)
        HCfarPad                =   np.fft.fftshift(HCfarPad, axes = 1)
        self.HCfar              =   np.fft.ifft2(HCfarPad)*self.BeamformingUla_RangeFFT*self.BeamformingUla_AngFFT
        self.HCfar              =   np.fft.fftshift(self.HCfar)
        print("HCFar: ", self.HCfar.shape)
        return self.HCfar

    def CfgBeamformingUla(self, dCfg):
        if 'NIni' in dCfg:
            self.BeamformingUla_NIni  =   dCfg["NIni"]
            if self.BeamformingUla_NIni < 0:
                self.BeamformingUla_NIni  =   0
        if 'RemoveMean' in dCfg:
            self.BeamformingUla_RemoveMean      =   dCfg["RemoveMean"]
        if 'Window' in dCfg:
            self.BeamformingUla_Window          =   dCfg["Window"]
        if 'RangeFFT' in dCfg:
            self.BeamformingUla_RangeFFT        =   dCfg["RangeFFT"]
            self.BeamformingUla_RangeFFT        =    round(self.BeamformingUla_RangeFFT/2)*2
        if 'AngFFT' in dCfg:
            self.BeamformingUla_AngFFT          =   dCfg["AngFFT"]
            self.BeamformingUla_AngFFT          =    round(self.BeamformingUla_AngFFT/2)*2
        if 'Abs' in dCfg:
            self.BeamformingUla_Abs             =   dCfg["Abs"]
        if 'dB' in dCfg:
            self.BeamformingUla_dB              =   dCfg["dB"]
        if 'FuSca' in dCfg:
            self.FuSca                          =   dCfg["FuSca"]
        if 'fs' in dCfg:
            self.fs                             =   dCfg["fs"]
        if 'kf' in dCfg:
            self.kf                             =   dCfg["kf"]
        if 'RMin' in dCfg:
            self.BeamformingUla_RMin            =   dCfg["RMin"]
        if 'RMax' in dCfg:
            self.BeamformingUla_RMax            =   dCfg["RMax"]
        if 'Ext' in dCfg:
            self.BeamformingUla_Ext             =   dCfg["Ext"]
        if 'CalData' in dCfg:
            self.BeamformingUla_CalData         =   dCfg["CalData"]
        if 'ChnOrder' in dCfg:
            self.BeamformingUla_ChnOrder        =   dCfg["ChnOrder"]

        # Update requried parameters
        Freq    =  np.arange(int(self.BeamformingUla_RangeFFT/2))/self.BeamformingUla_RangeFFT * self.fs

        if self.BeamformingUla_Ext > 0:
            Range       =   Freq*self.c0/(2*self.kf)
            self.BeamformingUla_IdxMin      =   np.argmin(abs(Range - self.BeamformingUla_RMin))
            self.BeamformingUla_IdxMax      =   np.argmin(abs(Range - self.BeamformingUla_RMax))

    def GetBeamformingUla(self, stSel):
        if stSel == 'Range':
            Freq    =   np.arange(int(self.BeamformingUla_RangeFFT/2))/self.BeamformingUla_RangeFFT * self.fs
            if self.BeamformingUla_Ext > 0:
                Range       =   Freq*self.c0/(2*self.kf)
                IdxMin      =   np.argmin(abs(Range - self.BeamformingUla_RMin))
                IdxMax      =   np.argmin(abs(Range - self.BeamformingUla_RMax))
                Range       =   Range[IdxMin:IdxMax]
            else:
                Range       =   Freq*self.c0/(2*self.kf)
            return Range
        if stSel == 'Freq':
            Freq    =   np.arange(int(self.BeamformingUla_RangeFFT/2))/self.BeamformingUla_RangeFFT * self.fs
            if self.BeamformingUla_Ext > 0:
                Range       =   Freq*self.c0/(2*self.kf)
                IdxMin      =   np.argmin(abs(Range - self.BeamformingUla_RMin))
                IdxMax      =   np.argmin(abs(Range - self.BeamformingUla_RMax))
                Freq        =   Freq[IdxMin:IdxMax]
            return Freq
        if stSel == 'AngFreqNorm':
            Freq            =   (np.arange(int(self.BeamformingUla_AngFFT)) - self.BeamformingUla_AngFFT/2)/self.BeamformingUla_AngFFT
            return Freq

    def RCSRP(self, D, Dmode="full"):
        if Dmode == "full":
            D = D[1:,:]
            Ny, Nx = D.shape
    
            # Remove mean
            Tmp = np.mean(D, axis=0)
            Tmp = np.tile(Tmp, (Ny, 1))
            D = D-Tmp
    
            # hanning window cost function
            Win = np.hanning(Ny)
            ScaWin = sum(Win)
            Win2D = np.tile(Win, (Nx, 1))
            Win2D = Win2D.transpose()

            D = D*Win2D
    
            # print("RCS_FuSca: "+str(self.RCS_FuSca))
            D = np.fft.fft(D, self.RCS_RFFT, 0)/ScaWin*self.RCS_FuSca
            dBV = abs(D)
            D = abs(D)

            # get range/freq/ext index
            Freq = np.arange(int(self.RCS_RFFT/2))/self.RCS_RFFT*self.RCS_fs
            Dist = self.c0*Freq/(2*self.RCS_kf)
            idmin = np.argmin(abs(Dist-self.RCS_RMin))
            idmax = np.argmin(abs(Dist-self.RCS_RMax))
            Freq = Freq[idmin:idmax]
            Dist = self.c0*Freq/(2*self.RCS_kf)
            D = D[idmin:idmax,:]
            dBV = dBV[idmin:idmax,:]
            dBV = np.mean(dBV, axis=1)

        elif Dmode == "dBV":
            D = (10**(D/20))
            dBV = D
            Freq = self.GetRangeProfile("Freq")
            Dist = self.GetRangeProfile("Range")
            Ny, Nx = D.shape

        elif Dmode == "None":
            dBV = abs(D)
            Freq = self.GetRangeProfile("Freq")
            Dist = self.GetRangeProfile("Range")
            if len(D.shape) > 1:
                Ny, Nx = D.shape
            else:
                Nx = 1

        # define rcs calc. variables
        GTx = 10**(13/10)
        GRx = 10**(11/10)
        GCc = 10**(17/10)
        C1  = 1e-7
        R1  = 5e3
        l   = self.c0/self.RCS_fc
        pi = np.pi

        # calc TxPwr as dBm and W
        TxdBm = np.polyval([-0.000007136913372, 0.001293223792425,
                            -0.086184394495573, 2.521879013288421,
                            -20.615765519181373], self.RCS_TxPwr)
        TxW = 10**(TxdBm/10) * 1e-3

        # calc highpass
        CutHigh = 1/(2*pi*C1*R1)

        Hpass = (Freq/CutHigh)/(1+Freq/CutHigh)

        if Nx > 1:
            High = np.tile(Hpass, (Nx, 1)).transpose()
            Rang = np.tile(Dist, (Nx, 1)).transpose()
        else:
            High = Hpass
            Rang = Dist

        Uin = abs(D)/abs(High)
        Pin = Uin**2/100
        Pr  = Pin/GCc
        
        rcs = ((4*pi*Rang**4)/TxW) * ((4*pi)/GTx) * ((4*pi)/GRx) *(Pr/(l**2))

        V0, sm0, loc, drop = self.RCS2dBV(self.RCS_RefRCS, self.RCS_RefDist)

        dBV = 20*np.log10(dBV)
        dBsm = 10*np.log10(rcs)
        
        return dBsm, dBV, Dist

    def RCSBeamformingUla(self, Data):
        Data = Data[1:,:]
        Ny, Nx = Data.shape
        CalData = self.RCS_CalData[:Nx]

        # Remove mean
        Tmp = np.mean(Data, axis=0)
        Tmp = np.tile(Tmp, (Ny, 1))
        Data = Data-Tmp

        # hanning window cost function
        Win = np.hanning(Ny)
        ScaWin = sum(Win)
        Win2D = np.tile(Win, (Nx, 1)).transpose()

        Data = Data*Win2D

        x = np.fft.fftshift(Data, axes=0)
        Data = np.fft.fft(x, self.RCS_RFFT, 0)/ScaWin*self.RCS_FuSca

        Freq = self.RCS_Freq[self.RCS_Idmin:self.RCS_Idmax]
        Dist = self.RCS_Dist[self.RCS_Idmin:self.RCS_Idmax]
        Degs = self.RCS_Degs.copy()
        Data = Data[self.RCS_Idmin:self.RCS_Idmax]

        Ny, Nx = Data.shape

        Win = np.hanning(Nx)
        ScaWin = sum(Win)
        Win = Win*CalData
        Win2D = np.tile(Win, (Ny, 1))
        Data = Data*Win2D

        Data = np.fft.fft(Data, self.RCS_AFFT, 1)/ScaWin
        Data = np.fft.fftshift(Data, axes=1)
        data = abs(Data)
        dBV = 20*np.log10(data)

        Ny, Nx = Data.shape

        GTx = 10**(13/10)
        GRx = 10**(11/10)
        GCc = 10**(17/10)
        C1  = 1e-7
        R1  = 5e3
        l   = self.c0/self.RCS_fc
        pi = np.pi

        # calc TxPwr as dBm and W
        TxdBm = np.polyval([-0.000007136913372, 0.001293223792425,
                            -0.086184394495573, 2.521879013288421,
                            -20.615765519181373], self.RCS_TxPwr)
        TxW = 10**(TxdBm/10) * 1e-3

        # calc highpass
        CutHigh = 1/(2*pi*C1*R1)

        Hpass = Freq/CutHigh/(1+Freq/CutHigh)

        High = np.tile(Hpass, (Nx, 1)).transpose()
        Rang = np.tile(Dist, (Nx, 1)).transpose()

        Uin = abs(Data)/abs(High)
        Pin = Uin**2/100
        Pr  = Pin/GCc

        rcs = ((4*pi*Rang**4)/TxW) * ((4*pi)/GTx) * ((4*pi)/GRx) * (Pr/l**2)

        dBsm = 10*np.log10(rcs)+3

        return dBsm, dBV, Dist, Degs
    

    def RCSCfg(self, Dict):
        if not isinstance(Dict, dict):
            return TypeError
        try:
            if "NFFT" in Dict:
                self.RCS_RFFT = Dict["NFFT"]
            else:
                self.RCS_RFFT = 4096
            if "AFFT" in Dict:
                self.RCS_AFFT = Dict["AFFT"]
            else:
                self.RCS_AFFT = 256
            if "fs" in Dict:
                self.RCS_fs = Dict["fs"]
            else:
                self.RCS_fs = -1
            if "kf" in Dict:
                self.RCS_kf = Dict["kf"]
            else:
                self.RCS_kf = -1
            if "RMin" in Dict:
                self.RCS_RMin = Dict["RMin"]
            else:
                self.RCS_RMin = 0
            if "RMax" in Dict:
                self.RCS_RMax = Dict["RMax"]
            else:
                self.RCS_RMax = 100
            if "fc" in Dict:
                self.RCS_fc = Dict["fc"]
            else:
                self.RCS_fc = -1
            if "TxPwr" in Dict:
                self.RCS_TxPwr = Dict["TxPwr"]
            else:
                self.RCS_TxPwr = -1
            if "FuSca" in Dict:
                self.RCS_FuSca = Dict["FuSca"]
            else:
                self.RCS_FuSca = 0.25/4096
            if "CalData" in Dict:
                self.RCS_CalData = Dict["CalData"]
                self.RCS_RefDist = self.RCS_CalData[33].imag
                self.RCS_RefRCS  = self.RCS_CalData[33].real
            else:
                self.RCS_CalData = -1
                
            self.RCS_Freq = np.arange(int(self.RCS_RFFT/2))/self.RCS_RFFT*self.RCS_fs
            self.RCS_Degs = np.rad2deg((np.arange(self.RCS_AFFT) - self.RCS_AFFT/2)/self.RCS_AFFT)
            self.RCS_Dist = self.RCS_Freq*self.c0/(2*self.RCS_kf)
        
            self.RCS_Idmax = np.argmin(abs(self.RCS_Dist-self.RCS_RMax))
            self.RCS_Idmin = np.argmin(abs(self.RCS_Dist-self.RCS_RMin))

        except:
            print("missing Variables!")
            return

    def RCSCornerCube(self, aCornerCube, DistCoCuRadar):
        TxdBm = np.polyval([-0.000007136913372, 0.001293223792425,
                            -0.086184394495573, 2.521879013288421,
                            -20.615765519181373], self.RCS_TxPwr)
        TxW = 10**(TxdBm/10) * 1e-3
        
        GTx = 10**(13/10)
        GRx = 10**(11/10)
        GCc = 10**(17/10)
        l = self.c0/self.RCS_fc
        pi = np.pi
        log = np.log10

        RCS = 4*pi*aCornerCube**4/(3*l**2)
        
        Pr = TxW/(4*pi*DistCoCuRadar**4)*GTx/(4*pi)*GRx/(4*pi)*RCS*l**2
        PrdBm = 10*log(Pr*1e3)
        PifdBm = PrdBm+10*log(GCc)
        Pif = 10**(PifdBm/10)*1e-3
        Uif = np.sqrt(Pif*50)*np.sqrt(2)
        dBV = 20*log(Uif)
        
        return RCS, dBV

    def RCS2dBV(self, RCS, Range):
        TxdBm = np.polyval([-0.000007136913372, 0.001293223792425,
                            -0.086184394495573, 2.521879013288421,
                            -20.615765519181373], self.RCS_TxPwr)
        TxW = 10**(TxdBm/10) * 1e-3
        
        GTx = 10**(13/10)
        GRx = 10**(11/10)
        GCc = 10**(17/10)
        l = self.c0/self.RCS_fc
        pi = np.pi
        log = np.log10
        
        Pr   = TxW/(4*pi*Range**4)*(GTx/(4*pi))*(GRx/(4*pi))*RCS*l**2
        drop = TxW/(4*pi*self.RCS_Dist**4)*(GTx/(4*pi))*(GRx/(4*pi))*RCS*l**2
        PrdBm = 10*log(Pr*1e3)
        drop = 10*log(drop*1e3)
        PifdBm = PrdBm+10*log(GCc)
        drop = drop+10*log(GCc)
        Pif = 10**(PifdBm/10)*1e-3
        drop = 10**(drop/10)*1e-3
        Uif = np.sqrt(Pif*50)*np.sqrt(2)
        drop = np.sqrt(drop*50)*np.sqrt(2)
        dBV = 20*log(Uif)
        drop = 20*log(drop)
        dBsm = 10*log(RCS)

        loc = np.argmin(abs(self.RCS_Dist-Range))

        V = 10**(dBV/20)
        sm = 10**(dBsm/10)
        drop = 10**(drop/20)

        return V, sm, loc, drop

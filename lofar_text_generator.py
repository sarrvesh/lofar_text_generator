#!/usr/bin/env python
import Tkinter as tk
import tkMessageBox
import datetime
from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np
from ephem import Observer, FixedBody, degrees, separation, Sun

class InvalidATeamError(Exception):
    """Raised when invalid demix source is specified"""
    pass

class TooManyAteamError(Exception):
    """Raised when more than 2 A-team sources are specified"""
    pass

class TooManyBeamletsError(Exception):
    """Raised if more than 488 beamlets are specified"""
    pass

class TooLongFolderNameError(Exception):
    """Raised when the main folder name is too long"""
    pass

class InvalidMainFolderNameError(Exception):
    """Raised when the main folder name is invalid"""
    pass

class InvalidDateTimeError(Exception):
    """Raised when the specified date/time is invalid"""
    pass

class InvalidElevationError(Exception):
    """Raised when the specified elevation is invalid"""
    pass

class InvalidAverageError(Exception):
    """Raised if the averaging parameters are wrong"""
    pass

class InvalidSubbandError(Exception):
    """Raised if the subband list is invalid"""
    pass

class InvalidDurationError(Exception):
    """Raised if the specified duration is invalid"""
    pass

class Imaging():
    """
    Imaging class defines all attributes and methods relevant for an 
    interferometric imaging observation.
    """

    # Have a list of valid calibrators
    VALID_CALIBS = ['3C295', '3C196', '3C48', '3C147', '3C380']
    
    # Have a list of valid A-team sources
    VALID_ATEAMS = ['CasA', 'CygA', 'TauA', 'VirA']
    
    def __init__(self, gui):
        """
        Initialize the Imaging class and do check for input validity
        """
        # Get the project name
        self.projectName = gui.projNameT.get()
        
        # Get the main folder name
        self.mainName = gui.mainNameT.get()
        if len(self.mainName) > 20:
            raise TooLongFolderNameError
        if self.mainName == '':
            raise InvalidMainFolderNameError

        #Parse datetime and make datetime object
        try:
            dy, dm, ds, th, tm, ts = gui.dateT.get().split('-')
            self.startTime = datetime.datetime(int(dy), int(dm), int(ds), \
                                               int(th), int(tm), int(ts))
        except:
            raise InvalidDateTimeError

        # Get minimum elevation to select a calibrator
        try:
            self.elevation = float(gui.elevationT.get())
        except ValueError:
            raise InvalidElevationError
        if self.elevation < 0. or self.elevation > 90.:
            raise InvalidElevationError
            
        # Get the averaging factors
        self.avg = gui.avgT.get()
        if len(self.avg.split(',')) != 2:
            raise InvalidAverageError
        try:
           float(self.avg.split(',')[0])
           float(self.avg.split(',')[1])
        except ValueError:
            raise InvalidAverageError

        # Get sub band list
        self.rcumode = gui.freqModeStr.get()
        self.clockFreq = self._getClockFreq()
        self.subbands = gui.subbandT.get()
        try:
            self.nSubBands = self._countSubBands()
        except:
            raise InvalidSubbandError
        
        # Get the pointing string
        try:
            self.targetLabel, self.targetRA, self.targetDec, self.demixLabel =\
                self._parsePointString(str(gui.pointT.get('1.0','end-1c')))
        except ValueError:
            raise InvalidSubbandError
        self.nBeams = len(self.targetLabel)
        
        # Check for the number of beamlets
        if self.nBeams * self.nSubBands > 488:
            raise TooManyBeamletsError
        
        # Get the observation duration
        try:
            self.targetObsLength = float(gui.durationT.get())
        except ValueError:
            raise InvalidDurationError
        if self.targetObsLength < 0.:
            raise InvalidDurationError
        
        # String common to all imaging blocks
        self.COMMON_STR = "split_targets=F\ncalibration=none\n"\
                "processing=Preprocessing\n"\
                "imagingPipeline=none\ncluster=CEP4\nrepeat=1\n"\
                "nr_tasks=122\nnr_cores_per_task=2\npackageDescription="\
                "HBA Dual Inner, {}, 8bits, ".format(self.rcumode) + \
                "48MHz@144MHz, 1s, 64ch/sb\nantennaMode=HBA Dual Inner\n"\
                "numberOfBitsPerSample=8\n"\
                "integrationTime=1.0\nchannelsPerSubband=64\n"\
                "stationList=all\ntbbPiggybackAllowed=T\n"\
                "aartfaacPiggybackAllowed=T\ncorrelatedData=T\n"\
                "coherentStokesData=F\nincoherentStokesData=F\nflysEye=F\n"\
                "coherentDedisperseChannels=False\n"\
                "flaggingStrategy=HBAdefault\n"\
                "timeStep1=60\ntimeStep2=60"

    def _getClockFreq(self):
        """
        Returns the appropriate clock frequency for the selected RCU mode.
        """
        if self.rcumode == '170-230 MHz':
            return '160 MHz'
        else:
            return '200 MHz'

    def _countSubBands(self):
        """
        Parse the subband string and count the number of subbands
        """
        print self.subbands.split(',')
        count = 0
        for item in self.subbands.split(','):
            # Is it a single number?
            if '..' not in item:
                # Raise a ValueError if item is not a number
                float(item)
                count += 1
            else:
                # Raise a ValueError if subband range is invalid
                float(item.split('..')[0])
                float(item.split('..')[1])
                count += (int(item.split('..')[1]) - \
                         int(item.split('..')[0]) + 1)
        return count

    def _parsePointString(self, strFromTextBox):
        """
        Parse the text mentioned in the pointing textbox
        """
        targetLabel = []
        targetRA = []
        targetDec = []
        demixLabel = []
        for line in strFromTextBox.splitlines():
            splitStr = line.split(',')
            targetLabel.append( splitStr[0] )
            targetRA.append( splitStr[1] )
            targetDec.append( splitStr[2] )
            demixLabel.append( splitStr[3:] )
        return targetLabel, targetRA, targetDec, demixLabel

    def makeHeader(self, outFile):
        """
        Write the header section to the output text file.
        """
        outFile.write('projectName={}\n'.format(self.projectName))
        outFile.write('mainFolderName={}\n'.format(self.mainName))
        outFile.write('mainFolderDescription=Preprocessing:HBA Dual Inner,'+\
                      ' {}, 8bits, 48MHz@144MHz, 1s, 64ch/sb\n\n'\
                      .format(self.rcumode))
    
    def findCalibrator(self, time):
        """
        For a given datetime, return the ``best'' flux density calibrator
        """
        # Create the telescope object
        # The following values were taken from otool.py which is part of the
        # LOFAR source visibility calculator.
        lofar = Observer()
        lofar.lon = '6.869882'
        lofar.lat = '52.915129'
        lofar.elevation = 15.
        lofar.date = time
        
        # Create a target object
        # If multiple targets are specified, use the first one
        target = FixedBody()
        target._epoch = '2000'
        coordTarget = SkyCoord('{} {}'.format(\
                              self.targetRA[0],
                              self.targetDec[0]),
                              unit=(u.hourangle, u.deg))
        target._ra = coordTarget.ra.radian
        target._dec = coordTarget.dec.radian
        target.compute(lofar)
        targetElevation = float(target.alt)*180./np.pi
        
        # Create the calibrator object
        calibrator = FixedBody()
        calibrator._epoch = '2000'
        calName = []
        distance = []
        for item in Imaging.VALID_CALIBS:
            myCoord = self._getCalPointing(item)
            calibrator._ra = myCoord.split(';')[0]
            calibrator._dec = myCoord.split(';')[1]
            calibrator.compute(lofar)
            tempElevation = float(calibrator.alt)*180./np.pi
            if tempElevation > self.elevation:
                calName.append(item)
                distance.append(np.absolute(tempElevation-targetElevation))
        return calName[np.argmin(distance)]

    def _getCalPointing(self, calName):
        """
        Returns coordinates of standard flux density calibrators.
        """
        return {
            '3C295':'14:11:20.5;52:12:10',
            '3C196':'08:13:36.0;48:13:03',
            '3C48' :'01:37:41.3;33:09:35',
            '3C147':'05:42:36.1;49:51:07',
            '3C380':'18:29:31.8;48:44:46',
            '3C286':'13:31:08.3;30:30:33',
            'CTD93':'16:09:13.3;26:41:29',
        }[calName]

    def writeCalibrator(self, startTime, calibName, outFile):
        """
        Write the calibrator section
        """
        outFile.write('BLOCK\n\n')
        outFile.write('packageName={}\n'.format(calibName))
        outFile.write('startTimeUTC={}\n'.format(startTime.isoformat(' ')))
        outFile.write('targetDuration_s=600\n')
        outFile.write('clock={}\n'.format(self.clockFreq))
        outFile.write('instrumentFilter={}\n'.format(self.rcumode))
        outFile.write(self.COMMON_STR+'\n')
        outFile.write('Global_Subbands={};{}\n'.format(self.subbands,\
                       self.nSubBands))
        outFile.write('targetBeams=\n')
        outFile.write('{};{};;;;;T;1800\n'.format(\
                      self._getCalPointing(calibName),\
                      calibName))
        outFile.write('Demix=4;1;64;10;;;F\n')
        outFile.write('\n')

        # Return the start time for the next block
        return startTime + datetime.timedelta(minutes=11)

    def writeTarget(self, startTime, outFile):
        """
        Write the target section.
        """
        outFile.write('BLOCK\n\n')
        if self.nBeams == 1:
            outFile.write('packageName={}\n'.format(self.targetLabel[0]))
        else:
            outFile.write('packageName={}-{}\n'.format(self.targetLabel[0],
                                                       self.targetLabel[1]))
        outFile.write('startTimeUTC={}\n'.format(startTime.isoformat(' ')))
        outFile.write('targetDuration_s={}\n'.format(int(\
                      self.targetObsLength*3600.)))
        outFile.write('clock={}\n'.format(self.clockFreq))
        outFile.write('instrumentFilter={}\n'.format(self.rcumode))
        outFile.write(self.COMMON_STR+'\n')
        outFile.write('Global_Subbands={};{}\n'.format(self.subbands,\
                      self.nSubBands))
        outFile.write('targetBeams=\n')
        # If we have more than one target beam, we need to set the 
        # reference tile beam.
        if self.nBeams > 1:
            refCoord = self._getTileBeam()
            outFile.write('{};REF;256;1;;;F;31200\n'\
                          .format(refCoord.to_string(style='hmsdms', sep=':')\
                          .replace(' ', ';')))
        # Write the user pointing
        for index in range(self.nBeams):
            if self.demixLabel[index] == [] or self.demixLabel[index] == ['']:
                demixStr = ''
            else:
                # Check if the specified demix sources are valid
                if len(self.demixLabel[index]) > 2:
                    raise TooManyAteamError
                for item in self.demixLabel[index]:
                    if item not in Imaging.VALID_ATEAMS:
                        raise InvalidATeamError
                demixStr = '{}'.format(self.demixLabel[index])
                demixStr = demixStr.replace("'", '').replace(' ','')
            outFile.write('{};{};{};;;;;T;31200\n'.format(\
                          self.targetRA[index], self.targetDec[index],\
                          self.targetLabel[index],))
            outFile.write('Demix={};64;10;;{};F\n'.format(\
                          self.avg.replace(',', ';'), demixStr))
        outFile.write('\n')
        # Return the start time for the next block
        return startTime + datetime.timedelta(hours=self.targetObsLength, \
               minutes=1)

    def _getTileBeam(self):
        """
        Compute the midpoint between the different mentioned pointings for the 
        tile beam. Note that the midpoint on the sky for large angular 
        separation is ill-defined. In our case, it is almost always within ~7 
        degrees and so this function should be fine. For more details, see
        https://github.com/astropy/astropy/issues/5766
        """
        tempRA = 0.
        tempDec = 0.
        for index in range(self.nBeams):
            coord = SkyCoord('{} {}'.format(\
                             self.targetRA[index], self.targetDec[index]),
                             unit=(u.hourangle, u.deg))
            tempRA += coord.ra.degree
            tempDec += coord.dec.degree
        return SkyCoord(tempRA/self.nBeams, tempDec/self.nBeams, unit=u.deg)

class GuiWindow():
    def __init__(self):
        """
        Initialize and generate GUI
        """
        self.root = tk.Tk()
        self.root.title('LOFAR Imaging Text Generator')
        self.root.geometry('580x400')
        self.root.option_add('*Font', 'helvetica 11')
                
        self.frame = tk.Frame(self.root, padx=5, pady=5)
        self.frame.grid()
        
        rowIdx = 0        
        self.projNameL = tk.Label(self.frame, text='Project Name:')
        self.projNameL.grid(row=rowIdx, sticky='E')
        self.projNameT = tk.Entry(self.frame, width=7)
        self.projNameT.grid(row=rowIdx, column=1, sticky='W')
        
        rowIdx += 1
        self.mainNameL = tk.Label(self.frame, text='Main folder name:')
        self.mainNameL.grid(row=rowIdx, sticky='E')
        self.mainNameT = tk.Entry(self.frame)
        self.mainNameT.grid(row=rowIdx, column=1, sticky='W')
        
        rowIdx += 1
        self.dateL = tk.Label(self.frame, text='Start date/time:')
        self.dateL.grid(row=rowIdx, sticky='E')
        self.dateT = tk.Entry(self.frame)
        self.dateT.insert(0, '2017-11-11-11-11-11')
        #self.dateT.bind('<Button-1>', self.clearEntry)
        self.dateT.grid(row=rowIdx, column=1, sticky='W')
        
        rowIdx += 1
        self.elevationL = tk.Label(self.frame, text='Min. calibrator '+\
                                   'elevation (deg):')
        self.elevationL.grid(row=rowIdx, sticky='E')
        self.elevationT = tk.Entry(self.frame, width=5)
        self.elevationT.insert(tk.END, '20')
        self.elevationT.grid(row=rowIdx, column=1, sticky='W')
        
        rowIdx += 1
        self.avgL = tk.Label(self.frame, text='Freq. and time. averaging:')
        self.avgL.grid(row=rowIdx, sticky='E')
        self.avgT = tk.Entry(self.frame, width=5)
        self.avgT.insert(0, '4,1')
        #self.avgT.bind('<Button-1>', self.clearEntry)
        self.avgT.grid(row=rowIdx, column=1, sticky='W')
        
        rowIdx += 1
        self.subbandL = tk.Label(self.frame, text='Sub band list:')
        self.subbandL.grid(row=rowIdx, sticky='E')
        self.freqModeStr = tk.StringVar()
        freqModes = {'210-290 MHz', '170-230 MHz', '110-190 MHz', '30-90 MHz',\
                     '10-90 MHz', '30-90 MHz', '10-90 MHz'}
        self.freqModeStr.set('110-190 MHz')
        self.freqModeOption = tk.OptionMenu(self.frame, self.freqModeStr, \
                                            *freqModes)
        self.freqModeOption.configure(state='disabled')
        self.freqModeOption.grid(row=rowIdx, column=1, sticky='W')
        rowIdx += 1
        self.subbandOption = tk.IntVar()
        self.subbandR1 = tk.Radiobutton(self.frame, text='Tier-1', \
                                        variable=self.subbandOption, value=1,\
                                        command=self._setSubbandText)
        self.subbandR1.grid(row=rowIdx, column=1, sticky='W')
        self.subbandR2 = tk.Radiobutton(self.frame, text='user-defined', \
                                        variable=self.subbandOption, value=2,\
                                        command=self._setSubbandText)
        self.subbandR2.grid(row=rowIdx, column=1, padx=80, sticky='W')
        rowIdx+= 1
        self.subbandT = tk.Entry(self.frame, width=45)
        self.subbandT.configure(state='readonly')
        self.subbandT.grid(row=rowIdx, column=1, sticky='W')
        
        rowIdx += 1
        self.pointL = tk.Message(self.frame, text='Target pointing, '+\
                                 'duration, demix (use multiple lines for '+\
                                 'multiple sources):', width=170)
        self.pointL.grid(row=rowIdx, sticky='E')
        self.pointT = tk.Text(self.frame, height=3, width=45)
        self.pointT.insert(tk.END, '<label>,0:0:0,0:0:0,<demix>')
        self.pointT.grid(row=rowIdx, column=1, sticky='W')
        
        rowIdx += 1
        self.durationL = tk.Label(self.frame, text='Target duration (hours):')
        self.durationL.grid(row=rowIdx, sticky='E')
        self.durationT = tk.Entry(self.frame, width=5)
        self.durationT.insert(0, '8')
        self.durationT.grid(row=rowIdx, column=1, sticky='W')
        
        rowIdx += 1
        self.submitB = tk.Button(self.frame, text='SUBMIT', justify=tk.CENTER,\
                                 command=self.actionSubmit)
        self.submitB.grid(row=rowIdx, column=1, sticky='W', pady=10)
        
        self.cancelB = tk.Button(self.frame, text='RESET', justify=tk.CENTER,\
                                 command=self.resetForms)
        self.cancelB.grid(row=rowIdx, column=1, padx=100, sticky='W', pady=10)

    def _setSubbandText(self):
        """
        Based on which radio button is enabled, set the appropriate value in 
        the subband list text box.
        """
        option = self.subbandOption.get()
        if option == 1:
            # This is tier-1 setup
            tier1List = '104..136,138..163,165..180,182..184,187..209,'+\
                    '212..213,215..240,242..255,257..273,275..300,302..328,'+\
                    '330..347,349,364,372,380,388,396,404,413,421,430,438,447'
            self.subbandT.configure(state='normal')
            self.subbandT.delete(0, tk.END)
            self.subbandT.insert(0, tier1List)
            self.subbandT.configure(state='readonly')
        elif option == 2:
            # This is for manual entry
            self.subbandT.configure(state='normal')
            self.subbandT.delete(0, tk.END)

    def resetForms(self):
        """
        Reset the gui to original state
        """
        self.projNameT.delete(0, tk.END)
        self.mainNameT.delete(0, tk.END)
        self.dateT.delete(0, tk.END)
        self.dateT.insert(0, 'yyyy-mm-dd-hh-mm-ss')
        self.elevationT.delete(0, tk.END)
        self.avgT.delete(0, tk.END)
        self.avgT.insert(0, '4,1')
        self.subbandOption.set(None)
        self.subbandT.configure(state='normal')
        self.subbandT.delete(0, tk.END)
        self.subbandT.configure(state='readonly')
        self.pointT.delete(1.0, tk.END)
        self.pointT.insert(tk.END, '<label>,<ra (hms)>,<dec (dms)>,<demix>')

    def clearEntry(self, event):
        event.widget.delete(0, 'end')
    
    def actionSubmit(self):
        """
        This function coordinates all the background processing that happens
        after the SUBMIT button is clicked.
        """
        outFile = open('output.txt', 'w')
        try:
            img = Imaging(self)
        except TooLongFolderNameError:
            showErrorPopUp('Main folder name cannot be longer than 20 '+\
                           'characters.')
            return None
        except InvalidMainFolderNameError:
            showErrorPopUp('Invalid main folder name.')
            return None
        except InvalidDateTimeError:
            showErrorPopUp('Entered date/time is invalid.')
            return None
        except InvalidElevationError:
            showErrorPopUp('Specified elevation is invalid.')
            return None
        except InvalidAverageError:
            showErrorPopUp('Invalid averaging parameters specified.')
            return None
        except InvalidSubbandError:
            showErrorPopUp('Invalid subband specified.')
            return None
        except TooManyBeamletsError:
            showErrorPopUp('No. of subbands * pointings cannot be more than'+\
                           '488.')
            return None
        except InvalidDurationError:
            showErrorPopUp('Specified target scan duration is invalid')
            return None
        except: 
            showErrorPopUp('Encountered unknown error. Contact Sarrvesh '+\
                           'if this happens.')
            return None

        # Write the header section
        img.makeHeader(outFile)
        # Write the first calibrator block
        startTime = img.startTime
        calName = img.findCalibrator(startTime)
        if calName is None:
            showErrorPopUp('Unable to find a suitable calibrator.')
            return None
        print 'INFO: Using {} as flux density calibrator'.format(calName)
        startTime = img.writeCalibrator(startTime, calName, outFile)
        # Write the target block
        try:
            startTime = img.writeTarget(startTime, outFile)
        except InvalidATeamError:
            showErrorPopUp('Invalid A-team source.')
            return None
        except TooManyAteamError:
            showErrorPopUp('Cannot demix more than 2 sources.')
            return None
        # Write the second calibrator block
        calName = img.findCalibrator(startTime)
        if calName is None:
            showErrorPopUp('Unable to find a suitable calibrator.')
            return None
        print 'INFO: Using {} as flux density calibrator'.format(calName)
        startTime = img.writeCalibrator(startTime, calName, outFile)
            
        outFile.close()

def showErrorPopUp(message):
    """
    Display an error pop-up message
    """
    tkMessageBox.showerror('Error', message)

if __name__ == '__main__':
    gui = GuiWindow()
    gui.root.mainloop()

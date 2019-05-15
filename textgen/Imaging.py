import datetime
from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np
from ephem import Observer, FixedBody, degrees, Sun, Moon

from textgen.errors import *
from textgen.GUIWindow import *

class Imaging():
    """
    Imaging class defines all attributes and methods relevant for an 
    interferometric imaging observation.
    """

    # Have a list of valid calibrators
    VALID_CALIBS = ['3C295', '3C196', '3C48']
    #VALID_CALIBS = ['3C295', '3C196', '3C48', '3C147', '3C380']
    
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
            
        # Get the array configuration
        arrayStr = gui.arrayConfigStr.get()
        self.arrayConfig = {'Super-terp only': 'superterp',
                            'Core stations': 'core',
                            'Dutch stations': 'NL',
                            'International': 'all'}[arrayStr]

        # Get sub band list
        self.antennaMode = gui.antennaModeStr.get()
        self.rcumode = gui.freqModeStr.get()
        self.clockFreq = self._getClockFreq()
        self.subbands = gui.subbandT.get()
        self._validateSubBands()
        self.nSubBands = self._countSubBands()
        
        # Check if dysco has to be enabled or disabled
        if gui.dyscoModeStr.get() == 'Enabled':
           storagemanager = "dysco"
        else:
           storagemanager = " "
                
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
        
        # Check if the listed targets are above 30 degrees for the entire
        # duration of the observation
        for beamIdx in range(self.nBeams):
            coord = '{};{}'.format(self.targetRA[beamIdx], \
                                   self.targetDec[beamIdx])
            if not self._isVisible(coord, self.startTime, self.targetObsLength):
                showWarningPopUp('One of the specified targets is below user '+\
                   'specified elevation [{} degrees].'.format(self.elevation) +\
                   ' Will generate text file anyway.')
            # Check the distance between the Sun and the target beams
            if self._findDistanceToSun(coord)< 30.:
                showWarningPopUp('Sun is within 30 degrees of source {}.'.\
                                 format(self.targetLabel[beamIdx]) +\
                                 'Will generate text file anyway.')
            # Check the distance between the Sun and the target beams
            print('INFO: Moon is {} degrees away from the pointing center.'.\
                  format(self._findDistanceToMoon(coord)) )
        
        # String common to all imaging blocks
        self.COMMON_STR = "split_targets=F\ncalibration=none\n"\
                "processing=Preprocessing\n"\
                "imagingPipeline=none\ncluster=CEP4\nrepeat=1\n"\
                "nr_cores_per_task=2\npackageDescription="\
                "{}, {}, 8bits, ".format(self.antennaMode, self.rcumode) + \
                "1s, 64ch/sb\nnumberOfBitsPerSample=8\n"\
                "integrationTime=1.0\nchannelsPerSubband=64\n"\
                "tbbPiggybackAllowed=T\n"\
                "aartfaacPiggybackAllowed=T\ncorrelatedData=T\n"\
                "coherentStokesData=F\nincoherentStokesData=F\nflysEye=F\n"\
                "coherentDedisperseChannels=False\n"\
                "storagemanager={}\n".format(storagemanager) + \
                "timeStep1=60\ntimeStep2=60"
        # Set the list of valid calibrators
        self.validCalibs = Imaging.VALID_CALIBS[:]

    def _findDistanceToMoon(self, coord):
        """
        Print the distance between the specified pointing center and the Moon.
        """
        moon = Moon()
        moon.compute(self.startTime)
        coordMoon = SkyCoord('{} {}'.format(moon.ra, moon.dec), \
                             unit=(u.hourangle, u.deg))
        coordTarget = SkyCoord('{} {}'.format(coord.split(';')[0], \
                              coord.split(';')[1]), \
                              unit=(u.hourangle, u.deg))

        # Find the separation between the Sun and the target
        return coordMoon.separation(coordTarget).deg
    
    def _findDistanceToSun(self, coord):
        """
        Print the distance between the specified pointing center and the Sun.
        """        
        # Find the coordinates of the Sun at the start of the observing run
        sun = Sun()
        sun.compute(self.startTime)
        coordSun = SkyCoord('{} {}'.format(sun.ra, sun.dec), 
                            unit=(u.hourangle, u.deg))
        coordTarget = SkyCoord('{} {}'.format(coord.split(';')[0], \
                              coord.split(';')[1]), \
                              unit=(u.hourangle, u.deg))

        # Find the separation between the Sun and the target
        return coordSun.separation(coordTarget).deg

    def _getClockFreq(self):
        """
        Returns the appropriate clock frequency for the selected RCU mode.
        """
        if self.rcumode == '170-230 MHz':
            return '160 MHz'
        else:
            return '200 MHz'

    def _validateSubBands(self):
        """
        Parse the subband string and check if they are all valid
        """
        for item in self.subbands.split(','):
            # Is it a single number?
            if '..' not in item:
                try: 
                    s1 = int(item)
                except:
                    raise InvalidSubbandError
                if self.rcumode == '30-90 MHz':
                    if s1<154 or s1>461:
                        raise OutOfBoundsSubBandError
                elif self.rcumode == '170-230 MHz':
                    if s1<64 or s1>448:
                        raise OutOfBoundsSubBandError
                else:
                    if s1<51 or s1>461:
                        raise OutOfBoundsSubBandError
            # Is it a range?
            else:
                try:
                    s1 = int(item.split('..')[0])
                    s2 = int(item.split('..')[1])
                except ValueError:
                    raise InvalidSubBandError
                if s1>s2:
                    raise InvalidSubBandOrderError
                if self.rcumode == '30-90 MHz':
                    if s1<154 or s2>461:
                        raise OutOfBoundsSubBandError
                elif self.rcumode == '170-230 MHz':
                    if s1<64 or s2>448:
                        raise OutOfBoundsSubBandError
                else:
                    if s1<51 or s2>461:
                        raise OutOfBoundsSubBandError

    def _countSubBands(self):
        """
        Parse the subband string and count the number of subbands
        """
        count = 0
        for item in self.subbands.split(','):
            # Is it a single number?
            if '..' not in item:
                count += 1
            else:
                s1 = int(item.split('..')[0])
                s2 = int(item.split('..')[1])
                count += (s2 - s1 + 1)
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
            # Remove spaces if there are any
            line = line.replace(' ', '')
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
        outFile.write('mainFolderDescription=Preprocessing:{},'\
                      ' {}, 8bits, 1s, 64ch/sb\n\n'\
                      .format(self.antennaMode, self.rcumode))
    
    def findHBACalibrator(self, time, exclude=None):
        """
        For a given datetime, return the ``best'' flux density calibrator
        for an HBA observation.
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
        calibElevation = []
        if exclude is not None:
            self.validCalibs.remove(exclude)
        for item in self.validCalibs:
            myCoord = self._getCalPointing(item)
            calibrator._ra = myCoord.split(';')[0]
            calibrator._dec = myCoord.split(';')[1]
            calibrator.compute(lofar)
            tempElevation = float(calibrator.alt)*180./np.pi
            #print 'Temp is', tempElevation
            #if tempElevation > self.elevation:
            #    calName.append(item)
            #    calibElevation.append(tempElevation)
            #print calibElevation
            calName.append(item)
            calibElevation.append(tempElevation)
        if calibElevation[np.argmax(calibElevation)] < self.elevation:
           showWarningPopUp('One of the chosen calibrator is below user '+\
               'specified elevation [{} degrees].'.format(self.elevation) +\
               ' Will generate text file anyway.')
        return calName[np.argmax(calibElevation)]

    def _findLBACalibrator(self, time):
        """
        For a given observation, return the ``best'' flux density calibrator
        for an LBA observation. Note that, for LBA, the calibrator must be 
        visibile for the entire duration of the target scan unlike
        _findHBACalibrator.
        """
        calName = self.findHBACalibrator(time)
        while True:
            coord = self._getCalPointing(calName)
            if self._isVisible(coord, time, self.targetObsLength):
                return calName
            else:
                print('{} is invisible'.format(calName))
                calName = self.findHBACalibrator(time, exclude=calName)
                print('Will try {} next'.format(calName))
        # If control reaches here, no suitable calibrator could be found
        raise NoGoodLBACalibratorError

    def _isVisible(self, coord, startTime, duration):
        """
        For a given source and datetime, check if the source is visible
        during the specified duration. Not that the horizon here is 
        the elevation specified by the user. Note that the coordinate of 
        source is specified as 'RA;Dec'
        """
        endTime = startTime + datetime.timedelta(hours=duration)
        time = startTime
        while time < endTime:
            lofar = Observer()
            lofar.lon = '6.869882'
            lofar.lat = '52.915129'
            lofar.elevation = 15.
            lofar.date = time
            
            target = FixedBody()
            target._epoch = '2000'
            coordTarget = SkyCoord('{} {}'.format(coord.split(';')[0], \
                              coord.split(';')[1]), \
                              unit=(u.hourangle, u.deg))
            target._ra = coordTarget.ra.radian
            target._dec = coordTarget.dec.radian
            target.compute(lofar)
            targetElevation = float(target.alt)*180./np.pi
            
            if targetElevation < self.elevation:
                return False

            time += datetime.timedelta(minutes=15)
        # Turns out this source is above the horizon
        return True

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
        Write the calibrator section. This is almost always used for HBA 
        and never for LBA observations.
        """
        outFile.write('BLOCK\n\n')
        outFile.write('packageName={}\n'.format(calibName))
        outFile.write('startTimeUTC={}\n'.format(startTime.isoformat(' ')))
        outFile.write('targetDuration_s=600\n')
        outFile.write('clock={}\n'.format(self.clockFreq))
        outFile.write('instrumentFilter={}\n'.format(self.rcumode))
        outFile.write('nr_tasks={}\n'.format(1+int(self.nSubBands)/2))
        outFile.write('antennaMode={}\n'.format(self.antennaMode))
        outFile.write('flaggingStrategy=HBAdefault\n')
        outFile.write('stationList={}\n'.format(self.arrayConfig))
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
        outFile.write('nr_tasks={}\n'.format(1+int(self.nSubBands)/2))
        outFile.write('antennaMode={}\n'.format(self.antennaMode))
        if self.rcumode == '10-90 MHz' or self.rcumode == '30-90 MHz':
            outFile.write("flaggingStrategy=LBAdefault\n")
        else:
            outFile.write("flaggingStrategy=HBAdefault\n")
        outFile.write('stationList={}\n'.format(self.arrayConfig))
        outFile.write(self.COMMON_STR+'\n')
        outFile.write('Global_Subbands={};{}\n'.format(self.subbands,\
                      self.nSubBands))
        outFile.write('targetBeams=\n')
        if self.rcumode == '10-90 MHz' or self.rcumode == '30-90 MHz':
            # Get the calibrator name for LBA
            calName = self._findLBACalibrator(startTime)
            print('INFO: Using {} as the flux density calibrator'.\
                   format(calName))
            outFile.write('{};{};;;;;T;1800\n'.format(\
                      self._getCalPointing(calName), calName))
            outFile.write('Demix={};64;10;;[CasA,CygA];F\n'.format(\
                      self.avg.replace(',', ';')))
        else:
            # If we have more than one target beam, we need to set the 
            # reference tile beam.
            if self.nBeams > 1:
                refCoord = self._getTileBeam()
                sapName1 = self.targetLabel[0].split('-')[0].split('+')[0]
                sapName2 = self.targetLabel[1].split('-')[0].split('+')[0]
                outFile.write('{};{}{}REF;256;1;;;F;31200\n'\
                          .format(refCoord.to_string(style='hmsdms', sep=':')\
                          .replace(' ', ';'), sapName1, sapName2))
        # Write the user pointing
        for index in range(self.nBeams):
            if self.demixLabel[index] == [] or self.demixLabel[index] == ['']:
                demixStr = ''
                demixInterval = '64;10'
            else:
                # Check if the specified demix sources are valid
                if len(self.demixLabel[index]) > 2:
                    raise TooManyAteamError
                for item in self.demixLabel[index]:
                    if item not in Imaging.VALID_ATEAMS:
                        raise InvalidATeamError
                # The time and frequency demixing intervals should be an integer 
                # multiple of the time and freq averaging values specified by 
                # the user
                demixInterval = '64;10'
                if 64%int(self.avg.split(',')[0]) != 0:
                    raise InvalidFreqAvgError
                if 10%int(self.avg.split(',')[1]) != 0:
                    demixInterval = '64;12'
                demixStr = '{}'.format(self.demixLabel[index])
                demixStr = demixStr.replace("'", '').replace(' ','')
            outFile.write('{};{};{};;;;;T;31200\n'.format(\
                          self.targetRA[index], self.targetDec[index],\
                          self.targetLabel[index],))
            outFile.write('Demix={};{};;{};F\n'.format(\
                          self.avg.replace(',', ';'), demixInterval, demixStr))
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
        _tileBeam = SkyCoord(tempRA/self.nBeams, tempDec/self.nBeams, unit=u.deg)
        if _tileBeam.separation(coord).deg > 7:
           # Specified pointings stradle the 0 degree line
           # Find the midpoint after shifting the coordinates
           # FIXME
           tempRA = 0.
           tempDec=0.
           for index in range(self.nBeams):
              coord = SkyCoord('{} {}'.format( \
                             self.targetRA[index], self.targetDec[index]), 
                             unit=(u.hourangle, u.deg))
              tempRA += ((coord.ra.degree + 10.)%360.)
              tempDec += coord.dec.degree
           _tileBeam = SkyCoord(tempRA/self.nBeams - 10., tempDec/self.nBeams, unit=u.deg)
        return _tileBeam
    
    def __exit__(self, *err):
        self.close()

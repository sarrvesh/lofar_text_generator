import Tkinter as tk
import tkMessageBox 

from errors import *
from Imaging import *

class GuiWindow():
    def __init__(self):
        """
        Initialize and generate GUI
        """
        self.root = tk.Tk()
        self.root.title('LOFAR Imaging Text Generator')
        self.root.geometry('580x440')
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
        freqModes = ['10-90 MHz', '30-90 MHz', '110-190 MHz', '170-230 MHz',\
                     '210-290 MHz']
        self.freqModeStr.set('110-190 MHz')
        self.freqModeOption = tk.OptionMenu(self.frame, self.freqModeStr, \
                                            *freqModes, \
                                            command=self._changeAntennaMode)
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
        AntennaModeL = tk.Label(self.frame, text='Antenna mode:')
        AntennaModeL.grid(row=rowIdx, sticky='E')
        self.antennaModeStr = tk.StringVar()
        self.antennaModeStr.set('HBA Dual Inner')
        antMode = ['HBA Zero', 'HBA Zero Inner', 'HBA One', \
                   'HBA One Inner', 'HBA Dual', 'HBA Dual Inner', \
                   'HBA Joined', 'HBA Joined Inner']
        self.antennaModeOption = tk.OptionMenu(self.frame, \
                                               self.antennaModeStr, *antMode)
        self.antennaModeOption.grid(row=rowIdx, column=1, sticky='W')        
        
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

    def _changeAntennaMode(self, *args):
        """
        Set the antenna mode dropdown button based on the chosen RCU mode. 
        Note that at the same time, we should also disable the Tier-1 
        option button
        """
        optionMenu = self.antennaModeOption.children["menu"]
        optionMenu.delete(0, "end")
        option = self.freqModeStr.get()
        if option == '210-290 MHz' or option == '170-230 MHz' or \
           option == '110-190 MHz':
            # Display all HBA modes
            antMode = ['HBA Zero', 'HBA Zero Inner', 'HBA One', \
                       'HBA One Inner', 'HBA Dual', 'HBA Dual Inner', \
                       'HBA Joined', 'HBA Joined Inner']
            self.antennaModeStr.set('HBA Dual Inner')
            self.subbandR1.configure(state='normal')
        else:
            # Display all LBA modes
            antMode = ['LBA Inner', 'LBA Outer', 'LBA Sparse Even', \
                       'LBA Sparse Odd', 'LBA X', 'LBA Y']
            self.antennaModeStr.set('LBA Outer')
            self.subbandR1.configure(state='disabled')
            self.subbandOption.set(2); self._setSubbandText()
        for mode in antMode:
            optionMenu.add_command(label=mode, command=tk._setit(\
                                   self.antennaModeStr, mode))

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
        self.subbandR1.configure(state='normal')
        self.subbandOption.set(None)
        self.subbandT.configure(state='normal')
        self.subbandT.delete(0, tk.END)
        self.subbandT.configure(state='readonly')
        self.pointT.delete(1.0, tk.END)
        self.pointT.insert(tk.END, '<label>,<ra (hms)>,<dec (dms)>,<demix>')
        self.freqModeStr.set('110-190 MHz')
        optionMenu = self.antennaModeOption.children["menu"]
        optionMenu.delete(0, "end")
        antMode = ['HBA Zero', 'HBA Zero Inner', 'HBA One', \
                   'HBA One Inner', 'HBA Dual', 'HBA Dual Inner', \
                   'HBA Joined', 'HBA Joined Inner']
        self.antennaModeStr.set('HBA Dual Inner')
        for mode in antMode:
            optionMenu.add_command(label=mode, command=tk._setit(\
                                   self.antennaModeStr, mode))
        

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
                           ' 488.')
            return None
        except InvalidDurationError:
            showErrorPopUp('Specified target scan duration is invalid')
            return None
        except OutOfBoundsSubBandError:
            showErrorPopUp('One of the specified subband is outside the '+\
                           'selected filter.')
            return None
        except InvalidSubBandOrderError:
            showErrorPopUp('Invalid subband specification. A cannot be '+\
                           'greater than B in "A..B".')
            return None
        #except: 
        #    showErrorPopUp('Encountered unknown error. Contact Sarrvesh '+\
        #                   'if this happens.')
        #    return None

        # Write the header section
        img.makeHeader(outFile)
        
        startTime = img.startTime
        if img.rcumode == '10-90 MHz' or img.rcumode == '30-90 MHz':
            try:
                startTime = img.writeTarget(startTime, outFile)
            except InvalidATeamError:
                showErrorPopUp('Invalid A-team source.')
                return None
            except TooManyAteamError:
                showErrorPopUp('Cannot demix more than 2 sources.')
                return None
            except NoGoodLBACalibratorError:
                showErrorPopUp('Could not find a good calibrator.')
                return None
        else:
            # Write the first calibrator block
            calName = img.findHBACalibrator(startTime)
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
            calName = img.findHBACalibrator(startTime, calName)
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

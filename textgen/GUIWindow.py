import Tkinter as tk
import tkMessageBox 
import subprocess
import os

from errors import *
from Imaging import *

class GuiWindow():
    def __init__(self):
        """
        Initialize and generate GUI
        """
        self.root = tk.Tk()
        self.root.title('LOFAR Imaging Text Generator')
        #self.root.geometry('580x470')
        self.root.option_add('*Font', 'helvetica 11')
                
        frame = tk.Frame(self.root, padx=10, pady=5)
        frame.grid()
        
        rowIdx = 0        
        projNameL = tk.Label(frame, text='Project Name:')
        projNameL.grid(row=rowIdx, sticky='E')
        self.projNameT = tk.Entry(frame, width=7)
        self.projNameT.grid(row=rowIdx, column=1, sticky='W')
        
        rowIdx += 1
        mainNameL = tk.Label(frame, text='Main folder name:')
        mainNameL.grid(row=rowIdx, sticky='E')
        self.mainNameT = tk.Entry(frame)
        self.mainNameT.grid(row=rowIdx, column=1, sticky='W')
        
        rowIdx += 1
        dateL = tk.Label(frame, text='Start date/time:')
        dateL.grid(row=rowIdx, sticky='E')
        self.dateT = tk.Entry(frame)
        self.dateT.insert(0, 'yyyy-mm-dd-hh-mm-ss')
        #self.dateT.bind('<Button-1>', self.clearEntry)
        self.dateT.grid(row=rowIdx, column=1, sticky='W')
        
        rowIdx += 1
        elevationL = tk.Label(frame, text='Min. '+\
                                   'elevation (deg):')
        elevationL.grid(row=rowIdx, sticky='E')
        self.elevationT = tk.Entry(frame, width=5)
        self.elevationT.insert(tk.END, '30')
        self.elevationT.grid(row=rowIdx, column=1, sticky='W')
        
        rowIdx += 1
        avgL = tk.Label(frame, text='Freq. and time. averaging:')
        avgL.grid(row=rowIdx, sticky='E')
        self.avgT = tk.Entry(frame, width=5)
        self.avgT.insert(0, '4,1')
        #self.avgT.bind('<Button-1>', self.clearEntry)
        self.avgT.grid(row=rowIdx, column=1, sticky='W')
        
        rowIdx += 1
        arrayConfigL = tk.Label(frame, text='Array configuration:')
        arrayConfigL.grid(row=rowIdx, sticky='E')
        self.arrayConfigStr = tk.StringVar()
        arrayConfig = ['Super-terp only', 'Core stations', 'Dutch stations',\
                       'International']
        self.arrayConfigStr.set('International')
        self.arrayConfigOption = tk.OptionMenu(frame, \
                                      self.arrayConfigStr, *arrayConfig)
        self.arrayConfigOption.grid(row=rowIdx, column=1, sticky='W')
        
        rowIdx += 1
        subbandL = tk.Label(frame, text='Sub band list:')
        subbandL.grid(row=rowIdx, sticky='E')
        self.freqModeStr = tk.StringVar()
        freqModes = ['10-90 MHz', '30-90 MHz', '110-190 MHz', '170-230 MHz',\
                     '210-290 MHz']
        self.freqModeStr.set('110-190 MHz')
        self.freqModeOption = tk.OptionMenu(frame, self.freqModeStr, \
                                            *freqModes, \
                                            command=self._changeAntennaMode)
        self.freqModeOption.grid(row=rowIdx, column=1, sticky='W')
        rowIdx += 1
        self.subbandOption = tk.IntVar()
        self.subbandR1 = tk.Radiobutton(frame, text='Tier-1', \
                                        variable=self.subbandOption, value=1,\
                                        command=self._setSubbandText)
        self.subbandR1.grid(row=rowIdx, column=1, sticky='W')
        self.subbandR2 = tk.Radiobutton(frame, text='user-defined', \
                                        variable=self.subbandOption, value=2,\
                                        command=self._setSubbandText)
        self.subbandR2.grid(row=rowIdx, column=1, padx=80, sticky='W')
        rowIdx+= 1
        self.subbandT = tk.Entry(frame, width=45)
        self.subbandT.configure(state='readonly')
        self.subbandT.grid(row=rowIdx, column=1, sticky='W')
        
        rowIdx += 1
        AntennaModeL = tk.Label(frame, text='Antenna mode:')
        AntennaModeL.grid(row=rowIdx, sticky='E')
        self.antennaModeStr = tk.StringVar()
        self.antennaModeStr.set('HBA Dual Inner')
        antMode = ['HBA Zero', 'HBA Zero Inner', 'HBA One', \
                   'HBA One Inner', 'HBA Dual', 'HBA Dual Inner', \
                   'HBA Joined', 'HBA Joined Inner']
        self.antennaModeOption = tk.OptionMenu(frame, \
                                               self.antennaModeStr, *antMode)
        self.antennaModeOption.grid(row=rowIdx, column=1, sticky='W')        
        
        rowIdx += 1
        pointL = tk.Message(frame, text='Target pointing, '+\
                                 'duration, demix (use multiple lines for '+\
                                 'multiple sources):', width=170)
        pointL.grid(row=rowIdx, sticky='E')
        self.pointT = tk.Text(frame, height=3, width=45)
        self.pointT.insert(tk.END, '<label>,<ra (hms)>,<dec (dms)>,<demix>')
        self.pointT.grid(row=rowIdx, column=1, sticky='W')
        
        rowIdx += 1
        durationL = tk.Label(frame, text='Target duration (hours):')
        durationL.grid(row=rowIdx, sticky='E')
        self.durationT = tk.Entry(frame, width=5)
        self.durationT.insert(0, '8')
        self.durationT.grid(row=rowIdx, column=1, sticky='W')
        
        rowIdx += 1
        compressL = tk.Label(frame, text='Dysco compression:')
        compressL.grid(row=rowIdx, sticky='E')
        self.dyscoModeStr = tk.StringVar()
        self.dyscoModeStr.set('Enabled')
        dyscoMode = ['Enabled', 'Disabled']
        self.dyscoModeOption = tk.OptionMenu(frame, self.dyscoModeStr, \
                                             *dyscoMode)
        self.dyscoModeOption.grid(row=rowIdx, column=1, sticky='W')
        
        rowIdx += 1
        self.submitB = tk.Button(frame, text='SUBMIT', justify=tk.CENTER,\
                                 command=self.actionSubmit)
        self.submitB.grid(row=rowIdx, column=1, sticky='W', pady=10)
        
        self.cancelB = tk.Button(frame, text='RESET', justify=tk.CENTER,\
                                 command=self.resetForms)
        self.cancelB.grid(row=rowIdx, column=1, padx=100, sticky='W', pady=10)

    def _changeAntennaMode(self, *args):
        """
        Set the antenna mode dropdown button based on the chosen RCU mode. 
        Note that at the same time, we should also disable the Tier-1 
        option button.
        Dysco compression should also be set here. Dysco compression is 
        enabled when HBA RCU modes are chosen.
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
            self.dyscoModeStr.set('Enabled')
        else:
            # Display all LBA modes
            antMode = ['LBA Inner', 'LBA Outer', 'LBA Sparse Even', \
                       'LBA Sparse Odd', 'LBA X', 'LBA Y']
            self.antennaModeStr.set('LBA Outer')
            self.subbandR1.configure(state='disabled')
            self.subbandOption.set(2); self._setSubbandText()
            self.dyscoModeStr.set('Disabled')
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
        self.elevationT.insert(0, '20')
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
        self.arrayConfigStr.set('International')
        optionMenu = self.antennaModeOption.children["menu"]
        optionMenu.delete(0, "end")
        antMode = ['HBA Zero', 'HBA Zero Inner', 'HBA One', \
                   'HBA One Inner', 'HBA Dual', 'HBA Dual Inner', \
                   'HBA Joined', 'HBA Joined Inner']
        self.antennaModeStr.set('HBA Dual Inner')
        self.dyscoModeStr.set('Enabled')
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
        
        try:
            img = Imaging(self)
        except:
            errString = getErrorMessage()
            showErrorPopUp(errString)
            return None

        outFileName='{}_{}_{}.txt'.format(img.projectName, \
                                  img.startTime.strftime('%Y%m%d'),\
                                  img.targetLabel[0])
        outFile = open(outFileName, 'w')

        # Write the header section
        img.makeHeader(outFile)
        
        startTime = img.startTime
        if img.rcumode == '10-90 MHz' or img.rcumode == '30-90 MHz':
            # In the case LBA
            try:
                startTime = img.writeTarget(startTime, outFile)
            except:
                errString = getErrorMessage()
                showErrorPopUp(errString)
                return None
        else:
            # In the case of HBA
            # Write the first calibrator block
            calName = img.findHBACalibrator(startTime)
            if calName is None:
                showErrorPopUp('Unable to find a suitable calibrator.')
                return None
            print GREEN_COLOR +\
                  'INFO: Using {} as flux density calibrator'.format(calName) +\
                  NO_COLOR
            startTime = img.writeCalibrator(startTime, calName, outFile)
            # Write the target block
            try:
                startTime = img.writeTarget(startTime, outFile)
            except:
                errString = getErrorMessage()
                showErrorPopUp(errString)
                return None
            # Write the second calibrator block
            calName = img.findHBACalibrator(startTime, calName)
            if calName is None:
                showErrorPopUp('Unable to find a suitable calibrator.')
                return None
            print GREEN_COLOR +\
                  'INFO: Using {} as flux density calibrator'.format(calName) +\
                  NO_COLOR
            startTime = img.writeCalibrator(startTime, calName, outFile)
            
        outFile.close()
        
        # If xmlgen.py exists, convert the text file to xml
        FNULL = open(os.devnull, 'w')
        try:
            subprocess.call(['./xmlgen.py', '-i', outFileName], stdout=FNULL, \
                            stderr=subprocess.STDOUT)
            print GREEN_COLOR + 'INFO: Found xmlgen.py. Generating XML file.' +\
                  NO_COLOR
        except OSError:
            print RED_COLOR + 'INFO: Could not find xmlgen.py in the ' +\
                  'current working directory.' + NO_COLOR
            try:
                subprocess.call(['xmlgen.py', '-i', outFileName], \
                           stdout=FNULL, stderr=subprocess.STDOUT)
                print GREEN_COLOR + \
                      'INFO: Found xmlgen.py. Generating XML file.' + NO_COLOR
            except OSError:
                print RED_COLOR + 'INFO: Could not find xmlgen.py in PATH'
                print 'INFO: Only text output will be generated.'
                print 'INFO: Run xmlgen.py manually to generate the xml file.'+\
                      NO_COLOR
        FNULL.close()
        
        print ''

#!/usr/bin/env python
import Tkinter as tk
import tkMessageBox
import datetime

class GuiWindow():
    def __init__(self):
        """
        Initialize and generate GUI
        """
        self.root = tk.Tk()
        self.root.title('LOFAR Imaging Text Generator')
        self.root.geometry('710x320')
        self.root.option_add('*Font', 'helvetica 14')
                
        self.frame = tk.Frame(self.root, padx=1, pady=5)
        self.frame.grid()
        
        self.projNameL = tk.Label(self.frame, text='Project Name:')
        self.projNameL.grid(row=0, sticky='E')
        self.projNameT = tk.Entry(self.frame, width=7)
        self.projNameT.grid(row=0, column=1, sticky='W')
        
        self.mainNameL = tk.Label(self.frame, text='Main folder name:')
        self.mainNameL.grid(row=1, sticky='E')
        self.mainNameT = tk.Entry(self.frame)
        self.mainNameT.grid(row=1, column=1, sticky='W')
        
        self.dateL = tk.Label(self.frame, text='Start date/time:')
        self.dateL.grid(row=2, sticky='E')
        self.dateT = tk.Entry(self.frame)
        self.dateT.insert(0, 'yyyy-mm-dd-hh-mm-ss')
        self.dateT.bind('<Button-1>', self.clearEntry)
        self.dateT.grid(row=2, column=1, sticky='W')
        
        self.elevationL = tk.Label(self.frame, text='Min. calibrator '+\
                                   'elevation (deg):')
        self.elevationL.grid(row=3, sticky='E')
        self.elevationT = tk.Entry(self.frame)
        self.elevationT.grid(row=3, column=1, sticky='W')
        
        self.avgL = tk.Label(self.frame, text='Freq. and time. averaging:')
        self.avgL.grid(row=4, sticky='E')
        self.avgT = tk.Entry(self.frame)
        self.avgT.insert(0, '4,1')
        self.avgT.bind('<Button-1>', self.clearEntry)
        self.avgT.grid(row=4, column=1, sticky='W')
        
        self.pointL = tk.Message(self.frame, text='Target pointing, '+\
                                 'duration, demix (use multiple lines for '+\
                                 'multiple sources):', width=250)
        self.pointL.grid(row=5, sticky='E')
        self.pointT = tk.Text(self.frame, height=3, width=50)
        self.pointT.insert(tk.END, '<label>,<ra (hms)>,<dec (dms)>,<hours>,<demix>')
        self.pointT.grid(row=5, column=1, sticky='W')
        
        tk.Label(self.frame).grid(row=6)
        
        self.submitB = tk.Button(self.frame, text='SUBMIT', justify=tk.CENTER,\
                                 command=self.generateText)
        self.submitB.grid(row=7, column=1, sticky='W')
        
        self.cancelB = tk.Button(self.frame, text='RESET', justify=tk.CENTER,\
                                 command=self.resetForms)
        self.cancelB.grid(row=7, column=1, padx=100, sticky='W')

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
        self.pointT.delete(1.0, tk.END)
        self.pointT.insert(tk.END, '<label>,<ra (hms)>,<dec (dms)>,<hours>,<demix>')

    def clearEntry(self, event):
        event.widget.delete(0, 'end')
    
    def parseAndValidateInput(self):
        """
        Parse input specified in all Entry and Text tkinter objects
        """
        self.projectName = self.projNameT.get()
        if self.projectName == '' or len(self.projectName) != 7:
            tkMessageBox.showerror('Error', 'Invalid project name')
            return None
        
        self.mainName = self.mainNameT.get()
        if len(self.mainName) > 20:
            tkMessageBox.showerror('Error', 'Main folder name cannot be '+\
                                   'longer than 2- characters')
            return None
        
        try:
            dy, dm, ds, th, tm, ts = self.dateT.get().split('-')
            self.startTime = datetime.datetime(int(dy), int(dm), int(ds), \
                                               int(th), int(tm), int(ts))
        except:
            tkMessageBox.showerror('Error', 'Invalid date/time specified.')
            return None
        
        
    
    def generateText(self):
        """
        This is the function that coordinates all the background processing.
        """
        # Parse user input 
        self.parseAndValidateInput()

if __name__ == '__main__':
    gui = GuiWindow()
    gui.root.mainloop()

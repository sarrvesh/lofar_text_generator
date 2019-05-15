#!/usr/bin/env python
import sys
from textgen._version import __version__

if __name__ == '__main__':
    print('LOFAR Imaging Text Generator')
    print('Version {}\n'.format(__version__))
    
    # Check for python 3
    if sys.version_info.major != 3:
       raise Exception("You need Python 3 to run the LOFAR Imaging Text Generator")
    
    from textgen.GUIWindow import *
    
    gui = GuiWindow()
    gui.root.mainloop()

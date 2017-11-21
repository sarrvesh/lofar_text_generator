#!/usr/bin/env python
from textgen.GUIWindow import *
from textgen.errors import *
from textgen.Imaging import *
from textgen._version import __version__

if __name__ == '__main__':
    print 'LOFAR Imaging Text Generator'
    print 'Version {}\n'.format(__version__)
    gui = GuiWindow()
    gui.root.mainloop()

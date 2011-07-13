#!/usr/bin/python

import os, sys
from PySide.QtCore import *
from PySide.QtGui import *

# directories to useful things
exeDir = os.path.abspath(os.path.dirname(sys.argv[0]))
resDir = os.path.abspath(exeDir+'/../Resources')

msgFile = open(resDir+'/hello.txt','r')
msg = msgFile.readline()
msgFile.close()

# Create a Qt application 
app = QApplication(sys.argv)
label = QLabel("<font color=red size=40>%s</font>" % msg)
label.show()
app.exec_()

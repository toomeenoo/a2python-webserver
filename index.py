#!/usr/bin/env python
import sys, os
from weblib import *
w = Weblib()

a = w.server("REQUEST_SCHEME")+"//"+w.server("SERVER_NAME")+w.server("REQUEST_URI")
w.write(a+"<br>")

w.write(str(w.query("get")))

w.write("<br><br>Dir<br>")
for name in dir():
    myvalue = eval(name)
    w.write( name+" => "+str(myvalue)+"<br>")

w.write("<br>Apache<br>")
for name, value in os.environ.items():
    w.write(name+" => "+value+"<br>")

w.write("<br>//end")
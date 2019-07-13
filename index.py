#!/usr/bin/env python3
import sys, os
from weblib import *
w = Weblib()
w.write("<!DOCTYPE html><head><title>Pythonwebserver</title></head><body>")
a = w.server("REQUEST_SCHEME")+"//"+w.server("SERVER_NAME")+w.server("REQUEST_URI")
w.write("URL: "+a+"<br>")

w.write("Get: "+str(w.get())+"<br>")
w.write("Post: "+str(w.post())+"<br>")
w.write("Cookie \"test\" should be set to: \"testcookie-value\", valid next 4hrs <br>")

w.write("<br><br><b>Dir</b> variables<br>")
for name in dir():
    myvalue = eval(name)
    w.write( name+" =&gt; "+str(myvalue).replace("&","&amp;").replace("<","&lt;").replace(">","&rt;")+"<br>")

w.write("<br><b>Apache</b> variables<br>")
for name, value in os.environ.items():
    w.write(name+" =&gt; "+value+"<br>")

w.setcookie("test", "testcookie-value", 60*60*4)
w.write("</body>")
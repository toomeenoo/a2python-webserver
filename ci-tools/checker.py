import sys, glob, os
for filename in glob.glob(filename = sys.argv[1]+"/*.py"):
    source = open(filename, 'r').read() + '\n'
    compile(source, filename, 'exec')
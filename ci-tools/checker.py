import sys, glob, os
for filename in glob.glob(sys.argv[1]+"/*.py"):
    source = open(filename, 'r').read() + '\n'
    compile(source, filename, 'exec')
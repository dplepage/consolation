# import atexit

from decorate import console

# atexit.register(console)

import sys

def tracer(frame, event, arg):
    # print event, frame.f_code.co_filename, frame.f_lineno, "->", arg
    if frame.f_code.co_filename == sys.argv[0]:
        console()
    # print frame.f_locals
    return tracer

# tracer is activated on the next call, return, or exception
sys.setprofile(tracer)

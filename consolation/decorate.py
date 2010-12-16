import sys
import os
from itertools import count
import __builtin__
from functools import wraps
import warnings
import plac
from progress_bar import progressinfo as pinf

#TODO hack this to use names of functions instead of functions themselves.

show_loops = False

class MultipleMainWarning(Warning):
    pass

def loop(x):
    if show_loops:
        return pinf(x)
    else:
        return x

def showprogress(fn):
    @wraps(fn)
    def tmp(*args, **kw):
        global show_loops
        x = show_loops
        show_loops = True
        fn(*args,**kw)
        show_loops = x
    return tmp
import time

subs = []
mains = []

def main(*args, **kwargs):
    def wrapper(fn):
        fn = plac.annotations(**kwargs)(fn)
        if fn.__module__ == '__main__':
            if mains:
                warnings.warn(MultipleMainWarning("Too many mains!"))
            mains.append(fn.__name__)
        return fn
    # for the @main case, instead of @main(args)
    if len(kwargs) == 0 and len(args) == 1:
        return wrapper(args[0])
    return wrapper

def subcommand(*args, **kwargs):
    def wrapper(fn):
        fn = plac.annotations(**kwargs)(fn)
        subs.append(fn.__name__)
        return fn
    # for the @subcommand case, instead of @subcommand(args)
    if len(kwargs) == 0 and len(args) == 1:
        return wrapper(args[0])
    return wrapper

def last_frame():
    frame = sys._getframe(0)
    for i in count(1):
        try:
            frame = sys._getframe(i)
        except ValueError:
            return frame

# TODO is it always the case that the last frame, as of importing this module,
# is always the file that was actually called? Probably there are toolkits 
# with their own magic frame manipulation that will break this. But 99% of 
# cases this should work.
_main_frame = last_frame() 

def getmainfunc(name):
    return _main_frame.f_globals[name]

def run_subcommands():
    if not subs: return
    class Foo(object):
        commands = [cmd for cmd in subs]
    
    for cmd in subs:
        setattr(Foo, cmd, staticmethod(getmainfunc(cmd)))
    plac.Interpreter.call(Foo)

def run_mains():
    if not mains: return
    for mname in mains:
        plac.call(getmainfunc(mname))

def console():
    if subs and mains:
        raise Exception("Cannot use @main and @subcommand in the same program!")
    if subs:
        run_subcommands()
    elif mains:
        run_mains()

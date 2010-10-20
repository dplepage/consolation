import sys
import __builtin__
from functools import wraps
import warnings
import plac
from progress_bar import progressinfo as pinf

show_loops = False

class MultipleMainWarning(Warning):
    pass

def main(fn):
    if fn.__module__ == '__main__':
        if hasattr(main,'_has_target'):
            warnings.warn(MultipleMainWarning("Too many mains!"))
        main._has_target=True
        def call(fn, *args, **kwargs):
            try:
                plac.call(fn,*args,**kwargs)
            except Exception,e:
                print "{0}: {1}: {2}".format(sys.argv[0], type(e).__name__, e)
        call(fn)

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
def subcommand(fn):
    subs.append(fn)
    return fn

def run_subcommands():
    class Foo(object):
        commands = [f.__name__ for f in subs]
    
    for cmd in subs:
        setattr(Foo, cmd.__name__, staticmethod(cmd))
    plac.Interpreter.call(Foo)

import sys
import __builtin__
from functools import wraps
import warnings
import plac
from progress_bar import progressinfo as pinf

show_loops = False

class MultipleMainWarning(Warning):
    pass

def main(*args, **kwargs):
    def wrapper(fn):
        fn = plac.annotations(**kwargs)(fn)
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
    # if it's used with no arguments but a function, call the function
    if len(kwargs) == 0 and len(args) == 1:
        return wrapper(args[0])
    return wrapper

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
def subcommand(*args, **kwargs):
    def wrapper(fn):
        fn = plac.annotations(**kwargs)(fn)
        subs.append(fn)
        return fn
    # for the @subcommand case, instead of @subcommand(args)
    if len(kwargs) == 0 and len(args) == 1:
        return wrapper(args[0])
    return wrapper


def run_subcommands():
    class Foo(object):
        commands = [f.__name__ for f in subs]
    
    for cmd in subs:
        setattr(Foo, cmd.__name__, staticmethod(cmd))
    plac.Interpreter.call(Foo)

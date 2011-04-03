import sys
import inspect

from app import Console

# =======================================================================
# = The following functions are not robust in the face of e.g. symlinks =
# =======================================================================
def inmain(frame):
    '''Check if frame is the global frame of the main file.'''
    return frame.f_code.co_filename == sys.argv[0]

def getmainname():
    '''Get the name of the main module'''
    return sys.argv[0]

# ===================
# = Namespace class =
# ===================
class AutoRunner(object):
    app = None

    @staticmethod
    def tracer(frame, event, _):
        '''A profiler that calls the autoapp when the main module exits'''
        if event == 'return' and frame.f_code.co_name == '<module>' and inmain(frame):
            sys.setprofile(None)
            AutoRunner.app.run()
    
    @staticmethod
    def setupDefaultApp():
        '''Initialize the app with sensible defaults, register the tracer'''
        if AutoRunner.app is not None: return
        AutoRunner.app = Console(getmainname())
        sys.setprofile(AutoRunner.tracer)

def main(*args, **kwargs):
    def wrap(fn):
        if inmain(inspect.currentframe(1)):
            AutoRunner.setupDefaultApp()
            return AutoRunner.app.main(*args, **kwargs)(fn)
        return fn
    return wrap

def subcommand(*args, **kwargs):
    def wrap(fn):
        if inmain(inspect.currentframe(1)):
            AutoRunner.setupDefaultApp()
            return AutoRunner.app.subcommand(*args, **kwargs)(fn)
        else:
            print "Skipping", fn.__name__
        return fn
    return wrap

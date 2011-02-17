import plac
import sys

from optargdec import dec_meth
from fmt_errors import format_errors

'''
Note - some sort of configuration scheme would be good.
'''

class Console(object):
    """A console application"""
    def __init__(self, name, autorun=False):
        super(Console, self).__init__()
        self.name = name
        class Subcommander(object):
            commands = []
        self.sc = Subcommander
        self.autorun = autorun
        self.main_fn = None
    
    @dec_meth
    def subcommand(self, fn, **annotations):
        fn = plac.annotations(**annotations)(fn)
        cmd = fn.__name__
        if cmd == 'commands':
            raise ValueError("'commands' cannot be the name of a subcommand.")
        setattr(self.sc, cmd, staticmethod(fn))
        self.sc.commands.append(cmd)
        return fn
    
    @dec_meth
    def main(self, fn, **annotations):
        self.main_fn = plac.annotations(**annotations)(fn)
        return self.main_fn
    
    def run(self, error_style="off", args = sys.argv[1:]):
        with format_errors(self.name, error_style):
            if self.main_fn:
                plac.call(self.main_fn, args)
            else:
                plac.Interpreter.call(self.sc, args)

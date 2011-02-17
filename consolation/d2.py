import plac

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
    
    def add_subcommand(self, fn, cmd=None):
        if cmd is None: cmd = fn.__name__
        setattr(self.sc, cmd, staticmethod(fn))
        self.sc.commands.append(cmd)
    
    def subcommand(self, cmd=None):
        return lambda f:self.add_subcommand(f, cmd)
    
    def set_main(self, fn):
        self.main_fn = fn
    
    def main(self):
        return lambda f:self.set_main(f)
    
    def run(self):
        if self.main_fn:
            plac.call(self.main_fn)
        else:
            plac.Interpreter.call(self.sc)

if __name__ == '__main__':
    app = Console(__name__, autorun=True)

    @app.subcommand('bar')
    def test(arg='foo'):
        print "test:",arg

    # @app.main()
    def test2(arg='bar'):
        print "test2:",arg
    
    import os
    app.add_subcommand(os.getenv)

    app.run()

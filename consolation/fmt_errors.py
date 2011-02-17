from contextlib import contextmanager

@contextmanager
def format_errors(name, style):
    try:
        yield
    except Exception,e:
        if style == 'off':
            raise
        elif style == 'oneline':
            print "{0}: {1}".format(name, e.message)            

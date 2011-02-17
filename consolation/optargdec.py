from functools import wraps

class Default:pass

def optargdec(fn):
    '''Convert a decorator into one that takes optional arguments.
    
    @optargdec
    def foo(f, *args, **kwargs):
        pass
    
    means that foo can be used as
    @foo
    def func(...)
    
    or
    @foo(arg1, arg2='blah', ...)
    def func(...)
    '''
    @wraps(fn)
    def newfn(fn_or_arg1=Default, *args, **kwargs):
        if fn_or_arg1 is Default:
            return lambda f: fn(f, *args, **kwargs)
        if (args or kwargs or not hasattr(fn_or_arg1, '__call__')):
            return lambda f: fn(f, fn_or_arg1, *args, **kwargs)
        return fn(fn_or_arg1)
    return newfn

def dec_meth(fn):
    '''Convert a method foo(self, fn, *args, **kwargs) to a decorator.
    
    The usage
    @x.foo(*args, **kwargs)
    def f(): ...
    
    will be identical to x.foo(f, *args, **kwargs)'''
    @wraps(fn)
    def newfn(self, *args, **kwargs):
        return lambda f: fn(self, f, *args, **kwargs)
    return newfn

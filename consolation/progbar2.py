# coding: utf-8

"""This code is adapted from the Modular toolkit for
Data Processing. Its license is:

This file is part of Modular toolkit for Data Processing (MDP).
All the code in this package is distributed under the following conditions:
 
Copyright (c) 2003-2010, Pietro Berkes <berkes@brandeis.edu>, 
                         Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl>,
                         Rike-Benjamin Schuppner <rike.schuppner@bccn-berlin.de>, 
                         Niko Wilbert <mail@nikowilbert.de>,   
                         Tiziano Zito  <tiziano.zito@bccn-berlin.de>
 
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the Modular toolkit for Data Processing (MDP) 
      nor the names of its contributors may be used to endorse or promote 
      products derived from this software without specific prior written 
      permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


from datetime import timedelta
from threading import Thread
import sys
import time
import os


def ioctl_GWINSZ(fd):                  #### TABULATION FUNCTIONS
     try:                                ### Discover terminal width
         import fcntl, termios, struct
         cr = struct.unpack('hh',
                            fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
     except:
         return None
     return cr

def get_termsize():
     ### decide on *some* terminal size
     # try open fds
     cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
     if not cr:
         # ...then ctty
         try:
             fd = os.open(os.ctermid(), os.O_RDONLY)
             cr = ioctl_GWINSZ(fd)
             os.close(fd)
         except:
             pass
     if not cr:
         env = os.environ
         # env vars or finally defaults
         try:
             cr = (env['LINES'], env['COLUMNS'])
         except:
             cr = (25, 80)
     return int(cr[0]), int(cr[1])

def fmt_time(t, delimiters):
    """Return time formatted as a timedelta object."""
    meta_t = timedelta(seconds=round(t))
    return ''.join([delimiters[0], str(meta_t), delimiters[1]])

def get_layout(style, custom):
    '''Build a layout dict for the given style'''
    if style == 'bar':
        layout = { 'indent': '',
                   'width' : get_termsize()[1],
                   'position' : 'middle',
                   'delimiters' : '[]',
                   'char1' : '=',
                   'char2' : '>',
                   'char3' : '.' }
        if custom is not None:
            dict.update(layout, custom)
        fixed_lengths = len(layout['indent']) + 4
        if layout['position'] in ['left', 'right']:
            fixed_lengths += 4
        layout['width'] = layout['width'] - fixed_lengths
    else:
        err_str = "Style `%s' not known." % style
        raise ValueError(err_str)
    return layout
    

class ProgressBar(object):
    """Configurable text-based progress display"""
    def __init__(self, style, layout):
        super(ProgressBar, self).__init__()
        self.style = style
        self.layout = get_layout(style, layout)
        self.last = None
    
    def render(self, done, total):
        percent = float(done)/float(total)
        style = self.style
        layout = self.layout
        # percentage string
        # percent_s = "%3d%%" % int(round(percent*100))
        percent_s = '%i/%i'%(done,total)
        if style == 'bar':
            # how many symbols for such percentage
            symbols = int(round(percent * layout['width']))
            # build percent done arrow
            done = ''.join([layout['char1']*(symbols), layout['char2']])
            # build remaining space
            todo = ''.join([layout['char3']*(layout['width']-symbols)])
            # build the progress bar
            box =  ''.join([layout['delimiters'][0],
                            done, todo,
                            layout['delimiters'][1]])
            if layout['position'] == 'left':
                # put percent left
                box = ''.join(['\r', layout['indent'], percent_s, box])
            elif layout['position'] == 'right':
                # put percent right
                box = ''.join(['\r', layout['indent'], box, percent_s])
            else:
                # put it in the center
                percent_s = percent_s.lstrip()
                percent_idx = (len(box) // 2) - len(percent_s) + 2
                box = ''.join(['\r', layout['indent'],
                               box[0:percent_idx],
                               percent_s,
                               box[percent_idx+len(percent_s):]])
        # print it only if something changed from last time
        if box != self.last:
            self.last = box
            sys.stdout.write(box)
            sys.stdout.flush()
        return
    
    def done(self, done, total):
        self.render(done, total)
        self.cleanup()
    
    def cleanup(self):
        self.last = None
        sys.stdout.write('\n\r')
        sys.stdout.flush()


def progressinfo(sequence, length = None, style = 'bar', layout = None):
    iterate_on_items = False
    # try to get the length of the sequence
    try:
        length = len(sequence)
    # if the object is unsized
    except TypeError:
        if length is None:
            err_str = "Must specify 'length' if sequence is unsized."
            raise Exception(err_str)
        elif length < 0:
            iterate_on_items = True
            length = -length
    length = float(length)
    # start main loop
    prog = ProgressBar(style, layout)
    total = 0.0
    for count, value in enumerate(sequence):
        # generate progress info
        if iterate_on_items:
            prog.render(value, length)
        else:
            prog.render(count, length)
        yield value
    else:
        # we need this for the 100% notice
        if iterate_on_items:
            prog.done(length, length)
        else:
            prog.done(count+1, length)

class Ticker(object):
    def __init__(self, length, style='bar', layout=None, render_on_start=False):
        self.bar = ProgressBar(style, layout)
        self.length = length
        self.done = False
        self.i = 0
        if render_on_start:
            self.bar.render(0, self.length)
    
    def tick(self, count=1):
        if self.done: return False
        self.i += count
        if self.i >= self.length:
            self.bar.done(self.length, self.length)
            self.done = True
            return False
        self.bar.render(self.i, self.length)
        return True
    
    def __call__(self, count = 1):
        return self.tick(count)

    def _runner(self, fn):
        def tmp(*args, **kwargs):
            self.result = fn(*args, **kwargs)
        return tmp

    def runGuarded(self, fn, *args, **kwargs):
        self.result = None
        t = Thread(target=self._runner(fn), args=args, kwargs=kwargs)
        try:
            t.start()
            while t.is_alive():
                time.sleep(.1)
        except KeyboardInterrupt:
            self.done = True
            t.join()
            sys.stdout.write('\n\r')
            sys.stdout.flush()
            raise
        return self.result

# execute this file for a demo of the progressinfo style
if __name__ == '__main__':
    import random
    import tempfile
    print 'Testing progressinfo...'
    # test various customized layouts
    cust_list = [ {'position' : 'left',
                   'indent': 'Progress: ',
                   'delimiters': '()',
                   'char3': ' '},
                  {},
                  {'position': 'right',
                   'width': 50} ]
    for cust in cust_list:
        test = 0
        for i in progressinfo(range(100, 600), style = 'bar', custom = cust):
            test += i
            time.sleep(0.001)
        if test != 174750:
            raise Exception('Something wrong with progressinfo...')
    # generate random character sequence
    inp_list = []
    for j in range(500):
       inp_list.append(chr(random.randrange(256)))
    string = ''.join(inp_list)
    # test various customized layouts
    cust_list = [ {'position': 'left',
                   'separator': ' | ',
                   'delimiters': '()'},
                  {'position':'right'}]
    for cust in cust_list:
        out_list = []
        for i in progressinfo(string, style = 'timer', custom = cust):
            time.sleep(0.02)
            out_list.append(i)
        if inp_list != out_list:
            raise Exception('Something wrong with progressinfo...' )

    # write random file
    fl = tempfile.TemporaryFile(mode='r+')
    for i in range(1000):
        fl.write(str(i)+'\n')
    fl.flush()
    # rewind
    fl.seek(0)
    lines = []
    for line in progressinfo(fl, 1000):
        lines.append(int(line))
        time.sleep(0.01)
    if lines != range(1000):
        raise Exception('Something wrong with progressinfo...' )

    # test iterate on items
    fl = tempfile.TemporaryFile(mode='r+')
    for i in range(10):
        fl.write(str(i)+'\n')
    fl.flush()
    # rewind
    fl.seek(0)
    def gen():
        for line_ in fl:
            yield int(line_)
    for line in progressinfo(gen(), -10, style='timer',
                             custom={'speed':'last'}):
        time.sleep(1)
    print 'Done.'

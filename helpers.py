# Helper functions for printing to console

import time

now = lambda : time.strftime('%H:%M:%S', time.localtime())
prn = lambda msg : print(f'{now()}: {msg}')

def print_exception (e, msg = '') :
    if hasattr(e, 'msg'): prn(f'Exception - {e.msg}\n\t{msg}')
    else: prn(e)

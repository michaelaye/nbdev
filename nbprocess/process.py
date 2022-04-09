# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_process.ipynb.

# %% auto 0
__all__ = ['extract_directives', 'opt_set', 'NBProcessor']

# %% ../nbs/02_process.ipynb 3
#|export
from .read import *
from .maker import *
from .imports import *

from fastcore.script import *
from fastcore.imports import *
from fastcore.xtras import *

from collections import defaultdict
from pprint import pformat
from inspect import signature,Parameter
import ast,contextlib,copy

# %% ../nbs/02_process.ipynb 7
#|export
def _directive(s):
    s = (s.strip()[2:]).strip().split()
    if not s: return None
    direc,*args = s
    return direc,args

# %% ../nbs/02_process.ipynb 8
#|export
def extract_directives(cell):
    "Take leading comment directives from lines of code in `ss`, remove `#|`, and split"
    ss = cell.source.splitlines(True)
    first_code = first(i for i,o in enumerate(ss) if not o.strip() or not re.match(r'\s*#\|', o))
    if not ss or first_code==0: return {}
    cell['source'] = ''.join(ss[first_code:])
    res = L(_directive(s) for s in ss[:first_code]).filter()
    return {k:v for k,v in res}

# %% ../nbs/02_process.ipynb 11
#|export
def opt_set(var, newval):
    "newval if newval else var"
    return newval if newval else var

# %% ../nbs/02_process.ipynb 12
#|export
class NBProcessor:
    "Process cells and nbdev comments in a notebook"
    def __init__(self, path=None, procs=None, preprocs=None, postprocs=None, nb=None, debug=False):
        self.nb = read_nb(path) if nb is None else nb
        self.procs,self.preprocs,self.postprocs = map(L, (procs,preprocs,postprocs))
        self.debug = debug

    def _process_cell(self, cell):
        self.cell = cell
        cell['directives_'] = extract_directives(cell)
        for proc in self.procs:
            if cell.cell_type=='code':
                for cmd,args in cell.directives_.items(): self._process_comment(proc, cmd, args)
            if callable(proc): cell = opt_set(cell, proc(cell))

    def _process_comment(self, proc, cmd, args):
        f = getattr(proc, f'_{cmd}_', None)
        if not f: return True
        if self.debug: print(cmd, args, f)
        return f(self, *args)
        
    def process(self):
        "Process all cells with `process_cell`"
        for proc in self.preprocs: self.nb = opt_set(self.nb, proc(self.nb))
        for i in range_of(self.nb.cells): self._process_cell(self.nb.cells[i])
        self.nb.cells = [c for c in self.nb.cells if c and getattr(c,'source',None) is not None]
        for proc in self.postprocs: self.nb = opt_set(self.nb, proc(self.nb))

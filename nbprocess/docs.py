# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/06_docs.ipynb.

# %% auto 0
__all__ = ['rm_blank_proc', 'strip_ansi_proc', 'html_escape', 'insert_warning', 'write_md']

# %% ../nbs/06_docs.ipynb 3
from .read import *
from .imports import *
from .export import *
from .sync import write_nb, nb2dict

from fastcore.script import *
from fastcore.imports import *
from fastcore.xtras import *

import uuid
import tempfile

# %% ../nbs/06_docs.ipynb 5
def rm_blank_proc(cell):
    "Remove empty cells"
    if(cell.source.strip()==''): cell.source = None

# %% ../nbs/06_docs.ipynb 6
_re_ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def strip_ansi_proc(cell):
    "Strip Ansi Characters"
    for o in cell.get('outputs', []):
        if o.get('name') == 'stdout': o['text'] = _re_ansi_escape.sub('', o.text)

# %% ../nbs/06_docs.ipynb 7
def html_escape(cell):
    "Place HTML in a codeblock and surround it with a <HTMLOutputBlock> component."
    for o in cell.get('outputs', []):
        html = nested_idx(o, 'data', 'text/html')
        if html:
            cell.metadata.html_output = True
            html = ''.join(html).strip()
            o['data']['text/html'] = f'```html\n{html}\n```'

# %% ../nbs/06_docs.ipynb 8
def _get_cell_id(id_length=36): return uuid.uuid4().hex[:id_length]

def _get_md_cell(content="<!--- WARNING: THIS FILE WAS AUTOGENERATED! DO NOT EDIT!-->"):
    return AttrDict({'cell_type': 'markdown', 'id': f'{_get_cell_id()}',
                     'metadata': {}, 'source': f'{content}'})

def insert_warning(nb):
    "Insert Autogenerated Warning Into Notebook after the first cell."
    nb.cells = nb.cells[:1] + [_get_md_cell()] + nb.cells[1:]

# %% ../nbs/06_docs.ipynb 10
def write_md(nb_path, procs=None, post_procs=None, tpl_file='ob.tpl'):
    nbp = NBProcessor(nb_path, procs)
    nb = nbp.nb
    nbp.process()
    for proc in L(post_procs): proc(nb)

    c = traitlets.config.Config()
    base = Path(__file__).parent.resolve()
    c.MarkdownExporter.template_file = str(base/'templates'/tpl_file)
    exp = MarkdownExporter(config=c)

    with tempfile.TemporaryFile('a+') as tmp:
        write_nb(nb, tmp)
        tmp.seek(0)
        md,_ = exp.from_file(tmp)

    dest = base/'../docusaurus/docs'/Path(nb_path).with_suffix('.md').name
    dest.write_text(md)
    return dest
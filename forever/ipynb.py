# coding: utf-8
"""> A set of tools for the notebook.  

## Import notebooks with


        %reload_ext forever.notebook
"""

from importlib.util import module_from_spec, spec_from_loader, LazyLoader
from importlib.machinery import SourceFileLoader, FileFinder
from IPython import display
from os import curdir
from os.path import exists, extsep, sep
from nbconvert import export, get_exporter
import nbformat, random, sys


class NotebookLoader(SourceFileLoader):
    def get_code(self, path):
        with open(self.path, 'r') as f:
            nb = nbformat.read(f, 4)
        return export(get_exporter('script'), nb)[0].encode('utf-8')


_NotebookLoader_ = LazyLoader.factory(NotebookLoader)


class NotebookFinder(object):
    def find_spec(self, name, paths, target=None):
        """Search paths for files matching `<name>.ipynb`.
        """
        for path in paths or [curdir]:
            notebook = extsep.join(
                [sep.join([path or curdir, name.split('.')[-1]]), 'ipynb'])
            if exists(notebook):
                spec = spec_from_loader(name, NotebookLoader(name, notebook))
                return spec
        return None


def notebook_module(name, path=None, target=None):
    path = name + '.ipynb' if not path else path
    return module_from_spec(NotebookFinder().find_spec(name, path, target))


finder = NotebookFinder()
hook = FileFinder.path_hook((NotebookLoader, ['.ipynb']))


def terminal(alias=None):
    return display.IFrame(
        "http://localhost:8888/terminals/{}".format(
            alias or random.randint(1000, 9999)),
        width=900,
        height=400)


def load_ipython_extension(ip=None):
    sys.meta_path.append(finder)
    sys.path_hooks.append(hook)
    sys.path_importer_cache.clear()


def unload_ipython_extension(ip=None):
    sys.path_hooks = list(filter(lambda x: x is not hook, sys.path_hooks))
    sys.meta_path = list(filter(lambda x: x is not finder, sys.meta_path))
    ip.log.warning(sys.modules.keys())
    sys.path_importer_cache.clear()
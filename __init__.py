bl_info = {
    "name": "Batch Assign",
    "description": (
        "Select properties with extended rna data path syntax "
        "then batch assign new value."
    ),
    "author": "fatboyzz",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": (
        "N Panel > Misc > Name Symmetrizer"
    ),
    "support": "COMMUNITY",
    "category": "Object"
}

import importlib
from . import utils
from . import model
from . import control
from . import view

modules = (
    model,
    control,
    view,
)

def register():
    importlib.reload(utils)
    for mod in modules:
        importlib.reload(mod)
        utils.register_module(mod)

def unregister():
    for mod in reversed(modules):
        utils.unregister_module(mod)

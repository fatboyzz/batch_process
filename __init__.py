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
        "N Panel > Misc > Batch Assign"
    ),
    "support": "COMMUNITY",
    "category": "Object"
}

import importlib

from . import utils
from . import expression_globals

from . import settings_model
from . import preset_model
from . import main_model

from . import preset_control
from . import main_control

from . import settings_view
from . import preset_view
from . import main_view


reload_modules = (
    utils,
    expression_globals,
)

register_modules = (
    settings_model,
    preset_model,
    main_model,

    preset_control,
    main_control,

    settings_view,
    preset_view,
    main_view,
)

def register():
    for mod in reload_modules:
        importlib.reload(mod)

    for mod in register_modules:
        importlib.reload(mod)
        utils.register_module(mod)

def unregister():
    for mod in reversed(register_modules):
        utils.unregister_module(mod)

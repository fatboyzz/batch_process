import bpy
from bpy.props import (
    BoolProperty,
)

from .utils import *

register_classes = []

@append(register_classes)
@model("batch_assign_settings_model")
class BatchAssign_SettingsModel(bpy.types.PropertyGroup):
    enable_debug_information : BoolProperty(
        name = "Enable Debug Information",
        default = False,
    )

    enable_erna_syntax_help : BoolProperty(
        name = "Enable Extended RNA Syntax Help",
        default = True,
    )

    enable_python_reserved_property : BoolProperty(
        name = "Enable Python Reserved Property",
        default = False,
    )

    enable_python_callable_property : BoolProperty(
        name = "Enable Python Callable Property",
        default = False,
    )

import bpy
from bpy.props import (
    BoolProperty,
)

from .utils import *

register_classes = []

@register_class
@model("batch_assign_settings_model")
class BatchAssign_SettingsModel(bpy.types.PropertyGroup):
    enable_debug_information : BoolProperty(
        name = "Enable Debug Information",
        default = False,
    )

    enable_update_when_erna_changed : BoolProperty(
        name = "Enable Update When ERNA Changed",
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

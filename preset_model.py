import bpy
from bpy.props import (
    StringProperty,
)

class BatchAssign_PresetModel(bpy.types.PropertyGroup):
    preset_file : StringProperty(
        name = "Preset File Name",
        default = "batch_assign_preset.txt"
    )


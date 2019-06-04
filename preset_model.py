import bpy

from bpy.props import (
    StringProperty,
)

from .utils import *

register_classes = []

class PresetError(Exception): pass

class PresetErrorFileNotExist(PresetError):
    def __init__(self, file):
        self.file = file
    def __str__(self):
        return "Preset File {0} Not Exist".format(self.file)

class PresetErrorEmpty(PresetError):
    def __str__(self): return "Preset Error Empty"

class PresetErrorLine(PresetError):
    def __init__(self, line): 
        self.line = line
    def __str__(self): 
        return "Preset Error At Line {0}".format(self.line)

class PresetErrorKeyAlreadyExist(PresetErrorLine):
    def __init__(self, key):
        self.key = key
    def __str__(self):
        return "Preset Key {0} Already Exist".format(self.key)


@register_class
@model("batch_assign_preset_model")
class BatchAssign_PresetModel(bpy.types.PropertyGroup):
    preset_file : StringProperty(
        name = "Preset File",
        default = "batch_assign_preset.txt",
    )

    preset_key : StringProperty(
        name = "Preset Key",
        default = "",
    )

    preset_error : StringProperty(
        name = "Preset Error",
        default = "",
    )

    unexpected_error : StringProperty(
        name = "Unexpected Error",
        default = "",
    )

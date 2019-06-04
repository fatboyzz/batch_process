import enum
import bpy
from bpy.props import (
    BoolProperty,
    IntProperty,
    StringProperty,
    EnumProperty,
    CollectionProperty,
)

from .utils import *
from .settings_model import *

class ERNAError(Exception): pass

class ERNAErrorEmpty(ERNAError): 
    def __str__(self): return "ERNA Empty"

class ERNAErrorIndex(ERNAError):
    def __init__(self, index, message):
        self.index = index
        self.message = message
    def __str__(self):
        return "Pos {0} : {1}".format(self.index, self.message)


class CollectionError(Exception): pass

class CollectionErrorEmpty(CollectionError):
    def __str__(self): return "Collection Empty"

class CollectionErrorPrevCollection(CollectionError):
    def __str__(self): return "Collection Error In Previous Collection"

class CollectionErrorOperation(CollectionError):
    def __str__(self): return "Collection Unknown Operation"

class CollectionErrorEval(CollectionError):
    def __init__(self, error): self.error = error
    def __str__(self): return str(self.error)

class CollectionErrorProperty(CollectionError):
    def __init__(self, prop):
        self.prop = prop
    def __str__(self): 
        return "Unknown Property {0}".format(self.prop)

class CollectionErrorFlatten(CollectionError):
    def __init__(self, prop):
        self.prop = prop
    def __str__(self):
        return "Property {0} is not iterable".format(self.prop)

class CollectionErrorAssignType(CollectionError):
    def __init__(self, expect, actual):
        self.expect = expect
        self.actual = actual
    def __str__(self):
        return "Assign Type {0} to Type {1}".format(
            self.expect.__name__, self.actual.__name__
        )


def main_model_update(self, context):
    settings = BatchAssign_SettingsModel.get()
    if settings.enable_update_when_erna_changed:
        bpy.ops.batch_assign.main_control_update()
    

@register_class
class BatchAssign_MainERNAModel(bpy.types.PropertyGroup):
    erna : StringProperty(
        name = "ERNA",
        description = "ERNA Data Path",
        default = "",
        update = main_model_update,
    )

    enable_collection_preview : BoolProperty(
        description = "Enable Collection Preview",
        default = True,
    )

    enable_accessable_property : BoolProperty(
        description = "Enable Accessable Property",
        default = False,
    )

    unexpected_error : StringProperty(
        description = "Unexpected Error",
        default = "",
    )

    erna_error : StringProperty(
        description = "ERNA Error",
        default = "",
    )

    erna_error_indicator : StringProperty(
        description = "ERNA Error Indicator",
        default = "",
    )

    collection_error : StringProperty(
        description = "Collection Error",
        default = "",
    )


@register_class
@model("batch_assign_main_model")
class BatchAssign_MainModel(bpy.types.PropertyGroup):
    erna_count : IntProperty(
        name = "ERNA Count",
        description = "ERNA Count",
        default = 2,
        min = 1,
        max = 16,
        update = main_model_update,
    )

    ernas : CollectionProperty(
        type = BatchAssign_MainERNAModel
    )

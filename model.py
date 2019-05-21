import enum
import bpy
from bpy.props import (
    BoolProperty,
    IntProperty,
    StringProperty,
    EnumProperty,
)

from .utils import *

register_classes = []

class ERNAError(Exception): pass
class ERNAErrorEmpty(ERNAError): 
    def __str__(self): return "ERNA Empty"
class ERNAErrorIndex(ERNAError):
    def __init__(self, index, message):
        self.index = index
        self.message = message
    def __str__(self):
        return "At {0} : {1}".format(self.index, self.message)

class CollectionError(Exception): pass
class CollectionErrorEmpty(CollectionError):
    def __str__(self): return "Collection Empty"
class CollectionErrorOperation(CollectionError):
    def __str__(self): return "Collection Unknown Operation"
class CollectionErrorProperty(CollectionError):
    def __init__(self, prop):
        self.prop = prop
    def __str__(self): 
        return "Unknown Property {0}".format(self.prop)

ErrorTable = [
    ("unexpected_error", Exception),
    ("erna_error", ERNAError),
    ("collection_error", CollectionError),
]


class ERNATokenType(enum.Enum):
    t_start = 1
    t_stop = 2


@append(register_classes)
class BatchAssign_Settings(bpy.types.PropertyGroup):
    enable_debug_infomation : BoolProperty(
        description = "Enable Debug Infomation",
        default = False,
    )

    enable_erna_syntax_help : BoolProperty(
        description = "Enable Extended RNA Syntax Help",
        default = True,
    )

@append(register_classes)
class BatchAssign_Errors(bpy.types.PropertyGroup):
    pass

@append(register_classes)
class BatchAssign_Properties(bpy.types.PropertyGroup):
    unexpected_error : StringProperty(
        description = "Unexpected Error",
        default = "",
    )

    erna_error : StringProperty(
        description = "ERNA Error",
        default = "",
    )

    erna_error_indicator : StringProperty(
        description = "ERNA Error Marker",
        default = "",
    )

    collection_error : StringProperty(
        description = "Collection Error",
        default = "",
    )

    assign_error : StringProperty(
        description = "Assign Error",
        default = "",
    )

    erna : StringProperty(
        description = "Extended RNA Data Path",
        default = "",
        update = lambda self, context:
            (bpy.ops.batch_assign.control_update(), None)[1]
    )

    assign_expression : StringProperty(
        description = "Python Expression Of Assign Value",
        default = "",
    )

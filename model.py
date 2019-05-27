import enum
import bpy
from bpy.props import (
    BoolProperty,
    IntProperty,
    StringProperty,
    EnumProperty,
)

from .utils import *

class SelectionError(Exception): pass
class SelectionErrorEmpty(SelectionError): 
    def __str__(self): return "Selection Empty"
class SelectionErrorChanged(SelectionError):
    def __str__(self): return "Selection Changed Click Update"

class ERNAError(Exception): pass
class ERNAErrorEmpty(ERNAError): 
    def __str__(self): return "ERNA Empty"
class ERNAErrorIndex(ERNAError):
    def __init__(self, index, message):
        self.index = index
        self.message = message
    def __str__(self):
        return "{0} : {1}".format(self.index, self.message)

class AssignExpError(Exception): pass
class AssignExpEmpty(AssignExpError): 
    def __str__(self): return "Assign Expression Empty"
class AssignExpErrorIndex(AssignExpError):
    def __init__(self, index, message):
        self.index = index
        self.message = message
    def __str__(self):
        return "{0} : {1}".format(self.index, self.message)
class AssignExpErrorInconsistantType(AssignExpError):
    def __init__(self, expect, actual):
        self.expect = expect
        self.actual = actual
    def __str__(self):
        return "Inconsistant Type Expect '{0}' Actual '{1}'".format(
            self.expect.__name__, self.actual.__name__
        )
class AssignExpErrorException(AssignExpError):
    def __init__(self, exception):
        self.exception = exception
    def __str__(self):
        return str(self.exception)

class CollectionError(Exception): pass
class CollectionErrorEmpty(CollectionError):
    def __str__(self): return "Collection Empty"
class CollectionErrorOperation(CollectionError):
    def __str__(self): return "Collection Unknown Operation"
class CollectionErrorNoPropertyAccessAtLast(CollectionError):
    def __str__(self): return "No Property Access At Last"
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
class CollectionErrorException(CollectionError):
    def __init__(self, exception):
        self.exception = exception
    def __str__(self):
        return str(self.exception)    
class CollectionErrorAssign(CollectionError): pass

register_classes = []

@append(register_classes)
class BatchAssign_Settings(bpy.types.PropertyGroup):
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

@append(register_classes)
class BatchAssign_Errors(bpy.types.PropertyGroup):
    unexpected_error : StringProperty(
        description = "Unexpected Error",
        default = "",
    )

    selection_error : StringProperty(
        description = "Selection Error",
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

    assign_exp_error : StringProperty(
        description = "Assign Expression Error",
        default = "",
    )

    assign_exp_error_indicator : StringProperty(
        description = "Assign Expression Error Indicator",
        default = "",
    )

    collection_error : StringProperty(
        description = "Collection Error",
        default = "",
    )

def control_update(self, context):
    bpy.ops.batch_assign.control_update()

@append(register_classes)
class BatchAssign_Properties(bpy.types.PropertyGroup):
    erna : StringProperty(
        description = "Extended RNA Data Path",
        default = "",
        update = control_update,
    )

    assign_exp : StringProperty(
        description = "Python Expression Of Assign Value",
        default = "",
        update = control_update,
    )

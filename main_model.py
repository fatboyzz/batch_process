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


class EXPRError(Exception): pass

class EXPREmpty(EXPRError): 
    def __str__(self): return "Assign Expression Empty"

class EXPRErrorIndex(EXPRError):
    def __init__(self, index, message):
        self.index = index
        self.message = message
    def __str__(self):
        return "{0} : {1}".format(self.index, self.message)

class EXPRErrorInconsistantType(EXPRError):
    def __init__(self, expect, actual):
        self.expect = expect
        self.actual = actual
    def __str__(self):
        return "Inconsistant Type Expect '{0}' Actual '{1}'".format(
            self.expect.__name__, self.actual.__name__
        )

class EXPRErrorException(EXPRError):
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
@model("batch_assign_main_errors")
class BatchAssign_MainErrors(bpy.types.PropertyGroup):
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

    expr_error : StringProperty(
        description = "Assign Expression Error",
        default = "",
    )

    expr_error_indicator : StringProperty(
        description = "Assign Expression Error Indicator",
        default = "",
    )

    collection_error : StringProperty(
        description = "Collection Error",
        default = "",
    )


def main_control_update(self, context):
    bpy.ops.batch_assign.main_control_update()


@append(register_classes)
@model("batch_assign_main_model")
class BatchAssign_MainModel(bpy.types.PropertyGroup):
    erna : StringProperty(
        name = "ERNA",
        description = "Extended RNA Data Path",
        default = "",
        update = main_control_update,
    )

    expr : StringProperty(
        name = "EXPR",
        description = "Python Assign Value Expression",
        default = "",
        update = main_control_update,
    )

import re
import bpy
from collections import ChainMap

from .utils import *
from .model import *
from .expression_globals import *

register_classes = []

class Selection:
    def __init__(self):
        self.datas = bpy.context.selected_objects
        self.check_selection_empty()
        self.check_selection_changed()

    def check_selection_empty(self):
        if len(self.datas) == 0:
            raise SelectionErrorEmpty()

    def check_selection_changed(self):
        if self.datas != bpy.context.selected_objects:
            raise SelectionErrorChanged()

class ERNA:
    def __init__(self, s : str):
        self.s = s
    
    t_count = counter(1)

    t_start = t_count()
    t_stop = t_count()
    t_symbol = t_count()
    t_name = t_count()
    t_number = t_count()
    t_expr = t_count()
    
    re_table = [
        (t_symbol, re.compile(r"""[\.\*@|\[:\]\%]""")),
        (t_name, re.compile(r"""[A-Za-z_][A-Za-z_0-9]*""")),
        (t_number, re.compile(r"""[0-9-]+""")),
        (t_expr, re.compile(r"""\$[^\$]*\$""")),
    ]

    def tokens(self):
        """
            Return generator of (t_type, t_index, t_string)
            t_type : t_start | t_stop | t_symbol | t_name | t_value
            t_index : start index of token 
            t_string : string of token
        """
        self.s_index = 0
        yield self.t_start, self.s_index, ""

        while True:
            if self.s_index >= len(self.s):
                yield self.t_stop, self.s_index, ""
                return

            if self.s[self.s_index].isspace():
                yield self.t_stop, self.s_index, ""
                return
                
            for t, regex in self.re_table:
                match = regex.match(self.s, self.s_index)
                if match:
                    t_index = self.s_index
                    self.s_index = match.end(0)
                    yield t, t_index, match.group(0)
                    break
            else:
                raise ERNAErrorIndex(self.s_index, "Unexpected Token")

    erna_count = counter(1)
    
    erna = erna_count()
    op = erna_count()
    op_prop = erna_count()
    op_flatten = erna_count()
    op_sort = erna_count()
    op_filter = erna_count()
    op_take = erna_count()
    op_var = erna_count()

    def next(self):
        self.t_type, self.t_index, self.t_string = self.t_sequence.__next__()
    
    def is_token(self, t_type):
        return self.t_type == t_type

    def match_token(self, t_type):
        if self.is_token(t_type):
            string = self.t_string
            self.next()
            return string
        else:
            raise ERNAErrorIndex(self.t_index, "Unexpected Token")

    def is_symbol(self, symbol):
        return self.t_type == self.t_symbol and \
            self.t_string == symbol
        
    def match_symbol(self, symbol):
        if self.is_symbol(symbol):
            string = self.t_string
            self.next()
            return string
        else:
            raise ERNAErrorIndex(
                self.t_index, "Expect Symbol {0}".format(symbol))

    def parse(self):
        """
            erna -> op* t_stop
            op -> op_prop | op_flatten | op_sort | op_filter | op_take | op_var
            op_prop -> ["."] t_name ("." op_prop)*
            op_flatten -> "*"
            op_sort -> "@" t_expr
            op_filter -> "|" t_expr
            op_take -> "[" t_number [ ":" t_number [ ":" t_number ]] "]"
            op_var -> "%" t_name
        """
        self.t_sequence = self.tokens()
        self.next()
        self.match_token(self.t_start)
        return self.parse_erna()
        
    def parse_erna(self):
        ret = []
        while not self.is_token(self.t_stop):
            ret.append(self.parse_op())

        if len(ret) == 0:
            raise ERNAErrorEmpty()

        return ret
    
    def parse_op(self):
        if self.is_token(self.t_name):
            return self.parse_op_prop()

        elif self.is_symbol("."):
            return self.parse_op_prop()

        elif self.is_symbol("*"):
            return self.parse_op_flatten()

        elif self.is_symbol("@"):
            return self.parse_op_sort()

        elif self.is_symbol("|"):
            return self.parse_op_filter()

        elif self.is_symbol("["):
            return self.parse_op_take()

        elif self.is_symbol("%"):
            return self.parse_op_var()
        
        else:
            raise ERNAErrorIndex(self.t_index, "Unexpected Operator")

    def parse_op_prop(self):
        """Return (op_prop, props)"""
        if self.is_symbol("."):
            self.next()
        
        props = []
        prop = self.match_token(self.t_name)
        props.append(prop)

        while self.is_symbol("."):
            self.next()
            prop = self.match_token(self.t_name)
            props.append(prop)

        if len(props) == 0:
            raise ERNAErrorIndex(self.t_index, "Expect Map Operator")

        return self.op_prop, props

    def parse_op_flatten(self):
        """Return (op_flatten, None)"""
        self.match_symbol("*")
        return self.op_flatten, None

    def parse_op_sort(self):
        """Return (op_sort, expr)"""
        self.match_symbol("@")
        expr = self.match_token(self.t_expr)
        return self.op_sort, expr[1:-1]

    def parse_op_filter(self):
        """Return (op_filter_xx, expr)"""
        self.match_symbol("|")
        expr = self.match_token(self.t_expr)
        return self.op_filter, expr[1:-1]

    def parse_op_take(self):
        """Return (op_take, (start, stop, step))"""
        self.match_symbol("[")

        start, stop, step = None, None, None

        start = int(self.match_token(self.t_number))

        if self.is_symbol(":"):
            self.next()
            stop = int(self.match_token(self.t_number))

            if self.is_symbol(":"):
                self.next()
                step = int(self.match_token(self.t_number))

        self.match_symbol("]")

        return self.op_take, (start, stop, step)

    def parse_op_var(self):
        """Return (op_var, name)"""
        self.match_symbol("%")
        name = self.match_token(self.t_name)
        return self.op_var, name

class Context:
    def __init__(self, data, ls = {}):
        self.data = data
        self.ls = ls

    def access_property(self, prop):
        data = getattr(self.data, prop, None)
        if data == None:
            raise CollectionErrorProperty(prop)
        return Context(data, self.ls)

    def access_properties(self, props):
        data = self.data
        for prop in props:
            data = getattr(self.data, prop, None)
            if data == None:
                raise CollectionErrorProperty(prop)
        return Context(data, self.ls)
    
    def accessable_properties(self) -> [str]:
        return sorted(dir(self.data))

    def extend_ls(self, ls_more):
        return Context(self.data, ChainMap(ls_more, self.ls))

    def eval(self, expr):
        data = eval(expr, Expression_Globals, self.ls)
        return Context(data, self.ls)

class Collection:
    def __init__(self, selection):
        self.contexts = [Context(data) for data in selection.datas]
        self.property = ""
        self.property_type = type(None)
        self.data_type = type(None)
        self.datas_assign = []

        if len(self.contexts) == 0:
            raise CollectionErrorEmpty()

    def accessable_properties(self):
        context = self.contexts[0]
        if len(self.property) > 0:
            context = context.access_property(self.property)
        return context.accessable_properties()
    
    def transform(self, erna):
        for op, value in erna[:-1]:

            if op == ERNA.op_prop:
                self.transform_op_prop(value)

            elif op == ERNA.op_flatten:
                self.transform_op_flatten()

            elif op == ERNA.op_sort:
                self.transform_op_sort(value)

            elif op == ERNA.op_filter:
                self.transform_op_filter(value)

            elif op == ERNA.op_take:
                self.transform_op_take(value)

            elif op == ERNA.op_var:
                self.transform_op_var(value)

            else:
                raise CollectionErrorOperation()

        op, value = erna[-1]
        if op != ERNA.op_prop:
            raise CollectionErrorNoPropertyAccessAtLast()
        else:
            self.transform_op_prop_last(value)

    def transform_op_prop(self, props):
        self.contexts = [
            context.access_properties(props) 
            for context in self.contexts
        ]

    def transform_op_prop_last(self, props):
        self.transform_op_prop(props[0:-1])

        context = self.contexts[0]
        self.data_type = type(context.data)
        self.property = props[-1]
        self.property_type = type(context.access_property(props[-1]).data)

    def transform_op_flatten(self):
        contexts_new = []
        for context in self.contexts:
            items, ls = context.data, context.ls

            if not hasattr(items, "__iter__"):
                raise CollectionErrorFlatten()

            for item in items:
                contexts_new.append(Context(item, ls))

        self.contexts = contexts_new
    
    def transform_op_sort(self, expr):
        length = len(self.contexts)

        def sort_key(context):
            ls_new = {"data" : context.data, "length" : length}
            return context.extend_ls(ls_new).eval(expr).data

        try:
            self.contexts.sort(key=sort_key)
        except Exception as error:
            raise CollectionErrorException(error) 
            
    def transform_op_filter(self, expr):
        contexts_new = []
        length = len(self.contexts)

        try:
            for index, context in enumerate(self.contexts):
                ls_new = {
                    "data" : context.data, 
                    "index" : index, 
                    "length" : length,
                }
                if context.extend_ls(ls_new).eval(expr).data:
                    contexts_new.append(context)

            if len(contexts_new) == 0:
                raise CollectionErrorEmpty()

            self.contexts = contexts_new
        except Exception as error:
            raise CollectionErrorException(error) 
            
    def transform_op_take(self, numbers):
        start, stop, step = numbers
        try:
            self.contexts = self.contexts[start:stop:step]
        except Exception as error:
            raise CollectionErrorException(error) 

    def transform_op_var(self, name):
        self.contexts = [
            context.extend_ls({name : context.data})
            for context in self.contexts
        ]

    def eval_assign_expr(self, expr):
        self.datas_assign = []
        length = len(self.contexts)

        try:
            for index, context in enumerate(self.contexts):
                if len(self.property) > 0:
                    context = context.access_property(self.property)
                
                ls_new = { 
                    "data" : context.data, 
                    "index" : index,
                    "length" : length, 
                }

                data_assign = context.extend_ls(ls_new).eval(expr).data

                expect, actual = self.property_type, type(data_assign)
                if expect != actual:
                    raise AssignExpErrorInconsistantType(expect, actual)
                
                self.datas_assign.append(data_assign)

        except SyntaxError as error:
            raise AssignExpErrorIndex(error.offset, error.msg)

        except Exception as error:
            raise AssignExpErrorException(error)

    def batch_assign(self):
        try:
            for context, data_assign in zip(self.contexts, self.datas_assign):
                setattr(context.data, self.property, data_assign)

        except Exception as error:
            raise CollectionErrorAssign(error) 

@append(register_classes)
class BatchAssign_Control:

    @classmethod
    def register_module(cls):
        from bpy.props import PointerProperty
        S, P = bpy.types.Scene, PointerProperty
        S.batch_assign_settings = P(type=BatchAssign_Settings)
        S.batch_assign_errors = P(type=BatchAssign_Errors)
        S.batch_assign_properties = P(type=BatchAssign_Properties)

    @classmethod
    def unregister_module(cls):
        S = bpy.types.Scene
        del S.batch_assign_properties
        del S.batch_assign_errors
        del S.batch_assign_settings

    @classmethod
    def settings(cls):
        return bpy.context.scene.batch_assign_settings

    @classmethod
    def errors(cls):
        return bpy.context.scene.batch_assign_errors

    @classmethod
    def properties(cls):
        return bpy.context.scene.batch_assign_properties

    def __init__(self):
        self.selection = None
        self.extended_rna = None
        self.collection = None
        self.traceback = None

    def clear_errors(self):
        errors = self.errors()
        errors.unexpected_error = ""
        errors.selection_error = ""
        errors.erna_error = ""
        errors.erna_error_indicator = ""
        errors.assign_expr_error = ""
        errors.assign_expr_error_indicator = ""
        errors.collection_error = ""

    def update(self):
        self.clear_errors()
        try:
            self.selection = Selection()

            erna_node = ERNA(self.properties().erna).parse()

            self.collection = Collection(self.selection)
            self.collection.transform(erna_node)

            assign_expr = self.properties().assign_expr
            self.collection.eval_assign_expr(assign_expr)

        except Exception as error:
            props = self.properties()
            errors = self.errors()

            if self.settings().enable_debug_information:
                print_traceback_and_set_clipboard()

            if isinstance(error, SelectionError):
                errors.selection_error = str(error)

            if isinstance(error, AssignExpError):
                if isinstance(error, AssignExpErrorIndex):
                    indicator = props.assign_expr[0:error.index] + "^"
                    errors.assign_expr_error_indicator = indicator
                errors.assign_expr_error = str(error)

            elif isinstance(error, CollectionError):
                errors.collection_error = str(error)

            elif isinstance(error, ERNAError):
                if isinstance(error, ERNAErrorIndex):
                    indicator = props.erna[0:error.index] + "^"
                    errors.erna_error_indicator = indicator
                errors.erna_error = str(error)

            else:
                errors.unexpected_error = str(error)

    def accessable_properties(self):
        props = self.collection.accessable_properties()
        if self.settings().enable_python_reserved_property:
            return props
        else:
            return [prop for prop in props if not prop.startswith("_")]

    def batch_assign(self):
        self.collection.batch_assign()
    
Control = BatchAssign_Control()

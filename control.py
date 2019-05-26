import re
import bpy
from collections import ChainMap

from .utils import *
from .model import *
from .expression_globals import *

register_classes = []

class Selection():
    def __init__(self):
        self.datas = bpy.context.selected_objects

    def check_selection_empty(self):
        return len(self.datas) == 0

    def check_selection_changed(self):
        return self.datas != bpy.context.selected_objects

    def check_selection_inconsistant_type(self):
        data_type = self.datas[0].type
        for data in self.datas[1:]:
            if data.type != data_type: 
                return True
        return False

class ERNA():
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
        (t_expr, re.compile(r"""$[^$]*$""")),
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
        return self.op_sort, expr

    def parse_op_filter(self):
        """Return (op_filter_xx, expr)"""
        self.match_symbol("|")
        expr = self.match_token(self.t_expr)
        return self.op_filter, expr

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

class Collection():
    def __init__(self, selection):
        self.contexts = [(data, {}) for data in selection.datas]
        self.property = ""
        self.property_type = type(None)
        self.data_type = type(None)
        self.datas_assign = []

        if len(self.contexts) == 0:
            raise CollectionErrorEmpty()

    def access_property(self, context, props):
        data, ls = context
        for prop in props:
            data = getattr(data, prop, None)
            if data == None:
                raise CollectionErrorProperty(prop)
        return data, ls

    def accessable_property(self):
        context = self.contexts[0]
        if len(self.property) > 0:
            context = self.access_property(context, [self.property])
        return sorted(dir(context[0]))
    
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
        contexts_new = []
        for context in self.contexts:
            context_new = self.access_property(context, props)
            contexts_new.append(context_new)
        self.contexts = contexts_new

    def transform_op_prop_last(self, props):
        self.transform_op_prop(props[0:-1])

        context = self.contexts[0]
        data, _ = context
        self.data_type = type(data)

        self.property = props[-1]
        prop_data, _ = self.access_property(context, props[-1:])
        self.property_type = type(prop_data)

    def transform_op_flatten(self):
        contexts_new = []
        for context in self.contexts:
            items, ls = context
            if not hasattr(items, "__iter__"):
                raise CollectionErrorFlatten()
            for item in items:
                contexts_new.append((item, ls))
        self.contexts = contexts_new
    
    def transform_op_sort(self, expr):
        gs = Expression_Globals
        length = len(self.contexts)

        def sort_key(context):
            data, ls = context
            ls_new = {"data" : data, "length" : length}
            eval(expr, gs, ChainMap(ls_new, ls))

        try:
            self.contexts.sort(sort_key)
        except Exception as e:
            raise CollectionErrorException(e)        
            
    def transform_op_filter(self, expr):
        gs = Expression_Globals
        contexts_new = []
        length = len(self.contexts)
        try:
            for index, context in enumerate(self.contexts):
                data, ls = context
                ls_new = {"data" : data, "index" : index, "length" : length}
                if eval(expr, gs, ChainMap(ls_new, ls)):
                    contexts_new.append(context)
        except Exception as e:
            raise CollectionErrorException(e)
            
    def transform_op_take(self, numbers):
        start, stop, step = numbers
        try:
            self.contexts = self.contexts[start:stop:step]
        except Exception as e:
            raise CollectionErrorException(e)

    def transform_op_var(self, name):
        context_new = []
        for data, ls in self.contexts:
            context_new.append(data, ChainMap({name : data}, ls))
        self.contexts = context_new

    def eval_assign_exp(self, exp):
        self.datas_assign = []

        gs = Expression_Globals

        try:
            length = len(self.contexts)

            for index, context in enumerate(self.contexts):
                data, ls = context
                ls_new = { "length" : length , "data" : data, "index" : index }

                data_assign = eval(exp, gs, ChainMap(ls_new, ls))

                expect_type, actual_type = self.property_type, type(data_assign)
                if expect_type != actual_type:
                    raise(AssignExpErrorInconsistantType(expect_type, actual_type))
                
                self.datas_assign.append(data_assign)

        except SyntaxError as e:
            raise AssignExpErrorIndex(e.offset, e.msg)

        except Exception as e:
            raise AssignExpErrorException(e)

    def batch_assign(self):
        try:
            for context, data_assign in zip(self.contexts, self.datas_assign):
                data, _ = context
                setattr(data, self.property, data_assign)

        except Exception as e:
            raise CollectionErrorAssign(e)

@append(register_classes)
class BatchAssign_Control():

    @classmethod
    def register_module(cls):
        from bpy.props import PointerProperty
        S = bpy.types.Scene
        S.batch_assign_settings = PointerProperty(type=BatchAssign_Settings)
        S.batch_assign_properties = PointerProperty(type=BatchAssign_Properties)

    @classmethod
    def unregister_module(cls):
        S = bpy.types.Scene
        del S.batch_assign_properties
        del S.batch_assign_settings

    @classmethod
    def settings(cls):
        return bpy.context.scene.batch_assign_settings

    @classmethod
    def properties(cls):
        return bpy.context.scene.batch_assign_properties

    def __init__(self):
        self.selection = None
        self.extended_rna = None
        self.collection = None
        self.traceback = None

    def check_selection(self):
        if self.selection == None:
            return "Click Update To Start"
        elif self.selection.check_selection_empty():
            return "Selection Empty"
        elif self.selection.check_selection_changed():
            return "Selection Changed Click Update"
        elif self.selection.check_selection_inconsistant_type():
            return "Selection Inconsistant Type"
        return ""
    
    def update(self):
        props = self.properties()

        props.unexpected_error = ""
        props.erna_error = ""
        props.erna_error_indicator = ""
        props.assign_exp_error = ""
        props.assign_exp_error_indicator = ""
        props.collection_error = ""

        try:
            self.update_internal()

        except Exception as error:
            print_traceback_and_set_clipboard()

            if isinstance(error, AssignExpError):
                if isinstance(error, AssignExpErrorIndex):
                    props.assign_exp_error_indicator = props.assign_exp[0:error.index] + "^"
                props.assign_exp_error = str(error)

            elif isinstance(error, CollectionError):
                props.collection_error = str(error)

            elif isinstance(error, ERNAError):
                if isinstance(error, ERNAErrorIndex):
                    props.erna_error_indicator = props.erna[0:error.index] + "^"
                props.erna_error = str(error)

            else:
                props.unexpected_error = str(error)
    
    def update_internal(self):
        self.selection = Selection()

        erna_node = ERNA(self.properties().erna).parse()

        self.collection = Collection(self.selection)
        self.collection.transform(erna_node)

        assign_exp = self.properties().assign_exp
        self.collection.eval_assign_exp(assign_exp)
        
    def batch_assign(self):
        self.collection.batch_assign()
    
Control = BatchAssign_Control()

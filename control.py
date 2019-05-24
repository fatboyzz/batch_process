import re
import bpy

from .utils import *
from .model import *

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
    t_value = t_count()

    re_table = [
        (t_symbol, re.compile(r"""[#\[\]\.\*@\|=<>:\$]""")),
        (t_name, re.compile(r"""[A-Za-z_][A-Za-z_0-9]*""")),
        (t_value, re.compile(r"""[0-9\-("][0-9\-.,()" ]*""")),
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
            if self.s_index >= len(self.s) or self.s[self.s_index].isspace():
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
    op_map = erna_count()
    op_flatten = erna_count()
    op_sort = erna_count()
    op_filter_eq = erna_count()
    op_filter_less = erna_count()
    op_filter_greater = erna_count()
    op_take = erna_count()

    def next(self):
        self.t_type, self.t_index, self.t_string = self.t_sequence.__next__()
    
    def is_token(self, t_type):
        return self.t_type == t_type

    def match_token(self, t_type):
        if self.is_token(t_type):
            ret = self.t_type, self.t_string
            self.next()
            return ret
        else:
            raise ERNAErrorIndex(self.t_index, "Unexpected Token Type")

    def is_symbol(self, symbol):
        return self.t_type == self.t_symbol and \
            self.t_string == symbol
        
    def match_symbol(self, symbol):
        if self.is_symbol(symbol):
            ret = self.t_type, self.t_string
            self.next()
            return ret
        else:
            raise ERNAErrorIndex(
                self.t_index, "Expect Symbol {0}".format(symbol))

    def parse(self):
        """
            erna : op*op_map
            op_map : .+t_name(.t_name)*
            op_flatten : [*] | *

            op_bracket : [(one of following op)]
            op_sort : @op_map | @
            op_filter_eq : |op_map=t_value
            op_filter_less : |op_map<t_value
            op_filter_greater : |op_map>t_value
            op_take : t_value:t_value:t_value
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

        op, _ = ret[-1]
        if op != self.op_map:
            raise ERNAErrorIndex(self.t_index, "Expect A Map Operator Ending")

        return ret
    
    def parse_op(self):
        if self.is_token(self.t_name) or self.is_symbol("."):
            return self.parse_op_map()

        elif self.is_symbol("*"):
            return self.parse_op_flatten()

        elif self.is_symbol("["):
            return self.parse_op_bracket()
        
        else:
            raise ERNAErrorIndex(self.t_index, "Unexpected Operator")

    def parse_op_map(self):
        """Return (op_map, props)"""
        if self.is_symbol("."):
            self.next()
        
        props = []
        _, prop = self.match_token(self.t_name)
        props.append(prop)

        while self.is_symbol("."):
            self.next()
            _, prop = self.match_token(self.t_name)
            props.append(prop)

        if len(props) == 0:
            raise ERNAErrorIndex(self.t_index, "Expect Map Operator")

        return self.op_map, props

    def parse_op_flatten(self):
        """Return (op_flatten, None)"""
        self.match_symbol("*")
        return self.op_flatten, None

    def parse_op_bracket(self):
        self.match_symbol("[")

        ret = None
        if self.is_symbol("*"):
            ret = self.parse_op_flatten()

        elif self.is_symbol("@"):
            ret = self.parse_op_sort()

        elif self.is_symbol("|"):
            ret = self.parse_op_filter()

        else:
            ret = self.parse_op_take()

        self.match_symbol("]")
        return ret

    def parse_op_sort(self):
        """Return (op_sort, prop)"""
        self.match_symbol("@")
        _, prop = self.parse_op_map()
        return self.op_sort, prop

    def parse_op_filter(self):
        """Return (op_filter_xx, (prop, value))"""
        self.match_symbol("|")
        _, prop = self.parse_op_map()

        op = None
        if self.is_symbol("="):
            self.next()
            op = self.op_filter_eq

        elif self.is_symbol("<"):
            self.next()
            op = self.op_filter_less

        elif self.is_symbol(">"):
            self.next()
            op = self.op_filter_greater

        else:
            raise ERNAErrorIndex(self.t_index, "Unexpected Filter Operator")

        _, t_string = self.match_token(self.t_value)
        value = eval(t_string)
        return op, (prop, value)

    def parse_op_take(self):
        """Return (op_take, (start, stop, step))"""
        _, value = self.match_token(self.t_value)
        start = exec(value)

        self.match_symbol(":")

        _, value = self.match_token(self.t_value)
        stop = exec(value)

        self.match_symbol(":")

        _, value = self.match_token(self.t_value)
        step = exec(value)

        return self.op_take, (start, stop, step)

class Collection():
    def __init__(self, selection):
        self.datas = selection.datas
        self.property = ""
        self.property_type = "NoneType"
        self.datas_assign = []

    def access_property(self, prop):
        datas_new = []
        for data in self.datas:
            data_new = getattr(data, prop, None)
            if data_new == None: 
                raise CollectionErrorProperty(prop)
            datas_new.append(data_new)

        self.datas = datas_new

    def accessable_property(self):
        data = self.datas[0]
        if len(self.property) > 0:
            data = getattr(data, self.property, None)
        return sorted(dir(data))

    def transform(self, erna):
        for op, value in erna[:-1]:
            if op == ERNA.op_map:
                self.transform_op_map(value)
            elif op == ERNA.op_flatten:
                self.transform_op_flatten()
            else:
                raise CollectionErrorOperation()
        
        _, props = erna[-1]
        self.transform_op_map(props[:-1])
        self.property = props[-1]

        data = getattr(self.datas[0], self.property, None)
        if data == None:
            raise CollectionErrorProperty(props[-1])
        else:
            self.property_type = type(data)

    def transform_op_map(self, props):
        for prop in props:
            self.access_property(prop)
        
    def transform_op_flatten(self):
        datas_new = []
        for datas in self.datas:
            for data in datas:
                datas_new.append(data)
                
        self.datas = datas_new
        self.property = ""

    def eval_assign_exp(self, exp):
        self.datas_assign = []

        import assign_exp_globals.AssignExpGlobals as gs

        try:
            length = len(self.datas)

            for index, data in enumerate(self.datas):
                ls = { "length" : length , "data" : data, "index" : index }

                data_assign = eval(exp, gs, ls)
                
                prop = getattr(data, self.property)
                expect, actual = type(prop), type(data_assign)
                if expect != actual:
                    raise(AssignExpErrorInconsistantType(expect, actual))
                
                self.datas_assign.append(data_assign)

        except SyntaxError as e:
            raise AssignExpErrorIndex(e.offset, e.msg)

        except Exception as e:
            raise AssignExpErrorException(e)

    def batch_assign(self):
        try:
            for data, data_assign in zip(self.datas, self.datas_assign):
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

        except AssignExpError as error:
            if isinstance(error, AssignExpErrorIndex):
                props.assign_exp_error_indicator = props.assign_exp[0:error.index] + "^"
            props.assign_exp_error = str(error)

        except CollectionError as error:
            props.collection_error = str(error)

        except ERNAError as error:
            if isinstance(error, ERNAErrorIndex):
                props.erna_error_indicator = props.erna[0:error.index] + "^"
            props.erna_error = str(error)

        except Exception as error:
            props.unexpected_error = str(error)

        if self.settings().enable_debug_infomation:
            self.print_traceback_and_set_clipboard()            
    
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

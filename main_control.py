import re
import bpy
from collections import (ChainMap, namedtuple)

from .utils import *
from .globals_model import *
from .settings_model import *
from .main_model import *


ERNAToken = namedtuple("ERNAToken", [ "t_type", "t_index", "t_string" ])


class ERNALexer:
    t_count = counter(1)

    t_start = t_count()
    t_stop = t_count()
    t_symbol = t_count()
    t_name = t_count()
    t_number = t_count()
    t_expr = t_count()

    re_table = [
        (t_symbol, re.compile(r"""[\.!*@|\[:\]%=\\]""")),
        (t_name, re.compile(r"""[A-Za-z_][A-Za-z_0-9]*""")),
        (t_number, re.compile(r"""[0-9-]+""")),
        (t_expr, re.compile(r"""\$[^\$]*\$""")),
    ]

    def __init__(self, s: str):
        self.s = s
        self.s_index = 0

    def tokens(self):
        """
            Return generator of ERNAToken
            t_type : t_start | t_stop | t_symbol | t_name | t_number | t_expr
            t_index : start index of token 
            t_string : token string
        """
        self.s_index = 0
        yield ERNAToken(self.t_start, self.s_index, "")

        while True:
            if self.s_index >= len(self.s):
                yield ERNAToken(self.t_stop, self.s_index, "")
                return

            if self.s[self.s_index].isspace():
                yield ERNAToken(self.t_stop, self.s_index, "")
                return

            for t, regex in self.re_table:
                match = regex.match(self.s, self.s_index)
                if match:
                    t_index = self.s_index
                    self.s_index = match.end(0)
                    yield ERNAToken(t, t_index, match.group(0))
                    break
            else:
                raise ERNAErrorIndex(self.s_index, "Unexpected Token")


ERNANode = namedtuple("ERNANode", ["op", "value"])

class ERNAParser:
    """LL(1) parser of erna"""

    erna_count = counter(1)

    erna = erna_count()
    op = erna_count()
    op_prop = erna_count()
    op_map = erna_count()
    op_init = erna_count()
    op_flatten = erna_count()
    op_sort = erna_count()
    op_filter = erna_count()
    op_take = erna_count()
    op_var = erna_count()
    op_assign = erna_count()
    op_delay = erna_count()

    def __init__(self, lexer):
        self.t_sequence = lexer.tokens()
        self.t_token = None
        self.next()

    def next(self):
        self.t_token = next(self.t_sequence)

    def is_token(self, t_type):
        return self.t_token.t_type == t_type

    def match_token(self, t_type):
        if self.is_token(t_type):
            token = self.t_token
            self.next()
            return token
        else:
            raise ERNAErrorIndex(
                self.t_token.t_index, "Unexpected Token"
            )

    def is_symbol(self, symbol):
        t_type, _, t_string = self.t_token
        return t_type == ERNALexer.t_symbol and t_string == symbol

    def match_symbol(self, symbol):
        if self.is_symbol(symbol):
            token = self.t_token
            self.next()
            return token
        else:
            raise ERNAErrorIndex(
                self.t_token.t_index, "Expect Symbol {0}".format(symbol)
            )

    def parse(self):
        """Return instance of ERNANode"""
        self.match_token(ERNALexer.t_start)
        return self.parse_erna()

    def parse_erna(self):
        ret = []
        while not self.is_token(ERNALexer.t_stop):
            ret.append(self.parse_op())

        if len(ret) == 0:
            raise ERNAErrorEmpty()

        return ret

    def parse_op(self):
        if self.is_token(ERNALexer.t_name):
            return self.parse_op_prop()

        if self.is_token(ERNALexer.t_expr):
            return self.parse_op_map()

        t_type, _, t_string = self.t_token
        if t_type != ERNALexer.t_symbol:
            raise ERNAErrorIndex(self.t_token.t_index, "Unexpected Token")

        table = {
            "." : self.parse_op_prop,
            "!" : self.parse_op_init,
            "*" : self.parse_op_flatten,
            "@" : self.parse_op_sort,
            "|" : self.parse_op_filter,
            "[" : self.parse_op_take,
            "%" : self.parse_op_var,
            "=" : self.parse_op_assign,
            "\\" : self.parse_op_delay,
        }

        parse_op = table.get(t_string, None)
        if parse_op is None:
            raise ERNAErrorIndex(self.t_token.t_index, "Unexpected Token")
        else:
            return parse_op()

    def parse_op_prop(self):
        """Return ERNANode(op_prop, prop)"""
        if self.is_symbol("."): self.next()
        prop = self.match_token(ERNALexer.t_name).t_string
        return ERNANode(self.op_prop, prop)

    def parse_op_map(self):
        """Return ERNANode(op_map, (expr_index, expr))"""
        _, index, expr = self.match_token(ERNALexer.t_expr)
        return ERNANode(self.op_map, (index + 1, expr[1:-1]))

    def parse_op_expr(self, symbol, op_type):
        """Return ERNANode(op_type, (expr_index, expr))"""
        self.match_symbol(symbol)
        _, index, expr = self.match_token(ERNALexer.t_expr)
        return ERNANode(op_type, (index + 1, expr[1:-1]))
    
    def parse_op_expr_allow_empty(self, symbol, op_type):
        """Return ERNANode(op_type, (expr_index, expr))"""
        self.match_symbol(symbol)
        if self.is_token(ERNALexer.t_expr):
            _, index, expr = self.match_token(ERNALexer.t_expr)
            return ERNANode(op_type, (index + 1, expr[1:-1]))
        else:
            return ERNANode(op_type, None)

    def parse_op_init(self):
        """Return ERNANode(op_map, (expr_index, expr))"""
        return self.parse_op_expr("!", self.op_init)

    def parse_op_flatten(self):
        """Return ERNANode(op_flatten, (expr_index, expr))"""
        return self.parse_op_expr_allow_empty("*", self.op_flatten)

    def parse_op_sort(self):
        """Return ERNANode(op_sort, (expr_index, expr))"""
        return self.parse_op_expr_allow_empty("@", self.op_sort)

    def parse_op_filter(self):
        """Return ERNANode(op_filter, (expr_index, expr))"""
        return self.parse_op_expr("|", self.op_filter)

    def parse_op_take(self):
        """Return ERNANode(op_take, (start, stop, step))"""
        self.match_symbol("[")

        start, stop, step = None, None, None

        if self.is_token(ERNALexer.t_number):
            start = int(self.match_token(ERNALexer.t_number).t_string)

        self.match_symbol(":")

        if self.is_token(ERNALexer.t_number):
            stop = int(self.match_token(ERNALexer.t_number).t_string)
    
        if self.is_symbol(":"):
            self.next()
            step = int(self.match_token(ERNALexer.t_number).t_string)

        self.match_symbol("]")

        return ERNANode(self.op_take, (start, stop, step))

    def parse_op_var(self):
        """Return ERNANode(op_var, (expr_index, expr))"""
        return self.parse_op_expr("%", self.op_var)

    def parse_op_assign(self):
        """Return ERNANode(op_filter, (name, expr_index, expr))"""
        self.match_symbol("=")
        name = self.match_token(ERNALexer.t_name).t_string
        _, index, expr = self.match_token(ERNALexer.t_expr)
        return ERNANode(self.op_assign, (name, index + 1, expr[1:-1]))

    def parse_op_delay(self):
        """Return ERNANode(op_var, (expr_index, expr))"""
        return self.parse_op_expr("\\", self.op_delay)


class Context:
    def __init__(self, data, ls={}):
        self.data = data
        self.ls = ls

    def access_property(self, prop):
        data = getattr(self.data, prop, None)
        if data == None:
            raise CollectionErrorProperty(prop)
        return Context(data, self.ls)

    def eval(self, ls, expr_value):
        try:
            expr_index, expr = expr_value
            return eval(expr, Expression_Globals, ChainMap(ls, self.ls))
        except SyntaxError as error:
            raise ERNAErrorIndex(expr_index + error.offset, error.msg)
        except Exception as error:
            raise CollectionErrorEval(error)


Assignment = namedtuple("Assignment", ["prop", "datas", "values"])
Delay = namedtuple("Delay", ["gs", "ls", "expr_value"])


class Collection:
    def __init__(self, contexts):
        if len(contexts) == 0:
            raise CollectionErrorEmpty()
        self.contexts = contexts
        self.assignments = []
        self.delays = []

    def accessable_properties(self):
        data = self.contexts[0].data
        props = sorted(dir(data))
        settings = BATCH_PROCESS_SettingsModel.get()

        if not settings.enable_python_reserved_property:
            props = [
                prop for prop in props
                if not prop.startswith("_")
            ]

        if not settings.enable_python_callable_property:
            props = [
                prop for prop in props
                if not callable(getattr(data, prop))
            ]

        return props

    def transform(self, erna_ast):
        table = {
            ERNAParser.op_prop : self.transform_op_prop,
            ERNAParser.op_map : self.transform_op_map,
            ERNAParser.op_init : self.transform_op_init,
            ERNAParser.op_flatten : self.transform_op_flatten,
            ERNAParser.op_sort : self.transform_op_sort,
            ERNAParser.op_filter : self.transform_op_filter,
            ERNAParser.op_take : self.transform_op_take,
            ERNAParser.op_var : self.transform_op_var,
            ERNAParser.op_assign : self.transform_op_assign,
            ERNAParser.op_delay : self.transform_op_delay,
        }

        for op, value in erna_ast:
            transform_op = table.get(op, None)
            if transform_op is None:
                raise CollectionErrorOperation()
            else:
                transform_op(value)

    def transform_op_prop(self, prop):
        self.contexts = [
            context.access_property(prop)
            for context in self.contexts
        ]

    def transform_op_map(self, value):
        contexts_new = []
        length = len(self.contexts)

        for index, context in enumerate(self.contexts):
            ls_ext = {
                "length" : length,
                "index" : index,
                "data" : context.data,
            }
            data_new = context.eval(ls_ext, value)
            context_new = Context(data_new, context.ls)
            contexts_new.append(context_new)

        self.contexts = contexts_new

    def transform_op_init(self, value):
        data = Context(None).eval({}, value)

        if not hasattr(data, "__iter__"):
                raise CollectionErrorNoIter(data)
        
        self.contexts = [Context(item) for item in data]

    def transform_op_flatten(self, value):
        contexts_new = []
        length = len(self.contexts)

        for index, context in enumerate(self.contexts):
            data, ls = context.data, context.ls

            if not hasattr(data, "__iter__"):
                raise CollectionErrorNoIter(data)

            length_data = len(data)

            if value is None:
                for item in data:
                    contexts_new.append(Context(item, ls))

            else:
                for index_item, item in enumerate(data):
                    ls_ext = {
                        "length" : length,
                        "index" : index,
                        "data" : data,
                        "length_data" : length_data,
                        "index_item" : index_item,
                        "item" : item,
                    }
                    context_item = Context(item, ls)
                    ls_new = context_item.eval(ls_ext, value)
                    context_item.ls = {**context_item.ls, **ls_new}
                    contexts_new.append(context_item)

        self.contexts = contexts_new

    def transform_op_sort(self, value):
        length = len(self.contexts)

        def sort_key(context):
            ls_ext = {"length": length, "data": context.data}
            return context.eval(ls_ext, value)
        
        if value is None:
            self.contexts.sort()
        else:
            self.contexts.sort(key=sort_key)

    def transform_op_filter(self, value):
        contexts_new = []
        length = len(self.contexts)

        for index, context in enumerate(self.contexts):
            ls_ext = {
                "length" : length,
                "index" : index,
                "data" : context.data,
            }
            if context.eval(ls_ext, value):
                contexts_new.append(context)

        if len(contexts_new) == 0:
            raise CollectionErrorEmpty()

        self.contexts = contexts_new

    def transform_op_take(self, numbers):
        start, stop, step = numbers
        self.contexts = self.contexts[start:stop:step]
        if len(self.contexts) == 0:
            raise CollectionErrorEmpty()

    def transform_op_var(self, value):
        contexts_new = []
        length = len(self.contexts)

        for index, context in enumerate(self.contexts):
            ls_ext = {
                "length" : length,
                "index" : index,
                "data" : context.data,
            }
            ls_new = context.eval(ls_ext, value)
            context.ls = {**context.ls, **ls_new}
            contexts_new.append(context)

        self.contexts = contexts_new

    def transform_op_assign(self, values):
        name, expr_index, expr = values
        assignment = Assignment(name, [], [])

        length = len(self.contexts)
        for index, context in enumerate(self.contexts):
            assign_data = context.data
            assignment.datas.append(assign_data)

            prop_data = context.access_property(name).data

            ls_ext = {
                "length": length,
                "index": index, 
                "data": assign_data, 
                "prop" : prop_data,
            }
            assign_value = context.eval(ls_ext, (expr_index, expr))

            expect, actual = type(prop_data), type(assign_value)
            if expect != actual:
                raise CollectionErrorAssignType(expect, actual)

            assignment.values.append(assign_value)
        
        self.assignments.append(assignment)

    def transform_op_delay(self, value):
        expr_index, expr = value

        length = len(self.contexts)
        for index, context in enumerate(self.contexts):
            ls_ext = {
                "length": length,
                "index": index, 
                "data": context.data, 
            }
            delay = Delay(ChainMap(ls_ext, context.ls), (expr_index, expr))
            self.delays.append(delay)

    def assign(self):
        try:
            for assignment in self.assignments:
                prop = assignment.prop
                for data, value in zip(assignment.datas, assignment.values):
                    setattr(data, prop, value)

            for delay in self.delays:
                eval(delay.expr_value.expr, delay.gs, delay.ls)

        except Exception as error:
            raise AssignError(error)


@singleton
class BATCH_PROCESS_MainControl:
    def __init__(self):
        self.collections = []

    def insert_erna(self, index):
        with MainModelChangeContext() as model:
            model.erna_count += 1
            model.ernas.add()
            for i in range(len(model.ernas) - 1, index, -1):
                model.ernas.move(i - 1, i)

    def remove_erna(self, index):
        with MainModelChangeContext() as model:
            model.erna_count -= 1
            model.ernas.remove(index)

    def update(self):
        model = BATCH_PROCESS_MainModel.get()
        erna_count = len(model.ernas)

        if erna_count < model.erna_count:
            for _ in range(erna_count, model.erna_count):
                model.ernas.add()

        elif erna_count > model.erna_count:
            for index in range(erna_count - 1, model.erna_count - 1, -1):
                model.ernas.remove(index)

        self.update_collections()

    def assign(self):
        model = BATCH_PROCESS_MainModel.get()
        model.assign_error = ""

        try:
            for collection in self.collections:
                collection.assign()

        except AssignError as error:
            settings = BATCH_PROCESS_SettingsModel.get()

            if settings.enable_debug_information:
                print_traceback_and_set_clipboard()

            model.assign_error = str(error)

    def update_collections(self):
        model = BATCH_PROCESS_MainModel.get()
        erna_count = len(model.ernas)
        self.collections = [None] * erna_count

        for index in range(erna_count):
            self.index = index
            self.update_collection()

    def erna_model(self):
        return BATCH_PROCESS_MainModel.get().ernas[self.index]

    def clear_errors(self):
        model = self.erna_model()
        model.unexpected_error = ""
        model.erna_error = ""
        model.erna_error_indicator = ""
        model.collection_error = ""

    def update_collection(self):
        self.clear_errors()
        model = self.erna_model()

        try:
            lexer = ERNALexer(model.erna)
            erna_ast = ERNAParser(lexer).parse()

            prev_collection = None
            if self.index == 0:
                prev_collection = Collection([Context(None)])
            else:
                prev_collection = self.collections[self.index - 1]
                
            if prev_collection is None:
                raise CollectionErrorPrevCollection()

            collection = Collection(prev_collection.contexts)
            collection.transform(erna_ast)

            self.collections[self.index] = collection

        except Exception as error:
            self.handle_errors(error)

    def handle_errors(self, error):
        settings = BATCH_PROCESS_SettingsModel.get()
        model = self.erna_model()

        if settings.enable_debug_information:
            print_traceback_and_set_clipboard()

        if isinstance(error, ERNAError):
            if isinstance(error, ERNAErrorIndex):
                indicator = model.erna[0:error.index] + "^"
                model.erna_error_indicator = indicator
            model.erna_error = str(error)

        elif isinstance(error, CollectionError):
            model.collection_error = str(error)

        else:
            model.unexpected_error = str(error)


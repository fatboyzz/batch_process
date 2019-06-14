from collections import OrderedDict
import bpy
from .utils import *
from .settings_model import *
from .main_model import *
from .preset_model import *

register_classes = []

class Preset:
    def __init__(self):
        self.datas = OrderedDict()

    def file_lines(self, file):
        text = bpy.data.texts[file]
        if len(text.lines) == 0: raise PresetErrorFileEmpty()
        for line in text.lines:
            body = line.body
            index = body.find("#")
            yield body[0:None if index == -1 else index]

    s_count = counter(1)
    s_empty = s_count()
    s_key = s_count()
    s_erna = s_count()

    def parse_lines(self, lines):
        state = self.s_empty
        line, key, ernas = None, None, None

        while True:
            if state == self.s_empty:
                line = next(lines, None)
                if line == None: 
                    return
                elif line == "":
                    state = self.s_empty
                else:
                    key = line
                    state = self.s_key

            elif state == self.s_key:
                line = next(lines, None)
                if line == None: 
                    raise PresetErrorERNAEmpty(key)
                elif line == "":
                    raise PresetErrorERNAEmpty(key)
                else:
                    ernas = [line]
                    state = self.s_erna

            elif state == self.s_erna:
                line = next(lines, None)
                if line == None: 
                    self.datas[key] = ernas
                    return
                elif line == "":
                    self.datas[key] = ernas
                    state = self.s_empty
                else:
                    ernas.append(line)

    def parse_file(self, file):
        self.datas = OrderedDict()
        self.parse_lines(self.file_lines(file))


@singleton
class BatchProcess_PresetControl:
    def __init__(self):
        self.preset = None
        self.preset_file_loaded = None
        self.preset_key_loaded = None

    def load_file(self, file):
        model = BatchProcess_PresetModel.get()
        model.preset_error = ""
        model.unexpected_error = ""
        
        try:
            self.preset_file_loaded = None
            self.preset_key_loaded = None
            self.preset = Preset()
            self.preset.parse_file(file)
            self.preset_file_loaded = file

        except Exception as error:
            settings = BatchProcess_SettingsModel.get()
            model = BatchProcess_PresetModel.get()

            if settings.enable_debug_information:
                print_traceback_and_set_clipboard()

            if isinstance(error, PresetError):
                model.preset_error = str(error)

            else:
                model.unexpected_error = str(error)
            

    def load_key(self, key):
        with MainModelChangeContext():
            self.preset_key_loaded = None
            model = BatchProcess_MainModel.get()

            ernas = self.preset.datas[key]
            model.erna_count = len(ernas)

            model.ernas.clear()
            for erna in ernas:
                model.ernas.add().erna = erna

            self.preset_key_loaded = key

    def write_ernas(self, file):
        texts = bpy.data.texts 
        text = texts.get(file, None)
        if text is None: return

        lines = [ "# ERNA", "ERNA" ]
        lines.extend([model.erna for model in BatchProcess_MainModel.get().ernas])
        lines.append("")
        
        text.write("\n".join(lines))
        
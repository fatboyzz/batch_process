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
        self.line_sequence = None
        self.line = None

    def next(self):
        text_line = next(self.line_sequence, None)
        self.line = text_line.body if text_line is not None else None

    def parse_file(self, file):
        """
            <empty line>*
            <key 0>
            <erna 0>
            <erna 1>
            <empty line>+
            <key 1>
            <erna 0>
            <erna 1>
            <empty line>+
        """
        text = bpy.data.texts[file]
        if len(text.lines) == 0: raise PresetErrorEmpty()

        self.datas = OrderedDict()
        self.line_sequence = text.lines.__iter__()
        self.next()
        self.parse_lines()

    def parse_lines(self):
        if self.line == None: 
            return

        elif self.line == "": 
            while self.line == "":
                self.next()

        else:
            key = self.line
            self.next()
            if key in self.datas:
                raise PresetErrorKeyAlreadyExist(key)

            ernas = []
            while self.line != "":
                ernas.append(self.line)
                self.next()

            self.datas[key] = ernas


@singleton
class BatchAssign_PresetControl:
    def __init__(self):
        self.preset = None
        self.preset_file_loaded = None
        self.preset_key_loaded = None

    def load_file(self, file):
        try:
            self.preset_file_loaded = None
            self.preset = Preset()
            self.preset.parse_file(file)
            self.preset_file_loaded = file

        except Exception as error:
            settings = BatchAssign_SettingsModel.get()
            model = BatchAssign_PresetModel.get()

            if settings.enable_debug_information:
                print_traceback_and_set_clipboard()

            if isinstance(error, PresetError):
                model.preset_error = str(error)

            else:
                model.unexpected_error = str(error)
            

    def load_key(self, key):
        self.preset_key_loaded = None

        settings = BatchAssign_SettingsModel.get()
        old_setting = settings.enable_update_when_erna_changed
        settings.enable_update_when_erna_changed = False

        model = BatchAssign_MainModel.get()

        ernas = self.preset.datas[key]
        model.erna_count = len(ernas)

        model.ernas.clear()
        for erna in ernas:
            model.ernas.add().erna = erna

        settings.enable_update_when_erna_changed = old_setting
        self.preset_key_loaded = key

        main_model_update(self, None)

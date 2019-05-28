import bpy
from .utils import *
from .main_model import *

register_classes = []

class Preset:
    def __init__(self, erna, expr):
        self.erna = erna
        self.expr = expr

    def load(self):
        model = BatchAssign_MainModel.get()
        model.erna = self.erna
        model.expr = self.expr

    def save(self):
        model = BatchAssign_MainModel.get()
        self.erna = model.erna
        self.expr = model.expr

@singleton
class BatchAssign_PresetControl:
    def __init__(self):
        self.presets = {}

    def load_preset(self, filename):
        print("load ", filename)

    def save_preset(self, filename):
        print("save ", filename)

    def load_key(self, key):
        self.presets[key].load()

    def save_key(self, key):
        self.presets[key].save()

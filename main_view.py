import bpy
from .utils import *
from .main_control import *

register_classes = []

@append(register_classes)
class BatchAssign_OP_MainControlUpdate(bpy.types.Operator):
    bl_idname = "batch_assign.main_control_update"
    bl_label = "Update Collection"
    bl_description = "Update Collection"

    def execute(self, context):
        BatchAssign_MainControl.get().update()
        return {'FINISHED'}

@append(register_classes)
class BatchAssign_OP_MainControlBatchAssign(bpy.types.Operator):
    bl_idname = "batch_assign.main_control_batch_assign"
    bl_label = "Update Collection"
    bl_description = "Batch Assign Value"
    
    def execute(self, context):
        BatchAssign_MainControl.get().batch_assign()
        return {'FINISHED'}
    
@append(register_classes)
class BatchAssign_PT_MainPanel(bpy.types.Panel):
    bl_idname = "BatchAssign_PT_MainPanel"
    bl_label = "Batch Assign Main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Misc"

    def draw_error(self, layout, error) -> bool:
        if len(error) > 0:
            layout.label(text = error, icon = "ERROR")
            return True
        else:
            return False
    
    def draw(self, context):
        self.context = context
        self.draw_update_button()

    def draw_update_button(self):
        layout = self.layout
        layout.operator(
            "batch_assign.main_control_update",
            text = "Update",
        )

        control = BatchAssign_MainControl.get()
        if control.collections is None:
            self.draw_error(layout, "Click Update To Start")
        else:
            self.draw_erna_count()

    def draw_erna_count(self):
        layout = self.layout
        layout.prop(
            data = BatchAssign_MainModel.get(),
            property = "erna_count",
        )

        self.draw_ernas()

    def draw_ernas(self):
        for index in range(BatchAssign_MainModel.get().erna_count):
            self.index = index
            self.draw_erna()

        self.draw_assign_button()

    def draw_assign_button(self):
        self.layout.operator(
            "batch_assign.main_control_batch_assign",
            text = "Assign",
        )

    def draw_erna(self):
        self.layout_erna = self.layout.box()

        model = BatchAssign_MainModel.get().ernas[self.index]
        layout = self.layout_erna
        
        layout_row = layout.row(align = True)
        layout_row.label(text = "ERNA {0}:".format(self.index))

        toggle = model.enable_collection_preview
        layout_row.prop(
            data = model,
            property = "enable_collection_preview",
            text = "",
            icon = "HIDE_OFF" if toggle else "HIDE_ON",
        )

        toggle = model.enable_accessable_property
        layout_row.prop(
            data = model,
            property = "enable_accessable_property",
            text = "",
            icon = "RESTRICT_VIEW_OFF" if toggle else "RESTRICT_VIEW_ON",
        )

        self.draw_erna_data()

    def draw_erna_data(self):
        model = BatchAssign_MainModel.get().ernas[self.index]
        layout = self.layout_erna
        layout_column = layout.column(align = True)

        layout_column.prop(
            data = model,
            property = "erna",
            text = "",
            icon = "TEXT",
        )

        if len(model.erna_error_indicator) > 0:
            layout.prop(
                data = model,
                property = "erna_error_indicator",
                text = "",
                icon = "ERROR",
            )

        error = model.unexpected_error
        if self.draw_error(layout, error): return

        error = model.erna_error
        if self.draw_error(layout, error): return

        error = model.collection_error
        if self.draw_error(layout, error): return

        if model.enable_collection_preview:
            self.draw_collection_preview()

        if model.enable_accessable_property:
            self.draw_accessable_property()

    def draw_collection_preview(self):
        control = BatchAssign_MainControl.get()
        collection = control.collections[self.index]

        layout = self.layout_erna
        layout_column = layout.column(align = True)

        if not collection.has_assign():
            for context in collection.contexts:
                layout_column.label(text = str(context.data))

        else:
            datas_values = zip(collection.assign_datas, collection.assign_values)
            for data, value in datas_values:
                layout_row = layout_column.row(align = True)

                if isinstance(data, bpy.types.bpy_struct):
                    layout_row.prop(
                        data = data,
                        property = collection.assign_property,
                        text = "",
                    )
                else:
                    layout_row.label(
                        text = str(getattr(data, collection.property))
                    )    

                layout_row.label(text = str(value))

    def draw_accessable_property(self):
        control = BatchAssign_MainControl.get()
        collection = control.collections[self.index]

        layout = self.layout_erna
        layout_column = layout.column_flow(align = True, columns = 2)

        for prop in collection.accessable_properties():
            layout_column.label(text = prop)

import bpy
from .utils import *
from .main_control import *

@register_class
class BatchAssign_OP_MainControlUpdate(bpy.types.Operator):
    bl_idname = "batch_assign.main_control_update"
    bl_label = "Update Collection"
    bl_description = "Update Collection"

    def execute(self, context):
        BatchAssign_MainControl.get().update()
        return {'FINISHED'}

@register_class
class BatchAssign_OP_MainControlAssign(bpy.types.Operator):
    bl_idname = "batch_assign.main_control_assign"
    bl_label = "Assign Value"
    bl_description = "Assign Value"
    
    def execute(self, context):
        BatchAssign_MainControl.get().assign()
        return {'FINISHED'}

@register_class
class BatchAssign_OP_MainControlInsertERNA(bpy.types.Operator):
    bl_idname = "batch_assign.main_control_insert_erna"
    bl_label = "Insert ERNA"
    bl_description = "Insert ERNA"

    index : IntProperty(
        description = "Insert Index",
        default = 0,
    )

    def execute(self, context):
        BatchAssign_MainControl.get().insert_erna(self.index)
        return {'FINISHED'}

@register_class
class BatchAssign_OP_MainControlRemoveERNA(bpy.types.Operator):
    bl_idname = "batch_assign.main_control_remove_erna"
    bl_label = "Remove ERNA"
    bl_description = "Remove ERNA"

    index : IntProperty(
        description = "Remove Index",
        default = 0,
    )

    def execute(self, context):
        BatchAssign_MainControl.get().remove_erna(self.index)
        return {'FINISHED'}
    
@register_class
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
            BatchAssign_OP_MainControlUpdate.bl_idname,
            text = "Update",
        )

        control = BatchAssign_MainControl.get()
        if control.collections is None:
            self.draw_error(layout, "Click Update To Start")
        else:
            self.draw_erna_count()

    def draw_erna_count(self):
        self.layout.prop(
            data = BatchAssign_MainModel.get(),
            property = "erna_count",
        )

        self.draw_ernas()

    def draw_ernas(self):
        control = BatchAssign_MainControl.get()
        model = BatchAssign_MainModel.get()

        for index in range(model.erna_count):
            self.index = index
            self.layout_erna = self.layout.box()
            self.model_erna = model.ernas[index]
            self.collection = control.collections[index]
            self.draw_erna()

        self.draw_assign_button()

    def draw_assign_button(self):
        model = BatchAssign_MainModel.get()

        self.layout.operator(
            BatchAssign_OP_MainControlAssign.bl_idname,
            text = "Assign",
        )

        error = model.assign_error
        self.draw_error(self.layout, error)

    def draw_erna(self):
        model = self.model_erna
        layout = self.layout_erna
        
        layout_row = layout.row(align = True)
        layout_row.label(text = "ERNA {0}:".format(self.index))

        toggle = model.enable_collection_preview
        layout_row.operator(
            BatchAssign_OP_MainControlInsertERNA.bl_idname,
            text = "",
            icon = "ADD",
        ).index = self.index

        layout_row.operator(
            BatchAssign_OP_MainControlRemoveERNA.bl_idname,
            text = "",
            icon = "REMOVE",
        ).index = self.index

        layout_row.prop(
            data = model,
            property = "enable_collection_preview",
            text = "",
            icon = "HIDE_OFF" if toggle else "HIDE_ON",
        )

        toggle = model.enable_assignment_preview
        layout_row.prop(
            data = model,
            property = "enable_assignment_preview",
            text = "",
            icon = "MODIFIER_OFF" if toggle else "MODIFIER_ON",
        )

        toggle = model.enable_accessable_property
        layout_row.prop(
            data = model,
            property = "enable_accessable_property",
            text = "",
            icon = "WORDWRAP_OFF" if toggle else "WORDWRAP_ON",
        )

        self.draw_erna_data()

    def draw_erna_data(self):
        model = self.model_erna
        layout = self.layout_erna
        layout_column = layout.column(align = True)

        layout_column.prop(
            data = model,
            property = "erna",
            text = "",
            icon = "TEXT",
        )

        if len(model.erna_error_indicator) > 0:
            layout_column.prop(
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

        if model.enable_assignment_preview:
            self.draw_assignment_preview()

        if model.enable_accessable_property:
            self.draw_accessable_property()


    def draw_collection_preview(self):
        collection = self.collection
        if len(collection.contexts) == 0: return

        layout = self.layout_erna
        layout_column = layout.column(align = True)

        for context in collection.contexts:
            layout_column.label(text = str(context.data))


    def draw_assignment_preview(self):
        collection = self.collection
        assignments = collection.assignments
        if len(assignments) == 0: return

        layout = self.layout_erna
        layout_column = layout.column(align = True)

        for assignment in assignments:
            for data, value in zip(assignment.datas, assignment.values):
                layout_row = layout_column.row(align = True)

                if isinstance(data, bpy.types.bpy_struct):
                    layout_row.prop(
                        data = data,
                        property = assignment.prop,
                        text = "",
                    )
                else:
                    layout_row.label(
                        text = str(getattr(data, collection.property))
                    )    

                layout_row.label(text = str(value))
    

    def draw_accessable_property(self):
        collection = self.collection
        props = collection.accessable_properties()
        if len(props) == 0: return

        layout = self.layout_erna
        layout_column = layout.column_flow(align = True, columns = 2)

        for prop in props:
            layout_column.label(text = prop)

    
import bpy
from .utils import *
from .main_control import *

@register_class
class BATCH_PROCESS_OP_MainControlUpdate(bpy.types.Operator):
    bl_idname = "batch_process.main_control_update"
    bl_label = "Update Collection"
    bl_description = "Update Collection"

    def execute(self, context):
        BATCH_PROCESS_MainControl.get().update()
        return {'FINISHED'}

@register_class
class BATCH_PROCESS_OP_MainControlAssign(bpy.types.Operator):
    bl_idname = "batch_process.main_control_assign"
    bl_label = "Assign Value"
    bl_description = "Assign Value"
    
    def execute(self, context):
        BATCH_PROCESS_MainControl.get().assign()
        return {'FINISHED'}

@register_class
class BATCH_PROCESS_OP_MainControlInsertERNA(bpy.types.Operator):
    bl_idname = "batch_process.main_control_insert_erna"
    bl_label = "Insert ERNA"
    bl_description = "Insert ERNA"

    index : IntProperty(
        description = "Insert Index",
        default = 0,
    )

    def execute(self, context):
        BATCH_PROCESS_MainControl.get().insert_erna(self.index)
        return {'FINISHED'}

@register_class
class BATCH_PROCESS_OP_MainControlRemoveERNA(bpy.types.Operator):
    bl_idname = "batch_process.main_control_remove_erna"
    bl_label = "Remove ERNA"
    bl_description = "Remove ERNA"

    index : IntProperty(
        description = "Remove Index",
        default = 0,
    )

    def execute(self, context):
        BATCH_PROCESS_MainControl.get().remove_erna(self.index)
        return {'FINISHED'}
    
@register_class
class BATCH_PROCESS_PT_MainPanel(bpy.types.Panel):
    bl_idname = "BATCH_PROCESS_PT_MainPanel"
    bl_label = "Batch Process Main"
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
            BATCH_PROCESS_OP_MainControlUpdate.bl_idname,
            text = "Update",
        )

        control = BATCH_PROCESS_MainControl.get()
        if control.collections is None:
            self.draw_error(layout, "Click Update To Start")
        else:
            self.draw_erna_count()

    def draw_erna_count(self):
        self.layout.prop(
            data = BATCH_PROCESS_MainModel.get(),
            property = "erna_count",
        )

        self.draw_ernas()

    def draw_ernas(self):
        control = BATCH_PROCESS_MainControl.get()
        model = BATCH_PROCESS_MainModel.get()

        if model.erna_count != len(control.collections):
            self.draw_error(self.layout, "Click Update To Start")
            return

        for index in range(model.erna_count):
            self.index = index
            self.layout_erna = self.layout.box()
            self.model_erna = model.ernas[index]
            self.collection = control.collections[index]
            self.draw_erna()

        self.draw_process_button()

    def draw_process_button(self):
        model = BATCH_PROCESS_MainModel.get()

        self.layout.operator(
            BATCH_PROCESS_OP_MainControlAssign.bl_idname,
            text = "Process",
        )

        error = model.assign_error
        self.draw_error(self.layout, error)

    def draw_erna(self):
        model = self.model_erna
        layout = self.layout_erna
        
        layout_row = layout.row(align = True)
        layout_row.label(text = "ERNA {0}:".format(self.index))

        layout_row.operator(
            BATCH_PROCESS_OP_MainControlInsertERNA.bl_idname,
            text = "",
            icon = "ADD",
        ).index = self.index

        layout_row.operator(
            BATCH_PROCESS_OP_MainControlRemoveERNA.bl_idname,
            text = "",
            icon = "REMOVE",
        ).index = self.index

        toggle = model.enable_data_preview
        layout_row.prop(
            data = model,
            property = "enable_data_preview",
            text = "",
            icon = "HIDE_OFF" if toggle else "HIDE_ON",
        )

        toggle = model.enable_variable_preview
        layout_row.prop(
            data = model,
            property = "enable_variable_preview",
            text = "",
            icon = "RESTRICT_VIEW_OFF" if toggle else "RESTRICT_VIEW_ON",
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

        self.draw_context_preview()
        self.draw_assignment_preview()
        self.draw_accessable_property()

    def draw_context_preview(self):
        model = self.model_erna
        data_preview = model.enable_data_preview
        variable_preview = model.enable_variable_preview
        if not data_preview and not variable_preview: return

        collection = self.collection
        if len(collection.contexts) == 0: return

        layout = self.layout_erna
        layout_column = layout.column(align = True)

        for context in collection.contexts:
            text = ""
            if data_preview:
                text += str(context.data)
            if variable_preview:
                text += str(context.ls)

            layout_column.label(text = text)


    def draw_assignment_preview(self):
        if not self.model_erna.enable_assignment_preview: return

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
        if not self.model_erna.enable_accessable_property: return

        collection = self.collection
        props = collection.accessable_properties()
        if len(props) == 0: return

        layout = self.layout_erna
        layout_column = layout.column_flow(align = True, columns = 2)

        for prop in props:
            layout_column.label(text = prop)

    
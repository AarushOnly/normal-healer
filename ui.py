import bpy
from . import operators


class NORMALHEALER_PT_main_panel(bpy.types.Panel):
    """Main NormalHealer panel in 3D Viewport Sidebar"""
    bl_label = "Normal Healer"
    bl_idname = "NORMALHEALER_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Normal Healer"

    def draw(self, context):
        layout = self.layout
        obj = context.active_object

        # --- Section 1: Boolean Shading Healer ---
        box = layout.box()
        box.label(text="Smart Boolean & Normal Cage", icon='MOD_BOOLEAN')
        
        col = box.column(align=True)
        col.scale_y = 1.3
        col.operator("normalhealer.smart_cut", text="Smart Cut & Heal", icon='MOD_BOOLEAN')
        
        col_heal = box.column(align=True)
        col_heal.operator("normalhealer.heal_existing", text="Heal Existing Shading", icon='AUTOMERGE_ON')

        # --- Section 2: Universal Auto Smooth ---
        box = layout.box()
        box.label(text="Universal Auto Smooth", icon='MOD_SMOOTH')
        row = box.row(align=True)
        row.scale_y = 1.2
        row.operator("normalhealer.quick_autosmooth", text="Apply Auto Smooth (35°)", icon='NORMALS_FACE').angle = 35.0
        row.operator("normalhealer.quick_autosmooth", text="60°", icon='NORMALS_FACE').angle = 60.0

        # --- Section 3: Diagnostic & Inspection ---
        box = layout.box()
        box.label(text="Surface Quality Inspection", icon='SHADING_RENDERED')
        col_diag = box.column(align=True)
        col_diag.operator("normalhealer.toggle_zebra_diagnostic", text="Toggle Zebra / Flow MatCap", icon='SHADING_TEXTURE')

        # --- Section 4: Finalize & Clean ---
        box = layout.box()
        box.label(text="Finalize & Export", icon='CHECKMARK')
        col_bake = box.column(align=True)
        col_bake.operator("normalhealer.bake_and_purge", text="Bake & Purge Cages", icon='FILE_TICK')

        # --- Section 5: Help & Support ---
        box_supp = layout.box()
        box_supp.label(text="Author: Integral", icon='USER')
        box_supp.operator("normalhealer.open_support", text="Support & Feedback", icon='HELP')



class NORMALHEALER_MT_pie_menu(bpy.types.Menu):
    """Quick Pie Menu for NormalHealer (Shift + Alt + N)"""
    bl_label = "Normal Healer Quick Menu"
    bl_idname = "NORMALHEALER_MT_pie_menu"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # Left
        pie.operator("normalhealer.heal_existing", text="Heal Existing Shading", icon='AUTOMERGE_ON')
        # Right
        pie.operator("normalhealer.smart_cut", text="Smart Cut & Heal", icon='MOD_BOOLEAN')
        # Bottom
        pie.operator("normalhealer.toggle_zebra_diagnostic", text="Toggle Surface Flow", icon='SHADING_TEXTURE')
        # Top
        pie.operator("normalhealer.quick_autosmooth", text="Auto Smooth 35°", icon='MOD_SMOOTH')


def draw_context_menu(self, context):
    """Adds NormalHealer actions to Right-Click Object context menu"""
    layout = self.layout
    layout.separator()
    layout.menu("NORMALHEALER_MT_pie_menu", text="Normal Healer", icon='MOD_BOOLEAN')

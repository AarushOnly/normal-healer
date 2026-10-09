bl_info = {
    "name": "NormalHealer: Smart Boolean & Shading Fixer",
    "author": "Integral",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Normal Healer & Shift+Alt+N",
    "description": "1-Click artifact-free boolean cuts and instant curved surface normal healing.",
    "warning": "",
    "doc_url": "mailto:integral7535@gmail.com",
    "tracker_url": "mailto:integral7535@gmail.com",
    "support": "COMMUNITY",
    "category": "Mesh",
}

import bpy
from . import operators
from . import ui

classes = (
    operators.NORMALHEALER_OT_smart_cut,
    operators.NORMALHEALER_OT_heal_existing,
    operators.NORMALHEALER_OT_quick_autosmooth,
    operators.NORMALHEALER_OT_toggle_zebra_diagnostic,
    operators.NORMALHEALER_OT_bake_and_purge,
    operators.NORMALHEALER_OT_open_support,
    ui.NORMALHEALER_PT_main_panel,
    ui.NORMALHEALER_MT_pie_menu,
)

addon_keymaps = []


def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if not kc:
        return

    # 3D Viewport shortcut: Shift + Alt + N
    km = kc.keymaps.new(name="3D View", space_type='VIEW_3D')
    kmi = km.keymap_items.new("wm.call_menu_pie", type='N', value='PRESS', shift=True, alt=True)
    kmi.properties.name = "NORMALHEALER_MT_pie_menu"
    addon_keymaps.append((km, kmi))


def unregister_keymaps():
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    addon_keymaps.clear()


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register Context Menu integration
    bpy.types.VIEW3D_MT_object_context_menu.append(ui.draw_context_menu)

    # Register Keyboard Shortcuts
    register_keymaps()


def unregister():
    unregister_keymaps()

    bpy.types.VIEW3D_MT_object_context_menu.remove(ui.draw_context_menu)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

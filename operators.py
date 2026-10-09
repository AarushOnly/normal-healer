import bpy
from . import utils


class NORMALHEALER_OT_smart_cut(bpy.types.Operator):
    """Perform a Boolean cut and instantly lock curved surface normals to eliminate shading glitches"""
    bl_idname = "normalhealer.smart_cut"
    bl_label = "Smart Cut & Heal"
    bl_options = {'REGISTER', 'UNDO'}

    operation: bpy.props.EnumProperty(
        name="Operation",
        description="Boolean operation type",
        items=[
            ('DIFFERENCE', "Difference", "Subtract cutter from target"),
            ('UNION', "Union", "Combine cutter and target"),
            ('INTERSECT', "Intersect", "Keep overlapping volume"),
        ],
        default='DIFFERENCE'
    )

    @classmethod
    def poll(cls, context):
        selected = context.selected_objects
        return len(selected) >= 2 and context.active_object in selected and context.active_object.type == 'MESH'

    def execute(self, context):
        target = context.active_object
        selected = [obj for obj in context.selected_objects if obj != target and obj.type == 'MESH']

        if not selected:
            self.report({'ERROR'}, "Please select at least one cutter mesh in addition to the active target mesh.")
            return {'CANCELLED'}

        cutter = selected[0]

        # 1. Ensure or create clean reference cage before boolean
        existing_cage = utils.find_existing_cage(target)
        if not existing_cage:
            cage = utils.create_normal_cage(target)
        else:
            cage = existing_cage

        # 2. Add or configure Boolean modifier
        bool_name = f"Bool_{cutter.name}"
        bool_mod = target.modifiers.get(bool_name)
        if not bool_mod:
            bool_mod = target.modifiers.new(name=bool_name, type='BOOLEAN')
        
        bool_mod.object = cutter
        bool_mod.operation = self.operation
        bool_mod.solver = 'EXACT'

        # Set cutter to non-obtrusive wireframe
        cutter.display_type = 'WIRE'
        cutter.hide_render = True

        # 3. Setup Data Transfer and Weighted Normal
        utils.setup_data_transfer(target, cage)
        utils.setup_weighted_normal(target)
        utils.ensure_smooth_shading(target, angle_deg=35.0)

        self.report({'INFO'}, f"Smart Cut & Normal Transfer applied on '{target.name}'.")
        return {'FINISHED'}


class NORMALHEALER_OT_heal_existing(bpy.types.Operator):
    """Heal shading on an object that already has Boolean cuts or shading pinching"""
    bl_idname = "normalhealer.heal_existing"
    bl_label = "Heal Existing Shading"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'

    def execute(self, context):
        target = context.active_object

        # Find boolean modifiers
        bool_mods = [m for m in target.modifiers if m.type == 'BOOLEAN']

        if bool_mods:
            # Temporarily turn off booleans to get pre-cut geometry snapshot
            states = [m.show_viewport for m in bool_mods]
            for m in bool_mods:
                m.show_viewport = False

            # Create clean cage snapshot
            cage = utils.create_normal_cage(target)

            # Re-enable booleans
            for m, state in zip(bool_mods, states):
                m.show_viewport = state

            utils.setup_data_transfer(target, cage)
            utils.setup_weighted_normal(target)
            utils.ensure_smooth_shading(target)
            self.report({'INFO'}, f"Generated reference cage and healed shading for '{target.name}'.")
        else:
            # No live booleans: Clean custom normals and apply weighted normal
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
            utils.setup_weighted_normal(target)
            utils.ensure_smooth_shading(target)
            self.report({'INFO'}, f"Refreshed split normals and weighted normal for '{target.name}'.")

        return {'FINISHED'}


class NORMALHEALER_OT_quick_autosmooth(bpy.types.Operator):
    """Quickly set angle-based auto-smooth across all selected meshes (Blender 3.6 - 4.2+ compatible)"""
    bl_idname = "normalhealer.quick_autosmooth"
    bl_label = "Universal Auto Smooth"
    bl_options = {'REGISTER', 'UNDO'}

    angle: bpy.props.FloatProperty(
        name="Angle (Degrees)",
        description="Threshold angle for sharp edge detection",
        default=30.0,
        min=0.0,
        max=180.0
    )

    @classmethod
    def poll(cls, context):
        return any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        count = 0
        for obj in context.selected_objects:
            if obj.type == 'MESH':
                utils.ensure_smooth_shading(obj, angle_deg=self.angle)
                count += 1

        self.report({'INFO'}, f"Auto-smoothed {count} mesh object(s) at {self.angle:.1f}°.")
        return {'FINISHED'}


class NORMALHEALER_OT_toggle_zebra_diagnostic(bpy.types.Operator):
    """Toggle viewport Zebra reflection inspection to check surface curvature and spot pinching"""
    bl_idname = "normalhealer.toggle_zebra_diagnostic"
    bl_label = "Inspect Surface Flow"
    bl_options = {'REGISTER'}

    def execute(self, context):
        shading = context.space_data.shading
        if shading.type != 'SOLID':
            shading.type = 'SOLID'

        # Toggle between Studio and MatCap Zebra
        if shading.light == 'MATCAP' and shading.studio_light in ['zebra.exr', 'reflection.exr']:
            shading.light = 'STUDIO'
            self.report({'INFO'}, "Inspection MatCap turned off.")
        else:
            shading.light = 'MATCAP'
            # Look for zebra or default reflective matcaps
            available_matcaps = [m.name for m in bpy.context.preferences.studio_lights]
            if "zebra.exr" in available_matcaps:
                shading.studio_light = "zebra.exr"
            elif "reflection.exr" in available_matcaps:
                shading.studio_light = "reflection.exr"
            self.report({'INFO'}, "Surface Inspection Mode enabled.")
        return {'FINISHED'}


class NORMALHEALER_OT_bake_and_purge(bpy.types.Operator):
    """Bake normal transfer to mesh and clean up reference cages for clean export"""
    bl_idname = "normalhealer.bake_and_purge"
    bl_label = "Bake & Purge Cages"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'

    def execute(self, context):
        target = context.active_object
        cage = utils.find_existing_cage(target)

        # Apply modifiers in order
        for mod in list(target.modifiers):
            if mod.name in ["NormalHealer_Transfer", "NormalHealer_Weighted"] or mod.type == 'BOOLEAN':
                try:
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                except Exception as e:
                    self.report({'WARNING'}, f"Could not apply modifier {mod.name}: {e}")

        # Purge cage
        if cage:
            utils.clean_object_cage(target)

        self.report({'INFO'}, f"Successfully baked shading and removed cages for '{target.name}'.")
        return {'FINISHED'}


class NORMALHEALER_OT_open_support(bpy.types.Operator):
    """Contact developer for support, feature requests, or bug reports"""
    bl_idname = "normalhealer.open_support"
    bl_label = "Contact Support"
    bl_options = {'REGISTER'}

    def execute(self, context):
        support_url = "mailto:integral7535@gmail.com?subject=NormalHealer%20Support%20Request"
        bpy.ops.wm.url_open(url=support_url)
        self.report({'INFO'}, "Opening support email to integral7535@gmail.com")
        return {'FINISHED'}


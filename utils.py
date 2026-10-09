import bpy
import math

CAGE_COLLECTION_NAME = "_NormalHealer_Cages"


def get_or_create_cage_collection():
    """Finds or creates a dedicated hidden collection for reference cages."""
    collection = bpy.data.collections.get(CAGE_COLLECTION_NAME)
    if not collection:
        collection = bpy.data.collections.new(CAGE_COLLECTION_NAME)
        bpy.context.scene.collection.children.link(collection)
        collection.hide_viewport = True
        collection.hide_render = True
    return collection


def create_normal_cage(target_obj):
    """
    Creates an exact geometry cage of the target object prior to boolean cuts.
    The cage is parented to the target so moving/scaling target maintains alignment.
    """
    cage_collection = get_or_create_cage_collection()

    # Clone mesh data
    cage_mesh = target_obj.data.copy()
    cage_name = f"{target_obj.name}_NormalCage"
    cage_mesh.name = f"{cage_name}_Mesh"

    cage_obj = bpy.data.objects.new(cage_name, cage_mesh)
    cage_obj.matrix_world = target_obj.matrix_world.copy()

    # Link to hidden collection
    cage_collection.objects.link(cage_obj)

    # Parent cage to target object to maintain relative coordinate alignment
    cage_obj.parent = target_obj
    cage_obj.matrix_parent_inverse = target_obj.matrix_world.inverted()

    # Hide cage from normal view
    cage_obj.hide_viewport = True
    cage_obj.hide_render = True
    cage_obj.display_type = 'WIRE'

    return cage_obj


def setup_data_transfer(target_obj, cage_obj, vgroup_name=""):
    """
    Configures Data Transfer modifier on target object to project pristine
    curvature normals from the cage.
    """
    mod_name = "NormalHealer_Transfer"
    dt_mod = target_obj.modifiers.get(mod_name)
    if not dt_mod:
        dt_mod = target_obj.modifiers.new(name=mod_name, type='DATA_TRANSFER')

    dt_mod.object = cage_obj
    dt_mod.use_loop_data = True
    dt_mod.data_types_loops = {'CUSTOM_NORMAL'}
    dt_mod.loop_mapping = 'NEAREST_POLYNOR'
    
    if vgroup_name and vgroup_name in target_obj.vertex_groups:
        dt_mod.vertex_group = vgroup_name

    return dt_mod


def setup_weighted_normal(target_obj):
    """Configures Weighted Normal modifier to flatten planar polygons and enhance bevels."""
    mod_name = "NormalHealer_Weighted"
    wn_mod = target_obj.modifiers.get(mod_name)
    if not wn_mod:
        wn_mod = target_obj.modifiers.new(name=mod_name, type='WEIGHTED_NORMAL')

    wn_mod.keep_sharp = True
    wn_mod.weight = 50
    return wn_mod


def ensure_smooth_shading(target_obj, angle_deg=30.0):
    """
    Ensures smooth shading with auto-smooth angles.
    Maintains compatibility across Blender 3.6, 4.0, 4.1, and 4.2+.
    """
    if target_obj.type != 'MESH':
        return

    # Set all polygons to smooth
    for poly in target_obj.data.polygons:
        poly.use_smooth = True

    # Pre-4.1 auto smooth handling
    if hasattr(target_obj.data, "use_auto_smooth"):
        target_obj.data.use_auto_smooth = True
        target_obj.data.auto_smooth_angle = math.radians(angle_deg)
    else:
        # Blender 4.1+ uses Smooth by Angle modifier
        mod_name = "Smooth by Angle"
        smooth_mod = target_obj.modifiers.get(mod_name)
        if not smooth_mod:
            try:
                # Add Geometry Nodes modifier 'Smooth by Angle' if node group exists
                node_group = bpy.data.node_groups.get("Smooth by Angle")
                if node_group:
                    smooth_mod = target_obj.modifiers.new(name=mod_name, type='NODES')
                    smooth_mod.node_group = node_group
            except Exception:
                pass


def find_existing_cage(target_obj):
    """Finds if a target object already has a connected NormalHealer cage."""
    for mod in target_obj.modifiers:
        if mod.type == 'DATA_TRANSFER' and mod.object:
            if "_NormalCage" in mod.object.name:
                return mod.object
    return None


def clean_object_cage(target_obj):
    """Safely removes cage and associated modifiers."""
    cage = find_existing_cage(target_obj)
    
    # Remove modifiers
    for mod_name in ["NormalHealer_Transfer", "NormalHealer_Weighted"]:
        mod = target_obj.modifiers.get(mod_name)
        if mod:
            target_obj.modifiers.remove(mod)

    # Delete cage object and its mesh datablock
    if cage:
        mesh_data = cage.data
        bpy.data.objects.remove(cage, do_unlink=True)
        if mesh_data and mesh_data.users == 0:
            bpy.data.meshes.remove(mesh_data)

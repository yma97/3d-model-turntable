import bpy
import os
import datetime
from mathutils import Vector

# Function to reset the origin to geometry
def reset_origin_to_geometry(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

# Function to scale and position the object to be fully visible in the default camera view
def fit_object_to_camera(obj):
    cam = bpy.data.objects['Camera']
    bpy.context.view_layer.objects.active = cam

    # Reset camera to its default position
    cam.location = (0, -10, 0)
    cam.rotation_euler = (1.5708, 0, 0)

    # Compute the bounding box center and size
    bbox_center = obj.location
    bbox_size = obj.dimensions

    # Calculate the scale needed to fit the object in the camera view
    max_dim = max(bbox_size)
    scale_factor = 5 / max_dim  # Adjust this factor if needed
    obj.scale = (scale_factor, scale_factor, scale_factor)

    # Adjust the object's location to be centered in the camera view
    obj.location = (0, 0, 0)

# Function to set background color to black
def set_background_color():
    bpy.context.scene.world.use_nodes = True
    bg = bpy.context.scene.world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (0, 0, 0, 1)  # Pure black

# Function to create and position lights
def setup_lights(target_obj):
    scene = bpy.context.scene

    # Create key light
    key_light_data = bpy.data.lights.new(name="KeyLight", type='POINT')
    key_light = bpy.data.objects.new(name="KeyLight", object_data=key_light_data)
    scene.collection.objects.link(key_light)
    key_light.location = (target_obj.location.x, target_obj.location.y + 6, target_obj.location.z + 6)
    key_light.data.energy = 1000

    # Create fill light
    fill_light_data = bpy.data.lights.new(name="FillLight", type='POINT')
    fill_light = bpy.data.objects.new(name="FillLight", object_data=fill_light_data)
    scene.collection.objects.link(fill_light)
    fill_light.location = (target_obj.location.x - 6, target_obj.location.y + 6, target_obj.location.z)
    fill_light.data.energy = 500

    # Create back light
    back_light_data = bpy.data.lights.new(name="BackLight", type='POINT')
    back_light = bpy.data.objects.new(name="BackLight", object_data=back_light_data)
    scene.collection.objects.link(back_light)
    back_light.location = (target_obj.location.x + 6, target_obj.location.y - 6, target_obj.location.z + 6)
    back_light.data.energy = 300

# Set end frame for a 250 frame animation
bpy.context.scene.frame_end = 250

# Find the first non-camera, non-light object
object_to_rotate = None
for obj in bpy.context.scene.objects:
    if obj.type not in {'CAMERA', 'LIGHT'}:
        object_to_rotate = obj
        break

# Check if an object was found
if object_to_rotate:
    # Reset origin to geometry
    reset_origin_to_geometry(object_to_rotate)

    # Fit object to camera view
    fit_object_to_camera(object_to_rotate)

    # Set background color to black
    set_background_color()

    # Setup lights
    setup_lights(object_to_rotate)

    # Create a new empty object at the center of your model for rotation
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=object_to_rotate.location)
    empty = bpy.context.object

    # Parent your model to the empty object
    object_to_rotate.select_set(True)
    empty.select_set(True)
    bpy.context.view_layer.objects.active = empty
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

    # Insert keyframes for rotation
    empty.rotation_euler = (0, 0, 0)
    empty.keyframe_insert(data_path='rotation_euler', frame=1)

    empty.rotation_euler = (0, 0, 6.28319)  # 360 degrees in radians
    empty.keyframe_insert(data_path='rotation_euler', frame=250)

    # Set the interpolation type to linear for smooth rotation
    for fcurve in empty.animation_data.action.fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = 'LINEAR'

    # Set render settings
    bpy.context.scene.render.fps = 24
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    bpy.context.scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    bpy.context.scene.render.image_settings.color_mode = 'RGB'  # Ensure textures are rendered

    # Generate a unique output file name
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    output_path = os.path.join(os.path.expanduser('~'), f'turntable_animation_{timestamp}.mp4')
    bpy.context.scene.render.filepath = output_path

    # Render the animation
    bpy.ops.render.render(animation=True)
else:
    print("No suitable object found to rotate.")


# -*- coding:utf-8 -*-

# #
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110- 1301, USA.
#
# 
# <pep8 compliant>

# ----------------------------------------------------------
# Author: Stephen Leger (s-leger)
#
# ----------------------------------------------------------
bl_info = {
    'name': 'Meshroom camera tracking import (.sfm)',
    'description': 'Import meshroom camera tracking solution (cameras.sfm)',
    'author': 's-leger support@blender-archipack.org',
    'license': 'GPL',
    'deps': '',
    'version': (0, 0, 1),
    'blender': (2, 80, 0),
    'location': 'File > import > Meshroom camera tracking (.sfm)',
    'warning': '',
    'wiki_url': 'https://github.com/s-leger/meshroom_sfm/',
    'tracker_url': 'https://github.com/s-leger/meshroom_sfm/issues/',
    'link': 'https://github.com/s-leger/meshroom_sfm/',
    'support': 'COMMUNITY',
    'category': 'Import-Export'
    }


import bpy
import json
from math import atan
from mathutils import Matrix
from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import (
    ImportHelper,
    axis_conversion,
    orientation_helper
)


def get_transform(transform):
    xx, xy, xz, yx, yy, yz, zx, zy, zz = map(float, transform["rotation"])
    x, y, z = map(float, transform["center"])
    # flip y and z axis
    return Matrix([
        [xx, -xy, -xz, x],
        [yx, -yy, -yz, y],
        [zx, -zy, -zz, z],
        [0, 0, 0, 1]
    ])

def compute_h_fov(intrinsics):
    width = float(intrinsics["width"])
    fdist = float(intrinsics["pxFocalLength"])
    return fdist / width


def sfm_import(self, context, file):
    global_matrix = axis_conversion(from_forward=self.axis_forward,
                                    from_up=self.axis_up,
                                    ).to_4x4()

    helper = bpy.data.objects.new(name="Meshroom sfm origin", object_data=None)
    helper.empty_display_type = "ARROWS"
    helper.empty_display_size = 1
    context.scene.collection.objects.link(helper)

    cam = bpy.data.cameras.new("Camera Meshroom")
    o = bpy.data.objects.new("Camera Meshroom", cam)
    context.scene.collection.objects.link(o)
    o.parent = helper
    o.data.sensor_fit = "HORIZONTAL"
    sensor_width = o.data.sensor_width
    
    with open(file, 'r') as f:
        _j = json.load(f)
        frames = [tuple([int(view["metadata"]["Frame"]), view["poseId"], view["intrinsicId"]]) for view in _j['views']]
        frames.sort(key=lambda x: x[0])
        poses = {pose["poseId"]: pose["pose"] for pose in _j["poses"]}
        h_fovs = {i["intrinsicId"]: compute_h_fov(i) for i in _j["intrinsics"]}

        for frame, poseId, intrinsicId in frames:
            if poseId in poses:
                pose = poses[poseId]
                context.scene.frame_set(frame)
                o.matrix_world = global_matrix @ get_transform(pose["transform"])
                o.data.lens = h_fovs[intrinsicId] * sensor_width
                o.keyframe_insert("location", frame=frame)
                o.keyframe_insert("rotation_euler", frame=frame)
                o.data.keyframe_insert("lens", frame=frame)


@orientation_helper(axis_forward='-Z', axis_up='Y')
class SLEGER_OT_ImportSfm(Operator, ImportHelper):
    bl_idname = "sleger.import_sfm"
    bl_label = "Meshroom camera tracking (.sfm)"
    bl_description = "Meshroom camera tracking importer"

    bl_options = {'PRESET', 'UNDO'}
    filename_ext = ".sfm"

    filter_glob: StringProperty(
        default="cameras.sfm",
        options={'HIDDEN'},
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "axis_forward")
        layout.prop(self, "axis_up")

    def execute(self, context):

        result = {'FINISHED'}
        sfm_import(self, context, self.filepath)

        return result


def menu_func_import(self, context):
    self.layout.operator(SLEGER_OT_ImportSfm.bl_idname)


def register():
    bpy.utils.register_class(SLEGER_OT_ImportSfm)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    import bpy
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.utils.unregister_class(SLEGER_OT_ImportSfm)


if __name__ == "main":
    register()

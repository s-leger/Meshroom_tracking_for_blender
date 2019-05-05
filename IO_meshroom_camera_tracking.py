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
    'location': 'File > import > Meshroom sfm',
    'warning': '',
    'wiki_url': 'https://github.com/s-leger/meshroom_sfm/',
    'tracker_url': 'https://github.com/s-leger/meshroom_sfm/issues/',
    'link': 'https://github.com/s-leger/meshroom_sfm/',
    'support': 'COMMUNITY',
    'category': 'Import-Export'
    }


import bpy
import json
from mathutils import Matrix
from bpy.types import Operator
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper


def get_transform(transform):
    xx, xy, xz, yx, yy, yz, zx, zy, zz = map(float, transform["rotation"])
    x, y, z = map(float, transform["center"])
    return Matrix([
        [xx, yx, zx, x],
        [xy, yy, zy, y],
        [xz, yz, zz, z],
        [0, 0, 0, 1]
    ])


def sfm_import(context, file):
    helper = bpy.data.objects.new(name="Meshroom sfm origin", object_data=None)
    helper.empty_display_type = "ARROWS"
    helper.empty_display_size = 1
    context.scene.collection.objects.link(helper)

    cam = bpy.data.cameras.new("Camera Meshroom")
    o = bpy.data.objects.new("Camera Meshroom", cam)
    context.scene.collection.objects.link(o)

    o.parent = helper

    with open(file, 'r') as f:
        _j = json.load(f)
        frames = [tuple([int(view["metadata"]["Frame"]), view["poseId"]]) for view in _j['views']]
        frames.sort(key=lambda x: x[0])
        poses = {pose["poseId"]: pose["pose"]["transform"] for pose in _j["poses"]}

        for frame, poseId in frames:
            if poseId in poses:
                context.scene.frame_set(frame)
                o.matrix_world = get_transform(poses[poseId])
                o.keyframe_insert("location", frame=frame)
                o.keyframe_insert("rotation_euler", frame=frame)


class SLEGER_OT_ImportSfm(Operator, ImportHelper):
    bl_idname = "sleger.import_sfm"
    bl_label = "Meshroom camera tracking (.sfm)"
    bl_description = "Meshroom camera tracking importer"

    bl_options = {'PRESET'}
    filename_ext = ".sfm"

    filter_glob: StringProperty(
        default="cameras.sfm",
        options={'HIDDEN'},
    )

    def execute(self, context):

        result = {'FINISHED'}
        sfm_import(context, self.filepath)

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
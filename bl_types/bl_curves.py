# ##### BEGIN GPL LICENSE BLOCK #####
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import bpy.types as T

from ..utils import get_preferences
from replication.protocol import ReplicatedDatablock
from .dump_anything import Dumper, Loader, np_load_collection, np_dump_collection, np_dump_attributes
from .bl_material import dump_materials_slots, load_materials_slots
from .bl_datablock import resolve_datablock_from_uuid
from .bl_action import (
    dump_animation_data,
    load_animation_data,
    resolve_animation_dependencies,
)




CURVES_METADATA = [
    'name',
    'curves',
    'normals',
    'point',
    'position_data',
    'selection_domain',
    'surface',
    'surface_collision_distance',
    'surface_uv_map',
    'use_mirror_x',
    'use_mirror_y',
    'use_mirror_z',
    'use_sculpt_collision'
]


class BlCurves(ReplicatedDatablock):
    use_delta = True

    bl_id = "hair_curves"
    bl_class = bpy.types.Curves
    bl_check_common = False
    bl_icon = 'CURVE_DATA'
    bl_reload_parent = False

    @staticmethod
    def construct(data: dict) -> object:
        return bpy.data.hair_curves.new(data["name"])

    @staticmethod
    def load(data: dict, datablock: object):
        load_animation_data(data.get('animation_data'), datablock)

        loader = Loader()
        loader.load(datablock, data)


        # MATERIAL SLOTS
        src_materials = data.get('materials', None)
        if src_materials:
            load_materials_slots(src_materials, datablock.materials)

    @staticmethod
    def dump(datablock: object) -> dict:
        dumper = Dumper()
        # Conflicting attributes
        dumper.include_filter = CURVE_METADATA

        dumper = Dumper()
        dumper.include_filter = CURVES_METADATA
        dumper.depth = 2
        data['attributes'] = np_dump_attributes(datablock.attributes)
        data['color_attributes'] = np_dump_attributes(datablock.color_attributes)
        data['materials'] = dump_materials_slots(datablock.materials)

        return data

    @staticmethod
    def resolve(data: dict) -> object:
        uuid = data.get('uuid')
        return resolve_datablock_from_uuid(uuid, bpy.data.curves)

    @staticmethod
    def resolve_deps(datablock: object) -> [object]:
        deps = []
        curve = datablock


        for material in datablock.materials:
            if material:
                deps.append(material)

        deps.extend(resolve_animation_dependencies(datablock))

        return deps

    @staticmethod
    def needs_update(datablock: object, data: dict) -> bool:
        return 'EDIT' not in bpy.context.mode \
            or get_preferences().sync_flags.sync_during_editmode


_type = [bpy.types.Curves]
_class = BlCurves

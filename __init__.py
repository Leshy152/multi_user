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


import logging

import bpy

from . import presence
from . import operators
from . import handlers
from . import ui
from . import icons
from . import preferences


def _register_props():
    bpy.types.WindowManager.session = bpy.props.PointerProperty(
        type=preferences.SessionProps
    )
    bpy.types.ID.uuid = bpy.props.StringProperty(
        default="", options={"HIDDEN", "SKIP_SAVE"}
    )
    bpy.types.WindowManager.online_users = bpy.props.CollectionProperty(
        type=preferences.SessionUser
    )
    bpy.types.WindowManager.user_index = bpy.props.IntProperty()
    bpy.types.WindowManager.server_index = bpy.props.IntProperty()


def _unregister_props():
    for attr in ("session", "online_users", "user_index", "server_index"):
        if hasattr(bpy.types.WindowManager, attr):
            try:
                delattr(bpy.types.WindowManager, attr)
            except Exception:
                pass
    if hasattr(bpy.types.ID, "uuid"):
        try:
            del bpy.types.ID.uuid
        except Exception:
            pass


def register():
    # Setup logging policy
    logging.basicConfig(
        format="%(asctime)s CLIENT %(levelname)-8s %(message)s",
        datefmt="%H:%M:%S",
        level=logging.INFO,
    )

    # Clean up any leftover state from a previous registration
    _unregister_props()

    preferences.register()
    presence.register()
    operators.register()
    handlers.register()
    ui.register()
    icons.register()

    _register_props()

    bpy.types.TOPBAR_MT_file_import.append(operators.menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(operators.menu_func_export)


def unregister():
    if operators.menu_func_import in bpy.types.TOPBAR_MT_file_import._dyn_ui_initialize():
        bpy.types.TOPBAR_MT_file_import.remove(operators.menu_func_import)
    if operators.menu_func_export in bpy.types.TOPBAR_MT_file_export._dyn_ui_initialize():
        bpy.types.TOPBAR_MT_file_export.remove(operators.menu_func_export)

    presence.unregister()
    ui.unregister()
    icons.unregister()
    handlers.unregister()
    operators.unregister()
    preferences.unregister()

    _unregister_props()

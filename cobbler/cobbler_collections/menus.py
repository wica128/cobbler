"""
Copyright 2021 Yuriy Chelpanov
Yuriy Chelpanov <yuriy.chelpanov@gmail.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301  USA
"""

from cobbler.items import menu
from cobbler.cobbler_collections import collection
from cobbler import utils
from cobbler.cexceptions import CX


class Menus(collection.Collection):
    """
    A menu represents an element of the hierarchical boot menu.
    """

    @staticmethod
    def collection_type() -> str:
        return "menu"

    @staticmethod
    def collection_types() -> str:
        return "menus"

    def factory_produce(self, collection_mgr, item_dict):
        """
        Return a Menu forged from item_dict

        :param collection_mgr: TODO
        :param item_dict: TODO
        :return:
        """
        new_menu = menu.Menu(collection_mgr)
        new_menu.from_dict(item_dict)
        return new_menu

    def remove(self, name: str, with_delete: bool = True, with_sync: bool = True, with_triggers: bool = True,
               recursive: bool = False):
        """
        Remove element named 'name' from the collection

        :param name: The name of the menu
        :param with_delete: TODO
        :param with_sync: TODO
        :param with_triggers: TODO
        :param recursive: TODO
        """
        name = name.lower()
        for profile in self.collection_mgr.profiles():
            if profile.menu and profile.menu.lower() == name:
                profile.set_menu(None)
        for image in self.collection_mgr.images():
            if image.menu and image.menu.lower() == name:
                image.set_menu(None)

        obj = self.find(name=name)
        if obj is not None:
            if recursive:
                kids = obj.get_children()
                for k in kids:
                    self.remove(k.name, with_delete=with_delete, with_sync=False, recursive=recursive)

            if with_delete:
                if with_triggers:
                    utils.run_triggers(self.collection_mgr.api, obj, "/var/lib/cobbler/triggers/delete/menu/pre/*", [])
            self.lock.acquire()
            try:
                del self.listing[name]
            finally:
                self.lock.release()
            self.collection_mgr.serialize_delete(self, obj)
            if with_delete:
                if with_triggers:
                    utils.run_triggers(self.collection_mgr.api, obj, "/var/lib/cobbler/triggers/delete/menu/post/*", [])
                    utils.run_triggers(self.collection_mgr.api, obj, "/var/lib/cobbler/triggers/change/*", [])
                if with_sync:
                    lite_sync = self.collection_mgr.api.get_sync()
                    lite_sync.remove_single_menu()
            return
        raise CX("cannot delete an object that does not exist: %s" % name)

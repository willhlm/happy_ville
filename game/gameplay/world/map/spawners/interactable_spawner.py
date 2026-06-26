from . import common as c


class InteractableSpawner(c.SpawnerCommon):
    def load_interactables(self, data, parallax, offset, map_def: c.MapDefinition, layer_name: str, viewport_center):
        loot_container_index = 1
        soul_essence_index = 1
        biome_room_name = self.game_objects.map.biome_room_name

        for obj in data["objects"]:
            object_position, object_size = c.calculate_object_position(obj, parallax, offset, viewport_center)
            properties = obj.get("properties", [])

            source, _, local_id = c.resolve_tileset(map_def, obj["gid"])
            if "interactables" not in source:
                continue

            if local_id == 2:
                self.game_objects.interactables.add(c.SavePoint(object_position, self.game_objects, biome_room_name))

            elif local_id == 3:
                runestone_id = next(property["value"] for property in properties if property["name"] == "ID")
                state = self.game_objects.world_state.objects.get_bucket(biome_room_name, "runestone").get(runestone_id, False)
                self.game_objects.interactables.add(c.Runestones(object_position, self.game_objects, state, runestone_id))

            elif local_id == 4:
                state = self.game_objects.world_state.objects.get_bucket(biome_room_name, "loot_container").get(str(loot_container_index), False)
                self.game_objects.interactables.add(c.Chest(object_position, self.game_objects, state, str(loot_container_index)))
                loot_container_index += 1

            elif local_id == 5:
                is_on = next((property["value"] for property in properties if property["name"] == "on"), False)
                self.game_objects.interactables.add(c.Fireplace(object_position, self.game_objects, is_on))

            elif local_id == 6:
                values = {}
                for property in properties:
                    if property["name"] in ("left", "up", "right", "down"):
                        values[property["name"]] = property["value"]
                self.game_objects.interactables.add(c.Sign(object_position, self.game_objects, values))

            elif local_id == 7:
                self.game_objects.interactables.add(c.FastTravel(object_position, self.game_objects, biome_room_name))

            elif local_id == 8:
                self.game_objects.interactables.add(c.Inorinoki(object_position, self.game_objects))

            elif local_id == 9:
                self.game_objects.interactables.add(c.UberRunestone(object_position, self.game_objects))

            elif local_id == 10:
                obj_props = c.props_list_to_dict(obj.get("properties", []))
                self.game_objects.interactables.add(c.Lever(object_position, self.game_objects, **obj_props))

            elif local_id == 11:
                obj_props = c.props_list_to_dict(obj.get("properties", []))
                self.game_objects.platforms.add(c.GatePlatform(object_position, self.game_objects, **obj_props))

            elif local_id == 12:
                statue_id = next(property["value"] for property in properties if property["name"] == "ID")
                self.game_objects.interactables.add(c.QuestStatue(object_position, self.game_objects, statue_id))

            elif local_id == 13:
                if not self.game_objects.world_state.objects.get_bucket(biome_room_name, "soul_essence").get(soul_essence_index, False):
                    self.game_objects.loot.add(c.SoulEssence(object_position, self.game_objects, soul_essence_index))
                soul_essence_index += 1

            elif local_id == 14:
                obj_props = c.props_list_to_dict(obj.get("properties", []))
                if not self.game_objects.world_state.objects.get_bucket(biome_room_name, "interactable_items").get(obj_props["interactable_item"], False):
                    item = self.game_objects.registry.fetch("items", obj_props["interactable_item"])(object_position, self.game_objects, **obj_props)
                    self.game_objects.loot.add(item)

            elif local_id == 15:
                obj_props = c.props_list_to_dict(obj.get("properties", []))
                self.game_objects.platforms.add(c.GatePlatformAlt(object_position, self.game_objects, **obj_props))

            elif local_id == 16:
                self.game_objects.interactables.add(c.AirDashUpgradeStatue(object_position, self.game_objects))

            elif local_id == 17:
                self.game_objects.interactables.add(c.EnemyWeb(object_position, self.game_objects, **c.props_list_to_dict(properties)))

            elif local_id == 18:
                state = self.game_objects.world_state.objects.get_bucket(biome_room_name, "loot_container").get(str(loot_container_index), False)
                self.game_objects.interactables.add(c.AmberBush(object_position, self.game_objects, state, str(loot_container_index)))
                loot_container_index += 1

            elif local_id == 19:
                state = self.game_objects.world_state.objects.get_bucket(biome_room_name, "loot_container").get(str(loot_container_index), False)
                self.game_objects.interactables.add(c.AmberBushSmall(object_position, self.game_objects, state, str(loot_container_index)))
                loot_container_index += 1

            elif local_id == 20:
                state = self.game_objects.world_state.objects.get_bucket(biome_room_name, "loot_container").get(str(loot_container_index), False)
                self.game_objects.interactables.add(c.AmberBushBreak(object_position, self.game_objects, state, str(loot_container_index)))
                loot_container_index += 1


            elif local_id == 190:
                self.game_objects.platforms.add(c.BreakableBlockCharge_1(object_position, self.game_objects))

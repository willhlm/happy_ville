from . import common as c


class StaticSpawner(c.SpawnerCommon):
    def load_statics(self, data, parallax, offset, ctx: c.LoadContext, map_def: c.MapDefinition, layer_name: str, viewport_center):
        for obj in data["objects"]:
            object_position, object_size = c.calculate_object_position(obj, parallax, offset, viewport_center)
            properties = obj.get("properties", [])

            if "polygon" in obj.keys():
                points_list = [(point["x"], point["y"]) for point in obj["polygon"]]
                new_block = c.CollisionRightAngle(object_position, points_list, obj.get("properties", True))
                self.game_objects.platforms.add(new_block)
                continue

            source, _, local_id = c.resolve_tileset(map_def, obj["gid"])
            if "static" not in source:
                continue

            if local_id == 0:
                if ctx.spawned:
                    continue
                for property in properties:
                    if property["name"] != "spawn":
                        continue
                    if isinstance(ctx.spawn, str):
                        if property["value"] != ctx.spawn:
                            continue
                        self.game_objects.player.body.set_pos(object_position)
                    else:
                        self.game_objects.player.body.set_pos(ctx.spawn)

                    self.game_objects.player.reset_movement()
                    ctx.spawned = True
                    for prop in properties:
                        if prop["name"] == "right":
                            self.game_objects.player.dir[0] = 1
                            self.game_objects.player.acceleration[0] = c.C.acceleration[0]
                        elif prop["name"] == "left":
                            self.game_objects.player.dir[0] = -1
                            self.game_objects.player.acceleration[0] = c.C.acceleration[0]
                        if prop["name"] == "up":
                            self.game_objects.player.velocity[1] = c.C.jump_vel_player
                    break

            elif local_id == 1:
                npc_name = next(property["value"] for property in properties if property["name"] == "class")
                self.game_objects.npcs.add(self.game_objects.registry.fetch("npcs", npc_name)(object_position, self.game_objects))

            elif local_id == 2:
                enemy_props = c.props_list_to_dict(properties)
                enemy_name = enemy_props.pop("class")
                enemy_cls = self.game_objects.registry.fetch("enemies", enemy_name)
                self.game_objects.enemies.add(enemy_cls(object_position, self.game_objects, **enemy_props))

            elif local_id == 3:
                path_props = c.props_list_to_dict(obj.get("properties", []))
                if not self.game_objects.world_state.narrative.is_boss_defeated(path_props["ID"]):
                    aggro = self.game_objects.world_state.narrative.is_flow_complete(path_props["ID"])
                    boss = self.game_objects.registry.fetch("enemies", path_props["class"])(object_position, self.game_objects, path_props["ID"])
                    self.game_objects.enemies.add(boss)
                    ctx.references[path_props["ID"]] = boss
                    if aggro:
                        boss.start_aggro()

            elif local_id == 5:
                kwargs = {}
                loot = None
                for property in properties:
                    if property["name"] == "item":
                        loot = property["value"]
                    elif property["name"] == "quest":
                        kwargs["quest"] = property["value"]
                self.game_objects.loot.add(self.game_objects.registry.fetch("items", loot)(object_position, self.game_objects))

            elif local_id == 7:
                particle_type = next((property["value"] for property in properties if property["name"] == "particles"), "dust")
                self.game_objects.platforms.add(c.SolidPlatform(object_position, size=object_size, run_particle=particle_type))

            elif local_id == 8:
                self.game_objects.platforms.add(c.HazardPlatform(object_position, size=object_size, damage=1, knockback_x=10, knockback_y=10))

            elif local_id == 9:
                destination = spawn = None
                for property in properties:
                    if property["name"] == "path_to":
                        destination = property["value"]
                    elif property["name"] == "spawn":
                        spawn = property["value"]
                self.game_objects.interactables.add(c.PathInteract(object_position, self.game_objects, object_size, destination, spawn))

            elif local_id == 10:
                destination = spawn = None
                for property in properties:
                    if property["name"] == "path_to":
                        destination = property["value"]
                    elif property["name"] == "spawn":
                        spawn = property["value"]
                self.game_objects.interactables.add(c.PathCollision(object_position, self.game_objects, object_size, destination, spawn))

            elif local_id == 11:
                particle_type = next((property["value"] for property in properties if property["name"] == "particles"), "dust")
                self.game_objects.platforms.add(c.OneWayUpPlatform(object_position, size=object_size, run_particle=particle_type))

            elif local_id == 12:
                self.game_objects.interactables.add(c.Hole(object_position, self.game_objects, object_size))

            elif local_id == 13:
                spawn_position = [object_position[0] + object_size[0] * 0.5, object_position[1] + object_size[1] * 0.5]
                for property in properties:
                    if property["name"] == "position":
                        spawn_position = [int(item) for item in property["value"].split(",")]
                self.game_objects.interactables.add(c.SafeSpawn(object_position, self.game_objects, object_size, spawn_position))

            elif local_id == 14:
                mode = "center"
                camera_offset = 0
                priority = 0
                for property in properties:
                    if property["name"] in ("direction", "mode"):
                        mode = property["value"]
                    elif property["name"] == "offset":
                        camera_offset = property["value"]
                    elif property["name"] == "priority":
                        priority = property["value"]
                self.game_objects.camera_blocks.add(c.Stop(self.game_objects, object_size, object_position, mode, camera_offset, priority))

            elif local_id == 16:
                kwargs = {}
                for property in properties:
                    if property["name"] == "ID":
                        kwargs["ID"] = property["value"]
                    elif property["name"] == "erect":
                        kwargs["erect"] = property["value"]
                    elif property["name"] == "vertical":
                        kwargs["vertical"] = property["value"]
                self.game_objects.platforms.add(c.EvilGatePlatform(object_position, self.game_objects, object_size, **kwargs))

            elif local_id == 18:
                kwargs = {}
                for property in properties:
                    if property["name"] == "angle":
                        kwargs["angle"] = 3.141592 * float(property["value"]) / 180
                    elif property["name"] == "falloff":
                        falloff = property["value"].split(",")
                        kwargs["falloff"] = [float(falloff[0]), float(falloff[1])]
                    elif property["name"] == "position":
                        position = property["value"].split(",")
                        kwargs["position"] = [float(position[0]), float(position[1])]
                    elif property["name"] == "colour":
                        colour = list(c.pygame.Color(property["value"]))
                        kwargs["colour"] = [colour[1] / 255, colour[2] / 255, colour[3] / 255, colour[0] / 255]
                god_rays = c.GodRays(object_position, self.game_objects, parallax, object_size, **kwargs)
                target_groups = self.game_objects.all_fgs if layer_name.startswith("fg") else self.game_objects.all_bgs
                target_groups.add(layer_name, god_rays)

            elif local_id == 19:
                kwargs = c.props_list_to_dict(properties)
                trigger_factory = self.game_objects.registry.fetch("event_triggers", kwargs["trigger"])
                trigger_cls = trigger_factory or self.game_objects.registry.fetch("event_triggers", "default")
                completion_key = trigger_cls.get_completion_key(kwargs)
                if getattr(trigger_cls, "blocks_on_flow_complete", False) and self.game_objects.world_state.narrative.is_flow_complete(completion_key):
                    continue
                if getattr(trigger_cls, "blocks_on_event_complete", False) and self.game_objects.world_state.narrative.is_event_complete(kwargs["trigger"]):
                    continue
                self.game_objects.interactables.add(trigger_cls(object_position, self.game_objects, object_size, **kwargs))

            elif local_id == 20:
                kwargs = {}
                for property in properties:
                    if property["name"] == "offset":
                        kwargs["offset"] = property["value"]
                    elif property["name"] == "speed":
                        kwargs["speed"] = property["value"]
                    elif property["name"] == "texture_parallax":
                        kwargs["texture_parallax"] = property["value"]
                    elif property["name"] == "water_texture_on":
                        kwargs["water_texture_on"] = property["value"]
                reflection = c.River(object_position, self.game_objects, parallax, object_size, layer_name, **kwargs)
                target_groups = self.game_objects.all_fgs if layer_name.startswith("fg") else self.game_objects.all_bgs
                target_groups.add(layer_name, reflection)

            elif local_id == 21:
                kwargs = {}
                for property in properties:
                    if property["name"] == "center":
                        kwargs["center"] = [float(item) for item in property["value"].split(",")]
                    elif property["name"] == "rate":
                        kwargs["rate"] = float(property["value"])
                    elif property["name"] == "scale":
                        kwargs["scale"] = float(property["value"])
                self.game_objects.interactables.add(c.ZoomCollision(object_position, self.game_objects, object_size, **kwargs))

            elif local_id == 22:
                c.AreaSpawner(object_position, self.game_objects, object_size, **c.props_list_to_dict(properties))

            elif local_id == 23:
                kwargs = {}
                for property in properties:
                    if property["name"] == "colour":
                        colour = list(c.pygame.Color(property["value"]))
                        kwargs["colour"] = [colour[1] / 255, colour[2] / 255, colour[3] / 255, colour[0] / 255]
                    elif property["name"] == "layers":
                        kwargs["layers"] = [layer.strip() for layer in property["value"].split(",")]
                    elif property["name"] == "scale":
                        kwargs["scale"] = property["value"]
                    elif property["name"] == "shader":
                        kwargs["shader"] = property["value"]
                self.game_objects.interactables.add(c.LayerTrigger(object_position, self.game_objects, object_size, **kwargs))

            elif local_id == 24:
                self.game_objects.cosmetics.add(c.DeathFog(object_position, self.game_objects, object_size))

            elif local_id == 25:
                kwargs = {"parallax": parallax}
                behaviours = []
                for property in properties:
                    if property["name"] == "radius":
                        kwargs["radius"] = float(property["value"])
                    elif property["name"] == "interact":
                        kwargs["normal_interact"] = property["value"]
                    elif property["name"] == "colour":
                        colour = list(c.pygame.Color(property["value"]))
                        kwargs["colour"] = [colour[1], colour[2], colour[3], colour[0]]
                    elif property["name"] == "flicker":
                        if property["value"]:
                            behaviours.append("flicker")
                    elif property["name"] == "fade":
                        if property["value"]:
                            behaviours.append({"type": "fade", "rate": 0.99})
                    elif property["name"] == "pulsting":
                        if property["value"]:
                            behaviours.append("pulsating")

                light_source = c.LightSource(object_position, self.game_objects, parallax, layer_name)
                self.game_objects.lights.create(light_source, components=behaviours, **kwargs)
                target_groups = self.game_objects.all_fgs if layer_name.startswith("fg") else self.game_objects.all_bgs
                target_groups.add(layer_name, light_source)

            elif local_id == 26:
                kwargs = {}
                for property in properties:
                    if property["name"] in ("water_tint", "darker_color", "line_color"):
                        colour = list(c.pygame.Color(property["value"]))
                        kwargs[property["name"]] = [colour[1] / 255, colour[2] / 255, colour[3] / 255, colour[0] / 255]
                self.game_objects.interactables_fg.add(c.TwoDLiquid(object_position, self.game_objects, object_size, layer_name, **kwargs))

            elif local_id == 27:
                sky = c.Sky(object_position, self.game_objects, parallax, object_size)
                target_groups = self.game_objects.all_fgs if layer_name.startswith("fg") else self.game_objects.all_bgs
                target_groups.add(layer_name, sky)

            elif local_id == 28:
                self.game_objects.cosmetics.add(c.ShadowLight_1(object_position, self.game_objects, object_size))

            elif local_id == 31:
                self.game_objects.all_bgs.add(layer_name, c.Rainbow(object_position, self.game_objects, object_size, parallax))

            elif local_id == 32:
                kwargs = {}
                for property in properties:
                    if property["name"] == "colour":
                        colour = list(c.pygame.Color(property["value"]))
                        kwargs["colour"] = [colour[1] / 255, colour[2] / 255, colour[3] / 255, colour[0] / 255]
                    elif property["name"] == "spawn_rate":
                        kwargs["spawn_rate"] = property["value"]
                    elif property["name"] == "radius":
                        kwargs["radius"] = property["value"]
                    elif property["name"] == "speed":
                        kwargs["speed"] = property["value"]
                    elif property["name"] == "horizontalSpread":
                        kwargs["horizontalSpread"] = property["value"]
                    elif property["name"] == "lifetime":
                        kwargs["lifetime"] = property["value"]
                    elif property["name"] == "spawn_position" and property["value"]:
                        kwargs["spawn_position"] = [float(item) for item in property["value"].strip("()").split(",")]
                self.game_objects.cosmetics.add(c.Smoke(object_position, self.game_objects, object_size, **kwargs))

            elif local_id == 33:
                vertical = horizontal = 0
                for property in properties:
                    if property["name"] == "up":
                        vertical -= int(property["value"])
                    elif property["name"] == "down":
                        vertical += int(property["value"])
                    elif property["name"] == "left":
                        horizontal -= int(property["value"])
                    elif property["name"] == "right":
                        horizontal += int(property["value"])
                self.game_objects.interactables_fg.add(c.UpStream(object_position, self.game_objects, object_size, vertical=vertical, horizontal=horizontal))

            elif local_id == 34:
                waterfall = c.Waterfall(object_position, self.game_objects, parallax, object_size, layer_name)
                target_groups = self.game_objects.all_fgs if layer_name.startswith("fg") else self.game_objects.all_bgs
                target_groups.add(layer_name, waterfall)

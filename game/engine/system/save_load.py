from gameplay.entities import entities
from engine.utils import read_files

class Save_load():
    def __init__(self, game_objects):
        self.game_objects = game_objects
        self.save_dict = {}

    def save(self):
        self.save_player()#organise things to save in to a dictionary
        self.save_world_state()#organise things to save in to a dictionary
        read_files.save_json(self.save_dict,'save')#name of the file, save one dict

    def load(self):
        data = read_files.load_json('save')#name of the file
        self.load_world_state(data)
        self.load_player(data)

    def save_world_state(self):
        world_state = self.game_objects.world_state
        world_state_dict = {'cutscenes_complete':world_state.cutscenes_complete,'statisics':world_state.statisics}
        self.save_dict['world_state'] = world_state_dict

    def save_player(self):
        player = self.game_objects.player
        health = {'max_health':player.max_health,'max_spirit':player.max_spirit,'health':player.health,'spirit':player.spirit}

        abilities = []
        for key in player.abilities.keys():
            abilities.append(key)

        player_dict = {'spawn_point':player.spawn_point,'inventory':player.inventory,'health':health,'abilities':abilities,'states':player.states}
        self.save_dict['player'] = player_dict

    def load_world_state(self,data):
        self.game_objects.world_state.cutscenes_complete = data['world_state']['cutscenes_complete']
        self.game_objects.world_state.statisics = data['world_state']['statisics']

    def load_player(self,data):
        player_data = data['player']
        self.game_objects.player.max_health=player_data['health']['max_health']
        self.game_objects.player.max_spirit=player_data['health']['max_spirit']
        self.game_objects.player.health=player_data['health']['health']
        self.game_objects.player.spirit=player_data['health']['spirit']

        self.game_objects.player.states = player_data['states']
        self.game_objects.player.inventory = player_data['inventory']

        self.game_objects.player.abilities={}
        for ability in player_data['abilities']:
                self.game_objects.player.abilities[ability] = getattr(entities, ability)

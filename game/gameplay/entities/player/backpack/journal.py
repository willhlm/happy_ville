class Journal:
    def __init__(self):
        self.kills = []

    def update_kill(self, enemy):#called when an enemy is killed
        self.kills.append(enemy)

#game settings
fps = 60
window_size = [480*1.35,270*1.35]
player_center = [window_size[0]*0.5,window_size[1]*0.5]
tile_size = 16

#physics
acceleration = [1,0.51]#y velocity need to be large than 1/2
friction = [0.5,0]
friction_player = [0.24,0.01]
max_vel = [30,7]
jump_time_player = 9#how long one goes vertically while pressing the jump button

#combat
invincibility_time_player = 50
invincibility_time_enemy = 20
sword_time_player = 15#how long one has to wait before can swing the sword again
hurt_animation_length = 15#how long enteties turn white upon dmg

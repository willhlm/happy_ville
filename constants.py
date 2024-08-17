#game settings
fps = 60#this is the screeen resfresh rate
window_size = [640, 360]
#window_size = [int(640*1.2), int(360*1.2)]
tile_size = 16

#physics
acceleration = [0.8,0.32]
friction = [0.5,0]#need to be less than 1
friction_player = [0.24,0.01]
jump_vel_player = -6
max_vel = [30,5.2]#[30,6]
jump_buffer_timer_player = 4##how many frames from falling in which the player can jump when landing
shroomjump_timer_player = 3#how many frames the player can press jump, after landing on a shroompolin, and do shroomjump
cayote_timer_player = 10#how many frames from falling in which the player can still jump
animation_framerate = 0.25#1/animation_framerate is the number of frames to blit before goging to next frame
air_timer = 7#for how long one can press A and keep jumping
dash_length = 7#how long  Aila dashes
dash_vel = 8
wall_timer = 3#how many frams from droping from wall you can still jump
wall_timer_2 = 7#how many frams from jumping till one change change the direction from wall you can still jump
pogo_vel = -6

#combat
invincibility_time_player = 50
invincibility_time_enemy = 20
sword_time_player = 25#how long one has to wait before can swing the sword again
hurt_animation_length = 15#how long enteties turn white upon dmg

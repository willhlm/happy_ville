#game settings
fps = 50
window_size = [576,324]
player_center = [window_size[0]*0.5,window_size[1]*0.5]
tile_size = 16

#physics
acceleration = [1,0.5]
friction = [0.5,0]#need to be less than 1
friction_player = [0.24,0.01]
max_vel = [30,7]
jump_time_player = 3##how many frames from falling in which the player can jump when landing
shroomjump_timer_player = 3#how many frames the player can press jump, after landing on a shroompolin, and do shroomjump
ground_timer_player = 3#how many frames from falling in which the player can still jump
animation_framerate = 0.25#1/animation_framerate is the number of frames to blit before goging to next frame

#combat
invincibility_time_player = 50
invincibility_time_enemy = 20
sword_time_player = 15#how long one has to wait before can swing the sword again
hurt_animation_length = 15#how long enteties turn white upon dmg

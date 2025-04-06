#game settings
fps = 60#this is the screeen resfresh rate
window_size = [640, 360]#[int(640*1.2), int(360*1.2)]
tile_size = 16

#physics
acceleration = [0.75,0.32]
friction = [0.5,0]#need to be less than 1
friction_player = [0.24,0.01]
jump_vel_player = -5
dash_jump_vel_player = -6.4
max_vel = [30,5]#[30,6]
pogo_vel = -6
dash_length = 7#how long  Aila dashes
dash_vel = 8
animation_framerate = 0.25#1/animation_framerate is the number of frames to blit before goging to next frame

#timers
jump_dash_wall_timer = 4#how many frames it should take before going into wall when doing dash jump
jump_dash_timer = 3#how many frames from pressing jump/dash to pressing dash/jump one can do dash jump
cayote_timer_player = 10#how many frames from falling in which the player can still jump
air_timer = 12#for how long one can press A and keep jumping

#input buffers
shroomjump_timer_player = 3#how many frames the player can press jump, after landing on a shroompolin, and do shroomjump
#jump_buffer_timer_player = 4##how many frames from falling in which the player can jump when landing

#combat
invincibility_time_player = 50
invincibility_time_enemy = 20
sword_time_player = 25#how long one has to wait before can swing the sword again
hurt_animation_length = 15#how long enteties turn white upon dmg

#colour
spirit_colour = [255*0.39, 255*0.78, 255, 255]
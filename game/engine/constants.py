#game settings
fps = 60#this is the screeen resfresh rate
window_size = [640, 360]#[int(640*1.2), int(360*1.2)]
tile_size = 16

#physics
acceleration = [0.72,0.32]
friction = [0.5,0]#need to be less than 1
friction_player = [0.24,0.01]
jump_vel_player = -5.5
max_vel = [30,7]#[30,6]
pogo_vel = -7
dash_length = 5#how long  Aila dashes
dash_jump_length = 8
dash_vel = 3
dash_jump_vel = -3.25
sprint_multiplier = 1.7
animation_framerate = 0.25#1/animation_framerate is the number of frames to blit before goging to next frame

#timers
jump_dash_wall_timer = 4#how many frames it should take before going into wall when doing dash jump
jump_dash_timer = 3#how many frames from pressing jump/dash to pressing dash/jump one can do dash jump
ground_dash_timer = 40 #cooldown frames between dash
cayote_timer_player = 4#how many frames from falling in which the player can still jump
air_timer = 14#for how long one can press A and keep jumping

#input buffers
shroomjump_timer_player = 3#how many frames the player can press jump, after landing on a shroompolin, and do shroomjump

#combat
invincibility_time_player = 50
invincibility_time_enemy = 20
sword_time_player = 25#how long one has to wait before can swing the sword again
hurt_animation_length = 15#how long enteties turn white upon dmg
default_enemydmg_hitstop = 7
down_angle = 0.45

#colour
spirit_colour = [255*0.39, 255*0.78, 255, 255]

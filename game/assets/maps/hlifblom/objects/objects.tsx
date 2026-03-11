<?xml version="1.0" encoding="UTF-8"?>
<tileset version="1.8" tiledversion="1.8.2" name="objects" tilewidth="80" tileheight="112" tilecount="8" columns="0">
 <grid orientation="orthogonal" width="1" height="1"/>
 <tile id="0">
  <image width="80" height="64" source="../../../sprites/entities/interactables/grass/hlifblom/cave_grass/idle/idle01.png"/>
 </tile>
 <tile id="1">
  <image width="32" height="32" source="../../../sprites/entities/visuals/environments/ljusmaskar/idle/ljusmaskar01.png"/>
 </tile>
 <tile id="2">
  <image width="32" height="32" source="../../../sprites/entities/interactables/sources/droplet/idle/source1.png"/>
 </tile>
 <tile id="3">
  <image width="16" height="48" source="../../../sprites/entities/interactables/sources/falling_rock/idle/idle.png"/>
 </tile>
 <tile id="4">
  <image width="32" height="112" source="../../../sprites/entities/visuals/environments/vines/vines_2/idle/idle.png"/>
 </tile>
 <tile id="5">
  <properties>
   <property name="cos_amp_scaler" type="float" value="0"/>
   <property name="init_delay" type="int" value="0"/>
   <property name="lifetime" type="int" value="0"/>
   <property name="spawnrate" type="int" value="0"/>
   <property name="state" value=""/>
  </properties>
  <image width="32" height="32" source="../../../sprites/entities/interactables/sources/bubble/idle/idle.png"/>
 </tile>
 <tile id="6">
  <image width="16" height="16" source="../../../sprites/entities/interactables/traps/spikes/idle/spikes1.png"/>
 </tile>
 <tile id="7">
  <properties>
   <property name="disappear_on_stand" type="bool" value="true"/>
   <property name="disappear_time" value=""/>
   <property name="respawn_time" value=""/>
   <property name="sprite_path" value="bubble"/>
  </properties>
  <image width="32" height="32" source="../../../sprites/entities/platforms/bubble/idle/idle.png"/>
 </tile>
</tileset>

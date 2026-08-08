<?xml version="1.0" encoding="UTF-8"?>
<tileset version="1.8" tiledversion="1.8.2" name="objects" tilewidth="224" tileheight="160" tilecount="5" columns="0">
 <grid orientation="orthogonal" width="1" height="1"/>
 <tile id="2">
  <image width="224" height="48" source="../../../sprites/entities/platforms/bridge/erect/bridge.png"/>
 </tile>
 <tile id="3">
  <image width="32" height="32" source="../../../sprites/entities/interactables/sources/droplet/idle/source1.png"/>
 </tile>
 <tile id="4">
  <properties>
   <property name="id" value=""/>
   <property name="initial_state" value="idle"/>
  </properties>
  <image width="160" height="160" source="../../../sprites/entities/visuals/environments/windmill/idle/idle.png"/>
 </tile>
 <tile id="5">
  <properties>
   <property name="id" value=""/>
   <property name="item_id" value="gear"/>
   <property name="target_level" value=""/>
   <property name="target_state" value="active"/>
   <property name="target_state_group" value="windmill"/>
  </properties>
  <image width="32" height="32" source="../../../sprites/entities/interactables/gear_box/idle/gearbox.png"/>
 </tile>
 <tile id="6">
  <properties>
   <property name="id" value=""/>
   <property name="target_level" value=""/>
   <property name="target_state" value="active"/>
   <property name="target_state_group" value="windmill"/>
  </properties>
  <image width="32" height="32" source="../../../sprites/entities/interactables/valve/idle/gearbox.png"/>
 </tile>
</tileset>

<?xml version="1.0" encoding="UTF-8"?>
<tileset version="1.8" tiledversion="1.8.2" name="objects" tilewidth="320" tileheight="320" tilecount="9" columns="0">
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
 <tile id="7">
  <properties>
   <property name="wind_network" value="golden_fields_liquid"/>
  </properties>
  <image width="32" height="32" source="../../../sprites/entities/platforms/piston/idle/rhoutta_encounter1.png"/>
 </tile>
 <tile id="8">
  <properties>
   <property name="blade_count" value="4"/>
   <property name="radius" value="56"/>
   <property name="rotation_phase" value="0"/>
   <property name="rotation_speed" value="2.5"/>
   <property name="wind_network" value="golden_fields_liquid"/>
  </properties>
  <image width="320" height="320" source="../../../sprites/entities/visuals/environments/blade_rig/idle/idle.png"/>
 </tile>
 <tile id="9">
  <properties>
   <property name="control_mode" value="map_transition"/>
   <property name="destination_continue_to" value=""/>
   <property name="destination_lift_id" value=""/>
   <property name="destination_map" value=""/>
   <property name="destination_station" type="int" value="0"/>
   <property name="lever_offset" value=""/>
   <property name="lift_id" value=""/>
   <property name="path" type="object" value="0"/>
   <property name="signal_id" value=""/>
   <property name="transition_direction" value=""/>
   <property name="transition_station" value=""/>
  </properties>
  <image width="144" height="64" source="../../../sprites/entities/platforms/liftcar/body/idle/rhoutta_encounter1.png"/>
 </tile>
 <tile id="10">
  <properties>
   <property name="boarding_offset" value=""/>
   <property name="boarding_size" value=""/>
   <property name="control_mode" value="signal"/>
   <property name="initial_station" value=""/>
   <property name="lever_offset" value=""/>
   <property name="lift_stations" value=""/>
   <property name="path" type="object" value="0"/>
   <property name="signal_id" value=""/>
  </properties>
  <image width="112" height="64" source="../../../sprites/entities/platforms/lifts/lift/body/idle/rhoutta_encounter1.png"/>
 </tile>
</tileset>

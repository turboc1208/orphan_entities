orphan_entities

Author : Chip Cox
Date : 18AUG2017

Release History
CC     18AUG2017      V0.1     Initial Release

Description:
This application populates a HA group with entities that are not being shown in another group. Because of the way the HA shows groups.  If an item in a in a class is not shown somewhere else, The generic group for that class will be shown along with any items that are part of that class.  To be honest the way HA decides which groups to show makes no sense what so ever.  But there is a good probibility that at least some of the items in any groups that show up on this page are not being shown somewhere else.

Setup
HomeAssistant
Create a group in Home Assistant and put one bogus entry in it as a place holder.
group.yaml<br>
orphan_entities:<br>
  view: yes<br>
  entities:<br>
    - light.bogus<br>
<br>
Appdaemon.YAML<br>
<span>
orphan_entities:<br>
  class: orphan_entities<br>
  module: orphan_entities<br>
  orphan_group: group.orphan_entities<br>
  exclusion_types: ['zwave']<br>
  interval: 120<br>
  on_demand: input_boolean.demand_update<br>
</span>
<br>
<ul>
<li>orphan_group - Required - group created in groups.yaml file to hold orphaned entities
<li>exclusion_types: - Optional - default ['group','zone'] - type entities not to include in view.  
<li>interval: Optional - default 120 seconds - seconds between updates
<li>on_demand: Optional - no default - input_boolean that can be toggled to force an update.  I recommend not putting this entity an any groups so it is always on this page. 
</ul>

orphan_entities

Author : Chip Cox
Date : 18AUG2017

Release History
CC     18AUG2017      V0.1     Initial Release

Description:
This application populates a HA group with entities that are not being shown in another group. Because of the way the HA shows groups.  If an item in a in a class is not shown somewhere else, The generic group for that class will be shown along with any items that are part of that class.  To be honest the way HA decides which groups to show makes no sense what so ever.  But there is a good probibility that at least some of the items in any groups that show up on this page are not being shown somewhere else.

Setup<br>
HomeAssistant<br>
Create a group in Home Assistant and put one bogus entry in it as a place holder.<br>
group.yaml<br>
<pre>
orphan_entities:
  view: yes
  entities:
    - light.bogus
</pre><br>
Appdaemon.YAML<br>
<pre>
orphan_entities:
  class: orphan_entities
  module: orphan_entities
  orphan_group: group.orphan_entities
  exclusion_types: ['zwave']
  interval: 120
  on_demand: input_boolean.demand_update
</pre>
<br>
<ul>
<li>orphan_group - Required - group created in groups.yaml file to hold orphaned entities
<li>exclusion_types: - Optional - default ['group','zone'] - type entities not to include in view.  
<li>interval: Optional - default 120 seconds - seconds between updates
<li>on_demand: Optional - no default - input_boolean that can be toggled to force an update.  I recommend not putting this entity an any groups so it is always on this page. 
</ul>

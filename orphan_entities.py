import appdaemon.appapi as appapi
import datetime
#################################
#  orphan_entities 
#
#  Author : Chip Cox
#  Date : 18AUG2017
#
#  Release History
#  CC     18AUG2017      V0.1     Initial Release
#
#  Description:
#    This application populates a HA group with entities that are not being shown in another group
#    Because of the way the HA shows groups.  If an item in a in a class is not shown somewhere else,
#    The generic group for that class will be shown along with any items that are part of that class.
#    To be honest the way HA decides which groups to show makes no sense what so ever.  But there
#    is a good probibility that at least some of the items in any groups that show up on this page
#    Are not being shown somewhere else.
#
#  Setup
#  HomeAssistant
#    Create a group in Home Assistant and put one bogus entry in it as a place holder.
#  group.yaml
#  orphan_entities:
#    view: yes
#    entities:
#      - light.bogus
#
#  Appdaemon.YAML
#  orphan_entities:
#    class: orphan_entities
#    module: orphan_entities
#    orphan_group: group.orphan_entities
#    exclusion_types: ['zwave']
#    interval: 120
#    on_demand: input_boolean.demand_update
#
#  orphan_group - Required - group created in groups.yaml file to hold orphaned entities
#  exclusion_types: - Optional - default ['group','zone'] - type entities not to include in view.  
#  interval: Optional - default 120 seconds - seconds between updates
#  on_demand: Optional - no default - input_boolean that can be toggled to force an update. 
#                                     I recommend not putting this entity an any groups so it is always on this page. 
#
#################################             
class orphan_entities(appapi.AppDaemon):

  def initialize(self):
    # self.LOGLEVEL="DEBUG"
    if "orphan_group" in self.args:
      self.orphan_group=self.args["orphan_group"]
    else:
      self.log("An orphan_group must be setup in Home Assistant with at least one entity.  The entity can be bogus  ( light.bogus ) for example")
      exit(0)

    self.log("Orphan Group set to {}".format(self.orphan_group))

    if "exclusion_types" in self.args:
      self.exclusion_types=list(set(["group","zone"]+self.args["exclusion_types"]))
    else:
      self.log("No exclusion group specified, excluding 'group' and 'zone'  entities by default")
      self.exclusion_types=["group","zone"]

    if "interval" in self.args:
      interval=self.args["interval"]
    else:
      self.log("setting default interval")
      interval=60*5

    self.log("interval set to {} seconds".format(interval))

    if "on_demand" in self.args:
      demand_entity=self.args["on_demand"]
      self.log("On Demand entity set to {}".format(demand_entity))
    else:
      demand_entity=None
      self.log("No demand_entity set")

    self.log("Exclusion types set to {}".format(self.exclusion_types))
    
    self.listen_event(self.HARestart,"HOMEASSISTANT_START")
    self.log("Event Listen event activated")
    self.run_every(self.timer_callback,self.datetime(), interval)
    self.log("Timer event registered for every {} seconds".format(interval))
    if not demand_entity==None :
      self.listen_state(self.demand_callback,demand_entity,new="on",old="off")
      self.log("Listening for {} to be turned on".format(demand_entity))

  #######
  #
  #  Timer Callback
  #
  #######

  def timer_callback(self,kwargs):
    self.log("Timer event fired")
    self.process_groups(self.orphan_group,self.exclusion_types)

  #######
  #
  # HA Restart Event Callback
  #
  #######

  def HARestart(self,event_name,dta,kwargs):
    self.log("HA Restarted creating orphan group membership")
    self.process_groups(self.orphan_group,self.exclusion_types)

  ######
  #
  # On demand listen_state callback
  #
  ######

  def demand_callback(self,entity,state,old,new,kwargs):
    self.log("on Demand callback fired")
    if new=="on":
      self.process_groups(self.orphan_group,self.exclusion_types)
      self.turn_off(entity)

  ######
  #
  # Process Groups - main work done here.
  #
  ######
  def process_groups(self,ogroup,etype_list):
    # first lets clear out the group.  Doing this up here, gives HA time to process the update.  We will put the new values in at the bottom
    self.set_state(ogroup,attributes={"entity_id":[]})
    # get a dictionary of all the groups in HA so we can build a list of everything that is already in a group
    allgroups=self.get_state("group")
    group_members=[]

    for g in allgroups:
      # I'm not sure if there is really a home group or not, but skip it since it if it exists since it does the same thing as this app
      if not g=="home":
        # build a unique group of entities that are already in groups
        group_members=list(set(group_members+allgroups[g]["attributes"]["entity_id"]))

    # get all the entities in HA
    allentities=self.get_state()
    newgroup=[]
   
    # loop through all the entities in HA
    for e in allentities:
      grptyp,grpnam = self.split_entity(e)
      if (e in group_members) or (grptyp in etype_list):
        # e is already in a group or is part of an excluded group, so skip it.
        #self.log("skipping {}".format(e))
        continue;
      else:
        # add new member to group
        self.log("Adding {}".format(e))
        newgroup.append(e)
    
    # set membership of orphan group
    self.set_state(ogroup,attributes={"entity_id": newgroup})


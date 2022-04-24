import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

# base_x: The corner of the map representing your base
base_x, base_y = [int(i) for i in input().split()]
heroes_per_player = int(input())  # Always 3

# enemy_base
if base_x == 0:
    enemy_x = 17630
    enemy_y = 9000
else:
    enemy_x = 0
    enemy_y = 0

current_targets = []
threat_m = []

class monster():    
    def __init__(self, id, x, y, health, vx, vy, nearBase, threatFor):
        self.id = id
        self.x = x
        self.y = y
        self.health=health, 
        self.vx=vx, 
        self.vy=vy, 
        self.nearBase=nearBase, 
        self.threatFor=threatFor

class hero():    
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
    
    def reset_target(self):
        self.target_x = None
        self.target_y = None
        self.wind_spell = None

    def get_distance(self, oppo):
        return pow(self.x-oppo.x, 2) + pow(self.y-oppo.y, 2)

    def find_closest(self, oppos, current_targets):
        target_id = None
        min_dis = 0
        for o in oppos:
            if o.id in current_targets:
                continue
            d = self.get_distance(o)
            if self.target_x is None or d < min_dis:
                self.target_x = o.x
                self.target_y = o.y
                min_dis = d
                target_id = o.id
        return target_id

    def find_chosest_threat(self, threats):
        print("find threat", file=sys.stderr, flush=True)
        min_dis = 0
        for t in threats:
            d = pow(t.x, 2) + pow(t.y, 2)
            if self.target_x is None or d <= min_dis:
                self.target_x = t.x
                self.target_y = t.y
                min_dis = d
        print(str(self.target_x) + " " + str(self.target_y), file=sys.stderr, flush=True)
    
    def spell_check(self, l_monster, curr_mana):
        # How many monster around me?
        # print("curr_mana: " + str(curr_mana), file=sys.stderr, flush=True)
        iCnt = 0
        for m in l_monster:
            if self.get_distance(m) < pow(1280, 2) + pow(1280, 2):
                iCnt += 1
        if iCnt > 0 and curr_mana > 10:
            self.wind_spell = True
        return self.wind_spell

    def set_base_distance(self, base_x, base_y):
        self.base_distance = pow(self.x-base_x, 2) + pow(self.y-base_y, 2)

# game loop
while True:
    round_health = []
    round_mana = []
    for i in range(2):
        # health: Each player's base health
        # mana: Ignore in the first league; Spend ten mana to cast a spell
        health, mana = [int(j) for j in input().split()]
        round_health.append(health)
        round_mana.append(mana)
    my_round_mana = round_mana[0]
    entity_count = int(input())  # Amount of heros and monsters you can see
    l_monster = []
    l_hero = []
    l_oppo_hero = []
    for i in range(entity_count):
        # _id: Unique identifier
        # _type: 0=monster, 1=your hero, 2=opponent hero
        # x: Position of this entity
        # shield_life: Ignore for this league; Count down until shield spell fades
        # is_controlled: Ignore for this league; Equals 1 when this entity is under a control spell
        # health: Remaining health of this monster
        # vx: Trajectory of this monster
        # near_base: 0=monster with no target yet, 1=monster targeting a base
        # threat_for: Given this monster's trajectory, is it a threat to 1=your base, 2=your opponent's base, 0=neither
        _id, _type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for = [int(j) for j in input().split()]
        if _type == 0:
            m = monster(id=_id, x=x, y=y, health=health, vx=vx, vy=vy, nearBase=near_base, threatFor=threat_for)
            l_monster.append(m)
        elif _type == 1:
            h = hero(id=_id, x=x, y=y)
            l_hero.append(h)    
        elif _type == 2:
            h = hero(id=_id, x=x, y=y)
            l_oppo_hero.append(h)  

    current_targets.clear()
    threat_m.clear()

    for i in l_monster:
        # print("m" + str(i.id) + " " + str(i.x) + " " + str(i.y), file=sys.stderr, flush=True)
        if i.threatFor == 1:
            threat_m.append(i)

    for i in l_oppo_hero:
        print("o" + str(i.id) + " " + str(i.x) + " " + str(i.y), file=sys.stderr, flush=True)

    # sort heros by distance to the base
    l_hero_sort = []
    for i in range(heroes_per_player):
        l_hero[i].reset_target()
        l_hero[i].set_base_distance(base_x, base_y)        
    l_hero_sort = sorted(l_hero, key=lambda hero: hero.base_distance)

    for i in range(heroes_per_player):
        curr_hero = l_hero_sort[i]
        print("Decision order: {}, curr ({}, {}), base ({}, {}), dis {}".format(
            curr_hero.id, curr_hero.x, curr_hero.y, base_x, base_y, curr_hero.base_distance), file=sys.stderr, flush=True)
        # First check if hero should spell wind:
        if curr_hero.spell_check(l_monster, my_round_mana):
            my_round_mana -= 10
            # print("Mana left: " + str(my_round_mana), file=sys.stderr, flush=True)

        if curr_hero.wind_spell:
            pass #
        else:
            current_targets.append(curr_hero.find_closest(threat_m, current_targets))
            # Write an action using print        
            if curr_hero.target_x is None:
                curr_hero.find_chosest_threat(threat_m)
            
    for h in l_hero:   
        print("Command order: " + str(h.id), file=sys.stderr, flush=True) 
        if h.wind_spell:
            print("SPELL WIND " + str(enemy_x) + " " + str(enemy_y))
        elif h.target_x:
            print("MOVE " + str(h.target_x) + " "+ str(h.target_y))
        else:
            print("MOVE " + str(base_x) + " " + str(base_y))
            

        # In the first league: MOVE <x> <y> | WAIT; In later leagues: | SPELL <spellParams>;
        #print("WAIT")

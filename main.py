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
    def __init__(self, id, x, y, health, shields, vx, vy, nearBase, threatFor):
        self.id = id
        self.x = x
        self.y = y
        self.health=health
        self.shld_lf=shields
        self.vx=vx
        self.vy=vy
        self.nearBase=nearBase
        self.threatFor=threatFor

class hero():    
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.defence = (id % 3) in (1, 2)
    
    def reset_target(self):
        self.target_x = None
        self.target_y = None
        self.wind_spell = None
        self.control_spell = None
        self.shield_spell = None

    def get_distance(self, oppo):
        return pow(self.x-oppo.x, 2) + pow(self.y-oppo.y, 2)

    # Offensive care about its own patrol position, defensive care about Gate and its own patrol area
    def check_care_area(self, m):
        return (pow(m.x - self.patrol_x, 2) + pow(m.y - self.patrol_y, 2) < pow(2200, 2)) \
                or (self.defence and pow(m.x - base_x, 2) + pow(m.y - base_y, 2) < pow(6000, 2))

    def find_closest(self, oppos, current_targets):
        target_id = None
        min_dis = 0
        for o in oppos:
            if o.id in current_targets:
                continue
            d = self.get_distance(o)
            if self.check_care_area(o) and (self.target_x is None or d < min_dis):
                self.target_x = o.x
                self.target_y = o.y
                min_dis = d
                target_id = o.id
        print("find target: " + str(self.target_x) + " " + str(self.target_y), file=sys.stderr, flush=True)
        return target_id

    def find_closest_threat(self, threats):
        # print("find threat", file=sys.stderr, flush=True)
        min_dis = 0
        for t in threats:
            d = pow(t.x, 2) + pow(t.y, 2)
            if self.check_care_area(t) and (self.target_x is None or d <= min_dis):
                self.target_x = t.x
                self.target_y = t.y
                min_dis = d
        print("find threat: " + str(self.target_x) + " " + str(self.target_y), file=sys.stderr, flush=True)

    def find_closest_patrol(self, l_m):
        min_dis = 0
        target_id = None
        for t in l_m:
            if t.threatFor == 2:
                continue
            d = pow(self.patrol_x - t.x, 2) + pow(self.patrol_y - t.y, 2)
            if self.target_x is None or d <= min_dis:
                self.target_x = t.x
                self.target_y = t.y
                min_dis = d
                target_id = t.id
        print("find closest patrol: {} {} {}".format(target_id, self.target_x, self.target_y), file=sys.stderr, flush=True)
    
    def spell_check(self, l_monster, curr_mana):
        # How many monster around me?
        # print("curr_mana: " + str(curr_mana), file=sys.stderr, flush=True)
        iWindCnt = 0
        lControlCnt = []

        for m in l_monster:
            if not m.shld_lf and self.get_distance(m) < pow(1280, 2):
                iWindCnt += 1
            if not m.shld_lf and self.get_distance(m) < pow(2200, 2):
                lControlCnt.append(m)

        if iWindCnt > 1 and curr_mana > 10:
            self.wind_spell = True
        elif len(lControlCnt) > 0 and curr_mana > 10:
            if lControlCnt[0].threatFor == 2 and not self.defence:
                self.shield_spell = str(lControlCnt[0].id)
            else:
                self.control_spell = str(lControlCnt[0].id)

        return self.wind_spell or self.control_spell or self.shield_spell

    def set_base_distance(self, base_x, base_y):
        self.base_distance = pow(self.x-base_x, 2) + pow(self.y-base_y, 2)

    def set_patrol_target(self):
        global base_x, base_y, enemy_x, enemy_y

        if self.defence:
            if self.id % 3 == 0:
                self.patrol_x = base_x + 6000 if base_x == 0 else base_x - 6000
                self.patrol_y = base_y + 6000 if base_y == 0 else base_y - 6000
            elif self.id % 3 == 1:
                self.patrol_x = base_x + 2200 if base_x == 0 else base_x - 2200
                self.patrol_y = base_y + 6000 if base_y == 0 else base_y - 6000
            elif self.id % 3 == 2:
                self.patrol_x = base_x + 6000 if base_x == 0 else base_x - 6000
                self.patrol_y = base_y + 2200 if base_y == 0 else base_y - 2200
        else:
            self.patrol_x = enemy_x + 6000 if enemy_x == 0 else enemy_x - 6000
            self.patrol_y = enemy_y + 6000 if enemy_y == 0 else enemy_y - 6000

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
            m = monster(id=_id, x=x, y=y, health=health, shields=shield_life, vx=vx, vy=vy, nearBase=near_base, threatFor=threat_for)
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

    # sort heros by distance to the base, the closest two will defence, the fastest one will offensive
    l_hero_sort = []
    for i in range(heroes_per_player):
        l_hero[i].reset_target()
        l_hero[i].set_base_distance(base_x, base_y)        
    l_hero_sort = sorted(l_hero, key=lambda hero: hero.base_distance)

    for i in range(heroes_per_player):
        curr_hero = l_hero_sort[i]
        print("Decision order: {}, curr ({}, {}), base ({}, {}), dis {}".format(
            curr_hero.id, curr_hero.x, curr_hero.y, base_x, base_y, curr_hero.base_distance), file=sys.stderr, flush=True)

        # Depend on def/off, set patrol target
        curr_hero.set_patrol_target()

        # First check if hero should spell wind:
        if curr_hero.spell_check(l_monster, my_round_mana):
            my_round_mana -= 10
            # print("Mana left: " + str(my_round_mana), file=sys.stderr, flush=True)

        if curr_hero.wind_spell or curr_hero.control_spell:
            pass #
        else:
            # If no spell, target order:
            # 1. closest threat (and the threat hasn't been targeted)
            current_targets.append(curr_hero.find_closest(threat_m, current_targets))
            # 2. other threat
            if curr_hero.target_x is None:
                curr_hero.find_closest_threat(threat_m)
            # 3. No threat, if hero is in care area, go to any monster close to patrol point
            if curr_hero.target_x is None:
                if curr_hero.check_care_area(curr_hero) or not curr_hero.defence:
                    curr_hero.find_closest_patrol(l_monster)
            # 99. No target, it will go to patrol point

            
    for h in l_hero:   
        print("Command order: " + str(h.id), file=sys.stderr, flush=True) 
        if h.wind_spell:
            print("SPELL WIND {} {}".format(enemy_x, enemy_y))
        elif h.shield_spell:
            print("SPELL SHIELD {}".format(h.shield_spell))
        elif h.control_spell:
            print("SPELL CONTROL {} {} {}".format(h.control_spell, enemy_x, enemy_y) )
        elif h.target_x:
            print("MOVE {} {} ".format(h.target_x, h.target_y))
        else:
            print("MOVE {} {} ".format(h.patrol_x, h.patrol_y))

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

global_info = []
current_targets = []
threat_m = []
goal_threat_m = []

class base():
    def __init__(self, x, y, health, mana):
        self.x = x
        self.y = y
        self.health = health
        self.mana = mana
        self.stratigic = 'O'

    def get_distance(self, o):
        return pow(self.x-o.x, 2) + pow(self.y-o.y, 2)

    def is_risky(self, o):
        return self.get_distance(o) < pow(5000, 2)


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
    def __init__(self, id, x, y, base, enemy_base):
        self.id = id
        self.x = x
        self.y = y
        self.defence = (id % 3) in (1, 2)
        self.base = base
        self.base_distance = pow(self.x-base.x, 2) + pow(self.y-base.y, 2)
        self.enemy_base = enemy_base
    
    def reset_target(self):
        self.target = None
        self.wind_spell = None
        self.control_spell = None
        self.shield_spell = None
        self.find_solution = None

    def get_distance_ab(self, a, b):
        return pow(a.x-b.x, 2) + pow(a.y-b.y, 2)

    def get_distance(self, oppo):
        return self.get_distance_ab(self, oppo)

    # Offensive care about its own patrol position, defensive care about Gate and its own patrol area
    def check_care_area(self, m):
        return (pow(m.x - self.patrol_x, 2) + pow(m.y - self.patrol_y, 2) < pow(2200, 2)) \
                or (self.role != 'O' and pow(m.x - base_x, 2) + pow(m.y - base_y, 2) < pow(6000, 2))

    def find_closest(self, start_point, oppos, current_targets):
        target_id = None
        min_dis = 0
        for o in oppos:
            if o.threatFor == 2:
                continue
            if o.id in current_targets:
                continue
            d = self.get_distance_ab(start_point, o)
            if self.check_care_area(o) and (self.target is None or d < min_dis):
                self.target = o
                min_dis = d
                target_id = o.id
        if self.target:
            print("find target {} ({}, {}): ".format(self.target.id, self.target.x, self.target.y), file=sys.stderr, flush=True)
        return target_id

    def spell_check(self, l_monster, curr_mana):
        # How many monster around me?
        # print("curr_mana: " + str(curr_mana), file=sys.stderr, flush=True)
        iWindCnt = 0
        lControlCnt = []
        lShieldCnt = []

        if self.target and self.find_solution[1] == 'T':
            # It is a threat target, what should I do?
            # If I'm goal keeper, and the target is within any spell, I should use spell
            if self.role[0] == 'G' and curr_mana >= 10:
                if self.get_distance(self.target) < pow(1280, 2):
                    self.wind_spell = True
                elif not self.target.shld_lf and self.get_distance(self.target) < pow(2200, 2) and self.target.threatFor != 2:
                    self.control_spell = str(self.target.id)
            if self.role[0] == 'D' and curr_mana >= 10:
                # Can I kill target before it reach base?
                the_turns_i_need_to_kill_it = round(self.target.health / 2)
                the_turns_it_will_reach_base = math.trunc((math.sqrt(self.get_distance_ab(self.target, self.base)) - 300) / 400)
                if the_turns_i_need_to_kill_it > the_turns_it_will_reach_base:
                    # I cannot kill the monster in time, I should use spell
                    if self.get_distance(self.target) < pow(1280, 2):
                        self.wind_spell = True
                    if not self.target.shld_lf and self.get_distance(self.target) < pow(2200, 2) and self.target.threatFor != 2:
                        self.control_spell = str(self.target.id)
        if self.target and self.find_solution[1] == 'O':
            # how close is my target to enemy_base?
            if self.get_distance_ab(self.target, self.enemy_base) < pow(7800, 2):
                if self.get_distance(self.target) < pow(1280, 2):
                    self.wind_spell = True
                if not self.target.shld_lf and self.get_distance(self.target) < pow(2200, 2) and self.target.threatFor != 2:
                    self.control_spell = str(self.target.id)
                if not self.target.shld_lf and self.get_distance(self.target) < pow(2200, 2) and self.target.threatFor == 2:
                    self.shield_spell = str(self.target.id)

        if not self.wind_spell and not self.control_spell and not self.shield_spell:
            # no threat target, no shooting, how many monster around me?
            for m in l_monster:
                if not m.shld_lf and self.get_distance(m) < pow(1280, 2):
                    iWindCnt += 1

            if iWindCnt > 4 and curr_mana > 50:
                self.wind_spell = True

        return self.wind_spell or self.control_spell or self.shield_spell

    def set_patrol_target(self):
        global base_x, base_y, enemy_x, enemy_y

        if self.role == 'G':
            self.patrol_x = base_x + 800 if base_x == 0 else base_x - 800
            self.patrol_y = base_y + 800 if base_y == 0 else base_y - 800
        elif self.role == 'D0':
            self.patrol_x = base_x + 2200 if base_x == 0 else base_x - 2200
            self.patrol_y = base_y + 6000 if base_y == 0 else base_y - 6000
        elif self.role == 'D1':
            self.patrol_x = base_x + 6000 if base_x == 0 else base_x - 6000
            self.patrol_y = base_y + 2200 if base_y == 0 else base_y - 2200
        else: # role == 'O'
            self.patrol_x = enemy_x + 8800 if enemy_x == 0 else enemy_x - 8800
            self.patrol_y = enemy_y + 4500 if enemy_y == 0 else enemy_y - 4500

    def find_target(self, goal_threat_m, threat_m, l_monster, current_targets, enemy_base):
        if self.role[0] == 'G':
            # goal keeper, find the most closest one to base
            self.find_closest(self.base, goal_threat_m, [])
            if self.target:
                self.find_solution = 'GT'
        elif self.role[0] == 'D':
            # defense
            if self.base.mana < 20:
                #can only use one spell, so find goal_threat
                self.find_closest(self.base, goal_threat_m, current_targets)
            if self.target:
                self.find_solution = 'GT'
            else: # no goal threat
                # find the closest threat one with itself
                self.find_closest(self, threat_m, current_targets)
                if self.target:
                    self.find_solution = 'DT'
                else: # not found untargeted threat
                    self.find_closest(self, l_monster, current_targets)
                    if self.target:
                        self.find_solution = 'DP'
        elif self.role[0] == 'O':
            # offense, if we don't have much mana, find closest one
            if self.base.mana <= 80:
                self.find_closest(self, l_monster, current_targets)
                if self.target:
                    self.find_solution = 'OP'
            else:
                # find the closest one to enemy_base
                self.find_closest(enemy_base, l_monster, current_targets)
                if self.target:
                    self.find_solution = 'OO'


        return self.target.id if self.target else None

    def get_detail(self):
        return "{}-{}-{}-{}".format(self.base.stratigic, self.role, self.target.id if self.target else -1, self.find_solution if self.find_solution else '')

# game loop
while True:
    global_info.clear()
    for i in range(2):
        # health: Each player's base health
        # mana: Ignore in the first league; Spend ten mana to cast a spell
        health, mana = [int(j) for j in input().split()]
        if i == 0:
            global_info.append(base(base_x, base_y, health, mana))
        else:
            global_info.append(base(enemy_x, enemy_y, health, mana))
    my_base = global_info[0]
    enemy_base = global_info[1]

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
            h = hero(id=_id, x=x, y=y, base=my_base, enemy_base=enemy_base)
            l_hero.append(h)    
        elif _type == 2:
            h = hero(id=_id, x=x, y=y, base=enemy_base, enemy_base=my_base)
            l_oppo_hero.append(h)  

    current_targets.clear()
    threat_m.clear()
    goal_threat_m.clear()

    for i in l_monster:
        # print("m{} ({},{}) => ({},{})".format(i.id, i.x,i.y, i.vx, i.vy), file=sys.stderr, flush=True)
        if i.threatFor == 1:
            threat_m.append(i)
            if my_base.is_risky(i):
                goal_threat_m.append(i)

    if len(goal_threat_m) >= 3:
        my_base.stratigic = 'D'
    else:
        my_base.stratigic = 'O'

    for i in l_oppo_hero:
        print("o" + str(i.id) + " " + str(i.x) + " " + str(i.y), file=sys.stderr, flush=True)

    # sort heros by distance to the base, the closest two will defence, the fastest one will offensive
    l_hero_sort = []
    for i in range(heroes_per_player):
        l_hero[i].reset_target()
    l_hero_sort = sorted(l_hero, key=lambda hero: hero.base_distance)

    for i in range(heroes_per_player):
        curr_hero = l_hero_sort[i]
        if my_base.stratigic == 'D':
            if i == 0:
                curr_hero.role = 'G' # goal_keeper
            else:
                curr_hero.role = 'D' + str(i-1)
        if my_base.stratigic == 'O':
            if i == 2:
                curr_hero.role = 'O'
            else:
                curr_hero.role = 'D' + str(i)

    for i in range(heroes_per_player):
        curr_hero = l_hero_sort[i]
        print("Decision order: {}, curr ({}, {}), base ({}, {}), dis {}, role {}-{}".format(
            curr_hero.id, curr_hero.x, curr_hero.y, base_x, base_y, curr_hero.base_distance, my_base.stratigic, curr_hero.role), file=sys.stderr, flush=True)

        # Depend on role, set patrol target
        curr_hero.set_patrol_target()

        # find monster target
        current_targets.append(curr_hero.find_target(goal_threat_m, threat_m, l_monster, current_targets, enemy_base))

        # First check if hero should spell wind:
        if curr_hero.spell_check(l_monster, my_base.mana):
            my_base.mana -= 10
            
    for h in l_hero:   
        # print("Command order: " + str(h.id), file=sys.stderr, flush=True)
        if h.wind_spell:
            print("SPELL WIND {} {} {}".format(enemy_x, enemy_y, h.get_detail()))
        elif h.shield_spell:
            print("SPELL SHIELD {} {}".format(h.shield_spell, h.get_detail()))
        elif h.control_spell:
            print("SPELL CONTROL {} {} {} {}".format(h.control_spell, enemy_x, enemy_y, h.get_detail()) )
        elif h.target:
            print("MOVE {} {} {}".format(h.target.x+h.target.vx, h.target.y+h.target.vy, h.get_detail()))
        else:
            print("MOVE {} {} {}".format(h.patrol_x, h.patrol_y, h.get_detail()))

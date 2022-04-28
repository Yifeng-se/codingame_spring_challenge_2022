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


class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y


def get_distance_ab(a, b):
    return math.sqrt(pow(a.x-b.x, 2) + pow(a.y-b.y, 2))


class Patrol():
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

    def go_next(self, p):
        self.next = p


class Base():
    def __init__(self, x, y, health, mana):
        self.x = x
        self.y = y
        self.health = health
        self.mana = mana
        self.stratigic = 'D'
        self.stratigic_change = False
        self.l_monster = []
        self.current_targets = []
        self.threat_m = []
        self.goal_threat_m = []
        self.heroes = {}

        # Defense patrol route
        self.bp = Patrol('base', x + 800 if x == 0 else x -
                         800, y + 800 if y == 0 else y - 800)
        self.dp0 = Patrol('dp0', x + 2200 if x == 0 else x - 2200,
                          y + 6000 if y == 0 else y - 6000)
        self.dp1 = Patrol('dp1', x + 6000 if x == 0 else x - 6000,
                          y + 2200 if y == 0 else y - 2200)
        self.dp2 = Patrol('dp2', 8800, 4500)
        self.dp0.go_next(self.dp1)
        self.dp1.go_next(self.dp2)
        self.dp2.go_next(self.dp0)
        self.l_d_patrol = [self.dp0, self.dp1, self.dp2]

        # Offense patrol route
        # self.fp0 = Patrol('fp0', 13500 if x == 0 else x - 13500,
        #                   5200 if y == 0 else y - 5200)
        # self.fp1 = Patrol('fp1', 10600, 2200)
        # self.fp2 = Patrol('fp2', 7000, 6800)
        self.fp0 = Patrol('fp0', enemy_x + 2200 if enemy_x == 0 else enemy_x - 2200,
                          enemy_y + 6000 if enemy_y == 0 else enemy_y - 6000)
        self.fp1 = Patrol('fp1', enemy_x + 6000 if enemy_x == 0 else enemy_x - 6000,
                          enemy_y + 2200 if enemy_y == 0 else enemy_y - 2200)
        self.fp2 = Patrol('fp2', 8800, 4500)
        self.fp0.go_next(self.fp1)
        self.fp1.go_next(self.fp2)
        self.fp2.go_next(self.fp0)
        self.l_f_patrol = [self.fp0, self.fp1, self.fp2]

    def get_distance(self, o):
        return get_distance_ab(self, o)

    def is_risky(self, o):
        return self.get_distance(o) < 5000

    def round_reset(self):
        self.l_monster.clear()
        self.current_targets.clear()
        self.threat_m.clear()
        self.goal_threat_m.clear()

    def mana_OO(self):
        return self.mana >= 80


my_base = Base(x=base_x, y=base_y, health=3, mana=0)
enemy_base = Base(x=enemy_x, y=enemy_y, health=3, mana=0)


class Monster():
    def __init__(self, id, x, y, health, shields, is_controlled, vx, vy, nearBase, threatFor):
        self.id = id
        self.x = x
        self.y = y
        self.health = health
        self.shld_lf = shields
        self.is_controlled = is_controlled
        self.vx = vx
        self.vy = vy
        self.nearBase = nearBase
        self.threatFor = threatFor


class Hero():
    def __init__(self, id, x, y, shieldLife, isControlled, base, enemy_base):
        self.id = id
        self.x = x
        self.y = y
        self.base = base
        self.base_distance = get_distance_ab(self, base)
        self.enemy_base = enemy_base
        self.shld_lf = shieldLife
        self.is_controlled = isControlled
        self.role = 'D'
        self.high_morale = 0
        self.act_log = []

    def round_set(self, x, y, shieldLife, isControlled):
        self.x = x
        self.y = y
        self.base_distance = get_distance_ab(self, self.base)
        self.shield_life = shieldLife
        self.is_controlled = isControlled

    def reset_target(self):
        self.target = None
        self.wind_spell = None
        self.control_spell = None
        self.shield_spell = None
        self.find_solution = None

    def get_distance(self, oppo):
        return get_distance_ab(self, oppo)

    # Offensive care about its own patrol position, defensive care about Gate and its own patrol area
    def check_care_area(self, m):
        return (self.role[0] == 'O' and get_distance_ab(m, self.base) >= 8000)\
            or (self.role[0] != 'O' and get_distance_ab(m, self.base) < 8000)
        # or get_distance_ab(m, self.patrol) < 3300 \

    def find_closest(self, start_point, oppos, current_targets):
        target_id = None
        min_dis = 0
        for o in oppos:
            if hasattr(o, 'threatFor') and o.threatFor == 2 \
                and not self.high_morale:
                continue
            if hasattr(o, 'id') and o.id in current_targets:
                continue
            d = get_distance_ab(start_point, o)
            if self.check_care_area(o) and (self.target is None or d < min_dis):
                self.target = o
                min_dis = d
                target_id = str(o.id)
        # if self.target:
        #    print("find target {} ({}, {}): ".format(self.target.id,
        #          self.target.x, self.target.y), file=sys.stderr, flush=True)
        return target_id

    def spell_check(self, l_monster, curr_mana):
        # How many monster around me?
        # print("curr_mana: " + str(curr_mana), file=sys.stderr, flush=True)
        iWindCnt = 0

        if self.target and self.find_solution[1] == 'T':
            # It is a threat target, what should I do?
            # If I'm goal keeper, and the target is within any spell, I should use spell
            if self.role[0] == 'G' and curr_mana >= 10:
                if not self.target.shld_lf and self.get_distance(self.target) < 1280:
                    self.wind_spell = True
                elif not self.target.shld_lf and self.get_distance(self.target) < 2200 and self.target.threatFor != 2:
                    self.control_spell = str(self.target.id)
            if self.role[0] == 'D' and curr_mana >= 10:
                # Can I kill target before it reach base?
                the_turns_i_need_to_kill_it = round(self.target.health / 2)
                the_turns_it_will_reach_base = math.trunc(
                    (get_distance_ab(self.target, self.base) - 300) / 400)
                if the_turns_i_need_to_kill_it > the_turns_it_will_reach_base:
                    # I cannot kill the monster in time, I should use spell
                    if not self.target.shld_lf and self.get_distance(self.target) < 1280:
                        self.wind_spell = True
                    if (not self.target.shld_lf and self.get_distance(self.target) < 2200
                        and not self.target.is_controlled
                            and self.target.threatFor != 2):
                        self.control_spell = str(self.target.id)
        if self.target and self.find_solution[1] == 'O':
            # how close is my target to enemy_base?
            if get_distance_ab(self.target, self.enemy_base) < 7800:
                if not self.target.shld_lf and self.get_distance(self.target) < 1280 and self.target.id > 5:
                    self.wind_spell = True
                if not self.target.shld_lf and self.get_distance(self.target) < 2200 and (self.target.id <= 5 or self.target.id > 5 and self.target.threatFor != 2):
                    self.control_spell = str(self.target.id)
                if not self.target.shld_lf and self.get_distance(self.target) < 2200 and self.target.id > 5 and self.target.threatFor == 2 and self.target.health >= 10:
                    self.shield_spell = str(self.target.id)


        if not self.wind_spell and not self.control_spell and not self.shield_spell:
            # no threat target, no shooting, how many monster around me?
            for m in l_monster:
                if not m.shld_lf and self.get_distance(m) < 1280:
                    iWindCnt += 1

            if iWindCnt > 4 and curr_mana > 50:
                self.wind_spell = True

        if not self.wind_spell and not self.control_spell and not self.shield_spell and curr_mana > 200:
            if iWindCnt > 1:
                self.wind_spell = True

        return self.wind_spell or self.control_spell or self.shield_spell

    def set_patrol_target(self, curr_targets):
        # Only need to do it when change stratigic
        if self.role[0] == 'G':
            self.patrol = self.base.bp
        elif self.role[0] == 'D':
            if self.base.dp0.id in curr_targets:
                self.patrol = self.base.dp1
            elif self.base.dp1.id in curr_targets:
                self.patrol = self.base.dp0
            elif self.get_distance(self.base.dp0) < self.get_distance(self.base.dp1):
                self.patrol = self.base.dp0
            else:
                self.patrol = self.base.dp1
        else:  # role[0] == 'O'
            self.patrol = self.base.fp1

        return self.patrol.id if self.patrol else None

    def find_target(self, goal_threat_m, threat_m, l_monster, current_targets, enemy_base):
        if self.role[0] == 'G':
            # goal keeper, find the most closest one to base
            if self.find_closest(self.base, goal_threat_m, []):
                self.find_solution = 'GT'
        elif self.role[0] == 'D':
            # defense
            if self.role == 'D0' or self.base.mana < 20:
                # can only use one spell, so find goal_threat
                self.find_closest(self.base, goal_threat_m, current_targets)
            if self.target:
                self.find_solution = 'GT'
            else:  # no goal threat
                # find the closest threat one with base/itself
                if self.find_closest(self.base if self.role == 'D0' else self, threat_m, current_targets):
                    self.find_solution = 'DT'
                elif self.find_closest(self, l_monster, current_targets):
                    self.find_solution = 'DP'
        elif self.role[0] == 'O':
            # offense, if we don't have much mana, find closest one
            if not self.base.mana_OO() and not self.high_morale:
                if self.find_closest(self, l_monster, current_targets):
                    self.find_solution = 'OP'
            else:
                # find the closest one to enemy_base
                if self.find_closest(enemy_base, l_monster + list(enemy_base.heroes.values()), current_targets):
                    self.find_solution = 'OO'

        # print("T{} ".format(self.target.id if self.target else None), file=sys.stderr, flush=True)
        return self.target.id if self.target else None

    def get_detail(self):
        return "{}-{}-{}-{}".format(self.base.stratigic, self.role, self.target.id if self.target else -1, self.find_solution if self.find_solution else '')


# game loop
while True:
    l_heroes = []
    my_base.round_reset()
    enemy_base.round_reset()
    enemy_base.heroes.clear()

    for i in range(2):
        # health: Each player's base health
        # mana: Ignore in the first league; Spend ten mana to cast a spell
        health, mana = [int(j) for j in input().split()]
        if i == 0:
            my_base.health = health
            my_base.mana = mana
        else:
            enemy_base.health = health
            enemy_base.mana = mana

    entity_count = int(input())  # Amount of heros and monsters you can see

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
        _id, _type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for = [
            int(j) for j in input().split()]
        if _type == 0:
            m = Monster(id=_id, x=x, y=y, health=health, shields=shield_life,
                        is_controlled=is_controlled, vx=vx, vy=vy, nearBase=near_base, threatFor=threat_for)
            my_base.l_monster.append(m)
        elif _type == 1:
            if _id not in my_base.heroes:
                h = Hero(id=_id, x=x, y=y, shieldLife=shield_life,
                         isControlled=is_controlled, base=my_base, enemy_base=enemy_base)
                my_base.heroes[_id] = h
            else:
                my_base.heroes[_id].round_set(
                    x=x, y=y, shieldLife=shield_life, isControlled=is_controlled)
            l_heroes.append(my_base.heroes[_id])
        elif _type == 2:
            h = Hero(id=_id, x=x, y=y, shieldLife=shield_life,
                        isControlled=is_controlled, base=enemy_base, enemy_base=my_base)
            enemy_base.heroes[_id] = h

    for i in my_base.l_monster:
        print("m{} ({},{}) => ({},{}), {}, {}".format(i.id, i.x, i.y, i.vx, i.vy, i.nearBase, i.threatFor), file=sys.stderr, flush=True)
        if i.threatFor == 1:
            my_base.threat_m.append(i)
            if my_base.is_risky(i):
                my_base.goal_threat_m.append(i)

    # sort heros by distance to the base
    l_hero_sort = []
    for k, v in my_base.heroes.items():
        v.reset_target()
        l_hero_sort.append(v)
    l_hero_sort = sorted(l_hero_sort, key=lambda hero: hero.base_distance)

    threat_hero_cnt = 0
    for h in enemy_base.heroes.values():
        if get_distance_ab(my_base, h) < 6000:
            threat_hero_cnt += 1

    if len(my_base.goal_threat_m) >= 3 and threat_hero_cnt > 0:
        if my_base.stratigic == 'O':
            # Change stratigic, need to reset patrol for heroes
            my_base.stratigic = 'D'
            my_base.stratigic_change = True
        else:
            my_base.stratigic_change = False
    else:
        if my_base.stratigic == 'D':
            my_base.stratigic = 'O'
            my_base.stratigic_change = True
        else:
            my_base.stratigic_change = False

    # Depense on hero base_distance and base stratigic, set role
    # Defense, one Goal_keeper, 2 defenser; otherwise 2 defenser, 1 forward (O)
    iDCnt = 0
    for i in range(heroes_per_player):
        curr_hero = l_hero_sort[i]

        if my_base.stratigic_change:
            if my_base.stratigic == 'D' and i == 0:
                curr_hero.role = 'G'  # goal_keeper
            elif my_base.stratigic == 'O' and i == 2:
                curr_hero.role = 'O'
            else:
                curr_hero.role = 'D' + str(iDCnt)
                iDCnt += 1
        elif curr_hero.role[0] == 'D':
            curr_hero.role = 'D' + str(iDCnt)
            iDCnt += 1

        if my_base.stratigic_change:
            # Reset hero Patrol route
            my_base.current_targets.append(
                curr_hero.set_patrol_target(my_base.current_targets))
            # print(*my_base.current_targets, file=sys.stderr, flush=True)
            # print("patrol ({}, {})".format(curr_hero.patrol.x, curr_hero.patrol.y), file=sys.stderr, flush=True)

        # If Offense and a lot mana, in high_morale for 5 rounds
        if curr_hero.role == 'O':
            if my_base.mana_OO():
                curr_hero.high_morale = 5
            else:
                curr_hero.high_morale -= 1
                curr_hero.high_morale = max(0, curr_hero.high_morale)
        else:
            curr_hero.high_morale = 0

    for k, v in enemy_base.heroes.items():
        print("o{} ({}, {})".format(k, v.x, v.y), file=sys.stderr, flush=True)

    for i in range(heroes_per_player):
        curr_hero = l_hero_sort[i]
        print("Decision order: {}, curr ({}, {}), high {}, act_log {}".format(
            curr_hero.id, curr_hero.x, curr_hero.y, curr_hero.high_morale, ' '.join(map(str, curr_hero.act_log[:5]))), file=sys.stderr, flush=True)

        # If arrived patrol, go to next one
        if curr_hero.get_distance(curr_hero.patrol) < 600 and hasattr(curr_hero.patrol, 'next'):
            curr_hero.patrol = curr_hero.patrol.next

        # find monster target
        my_base.current_targets.append(curr_hero.find_target(
            my_base.goal_threat_m, my_base.threat_m, my_base.l_monster, my_base.current_targets, enemy_base))
        # print(*my_base.current_targets, file=sys.stderr, flush=True)

        # should I use spell or should I just farming
        if curr_hero.spell_check(my_base.l_monster, my_base.mana):
            my_base.mana -= 10

    for h in l_heroes:
        # print("Command order: " + str(h.id), file=sys.stderr, flush=True)
        if h.wind_spell:
            print("SPELL WIND {} {} {}".format(
                enemy_base.x, enemy_base.y, h.get_detail()))
            h.act_log[:0] = ['W']
        elif h.shield_spell:
            print("SPELL SHIELD {} {}".format(h.shield_spell, h.get_detail()))
            h.act_log[:0] = ['S']
        elif h.control_spell:
            print("SPELL CONTROL {} {} {} {}".format(
                h.control_spell, enemy_base.x if int(h.control_spell) > 5 else 8800, enemy_base.y if int(h.control_spell) > 5 else 4500, h.get_detail()))
            h.act_log[:0] = ['C']
        elif h.high_morale and sum(x is not None for x in h.act_log[:3]) > 1:
            # High morale and spelled twice, move ahead to seek spell
            print("MOVE {} {} {}".format(3000 if h.enemy_base.x==0 else h.enemy_base.x-3000, 3000 if h.enemy_base.y==0 else h.enemy_base.y-3000, h.get_detail()))
            h.act_log[:0] = [None]
        elif h.target:
            if h.find_solution == 'OO' and h.target.id > 5:
                # Actually I want to protect it
                # Is there any enemy hero close to the targe?
                l_e_hero_sort = []
                for k, v in enemy_base.heroes.items():
                    v.protect_distance = get_distance_ab(v, h.target)
                    l_e_hero_sort.append(v)
                l_e_hero_sort = sorted(l_e_hero_sort, key=lambda hero: hero.protect_distance)
                control_enemy = None
                for i in l_e_hero_sort:
                    if not i.shld_lf and h.get_distance(i) < 2200 and my_base.mana >= 10:
                        control_enemy = str(i.id)
                        break
                if control_enemy:
                    print("SPELL CONTROL {} {} {} {}".format(
                    control_enemy, 8800, 4500, h.get_detail()+'-PRT'))
                    h.act_log[:0] = ['C']
                else:
                    print("MOVE {} {} {}".format(3000 if h.enemy_base.x==0 else h.enemy_base.x-3000, 3000 if h.enemy_base.y==0 else h.enemy_base.y-3000, h.get_detail()))
                    h.act_log[:0] = [None]
            else:
                print("MOVE {} {} {}".format(h.target.x+(h.target.vx if h.target.id>5 else 0),
                    h.target.y+(h.target.vy if h.target.id>5 else 0), h.get_detail()))
                h.act_log[:0] = [None]
        else:
            print("MOVE {} {} {}".format(h.patrol.x, h.patrol.y, h.get_detail()))
            h.act_log[:0] = [None]

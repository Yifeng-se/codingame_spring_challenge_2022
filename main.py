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
        self.threat_heros = []
        self.morale = 0

        # Defense patrol route
        self.bp = Patrol('base', x + 800 if x == 0 else x -
                         800, y + 800 if y == 0 else y - 800)
        self.dp0 = Patrol('dp0', x + 2200 if x == 0 else x - 2200,
                          y + 6000 if y == 0 else y - 6000)
        self.dp1 = Patrol('dp1', x + 6000 if x == 0 else x - 6000,
                          y + 2200 if y == 0 else y - 2200)
        self.dp2 = Patrol('dp2', x + 6000 if x == 0 else x - 6000,
                          y + 6000 if y == 0 else y - 6000)
        self.dp0.go_next(self.dp1)
        self.dp1.go_next(self.dp2)
        self.dp2.go_next(self.dp0)
        self.l_d_patrol = [self.dp0, self.dp1, self.dp2]

        # Offense patrol route
        # self.fp0 = Patrol('fp0', 13500 if x == 0 else x - 13500,
        #                   5200 if y == 0 else y - 5200)
        # self.fp1 = Patrol('fp1', 10600, 2200)
        # self.fp2 = Patrol('fp2', 7000, 6800)
        self.fp0 = Patrol('fp0', enemy_x + 1000 if enemy_x == 0 else enemy_x - 1000,
                          enemy_y + 5000 if enemy_y == 0 else enemy_y - 5000)
        self.fp1 = Patrol('fp1', enemy_x + 5000 if enemy_x == 0 else enemy_x - 5000,
                          enemy_y + 1000 if enemy_y == 0 else enemy_y - 1000)
        self.fp2 = Patrol('fp2', enemy_x + 4000 if enemy_x == 0 else enemy_x - 4000,
                        enemy_y + 4000 if enemy_y == 0 else enemy_y - 4000)
        self.fp3 = Patrol('fp3', enemy_x + 2200 if enemy_x == 0 else enemy_x - 2200,
                        enemy_y + 2200 if enemy_y == 0 else enemy_y - 2200)
        self.fp0.go_next(self.fp1)
        self.fp1.go_next(self.fp2)
        self.fp2.go_next(self.fp3)
        self.fp3.go_next(self.fp0)

        self.mp0 = Patrol('mp0', 8815, 4500)
        self.mp1 = Patrol('mp1', 13500 if x == 0 else x - 13500,
                        3500 if y == 0 else y - 3500)
        self.mp2 = Patrol('mp2', 9500 if x == 0 else x - 9500,
                        7500 if y == 0 else y - 7500)
        self.mp0.go_next(self.mp1)
        self.mp1.go_next(self.mp2)
        self.mp2.go_next(self.mp0)

    def get_distance(self, o):
        return get_distance_ab(self, o)

    def is_risky(self, o):
        return self.get_distance(o) < 5000

    def round_reset(self):
        self.l_monster.clear()
        self.current_targets.clear()
        self.threat_m.clear()
        self.goal_threat_m.clear()
        self.threat_heros.clear()
        self.morale = 1 if self.mana >= 120 else \
            0 if self.mana < 30 else self.morale

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
        self.enemy_base_distance = get_distance_ab(self, enemy_base)


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
        self.act_log = []
        self.threat_hero = False
        self.enemy_base_distance = get_distance_ab(self, self.enemy_base)
        self.ball = None

    def round_set(self, x, y, shieldLife, isControlled):
        self.x = x
        self.y = y
        self.base_distance = get_distance_ab(self, self.base)
        self.shld_lf = shieldLife
        self.is_controlled = isControlled
        self.enemy_base_distance = get_distance_ab(self, self.enemy_base)
        self.second_attack_arrive = False

    def reset_target(self):
        self.target = None
        self.wind_spell = None
        self.control_spell = None
        self.shield_spell = None
        self.find_solution = None
        self.ball = None

    def get_distance(self, oppo):
        return get_distance_ab(self, oppo)

    # Offensive care about its own patrol position, defensive care about Gate and its own patrol area
    def check_care_area(self, m):
        return (self.role[0] == 'O' and get_distance_ab(m, self.enemy_base) < 10000)\
            or (self.role[0] != 'O' and get_distance_ab(m, self.base) < 9000)
        # or get_distance_ab(m, self.patrol) < 3300 \

    def find_ball(self, start_point, oppos, shielded):
        min_dis = 0
        for o in oppos:
            d = get_distance_ab(start_point, o)
            if self.check_care_area(o) \
                and (self.ball is None or d < min_dis) \
                    and (o.shld_lf == shielded) \
                        and self.get_distance(o) <= 2200:
                self.ball = o
                min_dis = d
        return self.ball

    def find_closest(self, start_point, oppos, current_targets):
        target_id = None
        min_dis = 0
        for o in oppos:
            if hasattr(o, 'threatFor') and o.threatFor == 2 \
                and o.nearBase and not self.base.morale:
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
        iWindHPSum = 0

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
                    (get_distance_ab(self.target, self.base) - 300 - 1200) / 400)
                if the_turns_i_need_to_kill_it > the_turns_it_will_reach_base:
                    # I cannot kill the monster in time, I should use spell
                    if not self.target.shld_lf and self.get_distance(self.target) < 1280:
                        self.wind_spell = True
                    if (not self.target.shld_lf and self.get_distance(self.target) < 2200
                        and not self.target.is_controlled
                            and self.target.threatFor != 2):
                        self.control_spell = str(self.target.id)
        if self.target and self.find_solution[0] == 'D':
            if self.base.threat_heros \
                and not self.shld_lf \
                and self.base_distance < 8000 \
                and curr_mana >= 10:
                # Enemy hero! Shield myself
                self.shield_spell = str(self.id)

        # if self.target and self.find_solution[1] == 'O':
        #     # how close is my target to enemy_base?
        #     if get_distance_ab(self.target, self.enemy_base) < 7800:
        #         if not self.target.shld_lf and self.get_distance(self.target) < 1280 \
        #             and self.target.id > 5:
        #             self.wind_spell = True
        #         if not self.target.shld_lf and self.get_distance(self.target) < 2200 \
        #             and (self.target.id <= 5 or self.target.id > 5 and self.target.threatFor != 2):
        #             self.control_spell = str(self.target.id)
        #         if not self.target.shld_lf and self.get_distance(self.target) < 2200 \
        #             and self.target.id > 5 and self.target.threatFor == 2 \
        #             and self.target.health >= 15 and get_distance_ab(self.target, self.enemy_base) < 4000:
        #             self.shield_spell = str(self.target.id)

        if not self.wind_spell and not self.control_spell and not self.shield_spell:
            # no threat target, no shooting, how many monster around me?
            for m in l_monster:
                if not m.shld_lf and self.get_distance(m) < 1280:
                    iWindCnt += 1
                    iWindHPSum += m.health

            if (iWindCnt > 3 or iWindHPSum > 50) and curr_mana > 50:
                self.wind_spell = True

        # if not self.wind_spell and not self.control_spell and not self.shield_spell and curr_mana > 200:
        #    if iWindCnt > 1:
        #        self.wind_spell = True

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
            self.patrol = self.base.mp0

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
            if not self.base.morale:
                # find some monster near me and going ahead to enemy_base
                if self.enemy_base_distance > 7000:
                    l_near = [x for x in l_monster if get_distance_ab(self, x) <= 800]
                    l_near_sort = sorted(l_near, key=lambda m: m.enemy_base_distance)
                    if len(l_near_sort) > 0:
                        self.target = l_near_sort[0]
                        self.find_solution = 'OP'
                if not self.target:
                    if self.find_closest(self, l_monster, current_targets):
                        self.find_solution = 'OP'
            else:
                # find the closest one to enemy_base
                if self.find_closest(enemy_base, l_monster, current_targets):
                    self.find_solution = 'OO'

        # print("T{} ".format(self.target.id if self.target else None), file=sys.stderr, flush=True)
        return self.target.id if self.target else None

    def get_detail(self):
        return "{}-{}-{}-{}".format(
            self.base.stratigic,
            self.role,
            'B'+str(self.ball.id) if self.ball else 'T'+str(self.target.id) if self.target else -1,
            self.find_solution if self.find_solution else '')

    def get_mid_xy(self, ball):
        mid_x = enemy_base.x
        mid_y = enemy_base.y
        if enemy_base.x > h.ball.x:
            mid_x = min(h.ball.x+h.ball.vx+900, enemy_base.x - 1280)
        else:
            mid_x = max(h.ball.x+h.ball.vx-900, 1280)
        if enemy_base.y > h.ball.y:
            mid_y = min(h.ball.y+h.ball.vy+900, enemy_base.y - 1280)
        else:
            mid_y = max(h.ball.y+h.ball.vy-900, 1280)
        return (mid_x, mid_y)


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
    l_monster_sort = sorted(my_base.l_monster, key=lambda m: m.enemy_base_distance)

    # sort heros by distance to the base
    l_hero_sort = []
    for k, v in my_base.heroes.items():
        v.reset_target()
        l_hero_sort.append(v)
    l_hero_sort = sorted(l_hero_sort, key=lambda hero: hero.base_distance)

    # sometime O1 run further than O, change their order
    if l_hero_sort[2].role == 'O1':
        l_hero_sort[1], l_hero_sort[2] = l_hero_sort[2], l_hero_sort[1]

    for h in enemy_base.heroes.values():
        if h.enemy_base_distance < 6000:
            my_base.threat_heros.append(h)
            h.threat_hero = True

    if len(my_base.goal_threat_m) >= 3 and len(my_base.threat_heros) > 0:
        if my_base.stratigic != 'D':
            # Change stratigic, need to reset patrol for heroes
            my_base.stratigic = 'D'
            my_base.stratigic_change = True
        else:
            my_base.stratigic_change = False
    else:
        if my_base.stratigic != 'O':
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
            if i==2:
                curr_hero.role = 'O'
        elif curr_hero.role[0] == 'D':
            curr_hero.role = 'D' + str(iDCnt)
            iDCnt += 1

        if my_base.stratigic_change:
            # Reset hero Patrol route
            my_base.current_targets.append(
                curr_hero.set_patrol_target(my_base.current_targets))
            # print(*my_base.current_targets, file=sys.stderr, flush=True)
            # print("patrol ({}, {})".format(curr_hero.patrol.x, curr_hero.patrol.y), file=sys.stderr, flush=True)

        # use morale to decide patrol_point
        if curr_hero.role == 'O':
            if not my_base.morale \
                and curr_hero.enemy_base_distance >= 5600 \
                    and curr_hero.patrol.id[0] == 'f':
                curr_hero.patrol = curr_hero.base.mp0

    for k, v in enemy_base.heroes.items():
        print("o{} ({}, {})".format(k, v.x, v.y), file=sys.stderr, flush=True)

    for i in range(heroes_per_player):
        curr_hero = l_hero_sort[i]
        print("Decision order: {}, curr ({}, {}), high {}, act_log {}".format(
            curr_hero.id, curr_hero.x, curr_hero.y, my_base.morale, ' '.join(map(str, curr_hero.act_log[:5]))), file=sys.stderr, flush=True)

        # If arrived patrol, go to next one
        if curr_hero.get_distance(curr_hero.patrol) < 600 and hasattr(curr_hero.patrol, 'next'):
            curr_hero.patrol = curr_hero.patrol.next

        if not my_base.morale and curr_hero.role == 'O1':
            curr_hero.role = 'D1'
        # find monster target
        if curr_hero.role != 'O1': # O1 should clone O
            my_base.current_targets.append(curr_hero.find_target(
                my_base.goal_threat_m, my_base.threat_m, my_base.l_monster, my_base.current_targets, enemy_base))
            # print(*my_base.current_targets, file=sys.stderr, flush=True)

        if my_base.morale and curr_hero.role == 'D1':
            # Double attack, D1 => O
            curr_hero.role = 'O1'
        if curr_hero.role == 'O1':
            if curr_hero.get_distance(l_hero_sort[2]) < 800:
                l_hero_sort[2].second_attack_arrive = True

        if curr_hero.role == 'O' and my_base.morale:
            # Attack plan (if any) will over write previous target
            # Move patrol to fight patrol
            if curr_hero.patrol.id[0] == 'm':
                curr_hero.patrol = my_base.fp1
            # Plan how to goal:
            # If I'm close to enemy_base, and I don't have ball, find ball:
            for m in l_monster_sort:
                if get_distance_ab(m, enemy_base) > 7000:
                    break
                if not curr_hero.ball:
                    # Is it a ball?
                    if not m.shld_lf:
                        print("B {} {}".format(curr_hero.get_distance(m), get_distance_ab(m, enemy_base)), file=sys.stderr, flush=True)
                        if curr_hero.get_distance(m) <= 1280 \
                            and get_distance_ab(m, enemy_base) < 2200 + 400 + 30 + (2200 if curr_hero.second_attack_arrive and get_distance_ab(l_hero_sort[1], m) <= 1280 else 0):
                            # Near enough, kick it
                            curr_hero.ball = m
                            curr_hero.wind_spell = True
                            if (get_distance_ab(l_hero_sort[1], m) <= 1280 and l_hero_sort[1].role=='O1'):
                                l_hero_sort[1].wind_spell = True
                        elif m.threatFor != 2 \
                            and curr_hero.get_distance(m) <= 2200:
                            curr_hero.ball = m
                            curr_hero.control_spell = str(m.id)
                        elif m.health > get_distance_ab(m, enemy_base)/400*2 \
                            and curr_hero.get_distance(m) <= 2200:
                            # It's a strong ball, shield it
                            curr_hero.ball = m
                            curr_hero.shield_spell = str(m.id)
                        elif curr_hero.get_distance(m) <= 1280 \
                            and get_distance_ab(m, enemy_base) < 6500 \
                            and curr_hero.enemy_base_distance < m.enemy_base_distance:
                            curr_hero.ball = m
                            curr_hero.wind_spell = True
                        else: # it's ball, but either too far or too weak, Wait and see
                            curr_hero.ball = m
                    else: # it's shield
                        # Is it target enemy?
                        if m.threatFor == 2:
                            # Looks good, follow and protect
                            curr_hero.ball = m

        if curr_hero.ball:
            curr_hero.target = None
            curr_hero.patrol = curr_hero.base.fp3

        # should I use spell or should I just farming
        if curr_hero.role != 'O1':
            if curr_hero.spell_check(my_base.l_monster, my_base.mana):
                my_base.mana -= 10

    if l_hero_sort[1].role == 'O1':
        l_hero_sort[1].target = l_hero_sort[2].target if l_hero_sort[2].target else l_hero_sort[2]
        l_hero_sort[1].ball = l_hero_sort[2].ball
        l_hero_sort[1].find_solution = 'CL' # Clone

    for h in l_heroes:
        # print("Command order: " + str(h.id), file=sys.stderr, flush=True)
        if h.wind_spell:
            if h.role[0] == 'O':
                m = h.ball if h.ball else h.target
                print("SPELL WIND {} {} {}".format(
                    enemy_base.x-(m.x-h.x), # enemy_base.x if abs(m.x-enemy_base.x) > 30 else h.x,
                    enemy_base.y-(m.y-h.y), # enemy_base.y if abs(m.y-enemy_base.y) > 30 else h.y,
                    h.get_detail()))
            # elif len(my_base.threat_heros) == 1 and h.get_distance(my_base.threat_heros[0]) > 1280:
            #     t = my_base.threat_heros[0]
            #     if my_base.x == 0 and  t.x+2000 <= t.y:
            #         print("SPELL WIND {} {} {}".format(
            #             6500, 400, h.get_detail()))
            #     elif my_base.x == 0 and t.x > t.y+2000:
            #         print("SPELL WIND {} {} {}".format(
            #             400, 6500, h.get_detail()))
            #     elif my_base.x == 17630 and 17630-t.x+2000 <= 9000-t.y:
            #         print("SPELL WIND {} {} {}".format(
            #             17630-6500, 9000-400, h.get_detail()))
            #     elif my_base.x == 17630 and 17630-t.x > 9000-t.y+2000:
            #         print("SPELL WIND {} {} {}".format(
            #             17630-400, 9000-6500, h.get_detail()))
            #     else:
            #         print("SPELL WIND {} {} {}".format(
            #             enemy_base.x, enemy_base.y, h.get_detail()))
            else:
                print("SPELL WIND {} {} {}".format(
                    30 if enemy_base.x == 0 else enemy_base.x - 30,
                    30 if enemy_base.y == 0 else enemy_base.y - 30, h.get_detail()))
            h.act_log[:0] = ['W']
        elif h.shield_spell:
            print("SPELL SHIELD {} {}".format(h.shield_spell, h.get_detail()))
            h.act_log[:0] = ['S']
        elif h.control_spell:
            print("SPELL CONTROL {} {} {} {}".format(
                h.control_spell, enemy_base.x if int(h.control_spell) > 5 else 8800, enemy_base.y if int(h.control_spell) > 5 else 4500, h.get_detail()))
            h.act_log[:0] = ['C']
        elif h.ball:
            # If ball is threat, I want to protect it, otherwise I just follow it
            if h.ball.threatFor == 2 and h.ball.nearBase and h.role=='O':
                # Is there any enemy hero close to the ball?
                l_e_hero_sort = []
                for k, v in enemy_base.heroes.items():
                    v.protect_distance = get_distance_ab(v, h.ball)
                    l_e_hero_sort.append(v)
                l_e_hero_sort = sorted(l_e_hero_sort, key=lambda hero: hero.protect_distance)

                control_enemy = None
                for i in l_e_hero_sort:
                    if not i.shld_lf and h.get_distance(i) < 2200 \
                        and my_base.mana >= 10 and get_distance_ab(i, h.ball) < 2200:
                        control_enemy = str(i.id)
                        break
                if control_enemy:
                    print("SPELL CONTROL {} {} {} {}".format(
                    control_enemy, 8800, 4500, h.get_detail()+'-PRT'))
                    h.act_log[:0] = ['C']
                else:
                    mid = h.get_mid_xy(h.ball)
                    print("MOVE {} {} {}".format(mid[0], mid[1], h.get_detail()+'-MID'))
                    h.act_log[:0] = [None]
            else:
                # Go between ball and enemy_base
                mid = h.get_mid_xy(h.ball)
                print("MOVE {} {} {}".format(mid[0], mid[1], h.get_detail()))
                h.act_log[:0] = [None]
        elif h.target:
            print("MOVE {} {} {}".format(h.target.x+(h.target.vx if h.target.id>5 else 0),
                h.target.y+(h.target.vy if h.target.id>5 else 0), h.get_detail()))
            h.act_log[:0] = [None]
        else:
            print("MOVE {} {} {}".format(h.patrol.x, h.patrol.y, h.get_detail()))
            h.act_log[:0] = [None]

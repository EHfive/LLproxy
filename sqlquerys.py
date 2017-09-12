import json
import time
import hashlib
import sqlite3
from urllib import parse
from pymysql import escape_string


def game_db_init():
    global live_setting_id, unit_db
    unit_db = sqlite3.connect("./db/unit/unit.db_", check_same_thread=False)
    battle = sqlite3.connect("./db/event/battle.db_").execute(
        "SELECT live_difficulty_id,live_setting_id FROM event_battle_live_m").fetchall()
    festival = sqlite3.connect("./db/event/festival.db_").execute(
        "SELECT live_difficulty_id,live_setting_id FROM event_festival_live_m").fetchall()
    marathon = sqlite3.connect("./db/event/marathon.db_").execute(
        "SELECT live_difficulty_id,live_setting_id FROM event_marathon_live_m").fetchall()
    challenge = sqlite3.connect("./db/challenge/challenge.db_").execute(
        "SELECT live_difficulty_id,live_setting_id FROM event_challenge_live_m").fetchall()
    live_db = sqlite3.connect("./db/live/live.db_")
    live_setting_normal = live_db.execute("SELECT live_difficulty_id,live_setting_id FROM normal_live_m").fetchall()
    live_setting_special = live_db.execute("SELECT live_difficulty_id,live_setting_id FROM special_live_m").fetchall()
    ress = []
    ress.extend(live_setting_normal)
    ress.extend(live_setting_special)
    ress.extend(marathon)
    ress.extend(battle)
    ress.extend(festival)
    ress.extend(challenge)
    live_setting_id = dict(ress)


def get_setting_id(live_difficulty_id, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    try:
        return live_setting_id[live_difficulty_id]
    except KeyError:
        game_db_init()
        try:
            return live_setting_id[live_difficulty_id]
        except KeyError:
            return 'null'


def add_user(user_info_source, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    user = user_info_source["res_data"]["user"]

    sql = """
    INSERT INTO `llproxy`.`users` (
    	`uid`, `name`, `token`, 
    	`level`, `invite_code`, `update_time`
    ) 
    VALUES 
    	(
    		'{uid}', '{name}', '{token}', 
    		'{level}', '{invite_code}', '{update_time}'
    	)
    ON DUPLICATE KEY UPDATE `name`=VALUES(`name`),`token`=VALUES(`token`),`level`=VALUES(`level`),
    `invite_code`=VALUES(`invite_code`),`update_time`=VALUES(`update_time`);
        """.format(
        uid=user["user_id"],
        name=escape_string(user['name']),
        level=user["level"],
        token=user_info_source["token"],
        invite_code=user["invite_code"],
        update_time=update_time
    )

    return sql,


def update_user(dict, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    sql = []

    if 'name' in dict:
        sqln = """
        INSERT INTO `llproxy`.`users` (
        	`uid`, `name`, `update_time`
        ) 
        VALUES 
        	(
        		'{uid}', '{name}', '{update_time}'
        	)
        ON DUPLICATE KEY UPDATE `name`=VALUES(`level`),update_time=VALUES(update_time);
        """.format(
            uid=dict["uid"],
            name=escape_string(dict["name"]),
            update_time=update_time
        )
        sql.append(sqln)
    if 'level' in dict:
        sqln = """
        INSERT INTO `llproxy`.`users` (
        	`uid`, `level`, `update_time`
        ) 
        VALUES 
        	(
        		'{uid}', '{level}', '{update_time}'
        	)
        ON DUPLICATE KEY UPDATE `level`=VALUES(`level`),update_time=VALUES(update_time);
            """.format(
            uid=dict["uid"],
            level=dict["level"],
            update_time=update_time
        )
        sql.append(sqln)
    if 'login_key' in dict:
        sqln = """
        INSERT INTO `llproxy`.`users` (
        	`uid`, `login_key`, `update_time`
        ) 
        VALUES 
        	(
        		'{uid}', '{login_key}', '{update_time}'
        	)
        ON DUPLICATE KEY UPDATE `login_key`=VALUES(login_key),update_time=VALUES(update_time);
            """.format(
            uid=dict["uid"],
            login_key=dict["login_key"],
            update_time=update_time
        )
        sql.append(sqln)
    return sql


def replace_unit(uid, unit_info_array, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    sql = []
    sql0 = "DELETE FROM unit_unitAll  WHERE status = 0"
    sql1 = "UPDATE unit_unitAll set status=0 WHERE uid=%s" % uid

    keysl = list(unit_info_array[0].keys())
    keys = "(`uid`,`update_time`,`status`,`unit_number`, `unit_type_id`, `rarity`, `attribute_id`, " + ",".join(
        keysl) + ")"
    valuesl = []
    cur = unit_db.cursor()
    for i in unit_info_array:
        unit_id = i['unit_id']
        cur.execute("SELECT unit_number,unit_type_id,rarity,attribute_id FROM unit_m WHERE unit_id = %s" % unit_id)
        u = cur.fetchone()
        if u:
            s = "('{}','{}','{}','{}','{}','{}','{}'".format(uid, update_time, 1, u[0], u[1], u[2], u[3])
        else:
            s = "('{}','{}','{}',NULL,NULL,NULL,NULL".format(uid, update_time, 1)
        for k in i.values():
            if k is True:
                k = 1
            elif k is False:
                k = 0
            s += ",'%s'" % k

        s += ")"
        valuesl.append(s)

    values = ",".join(valuesl)

    sql2 = """
        REPLACE INTO `llproxy`.`unit_unitAll`
        {}
        VALUES
        {}
        """.format(keys, values)
    sql3 = """
                INSERT INTO `llproxy`.`deck_and_removable_Info` (`uid`, `update_time`, `unit_info`) 
                VALUES ('{}', '{}', '{}')
                ON DUPLICATE KEY UPDATE `unit_info`=VALUES(unit_info),update_time=VALUES(update_time);
                """.format(uid, update_time,
                           escape_string(json.dumps(unit_info_array, separators=(',', ':'), ensure_ascii=False)))

    sql.append(sql0)
    sql.append(sql1)
    sql.append(sql2)
    sql.append(sql3)
    return sql


def score_match_status_0(uid, event_id, room_id, res, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    sql = []

    total_event_point = 0
    event_rank = 0
    unit_id = 0
    display_rank = 1
    setting_award_id = 1
    playes = []
    for u in res['matching_user']:
        if 'user_info' in u:
            user_id = u['user_info']['user_id']
            playes.append(str(user_id))
            if int(user_id) == int(uid):
                total_event_point = u['event_status']['total_event_point']
                event_rank = u['event_status']['event_rank']
                unit_id = u['center_unit_info']['unit_id']
                display_rank = u['center_unit_info']['display_rank']
                setting_award_id = u['setting_award_id']

    if 'live_info' in res:
        setting_id = get_setting_id(res['live_info'][0]['live_difficulty_id'])
        sql1 = """
        INSERT INTO `llproxy`.`score_match` (`uid`, `status`, `event_id`, `event_battle_room_id`, `event_rank`, `total_event_point`, `added_event_point`, `unit_id`, `display_rank`,
         `setting_award_id`, `live_difficulty_id`, `live_setting_id`,`use_quad_point`, `is_random`, `dangerous`,`update_time`,`judge_card`)
    VALUES ('{}', '{}', '{}', '{}', '{}','{}', '{}', '{}', '{}', '{}', '{}', {},{}, {}, {},{},{});
        """.format(uid, 0, event_id, room_id, event_rank, total_event_point, 0, unit_id, display_rank,
                   setting_award_id, res['live_info'][0]['live_difficulty_id'], setting_id,
                   res['live_info'][0]['use_quad_point'],
                   res['live_info'][0]['is_random'], res['live_info'][0]['dangerous'], update_time, -1)
        sql.append(sql1)

        sql2 = """
        REPLACE INTO `llproxy`.`score_match_rooms` (`event_id`, `update_time`, `event_battle_room_id`, `status`, `players`, `matching_user`, `live_difficulty_id`, `live_setting_id`,
        `use_quad_point`, `is_random`, `dangerous`)
         VALUES ('{}', '{}', '{}', '0', '{}', '{}', '{}',{}, {}, {}, {});
        """.format(event_id, update_time, room_id, ','.join(playes),
                   escape_string(json.dumps(res['matching_user'], separators=(',', ':'), ensure_ascii=False)),
                   res['live_info'][
                                      0]['live_difficulty_id'], setting_id, res['live_info'][0]['use_quad_point'],
                   res['live_info'][0]['is_random'], res['live_info'][0]['dangerous'])
        sql.append(sql2)
    else:
        sql2 = """
                UPDATE `llproxy`.`score_match_rooms` SET  `update_time`='{}', `status`='0',`players`='{}', 
                `matching_user`='{}' WHERE  event_battle_room_id ='{}' AND event_id={}
                """.format(update_time, ','.join(playes),
                           escape_string(json.dumps(res['matching_user'], separators=(',', ':'), ensure_ascii=False)),
                           room_id, event_id)
        sql.append(sql2)
    return sql


def score_match_status_1(uid, event_id, room_id, req, judge_card=-1, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    sql1 = "UPDATE `llproxy`.`score_match` SET `status` = '1',`update_time`={},`judge_card`={} WHERE uid = {} AND event_battle_room_id ={} AND event_id={};".format(
        update_time, judge_card, uid, room_id, event_id)
    sql2 = "UPDATE `llproxy`.`score_match_rooms` SET `status` = '1',`update_time`={} WHERE  event_battle_room_id ={} AND event_id={};".format(
        update_time, room_id, event_id)
    return sql1, sql2


def pub_live_info(live_difficulty_id, merge_live_info, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    setting_id = get_setting_id(live_difficulty_id)
    json_str = json.dumps(merge_live_info, separators=(',', ':'))
    sql = """
    REPLACE INTO `llproxy`.`pub_live_info` (`live_difficulty_id`, `live_setting_id`,`update_time`, `is_random`, `dangerous`, `notes_speed`,  `merge_info_json`)
     VALUES ('{}',{}, '{}', {}, {}, {}, '{}')
    """.format(live_difficulty_id, setting_id, update_time, merge_live_info['live_info']['is_random'],
               merge_live_info['live_info']['dangerous'], merge_live_info['live_info']['notes_speed'],
               json_str)
    return sql,


def score_match_status_2(uid, event_id, room_id, req, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    sql1 = "UPDATE `llproxy`.`score_match` SET `status` = '2',`perfect_cnt` = '{}', `great_cnt` = '{}', `good_cnt` = '{}', `bad_cnt` = '{}', `love_cnt` = '{}', `miss_cnt` = '{}',`max_combo` = '{}',`score`= '{}',`update_time`={} WHERE uid = {} AND event_battle_room_id ={} AND event_id={};".format(
        req['perfect_cnt'], req['great_cnt'], req['good_cnt'], req['bad_cnt'], req['love_cnt'],
        req['miss_cnt'], req['max_combo'], req['score_smile'] + req['score_cute'] + req['score_cool'],
        update_time, uid, room_id, event_id)
    sql2 = "UPDATE `llproxy`.`score_match_rooms` SET `status` = '2',`update_time`={} WHERE  event_battle_room_id ={} AND event_id={};".format(
        update_time, room_id, event_id)
    return sql1, sql2


def score_match_status_3(uid, event_id, room_id, res, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    point_info = res['event_info']['event_point_info']
    sql1 = "UPDATE `llproxy`.`score_match` SET `status` = '3',`total_event_point` = '{}', `added_event_point` = '{}',`update_time`={}  WHERE uid = {} AND event_battle_room_id ={} AND event_id={};".format(
        point_info['after_total_event_point'], point_info['added_event_point'], update_time, uid,
        room_id, event_id)

    sql2 = """
        UPDATE `llproxy`.`score_match_rooms` SET `update_time`='{}', `status`='3',  `matching_user`='{}' WHERE  event_battle_room_id ={} AND event_id={}
        """.format(update_time,
                   escape_string(json.dumps(res['matching_user'], separators=(',', ':'), ensure_ascii=False)), room_id,
                   event_id)

    return sql1, sql2


def live_play(source, judge_card=-1, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    sqln = []
    res = source['res_data']
    req = source['req_data']
    uid = source['user_id']
    live_info = (res['live_info'][0]['live_difficulty_id'],
                 res['live_info'][0]['is_random'],
                 res['live_info'][0]['dangerous'],
                 res['live_info'][0]['use_quad_point']
                 )
    setting_id = get_setting_id(live_info[0])
    notes_info = (req['perfect_cnt'],
                  req['great_cnt'],
                  req['good_cnt'],
                  req['bad_cnt'],
                  req['miss_cnt'],
                  req['max_combo']
                  )
    score_info = (
        req['score_smile'] + req['score_cute'] + req['score_cool'],
        req['love_cnt']
    )
    event_info = [req['event_id'], req['event_point']]
    if event_info[0] is None:
        event_info[0] = 'NULL'
    elif 'event_info' in res:
        item_ids = []
        add_types = []
        amounts = []
        for reward in res['event_info']['event_reward_info']:
            if 'item_id' in reward:
                item_ids.append(str(reward['item_id']))
            else:
                item_ids.append('')
            add_types.append(str(reward['add_type']))
            amounts.append(str(reward['amount']))
        eventIFO = [res['event_info']['event_id'], res['event_info']['event_point_info']['after_event_point'],
                    res['event_info']['event_point_info']['after_total_event_point'],
                    res['event_info']['event_point_info']['added_event_point']]
        if req['event_point'] == 0:
            iseventsong = 1
        else:
            iseventsong = 0

        sqle = """
            INSERT INTO `llproxy`.`event_traditional` (`id`, `update_time`, `uid`,`live_setting_id`, `live_difficulty_id`, `is_random`, `dangerous`,`use_quad_point`, `score`, 
            `perfect_cnt`, `great_cnt`, `good_cnt`, `bad_cnt`, `miss_cnt`, `max_combo`, `love_cnt`, `event_id`, `event_point`,
            `total_event_point`,`added_event_point`,`event_rewards_item_id`,`event_rewards_add_type`,`event_rewards_amount`,`is_event_song`,`judge_card`)
             VALUES (NULL, '{}', '{}', {},'{}', {}, {}, {},'{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', {}, '{}', '{}', '{}', '{}', '{}', '{}',{},{})
            """.format(update_time, uid, setting_id, live_info[0], live_info[1], live_info[2], live_info[3],
                       score_info[0],
                       notes_info[0], notes_info[1], notes_info[2], notes_info[3], notes_info[4], notes_info[5],
                       score_info[1], eventIFO[0], eventIFO[1],
                       eventIFO[2], eventIFO[3], ','.join(item_ids), ','.join(add_types), ','.join(amounts),
                       iseventsong, judge_card
                       )
        sqln.append(sqle)

    sql = """
    INSERT INTO `llproxy`.`live` (`id`, `update_time`, `uid`,`live_setting_id`, `live_difficulty_id`, `is_random`, `dangerous`,`use_quad_point`, `score`, 
    `perfect_cnt`, `great_cnt`, `good_cnt`, `bad_cnt`, `miss_cnt`, `max_combo`, `love_cnt`,  `event_id`, `event_point`,`judge_card`)
     VALUES (NULL, '{}', '{}',{}, '{}', {}, {}, {},'{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', {}, '{}',{})
    """.format(update_time, uid, setting_id, live_info[0], live_info[1], live_info[2], live_info[3],
               score_info[0],
               notes_info[0], notes_info[1], notes_info[2], notes_info[3], notes_info[4], notes_info[5], score_info[1],
               event_info[0], event_info[1], judge_card)
    sqln.append(sql)

    return sqln


def deck_info(source, notbyApi=False, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    uid = source['user_id']

    if notbyApi is False:
        res = source['res_data']['result']
    else:
        res = source['req_data']['unit_deck_list']
        for k in range(0, len(res)):
            res[k]['unit_owning_user_ids'] = res[k]['unit_deck_detail']
            del res[k]['unit_deck_detail']

    sql = """
            INSERT INTO `llproxy`.`deck_and_removable_Info` (`uid`, `update_time`, `deck_info`, `removable_info`) 
            VALUES ('{}', '{}', '{}', NULL)
            ON DUPLICATE KEY UPDATE `deck_info`=VALUES(deck_info),update_time=VALUES(update_time);
            """.format(uid, update_time, escape_string(json.dumps(res, separators=(',', ':'), ensure_ascii=False)))

    return sql,


def removeable_skill_info(source, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    sqln = []
    uid = source['user_id']
    res = source['res_data']['result']
    sql = """
                INSERT INTO `llproxy`.`deck_and_removable_Info` (`uid`, `update_time`, `deck_info`, `removable_info`) 
                VALUES ('{}', '{}', NULL, '{}')
                ON DUPLICATE KEY UPDATE `removable_info`=VALUES(removable_info),update_time=VALUES(update_time);
                """.format(uid, update_time,
                           escape_string(json.dumps(res, separators=(',', ':'), ensure_ascii=False)))
    sqln.append(sql)
    for k, v in res['equipment_info'].items():
        detail = [str(x['unit_removable_skill_id']) for x in v['detail']]
        sqli = """
        UPDATE `llproxy`.`unit_unitAll` SET `unit_removable_skill_id` = '{}' WHERE `unit_unitAll`.`unit_owning_user_id` = {} 
        """.format(','.join(detail), v['unit_owning_user_id'])
        sqln.append(sqli)

    return sqln


def secretbox(source, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    uid = source['user_id']
    res = source['res_data']
    boxifo = res['secret_box_info']
    is_support_member = 0
    cnt = [-99, 0, 0, 0, 0, 0]
    unit_ids = []
    rarity_ids = []
    count = 1
    if 'count' in source['req_data']:
        count = source['req_data']['count']
    for unit in res['secret_box_items']['unit']:
        cnt[unit['unit_rarity_id']] += 1
        unit_ids.append(str(unit['unit_id']))
        rarity_ids.append(str(unit['unit_rarity_id']))
        if unit['is_support_member']:
            is_support_member = 1
    if ('item_id' not in boxifo['cost']) or (boxifo['cost']['item_id'] is None):
        boxifo['cost']['item_id'] = 'NULL'

    sql = """
    INSERT INTO `llproxy`.`secretbox` (`uid`, `update_time`, `secret_box_page_id`, `secret_box_id`, `name`, `cost_item_id`, 
    `result_unit_ids`, `result_rarity_ids`,`n_cnt`, `r_cnt`, `sr_cnt`, `ssr_cnt`, `ur_cnt`, `is_support_member`, `multi_count`) 
    VALUES ('{}', '{}', '{}', '{}', '{}', {}, 
    '{}', '{}', '{}', '{}','{}', '{}', '{}', '{}','{}')
    """.format(uid, update_time, res['secret_box_page_id'], boxifo['secret_box_id'], boxifo['name'],
               boxifo['cost']['item_id'],
               ','.join(unit_ids), ','.join(rarity_ids), cnt[1], cnt[2], cnt[3], cnt[5], cnt[4], is_support_member,
               count)

    return sql,


def effort_point_box(uid, effort_point_array, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    sqln = []
    for box in effort_point_array:
        if len(box['rewards']) == 0:
            continue
        box_spec_id = box['live_effort_point_box_spec_id']
        capacity = box['capacity']
        item_ids = []
        add_types = []
        amounts = []
        for reward in box['rewards']:
            if 'item_id' in reward:
                item_ids.append(str(reward['item_id']))
            elif 'unit_id' in reward:
                item_ids.append(str(reward['unit_id']))
            else:
                item_ids.append('')
                open('log.txt', 'a').write(json.dumps(effort_point_array) + '\n\n')
            add_types.append(str(reward['add_type']))
            amounts.append(str(reward['amount']))
        sql = """INSERT INTO `llproxy`.`effort_point_box` 
              (`uid`, `update_time`, `box_spec_id`, `capacity`, `rewards_item_id`, `rewards_add_type`, `rewards_amount`)
              VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')
              """.format(uid, update_time, box_spec_id, capacity, ','.join(item_ids),
                         ','.join(add_types), ','.join(amounts))
        sqln.append(sql)
    return sqln


def user_info(user_info_obj, user_id=None, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    u = user_info_obj
    if user_id is None:

        sql = """
        REPLACE INTO `llproxy`.`user_info` 
        (`user_id`, `name`, `level`, `exp`, `previous_exp`, `next_exp`, `game_coin`, `sns_coin`, `paid_sns_coin`, 
        `social_point`, `unit_max`, `energy_max`, `energy_full_time`, 
         `over_max_energy`, `friend_max`, `invite_code`, `insert_date`, `update_date`, `update_time`) 
        VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', 
        '{}','{}', '{}', '{}', 
        '{}', '{}', '{}', '{}', '{}', '{}')
        """.format(u['user_id'], escape_string(u['name']), u['level'], u['exp'], u['previous_exp'], u['next_exp'],
                   u['game_coin'],
                   u['sns_coin'], u['paid_sns_coin']
                   , u['social_point'], u['unit_max'], u['energy_max'], u['energy_full_time'],
                   u['over_max_energy'], u['friend_max'], u['invite_code'], u['insert_date'], u['update_date'],
                   update_time)
    else:
        sql = """
        UPDATE `llproxy`.`user_info` set `level`='{}',`exp`='{}', `previous_exp`='{}', `next_exp`='{}', `game_coin`='{}', `sns_coin`='{}', 
        `social_point`='{}', `unit_max`='{}', `energy_max`='{}', `energy_full_time`='{}', 
         `over_max_energy`='{}', `friend_max`='{}',`update_time`='{}' WHERE user_id='{}'
        """.format(u['level'], u['exp'], u['previous_exp'], u['next_exp'], u['game_coin'], u['sns_coin']
                   , u['social_point'], u['unit_max'], u['energy_max'], u['energy_full_time']
                   , u['over_max_energy'], u['friend_max'], update_time, user_id)
    # print(sql)
    return sql,


def user_navi(navi_info_dict, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    i = navi_info_dict
    sql = """
            UPDATE `llproxy`.`user_info` set `navi_owning_id`={},update_time={} WHERE user_id='{}'
            """.format(i['unit_owning_user_id'], update_time, i['uid'])

    return sql,


def display_rank(info_dict, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    i = info_dict
    sql = """
    UPDATE `llproxy`.`unit_unitAll` set `display_rank` = {} ,`update_time`={} WHERE unit_owning_user_id ={}
    """.format(i['display_rank'], update_time, i['unit_owning_user_id'])

    return sql,


def challenge_user_rplc(info_dict, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    i = info_dict
    sql = """
    REPLACE INTO event_challenge_users (uid, event_id, curr_pair_id, curr_round, total_event_point, high_score, finalized, update_time)
    VALUES (
    '{}','{}','{}','{}','{}','{}',{},'{}'
    )
    """.format(i['uid'], i['event_id'], i['curr_pair_id'], i['curr_round'], i['total_event_point'], i['high_score'],
               i['finalized'], update_time)
    return sql,


def challenge_pair_init(uid, event_id, pair_id, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    sql = """
    INSERT INTO `event_challenge_pairs` (`uid`,`event_id`,`pair_id`,`curr_round`,`finalized`,`update_time`)
    VALUES ('{}','{}','{}','0','0','{}')
    """.format(uid, event_id, pair_id, update_time)
    return sql,


def challenge_proceed(s_proceed, s_check, pair_id, round_n, finalized, judge_card=-1, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    sqln = []
    if s_proceed:
        challenge_items = s_proceed['req_data']['event_challenge_item_ids']
    else:
        challenge_items = []
    req = s_check['req_data']
    res = s_check['res_data']
    try:
        setid = live_setting_id[req['live_difficulty_id']]
    except KeyError:
        setid = 'NULL'
    chall_res = res['challenge_result']
    linf = chall_res['live_info'][0]
    lp = 0
    for mission in chall_res['mission_result']:
        if (mission['bonus_type'] == 3050) and mission['achieved']:
            lp += int(mission['bonus_param'])
    item_cost = [0, 15000, 5000, 12500, 12500, 25000, 50000, 0]
    try:
        sum_cost = sum([item_cost[x] for x in challenge_items])
    except:
        sum_cost = 0
    challenge_items = json_dump(challenge_items)
    if finalized:
        sql = """
            update  `event_challenge_pairs` set `curr_round`='{}',finalized={},update_time='{}',round_setid_{}='{}',
            lp_add=lp_add+{}, coin_cost=coin_cost+{}
            WHERE uid= {} AND pair_id= {}
            """.format(round_n, finalized, update_time, round_n, setid, lp, sum_cost, s_check['user_id'], pair_id)
        sqln.append(sql)
    elif res['challenge_info']:
        reward_i = res['challenge_info']['accumulated_reward_info']
        rarity_l = [0, 0, 0, 0]
        for r in reward_i['reward_rarity_list']:
            rarity_l[r['rarity']] = r['amount']

        sql = """
            update  `event_challenge_pairs` set `curr_round`='{}',finalized={},player_exp='{}',game_coin='{}',
            event_point='{}',rarity_3_cnt='{}',rarity_2_cnt='{}',rarity_1_cnt='{}',update_time='{}',round_setid_{}={},
            lp_add=lp_add+{}, coin_cost=coin_cost+{}
            WHERE uid={} AND pair_id= {}
            """.format(round_n, finalized, reward_i['player_exp'], reward_i['game_coin'], reward_i['event_point'],
                       rarity_l[3], rarity_l[2], rarity_l[1], update_time, round_n, setid,
                       lp, sum_cost, s_check['user_id'], pair_id)
        sqln.append(sql)

    sql2 = """
    INSERT INTO event_challenge (pair_id, round, update_time, uid, live_setting_id, live_difficulty_id, is_random, dangerous,
                             use_quad_point, score, perfect_cnt, great_cnt, good_cnt, bad_cnt, miss_cnt, max_combo, 
                             love_cnt, judge_card, event_id, event_point, rank, combo_rank, mission_result, 
                             reward_rarity_list, bonus_list,event_challenge_item_ids) 
    VALUES ('{}','{}','{}','{}',{},'{}',{},{},
    {},'{}','{}','{}','{}','{}','{}','{}',
    '{}',{},'{}','{}','{}','{}','{}',
    '{}','{}','{}'
    )""".format(
        pair_id, round_n, update_time, s_check['user_id'], setid, linf['live_difficulty_id'], linf['is_random'],
        linf['dangerous'], linf['use_quad_point'], req['score_smile'] + req['score_cute'] + req['score_cool'],
        req['perfect_cnt'], req['great_cnt'], req['good_cnt'], req['bad_cnt'], req['miss_cnt'],
        req['max_combo'], req['love_cnt'], judge_card, req['event_id'], chall_res['reward_info']['event_point'],
        chall_res['rank'], chall_res['combo_rank'], escape_string(json.dumps(chall_res['mission_result'])),
        escape_string(json.dumps(chall_res['reward_info']['reward_rarity_list'])),
        escape_string(json.dumps(chall_res['bonus_list'])), challenge_items
    )
    sqln.append(sql2)
    return sqln


def challenge_finalize(source, pair_id, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    res = source['res_data']
    eventp = res['event_info']['event_point_info']
    rarity_l = [0, 0, 0, 0]
    ticket = 0
    exp = 0
    coin = 0
    for r in res['reward_item_list']:
        rarity_l[r['rarity']] += 1
        if r['add_type'] == 1000 and r['item_id'] == 1:
            ticket += r['amount']
        elif r['add_type'] == 3000:
            coin += r['amount']
        elif r['add_type'] == 1001:
            try:
                unit_id = r['unit_id']
            except KeyError:
                continue

            if unit_id < 379 or unit_id > 1142:
                continue
            if 382 >= unit_id >= 379:
                exp += 10
            elif unit_id <= 386 or unit_id == 1050:
                exp += 100
            elif unit_id <= 390 or unit_id == 1085:
                exp += 1000
    sql = """
    UPDATE event_challenge_pairs SET finalized=1,player_exp='{}',game_coin='{}',event_point='{}',after_event_point='{}',
    total_event_point='{}',added_event_point='{}',reward_item_list='{}',update_time='{}',rarity_3_cnt={},rarity_2_cnt={}
    ,rarity_1_cnt={},ticket_add={},skill_exp_add={},coin_reward={} WHERE uid = '{}' AND pair_id='{}'
    """.format(res['base_reward_info']['player_exp'], res['base_reward_info']['game_coin'],
               eventp['added_event_point'], eventp['after_event_point'], eventp['after_total_event_point'],
               eventp['added_event_point'], escape_string(json.dumps(res['reward_item_list'])), update_time,
               rarity_l[3], rarity_l[2], rarity_l[1], ticket, exp, coin,
               source['user_id'], pair_id
               )
    sql2 = """
    update `event_challenge_users` set finalized=1,total_event_point = '{}'
    """.format(eventp['after_total_event_point'])
    return sql, sql2


def request_cache(source, stat=1, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    s = source
    m = source['modules']
    sql = """INSERT INTO request_cache (status, uid, m0, m1, path, headers, request, response, req_time) 
          VALUES ({},{},'{}','{}','{}','{}','{}','{}',{})""".format(stat, s['user_id'], m[0], m[1],
                                                                    escape_string(s['path']),
                                                                    json_dump(s['headers'].items()),
                                                                    json_dump(s['req_data']),
                                                                    json_dump(s['res_data']), update_time)

    return sql,


def festival_start(source, pair_id, judge_card=-1, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    s = source
    req = s['req_data']
    res = s['res_data']
    song_diff_ids = []
    song_set_ids = []
    total_combo = 0
    guest_bonus = []
    sub_guest_bonus = []
    item_cost = [0, 30000, 10000, 5000, 25000, 25000, 50000, 100000, 50000]
    sum_cost = sum([item_cost[x] for x in req['event_festival_item_ids']])
    for live in res['live_info']:
        song_diff_ids.append(live['live_difficulty_id'])
        song_set_ids.append(live_setting_id[live['live_difficulty_id']])
        total_combo += len(live['notes_list'])
        del live['notes_list']

        try:
            guest_bonus.append(live['guest_bonus'])
        except KeyError:
            # print(live)
            guest_bonus.append(None)
        try:
            sub_guest_bonus.append(live['sub_guest_bonus'])
        except KeyError:
            sub_guest_bonus.append(None)
    sql = """INSERT INTO event_festival_users (uid, event_id, curr_pair_id, `status`, update_time, last_song_set_ids) 
    VALUES ('{}','{}','{}',0,'{}','{}')
    ON DUPLICATE KEY UPDATE event_id = VALUES(event_id),curr_pair_id = VALUES(curr_pair_id),`status`=VALUES(`status`),
    update_time=VALUES(update_time),last_song_set_ids=VALUES(last_song_set_ids)
    """.format(s['user_id'], req['event_id'], pair_id, update_time, json_dump(song_set_ids))
    sql2 = """INSERT INTO event_festival (uid, event_id, `status`, pair_id, song_diff_ids, song_set_ids, update_time, 
    total_combo, event_festival_item_ids, guest_bonus,sub_guest_bonus,coin_cost,judge_card) 
    VALUES ('{}','{}',0,'{}','{}','{}','{}','{}','{}','{}','{}','{}',{})
    """.format(s['user_id'], req['event_id'], pair_id, json_dump(song_diff_ids), json_dump(song_set_ids),
               update_time, total_combo, json_dump(req['event_festival_item_ids']), json_dump(guest_bonus),
               json_dump(sub_guest_bonus), sum_cost, judge_card)
    return sql, sql2


def festival_reward(source, pair_id, score, update_time=None):
    if update_time is None:
        update_time = int(time.time())
    s = source
    req = s['req_data']
    res = s['res_data']
    reward_items = []
    ticket_add = 0
    rarity_cnt = [0, 0, 0, 0]
    pt_ifo = res['event_info']['event_point_info']
    exp = 0
    coin = 0
    for reward_type in res['reward_item_list'].values():
        for reward in reward_type:
            add_type = reward['add_type']
            re = {
                'add_type': add_type,
                'rarity': reward['rarity'],
                'amount': reward['amount']
            }
            rarity_cnt[reward['rarity']] += 1
            if add_type == 1001:
                re['unit_id'] = reward['unit_id']
                unit_id = reward['unit_id']
                if unit_id < 379 or unit_id > 1142:
                    continue
                if 382 >= unit_id >= 379:
                    exp += 10
                elif unit_id <= 386 or unit_id == 1050:
                    exp += 100
                elif unit_id <= 390 or unit_id == 1085:
                    exp += 1000
            else:
                re['item_id'] = reward['item_id']
            if add_type == 1000 and reward['item_id'] == 1:
                ticket_add += reward['amount']
            elif add_type == 3000:
                coin += reward['amount']
            reward_items.append(re)
    score_curr = req['score_smile'] + req['score_cute'] + req['score_cool']
    sql = """UPDATE event_festival_users SET total_event_point='{}',high_score='{}',curr_pair_id='{}',
    `status`=1,update_time='{}' WHERE uid = '{}' AND event_id ='{}'
    """.format(pt_ifo['after_total_event_point'], max(score, score_curr), pair_id, update_time, s['user_id'],
               req['event_id'])
    sql2 = """UPDATE event_festival SET perfect_cnt='{}',great_cnt='{}',good_cnt='{}',bad_cnt='{}',miss_cnt='{}',
    max_combo='{}',score='{}',love_cnt='{}',`status`=1,total_event_point='{}', added_event_point='{}', rank='{}', 
    combo_rank='{}', rarity_3_cnt='{}', rarity_2_cnt='{}', rarity_1_cnt='{}', ticket_add='{}', reward_items='{}',
    update_time='{}' ,sub_bonus_flag='{}',skill_exp_add='{}',coin_reward='{}' WHERE uid ='{}' AND event_id ='{}' AND pair_id ='{}'
    """.format(req['perfect_cnt'], req['great_cnt'], req['good_cnt'], req['bad_cnt'], req['miss_cnt'], req['max_combo'],
               score_curr, req['love_cnt'],
               pt_ifo['after_total_event_point'], pt_ifo['added_event_point'], res['rank'], res['combo_rank'],
               rarity_cnt[3], rarity_cnt[2], rarity_cnt[1], ticket_add, json_dump(reward_items), update_time,
               json_dump(req['sub_bonus_flag']), exp, coin, s['user_id'], req['event_id'], pair_id)
    return sql, sql2


def festival_last(source, update_time=None):
    req = source['req_data']
    res = source['res_data']
    if update_time is None:
        update_time = int(time.time())
    song_diff_ids = []
    song_set_ids = []
    if 'festival' not in res:
        return
    for live in res['festival']['event_festival_live_list']:
        song_diff_ids.append(live['live_difficulty_id'])
        song_set_ids.append(live_setting_id[live['live_difficulty_id']])

    sql = """INSERT INTO event_festival_last (uid, event_id, last_song_set_ids, last_song_diff_ids, update_time) 
    VALUES ('{}','{}','{}','{}','{}')
    ON DUPLICATE KEY UPDATE event_id = VALUES(event_id),last_song_set_ids=VALUES(last_song_set_ids),
    last_song_diff_ids=VALUES(last_song_diff_ids),update_time=VALUES(update_time)
    """.format(source['user_id'], req['event_id'], json_dump(song_set_ids), json_dump(song_diff_ids), update_time)

    return sql,


def recovery(source, update_time=None):
    res = source['res_data']
    if update_time is None:
        update_time = int(time.time())
    sql = """insert into recovery (uid, energy_max,over_max_energy, before_sns_coin, after_sns_coin, update_time) VALUES 
    ('{}','{}','{}','{}','{}','{}')""".format(source['user_id'], res['energy_max'], res['over_max_energy'],
                                              res['before_sns_coin'], res['after_sns_coin'], update_time)
    return sql,


def json_dump(json_object, useascii=True):
    return escape_string(json.dumps(json_object, separators=(',', ':'), ensure_ascii=useascii))


def update_removable(owning_id, skill_ids):
    sql = "update unit_unitAll set unit_removable_skill_id = '{}' WHERE unit_owning_user_id = '{}'".format(
        ','.join([str(x) for x in skill_ids]), owning_id)
    return sql,


game_db_init()

import json
import time
import hashlib
import sqlite3
import config as cfg
import pymysql
from pymysql.cursors import DictCursor
import sqlquerys as sq
import threading
import queue

database_q = queue.Queue()


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


def get_setting_id(live_difficulty_id):
    try:
        return live_setting_id[live_difficulty_id]
    except KeyError:
        game_db_init()
        try:
            return live_setting_id[live_difficulty_id]
        except KeyError:
            return None


def setting_tran():
    db = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME, charset=cfg.DB_CHARSET)
    cur = db.cursor()
    dbs = ['live', 'pub_live_info', 'event_traditional']
    for dbname in dbs:
        sql = "SELECT `id`,`live_difficulty_id` from `{}` where `live_setting_id` is NULL".format(dbname)
        cur.execute(sql)
        for result in cur.fetchall():
            id = get_setting_id(result[1])
            if id:
                print(result, "=>", id)
                sqlc = "update `{}` set `live_setting_id` = {} WHERE `id`={} ".format(dbname, id, result[0])

                cur.execute(sqlc)
                db.commit()
            else:
                print('notfound', result[1])


def secretbox_raity_tran():
    db = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME, charset=cfg.DB_CHARSET)
    cur = db.cursor()
    curlite = unit_db.cursor()

    sql = "SELECT `id`,`result_unit_ids` FROM `secretbox`"
    cur.execute(sql)
    for result in cur.fetchall():
        unit_ids = result[1].split(',')

        rarity_ids = []
        for unit_id in unit_ids:
            sql = "SELECT rarity FROM unit_m WHERE unit_id = {}".format(unit_id)
            curlite.execute(sql)
            rarity = curlite.fetchone()[0]

            rarity_ids.append(str(rarity) or '')
        raritys = ",".join(rarity_ids)
        if len(rarity_ids) == len(unit_ids):

            sqlc = "update `secretbox` set `result_rarity_ids` = '{}' WHERE `id`={}".format(raritys, result[0])
            print(result[1], "=>", raritys)
            cur.execute(sqlc)
            db.commit()
        else:
            print(result[0], result[1], "结果不对应", raritys)


def challenge_tran():
    db = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME, charset=cfg.DB_CHARSET)
    cur = db.cursor()
    sql = "SELECT id,reward_item_list,uid FROM event_challenge_pairs WHERE reward_item_list IS NOT NULL AND finalized=1"
    cur.execute(sql)
    for pair in cur.fetchall():
        try:
            item_list = json.loads(pair[1])
        except Exception as e:
            print(e)
        else:
            rarity_l = [0, 0, 0, 0]
            ticket = 0
            for r in item_list:
                rarity_l[r['rarity']] += 1
                if r['add_type'] == 1000 and r['item_id'] == 1:
                    ticket += r['amount']
            sql = "update event_challenge_pairs set rarity_3_cnt={},rarity_2_cnt={},rarity_1_cnt={},ticket_add={} WHERE id={}".format(
                rarity_l[3],
                rarity_l[2],
                rarity_l[1],
                ticket,
                pair[0])
            cur.execute(sql)
            db.commit()
            print(pair[0], "user", pair[2], ticket, rarity_l[1:])
    sql = "SELECT id,uid,max(score) FROM `event_challenge` GROUP BY uid"
    cur.execute(sql)
    for line in cur.fetchall():
        sql = "update event_challenge_users set high_score = {} WHERE uid={}".format(line[2], line[1])
        cur.execute(sql)
        db.commit()
        print(line[1], '=>', line[2])
    sql = "SELECT id,uid,max(total_event_point) FROM `event_challenge_pairs` GROUP BY uid"
    cur.execute(sql)
    for line in cur.fetchall():
        sql = "update event_challenge_users set total_event_point = {} WHERE uid={}".format(line[2], line[1])
        cur.execute(sql)
        db.commit()
        print(line[1], '=>', line[2])
    sql = "SELECT pair_id,uid FROM event_challenge_pairs"
    cur.execute(sql)
    for pair in cur.fetchall():
        pair_id = pair[0]
        uid = pair[1]
        sql = "select mission_result from event_challenge WHERE pair_id = %s AND uid = %s" % (pair_id, uid)
        cur.execute(sql)
        lp = 0
        for line in cur.fetchall():
            if line:
                for mission in json.loads(line[0]):
                    if mission['bonus_type'] == 3050 and mission['achieved']:
                        lp += int(mission['bonus_param'])
        cur.execute("update event_challenge_pairs set lp_add = %s WHERE pair_id = %s AND uid = %s" % (lp, pair_id, uid))
        db.commit()
        print(pair_id, lp, uid)


def festival_record_tran():
    db = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME, charset=cfg.DB_CHARSET)
    cur = db.cursor()
    cur.execute(
        "SELECT uid,curr_pair_id FROM `event_festival_users` ")
    pair_id_by_u = dict(cur.fetchall())
    cur = db.cursor(DictCursor)
    cur.execute(
        "SELECT * FROM `request_cache` WHERE (`m1` LIKE 'liveStart' OR `m1` LIKE 'liveReward') AND `status`=2 AND uid =865384 ORDER BY id ASC ")
    # put_sqls(["TRUNCATE event_festival", "TRUNCATE event_festival_users"])

    score_by_u = {}
    res_all = cur.fetchall()
    if not res_all:
        return
    last_id = res_all[0]['id']
    for result in res_all:
        req = json.loads(result['request'])
        res = json.loads(result['response'])
        s = {
            "user_id": result['uid'],
            "req_data": req,
            "res_data": res
        }
        pair_id = None
        if result['m1'] == 'liveStart':
            if result['uid'] in pair_id_by_u:
                pair_id_by_u[result['uid']] += 1
            else:
                pair_id_by_u[result['uid']] = 1
            pair_id = pair_id_by_u[result['uid']]
            put_sqls(
                sq.festival_start(s, pair_id, req['timeStamp'])
            )
        elif result['m1'] == 'liveReward':
            if result['id'] >= last_id:
                put_sqls(sq.effort_point_box(result['uid'], res['effort_point'], req['timeStamp']))
            score_curr = req['score_smile'] + req['score_cute'] + req['score_cool']
            if result['uid'] in score_by_u:
                score_by_u[result['uid']] = max(score_by_u[result['uid']], score_curr)
            else:
                score_by_u[result['uid']] = score_curr
            if result['uid'] in pair_id_by_u:
                pair_id = pair_id_by_u[result['uid']]
                put_sqls(
                    sq.festival_reward(s, pair_id, score_by_u[result['uid']], req['timeStamp'])
                )

        print(result['id'], result['uid'], pair_id, result['m1'])
        put_sqls(("UPDATE request_cache SET `status`=0 WHERE id = '{}'".format(result['id']),))


game_db_init()

db_o = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME, charset=cfg.DB_CHARSET)
cur_o = db_o.cursor()


def put_sqls(sqls):
    for x in sqls:
        cur_o.execute(x)
        db_o.commit()


festival_record_tran()

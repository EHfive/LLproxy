import json
import queue
import threading
import pymysql
import config as cfg
import sqlquerys as sq
from mysql import Mysql
from pll_tools import user_cache
import redis as rds
from pll_tools.db_tools import is_judge_card

# import traceback

r = rds.StrictRedis(host='localhost')

battle_dict = {}
database_q = queue.Queue()
live_maps = []


def jugde_card_set(uid, deck_info):
    db = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME, charset=cfg.DB_CHARSET)
    cur = db.cursor()
    for deck in deck_info:
        cnt = 0
        for owning in deck['unit_owning_user_ids']:
            ownid = owning['unit_owning_user_id']
            try:
                code = r.get(ownid)
                if code is None:
                    cur.execute("select unit_id from unit_unitAll WHERE unit_owning_user_id = {}".format(ownid))
                    unit_id = cur.fetchone()[0]
                    code = is_judge_card(unit_id)
                    assert code != -1
                    r.set(ownid, code)
                else:
                    code = int(code)
            except:
                cnt = -1
                break
            if code == 1:
                cnt += 1
        if cnt == -1:
            continue
        k = ','.join([
            str(uid),
            'deck',
            str(deck['unit_deck_id'])
        ])
        print(k, '=>', cnt)
        r.set(k, cnt)


def get_deck_judge(uid, deckid):
    try:
        k = ','.join([
            str(uid),
            'deck',
            str(deckid)
        ])
        code = r.get(k)
        if code is None:
            code = -1
        else:
            code = int(code)
    except:
        code = -1
    print(code)
    return code


def val_init():
    tag = 0
    for i in range(3):
        try:
            db = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME, charset=cfg.DB_CHARSET)
            cur = db.cursor()
        except Exception as e:
            print(e)
        else:
            tag = 1
            break
    if tag == 0:
        exit("database access failed")

    cur.execute("SELECT live_difficulty_id FROM pub_live_info")
    for x in cur.fetchall():
        live_maps.append(x[0])
        # print(live_maps)


class DataHandler:
    def __init__(self, source):
        self.s = source
        self.id = self.s["user_id"]
        self.req_data = self.s["req_data"]
        self.res_data = self.s["res_data"]
        self.modules = self.s["modules"]

    def fenfa(self):
        m = self.modules
        if m[0] == 'battle':

            if m[1] in ('matching', 'startWait', 'liveStart', 'liveEnd', 'endWait', 'endRoom'):
                self.score_match(m[1])
        elif m[0] == 'mission':
            if m[1] == 'proceed':
                battle_dict[self.id] = self.s
                print("battle_dict length", len(battle_dict))
                try:
                    put_sqls(sq.user_info(self.res_data['after_user_info'], self.id))
                except KeyError:
                    print("challenge proceed 无 after_user_info")
        elif m[0] == 'challenge':
            if m[1] == 'proceed':
                battle_dict[self.id] = self.s
                print("battle_dict length", len(battle_dict))
                try:
                    put_sqls(sq.user_info(self.res_data['after_user_info'], self.id))
                except KeyError:
                    print("challenge proceed 无 after_user_info")
            elif m[1] == 'checkpoint':
                if self.id in battle_dict:
                    s_proceed = battle_dict[self.id]
                    jugde_card = get_deck_judge(self.id, s_proceed['req_data']['unit_deck_id'])
                else:
                    s_proceed = None
                    jugde_card = -1
                db = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME, charset=cfg.DB_CHARSET)
                cur = db.cursor(cursor=pymysql.cursors.DictCursor)
                event_id = self.req_data['event_id']

                if self.res_data['challenge_info']:
                    c_round = self.res_data['challenge_info']['round'] - 1
                    round_n = c_round
                else:
                    round_n = 1
                    c_round = -1
                cur.execute("SELECT * FROM event_challenge_users WHERE uid= %s AND event_id = %s", (self.id, event_id))
                event_user = cur.fetchone()
                final = 1 if c_round == -1 else 0

                need_init = True
                if event_user:
                    pair_id = event_user['curr_pair_id'] + 1
                    point = event_user['total_event_point']
                    high_score = max(event_user['high_score'],
                                     self.req_data['score_smile'] + self.req_data['score_cute'] + self.req_data[
                                         'score_cool'])
                    print('high score', high_score)
                    if event_id == event_user['event_id']:
                        if c_round > event_user['curr_round']:
                            pair_id = event_user['curr_pair_id']
                            round_n = c_round
                            need_init = False
                        elif c_round == -1:
                            pair_id = event_user['curr_pair_id']
                            round_n = event_user['curr_round'] + 1
                            need_init = False
                else:
                    point = 0
                    high_score = 0
                    pair_id = 1

                put_sqls(sq.challenge_user_rplc({
                    'uid': self.id,
                    'event_id': event_id,
                    'curr_pair_id': pair_id,
                    'curr_round': round_n,
                    'total_event_point': point,
                    'high_score': high_score,
                    'finalized': final
                }))
                if need_init:
                    put_sqls(sq.challenge_pair_init(self.id, event_id, pair_id))

                put_sqls(sq.challenge_proceed(s_proceed, self.s, pair_id, round_n, final, jugde_card))
                put_sqls(sq.effort_point_box(self.id, self.res_data['effort_point']))
            elif m[1] in ('finalize', 'gameover'):
                put_sqls(sq.user_info(self.res_data['after_user_info'], self.id))
                db = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME, charset=cfg.DB_CHARSET)
                cur = db.cursor(cursor=pymysql.cursors.DictCursor)
                cur.execute("SELECT * FROM event_challenge_users WHERE uid= %s", self.id)
                event_user = cur.fetchone()
                if event_user:
                    pair_id = event_user['curr_pair_id']
                    put_sqls(sq.challenge_finalize(self.s, pair_id))

        elif m[0] in ('live', 'rlive'):
            if m[1] == 'reward' and '/reward' in self.s['path']:
                try:
                    deckid = int(r.get(','.join([
                        str(self.id),
                        'deck'
                    ])))
                except:
                    deckid = None
                jugde_card = get_deck_judge(self.id, deckid) if deckid else -1
                put_sqls(sq.live_play(self.s, jugde_card))
                put_sqls(sq.effort_point_box(self.id, self.res_data['effort_point']))
                put_sqls(sq.user_info(self.res_data['after_user_info'], self.id))
                print("live reward inserted")
            elif m[1] == 'play':
                try:
                    r.set(','.join([
                        str(self.id),
                        'deck'
                    ]), self.req_data['unit_deck_id'])
                except:
                    pass
                for rank_info, live_info in zip(self.res_data['rank_info'], self.res_data['live_list']):
                    live_info = live_info['live_info']
                    live_id = live_info['live_difficulty_id']
                    if live_id not in live_maps:
                        merge_info = {
                            "rank_info": rank_info,
                            "live_info": live_info
                        }
                        put_sqls(sq.pub_live_info(live_id, merge_info))
                        live_maps.append(live_id)

        elif m[0] == 'common':
            if m[1] == 'recoveryEnergy':
                put_sqls(sq.recovery(self.s))

        elif m[0] == 'festival':
            db = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME, charset=cfg.DB_CHARSET)
            cur = db.cursor(cursor=pymysql.cursors.DictCursor)
            # if m[1] != 'festivalInfo':
            #     put_sqls(sq.request_cache(self.s, stat=2))
            if m[1] == 'liveStart':
                cur.execute(
                    "SELECT curr_pair_id,high_score FROM event_festival_users WHERE uid = {} AND event_id = {}".format(
                        self.id, self.req_data['event_id']
                    ))
                result = cur.fetchone()
                if result:
                    pair_id = result['curr_pair_id'] + 1

                else:
                    pair_id = 1
                jugde_card = get_deck_judge(self.id, self.req_data['unit_deck_id'])
                put_sqls(sq.festival_start(self.s, pair_id, jugde_card))
                print(result)
            elif m[1] == 'liveReward':
                cur.execute(
                    "SELECT `curr_pair_id`,`high_score`,`status` FROM event_festival_users WHERE uid = {} AND event_id = {}".format(
                        self.id, self.req_data['event_id']
                    ))
                result = cur.fetchone()
                if result:
                    if result['status'] == 1:
                        cur.execute(
                            "UPDATE  event_festival_users set curr_pair_id = curr_pair_id + 1 WHERE uid = {} AND event_id = {}".format(
                                self.id, self.req_data['event_id']
                            ))
                        db.commit()
                        return
                    high_score = result['high_score'] or 0
                    pair_id = result['curr_pair_id']
                    put_sqls(sq.festival_reward(self.s, pair_id, high_score))
                put_sqls(sq.effort_point_box(self.id, self.res_data['effort_point']))
                put_sqls(sq.user_info(self.res_data['after_user_info'], self.id))
                print(result)
            elif m[1] in ('deckList', 'updateLiveList'):
                put_sqls(sq.festival_last(self.s))
        elif m[0] == 'user':
            if m[1] == 'userInfo':
                if 'result' in self.res_data:
                    self.res_data['user'] = self.res_data['result']['user']
                    put_sqls(sq.add_user(self.s))
                    put_sqls(sq.user_info(self.res_data['user'], self.id))
                else:

                    put_sqls(sq.add_user(self.s))
                    put_sqls(sq.user_info(self.res_data['user']))
                    print("tiny userInfo inserted")

            elif m[1] == 'getNavi':
                put_sqls(sq.user_navi({
                    'uid': self.res_data['result']['user']['user_id'],
                    'unit_owning_user_id': self.res_data['result']['user']['unit_owning_user_id']
                }))
            elif m[1] == 'changeNavi':
                print("battle_dict", len(battle_dict), battle_dict)
                put_sqls(sq.user_navi({
                    'uid': self.id,
                    'unit_owning_user_id': self.req_data['unit_owning_user_id']
                }))

        elif self.s['path'] == '/main.php/login/login':
            put_sqls(sq.update_user({
                'uid': self.res_data['user_id'],
                'login_key': self.req_data['login_key']
            }))
            print("login_key inserted")

        elif m[0] == 'unit':
            if m[1] == 'unitAll':
                result = self.res_data["result"]
                print("卡牌数 %s" % len(result))
                put_sqls(sq.replace_unit(self.id, result))
                print("unitAll inserted")

            elif m[1] == 'deckInfo':
                put_sqls(sq.deck_info(self.s))
                deck_info = self.res_data['result']
                jugde_card_set(self.id, deck_info)
            elif m[1] == 'deck':
                put_sqls(sq.deck_info(self.s, True))
                deck_info = self.req_data['unit_deck_list']
                jugde_card_set(self.id, deck_info)

            elif m[1] == 'removableSkillInfo':
                put_sqls(sq.removeable_skill_info(self.s))
            elif m[1] == 'removableSkillEquipment':
                db = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME, charset=cfg.DB_CHARSET)
                cur = db.cursor(cursor=pymysql.cursors.DictCursor)
                ids = lambda ownid: cur.execute(
                    "select unit_removable_skill_id from unit_unitAll WHERE unit_owning_user_id = '{}'".format(
                        ownid)) and cur.fetchone()['unit_removable_skill_id']
                cache_rmv = set()
                for rmv in self.req_data['remove']:
                    str_ids = ids(rmv['unit_owning_user_id'])
                    rmv_ids = str_ids.split(',') if str_ids else []
                    sid = str(rmv['unit_removable_skill_id'])
                    if sid in rmv_ids:
                        rmv_ids.remove(sid)
                    print("removed", rmv_ids)
                    cache_rmv.add(sid)
                    put_sqls(sq.update_removable(rmv['unit_owning_user_id'], rmv_ids))
                for rmv in self.req_data['equip']:
                    str_ids = ids(rmv['unit_owning_user_id'])
                    rmv_ids = str_ids.split(',') if str_ids else []
                    rmv_ids = list(set(rmv_ids) - cache_rmv)
                    sid = str(rmv['unit_removable_skill_id'])
                    if sid not in rmv_ids:
                        rmv_ids.append(sid)
                    print("equiped", rmv_ids)
                    put_sqls(sq.update_removable(rmv['unit_owning_user_id'], rmv_ids))
            elif m[1] == 'setDisplayRank':
                put_sqls(sq.display_rank({
                    'unit_owning_user_id': self.req_data['unit_owning_user_id'],
                    'display_rank': self.req_data['display_rank']
                }))
        elif m[0] == 'secretbox':
            if m[1] in ['pon', 'multi']:
                put_sqls(sq.secretbox(self.s))

    def score_match(self, act):
        if act == 'matching':

            if str(self.id) in battle_dict:
                del battle_dict[str(self.id)]['thread']
                del battle_dict[str(self.id)]['queue']
                del battle_dict[str(self.id)]
            battle_dict[str(self.id)] = {
                'thread': threading.Thread(target=score_match_thread, args=(str(self.id),), daemon=True),
                'room_id': self.res_data['event_battle_room_id'],
                'queue': queue.Queue()
            }
            battle_dict[str(self.id)]['queue'].put({
                'action': act,
                'req_data': self.req_data,
                'res_data': self.res_data
            })

            battle_dict[str(self.id)]['thread'].start()
        elif str(self.id) in battle_dict:
            if self.req_data['event_battle_room_id'] == battle_dict[str(self.id)]['room_id']:
                battle_dict[str(self.id)]['queue'].put({
                    'action': act,
                    'req_data': self.req_data,
                    'res_data': self.res_data
                })


def score_match_thread(u_id):
    info = battle_dict[u_id]['queue'].get()
    final_room_info = {}
    room_id = 0
    event_id = 0
    while info is not None:
        act = info['action']
        req = info['req_data']
        res = info['res_data']
        players = []
        playtag = 0

        if act == 'startWait':
            final_room_info = info
            playtag = 1
        elif act == 'matching':
            room_id = res['event_battle_room_id']
            event_id = res['event_id']
            print(u_id, act, str(room_id) + ':' + str(event_id),
                  '玩家 {}'.format(res['battle_player_num']), end='\n\n')
            put_sqls(sq.score_match_status_0(u_id, event_id, room_id, res))
            playtag = 1
        elif act == 'liveStart':
            jugde_card = get_deck_judge(u_id, req['unit_deck_id'])
            put_sqls(sq.score_match_status_0(u_id, event_id, room_id, final_room_info['res_data']))
            put_sqls(sq.score_match_status_1(u_id, event_id, room_id, req, jugde_card))
            live_info = res['live_info'][0]
            liveinfo = {
                'live_difficulty_id': live_info['live_difficulty_id'],
                'is_random': live_info['is_random'],
                'dangerous': live_info['dangerous'],
                'notes_speed': live_info['notes_speed'],
                'notes_list_len': len(live_info['notes_list']),
            }
            # print('liveStart')
            # print(json.dumps(liveinfo, indent=4), end='\n\n')
        elif act == 'liveEnd':
            put_sqls(sq.score_match_status_2(u_id, event_id, room_id, req))
        elif act == 'endRoom':

            put_sqls(sq.score_match_status_3(u_id, event_id, room_id, res))
            put_sqls(sq.effort_point_box(u_id, res['effort_point']))
            put_sqls(sq.user_info(res['after_user_info'], u_id))

            # print('live end', end='\n\n')
            return
        if playtag == 1:
            players_n = []
            for x in res['matching_user']:
                i = {}
                try:
                    i['uid'] = x['user_info']['user_id']
                    i['name'] = x['user_info']['name']
                    i['level'] = x['user_info']['level']
                except KeyError:
                    i['uid'] = "NPC-%s" % x['npc_info']['npc_id']
                    i['name'] = "NPC-%s" % x['npc_info']['name']
                    i['level'] = "%s" % x['npc_info']['level']

                i['unit_id"'] = x['center_unit_info']["unit_id"]
                i['unit_level'] = x['center_unit_info']["level"]
                i['max'] = x['center_unit_info']['cute'] + x['center_unit_info']['smile'] + x['center_unit_info'][
                    'cool']
                i['skill_ids'] = x['center_unit_info']['removable_skill_ids']
                players_n.append(i)
            if len(players_n) != len(players):
                players = players_n
                if act != 'startWait':
                    for x in players:
                        print(x)

        info = battle_dict[u_id]['queue'].get()


def datainserter():
    my = Mysql(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME)
    while True:
        sqlq = database_q.get()
        # print(sqlq)
        try:
            my.query(sqlq)
        except Exception as e:
            try:
                my = Mysql(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME)
            except Exception as e2:
                print(e)
                print("\nSQL:\n" + sqlq, end="\n\n")
                print(e, e2)
            else:
                my.query(sqlq)


def datainserter_old():
    tag = 0
    db = None
    cur = None
    for i in range(3):
        try:
            db = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME, charset=cfg.DB_CHARSET)
            cur = db.cursor()
        except Exception as e:
            print(e)
        else:
            tag = 1
            break

    if tag == 0:
        exit("database access failed")

    while True:
        sqlq = database_q.get()
        try:
            # db = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME, charset=cfg.DB_CHARSET)
            # cur = db.cursor()
            cur.execute(sqlq)
            db.commit()
        except Exception as e:
            try:
                db = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME, charset=cfg.DB_CHARSET)
                cur = db.cursor()
            except Exception as e2:
                print(e)
                print("\nSQL:\n" + sqlq, end="\n\n")
                print(e, e2)
            else:
                cur.execute(sqlq)
                db.commit()
                # print("db inserted")


def put_sqls(sqls):
    for x in sqls:
        database_q.put(x)

import sqlite3

unit_db = sqlite3.connect("db/unit/unit.db_", check_same_thread=False)
unit_cur = unit_db.cursor()


def is_judge_card(unit_id):
    try:
        sqlunit_m = "select default_unit_skill_id from unit_m WHERE `unit_id` = {}".format(
            unit_id)
        unit_cur.execute(sqlunit_m)
        res_unit_m = unit_cur.fetchone()
        skill_id = res_unit_m[0]
        unit_cur.execute(
            "SELECT skill_effect_type,trigger_type FROM unit_skill_m WHERE unit_skill_id = {}".format(skill_id))
        res_skill = unit_cur.fetchone()
    except:
        return -1
    et = res_skill[0]
    # tt = res_skill[1]
    if et in (4, 5):
        return 1

    return 0

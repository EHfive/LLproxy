import sqlite3

db_list = []


def defaultpairs(colnames):
    return [
        {
            'colname': colname,
            'pairs': [
                ('爱心', 'Loveca'),
                ('将等级', '将Rank'),
                ('演唱会', 'LIVE'),
                ('连击', 'COMBO'),
                ('甜美点数', 'SmileP'),
                ('清纯点数', 'PureP'),
                ('洒脱点数', 'CoolP'),
                ('甜美', 'Smile'),
                ('清纯', 'Pure'),
                ('洒脱', 'Cool'),
                ('友情点', '友情pt'),
                ('耐力', 'LP'),
                ('全连击', 'Full Combo'),
                ('分数', 'Score'),
                ('全连', 'Full Combo'),
                ('容易', 'EASY'),
                ('普通', 'NORMAL'),
                ('困难', 'HARD'),
                ('专家', 'EXPRET'),
                ('大师', 'MASTER'),
                ('得分', 'SCORE')

            ]
        } for colname in colnames
    ]


def str_replace(dbpath, tablename, colpairs):
    db = sqlite3.connect(dbpath)
    db.row_factory = lambda c, r: dict([(col[0], r[idx]) for idx, col in enumerate(c.description)])
    cur = db.cursor()

    for col in colpairs:
        for pair in col['pairs']:
            cur.execute('UPDATE {} SET {} = replace({},?,?)'.format(tablename, col['colname'], col['colname']),
                        (pair[0], pair[1]))
            db.commit()
    if dbpath not in db_list:
        db_list.append(dbpath)


if __name__ == '__main__':
    str_replace('db/achievement/achievement.db_', 'achievement_m', [
        {
            'colname': 'title',
            'pairs': [
                ('将等级', '将Rank'),
                ('演唱会', 'LIVE'),
                ('甜美', 'Smile'),
                ('清纯', 'Pure'),
                ('洒脱', 'Cool'),
                ('全连击', 'FULL COMBO'),
                ('专家', 'EXPRET'),
                ('得分', 'SCORE')

            ]
        },
        {
            'colname': 'description',
            'pairs': [
                ('甜美', 'Smile'),
                ('清纯', 'Pure'),
                ('洒脱', 'Cool'),

                ('专家', 'EXPRET'),

                ('全连击', 'FULL COMBO'),
            ]
        }
    ])
    str_replace('db/achievement/achievement.db_', 'achievement_description_m', [
        {
            'colname': 'description',
            'pairs': [
                ('将等级', '将Rank'),
                ('演唱会', 'LIVE'),
                ('甜美', 'Smile'),
                ('清纯', 'Pure'),
                ('洒脱', 'Cool'),
                ('全连击', 'FULL COMBO'),
                ('连击等级', 'COMBO RANK'),
                ('得分等级', 'SCORE RANK')

            ]
        }
    ])
    str_replace('db/challenge/challenge.db_', 'event_challenge_item_m', [
        {
            'colname': 'name',
            'pairs': [
                ('经验值', 'EXP'),
                ('点数', 'pt'),
                ('分数', 'SCORE'),

            ]
        }
    ])
    str_replace('db/common/game_mater.db_', 'add_type_m', [
        {
            'colname': 'name',
            'pairs': [
                ('经验', 'EXP'),
                ('友情点', '友情pt'),
                ('爱心', 'Loveca'),
                ('演唱会', 'LIVE'),
                ('金币', 'G')
            ]
        }
    ])
    str_replace('db/common/game_mater.db_', 'sort_condition_m', [
        {
            'colname': 'sort_label',
            'pairs': [
                ('爱心', 'Loveca'),
                ('甜美', 'Smile'),
                ('清纯', 'Pure'),
                ('洒脱', 'Cool'),
                ('经验', 'EXP'),
                ('友情点', '友情pt'),
                ('爱心', 'Loveca'),
                ('演唱会', 'LIVE'),
                ('金币', 'G')
            ]
        }
    ])
    str_replace('db/common/game_mater.db_', 'strings_m', [
        {
            'colname': 'string_label',
            'pairs': [
                ('将等级', '将Rank'),
                ('爱心', 'Loveca'),
                ('耐力', 'LP'),
                ('金币', 'G'),
                ('友情点', '友情pt'),
                ('甜美', 'Smile'),
                ('清纯', 'Pure'),
                ('洒脱', 'Cool'),
                ('经验值', 'EXP'),
                ('经验', 'EXP'),
                ('全连击', 'FULL COMBO'),
                ('连击', 'COMBO'),
                ('得分', 'SCORE'),
                ('绊点数', '绊pt'),
                ('演唱会', 'LIVE'),
                ('容易', 'EASY'),
                ('普通', 'NORMAL'),
                ('困难', 'HARD'),
                ('专家', 'EXPRET'),
                ('大师', 'MASTER'),
                ('高分', 'HIGH SCORE'),
                ('NORMAL生', '普通生')
            ]
        }
    ])
    str_replace('db/common/other.db_', 'chat_m', [
        {
            'colname': 'chat_label',
            'pairs': [
                ('全连击', 'FULL COMBO')
            ]
        }
    ])
    str_replace('db/event/festival.db_', 'event_festival_item_m', [
        {
            'colname': 'name',
            'pairs': [
                ('经验值', 'EXP'),
                ('活动点', '活动pt'),
                ('分数', 'SCORE'),

            ]
        }
    ])
    str_replace('db/item/item.db_', 'kg_item_m', [
        {
            'colname': 'name',
            'pairs': [
                ('金币', 'G'),
                ('友情点', '友情pt'),
                ('爱心', 'Loveca'),

            ]
        },
        {
            'colname': 'detailed_description',
            'pairs': [
                ('金币', 'G'),
                ('友情点', '友情pt'),
                ('爱心', 'Loveca'),
            ]
        }
    ])
    str_replace('db/item/item.db_', 'award_m', [
        {
            'colname': 'name',
            'pairs': [
                ('演唱会', 'LIVE'),
                ('全连击', 'FULL COMBO'),
                ('全连', 'FULL COMBO')
            ]
        },
        {
            'colname': 'description',
            'pairs': [
                ('演唱会', 'LIVE'),
                ('全连击', 'FULL COMBO'),
                ('全连', 'FULL COMBO')
            ]
        }
    ])
    str_replace('db/unit/unit.db_', 'unit_attribute_m', [
        {
            'colname': 'name',
            'pairs': [

                ('甜美', 'Smile'),
                ('清纯', 'Pure'),
                ('洒脱', 'Cool'),

            ]
        }
    ])
    str_replace('db/unit/unit.db_', 'unit_leader_skill_m', [
        {
            'colname': 'name',
            'pairs': [
                ('甜美点数', 'SmileP'),
                ('清纯点数', 'PureP'),
                ('洒脱点数', 'CoolP'),
                ('甜美', 'Smile'),
                ('清纯', 'Pure'),
                ('洒脱', 'Cool'),
                ('洒脱e', 'Cool'),

            ]
        },
        {
            'colname': 'description',
            'pairs': [
                ('甜美点数', 'SmileP'),
                ('清纯点数', 'PureP'),
                ('洒脱点数', 'CoolP'),
                ('甜美', 'Smile'),
                ('清纯', 'Pure'),
                ('洒脱', 'Cool'),

            ]
        }
    ])
    str_replace('db/unit/unit.db_', 'unit_removable_skill_m', [
        {
            'colname': 'name',
            'pairs': [

                ('甜美', 'Smile'),
                ('清纯', 'Pure'),
                ('洒脱', 'Cool'),

            ]
        },
        {
            'colname': 'description',
            'pairs': [
                ('甜美', 'Smile'),
                ('清纯', 'Pure'),
                ('洒脱', 'Cool'),
                # ('得分', 'SCORE'),

            ]
        }
    ])
    str_replace('db/unit/unit.db_', 'unit_m', [
        {
            'colname': 'name',
            'pairs': [

                ('日香', '妮可'),
                ('香香', '妮可'),
                ('琴梨', '小鸟'),

            ]
        },
        {
            'colname': 'eponym',
            'pairs': [
                ('日香', '妮可'),
                ('香香', '妮可'),
                ('琴梨', '小鸟'),
                ('小琴', '小鸟'),
                ('微笑小香香','niconico~ni~')

            ]
        }
    ])
    str_replace('db/unit/unit.db_', 'unit_skill_m', [
        {
            'colname': 'name',
            'pairs': [

                ('日香', '妮可'),
                ('香香', '妮可'),
                ('琴梨', '小鸟'),

            ]
        }
    ])
    str_replace('db/unit/unit.db_', 'unit_type_m', [
        {
            'colname': 'name',
            'pairs': [

                ('日香', '妮可'),
                ('琴梨', '小鸟'),

            ]
        }
    ])
    str_replace('db/common/asset.db_', 'asset_voice_m', [
        {
            'colname': 'voice_content',
            'pairs': [
                ('甜美', 'Smile'),
                ('清纯', 'Pure'),
                ('洒脱', 'Cool'),
                ('日香', '妮可'),
                ('微笑小香香','niconico~ni~'),
                ('香香', '妮可'),
                ('琴梨', '小鸟'),
                ('小琴', '小鸟')
            ]
        }
    ])
    str_replace('db/scenario/scenario.db_', 'scenario_setting_m', [
        {
            'colname': 'character_name',
            'pairs': [
                ('日香', '妮可'),
                ('香香', '妮可'),
                ('琴梨', '小鸟'),
            ]
        }
    ])
    str_replace('db/subscenario/subscenario.db_', 'subscenario_m', [
        {
            'colname': 'title',
            'pairs': [
                ('日香', '妮可'),
                ('微笑小香香','niconico~ni~'),
                ('香香', '妮可'),
                ('琴梨', '小鸟'),
            ]
        }
    ])
    str_replace('db/subscenario/subscenario.db_', 'subscenario_setting_m', [
        {
            'colname': 'character_name',
            'pairs': [
                ('日香', '妮可'),
                ('香香', '妮可'),
                ('琴梨', '小鸟'),
            ]
        }
    ])
    for path in db_list:
        print(path)

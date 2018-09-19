import json
import sqlquerys

reqs = """
{"module":"live","action":"reward","good_cnt":0,"miss_cnt":0,"great_cnt":64,"commandNum":"40410961.1493824697.9","love_cnt":90,"max_combo":498,"score_smile":477935,"perfect_cnt":434,"bad_cnt":0,"event_point":0,"live_difficulty_id":1569,"timeStamp":1493824697,"mgd":2,"score_cute":0,"score_cool":0,"event_id":null}
"""
ress = """
{
	"response_data": {
		"live_info": [{
			"live_difficulty_id": 1569,
			"is_random": false,
			"dangerous": false,
			"use_quad_point": false
		}],
		"rank": 1,
		"combo_rank": 1,
		"total_love": 90,
		"is_high_score": false,
		"hi_score": 539616,
		"base_reward_info": {
			"player_exp": 83,
			"player_exp_unit_max": {
				"before": 144,
				"after": 144
			},
			"player_exp_friend_max": {
				"before": 27,
				"after": 27
			},
			"player_exp_lp_max": {
				"before": 85,
				"after": 85
			},
			"game_coin": 4500,
			"game_coin_reward_box_flag": false,
			"social_point": 10
		},
		"reward_unit_list": {
			"live_clear": [{
				"add_type": 1001,
				"amount": 1,
				"item_category_id": 0,
				"unit_id": 310,
				"unit_owning_user_id": null,
				"is_support_member": false,
				"exp": 0,
				"next_exp": 6,
				"max_hp": 2,
				"level": 1,
				"skill_level": 0,
				"rank": 1,
				"love": 0,
				"is_rank_max": false,
				"is_level_max": false,
				"is_love_max": false,
				"new_unit_flag": false,
				"reward_box_flag": true,
				"unit_skill_exp": 0,
				"display_rank": 1,
				"unit_removable_skill_capacity": 0
			}],
			"live_rank": [{
				"add_type": 1001,
				"amount": 1,
				"item_category_id": 0,
				"unit_id": 510,
				"unit_owning_user_id": null,
				"is_support_member": false,
				"exp": 669,
				"next_exp": 793,
				"max_hp": 2,
				"level": 12,
				"skill_level": 0,
				"rank": 1,
				"love": 0,
				"is_rank_max": false,
				"is_level_max": false,
				"is_love_max": false,
				"new_unit_flag": false,
				"reward_box_flag": true,
				"unit_skill_exp": 0,
				"display_rank": 1,
				"unit_removable_skill_capacity": 0
			}],
			"live_combo": [{
				"add_type": 1001,
				"amount": 1,
				"item_category_id": 0,
				"unit_id": 466,
				"unit_owning_user_id": null,
				"is_support_member": false,
				"exp": 0,
				"next_exp": 6,
				"max_hp": 2,
				"level": 1,
				"skill_level": 0,
				"rank": 1,
				"love": 0,
				"is_rank_max": false,
				"is_level_max": false,
				"is_love_max": false,
				"new_unit_flag": false,
				"reward_box_flag": true,
				"unit_skill_exp": 0,
				"display_rank": 1,
				"unit_removable_skill_capacity": 0
			}]
		},
		"unlocked_subscenario_ids": [],
		"effort_point": [{
			"live_effort_point_box_spec_id": 4,
			"capacity": 2000000,
			"before": 951840,
			"after": 1429775,
			"rewards": []
		}],
		"unit_list": [{
			"unit_owning_user_id": 2516036707,
			"unit_id": 937,
			"position": 1,
			"level": 80,
			"unit_skill_level": 1,
			"before_love": 500,
			"love": 500,
			"max_love": 500,
			"is_rank_max": true,
			"is_love_max": true,
			"is_level_max": true
		}, {
			"unit_owning_user_id": 2516036697,
			"unit_id": 954,
			"position": 2,
			"level": 90,
			"unit_skill_level": 1,
			"before_love": 750,
			"love": 750,
			"max_love": 750,
			"is_rank_max": true,
			"is_love_max": true,
			"is_level_max": true
		}, {
			"unit_owning_user_id": 2546699621,
			"unit_id": 979,
			"position": 3,
			"level": 80,
			"unit_skill_level": 2,
			"before_love": 500,
			"love": 500,
			"max_love": 500,
			"is_rank_max": true,
			"is_love_max": true,
			"is_level_max": true
		}, {
			"unit_owning_user_id": 2527960033,
			"unit_id": 885,
			"position": 4,
			"level": 80,
			"unit_skill_level": 2,
			"before_love": 500,
			"love": 500,
			"max_love": 500,
			"is_rank_max": true,
			"is_love_max": true,
			"is_level_max": true
		}, {
			"unit_owning_user_id": 2521098549,
			"unit_id": 957,
			"position": 5,
			"level": 80,
			"unit_skill_level": 1,
			"before_love": 500,
			"love": 500,
			"max_love": 500,
			"is_rank_max": false,
			"is_love_max": false,
			"is_level_max": false
		}, {
			"unit_owning_user_id": 2269881948,
			"unit_id": 643,
			"position": 6,
			"level": 60,
			"unit_skill_level": 1,
			"before_love": 250,
			"love": 250,
			"max_love": 250,
			"is_rank_max": false,
			"is_love_max": false,
			"is_level_max": false
		}, {
			"unit_owning_user_id": 2521535634,
			"unit_id": 936,
			"position": 7,
			"level": 60,
			"unit_skill_level": 1,
			"before_love": 250,
			"love": 250,
			"max_love": 250,
			"is_rank_max": false,
			"is_love_max": false,
			"is_level_max": false
		}, {
			"unit_owning_user_id": 2168792807,
			"unit_id": 311,
			"position": 8,
			"level": 60,
			"unit_skill_level": 1,
			"before_love": 250,
			"love": 250,
			"max_love": 250,
			"is_rank_max": false,
			"is_love_max": false,
			"is_level_max": false
		}, {
			"unit_owning_user_id": 2201094254,
			"unit_id": 604,
			"position": 9,
			"level": 60,
			"unit_skill_level": 1,
			"before_love": 250,
			"love": 250,
			"max_love": 250,
			"is_rank_max": false,
			"is_love_max": false,
			"is_level_max": false
		}],
		"before_user_info": {
			"level": 120,
			"exp": 127103,
			"previous_exp": 125421,
			"next_exp": 129004,
			"game_coin": 814417,
			"sns_coin": 270,
			"social_point": 15765,
			"unit_max": 144,
			"energy_max": 85,
			"friend_max": 27,
			"tutorial_state": -1,
			"energy_full_time": "2017-05-04 04:20:29",
			"over_max_energy": 0,
			"unlock_random_live_muse": 1,
			"unlock_random_live_aqours": 1
		},
		"after_user_info": {
			"level": 120,
			"exp": 127186,
			"previous_exp": 125421,
			"next_exp": 129004,
			"game_coin": 818917,
			"sns_coin": 271,
			"social_point": 15775,
			"unit_max": 144,
			"energy_max": 85,
			"friend_max": 27,
			"tutorial_state": -1,
			"energy_full_time": "2017-05-04 04:20:29",
			"over_max_energy": 0,
			"unlock_random_live_muse": 1,
			"unlock_random_live_aqours": 1
		},
		"next_level_info": [{
			"level": 120,
			"from_exp": 127103
		}],
		"goal_accomp_info": {
			"achieved_ids": [11264],
			"rewards": [{
				"item_id": 4,
				"add_type": 3001,
				"amount": 1,
				"item_category_id": 0,
				"reward_box_flag": false
			}]
		},
		"special_reward_info": [],
		"event_info": [],
		"daily_reward_info": []
	},
	"release_info": [],
	"status_code": 200
}
"""

source = {
    "req_data": json.loads(reqs),
    "res_data": json.loads(ress)['response_data'],
    "user_id": 123456
}


sqls = sqlquerys.live_play(source)

for x in sqls:
    print(x)

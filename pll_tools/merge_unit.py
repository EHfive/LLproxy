import sqlite3


def unit_merge(to_unit_db, from_unit_db):
    to_unit = sqlite3.connect(to_unit_db, check_same_thread=False)
    cur = to_unit.cursor()
    from_unit = sqlite3.connect(from_unit_db, check_same_thread=False)

    tables = to_unit.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    tables = [x[0] for x in tables]

    for table in tables:

        try:
            table_info_to = to_unit.execute("PRAGMA table_info(%s)" % table).fetchall()
            table_info_from = from_unit.execute("PRAGMA table_info(%s)" % table).fetchall()
            table_info = list(set(table_info_from) & set(table_info_to))
            words = [x[1] for x in table_info]

            words_s = ",".join(words)
            # print(words_s)
            logs = from_unit.execute("SELECT %s FROM %s WHERE 1" % (words_s, table)).fetchall()
            # print(logs)
            for log in logs:
                log = [str(x) for x in log][:len(table_info)]
                vals = ' " ' + '","'.join(log) + ' " '
                # print(table, vals)
                cur.execute("INSERT OR IGNORE INTO %s (%s) VALUES (%s)" %
                            (table, words_s, vals))
        except sqlite3.OperationalError as e:
            print('OperationalError', e)
            continue
        to_unit.commit()


if __name__ == '__main__':
    unit_merge("../db/unit/unit.db_", "../db/unit/unit_jp.db_")
    unit_merge("../db/live/live.db_", "../db/live/live_jp.db_")

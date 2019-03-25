import json
import random
import re
import sqlite3
import urllib.request
# from pprint import pprint


def store_faction_data(this_id, this_name):
    conn = sqlite3.connect('donations.sqlite')
    c = conn.cursor()
    query = """INSERT INTO factions(faction, faction_name)
        VALUES(?, ?)
        ON CONFLICT(faction) DO UPDATE SET
            faction_name = excluded.faction_name;"""
    c.execute(query, (this_id, this_name))
    conn.commit()
    c.close()
    conn.close()


def store_all_members_data(all_members):
    conn = sqlite3.connect('donations.sqlite')
    c = conn.cursor()
    for this_key, this_member in all_members.items():
        query = """INSERT INTO members(member, member_name, faction)
                VALUES(?, ?, ?)
                ON CONFLICT(member) DO UPDATE SET 
                    member_name = excluded.member_name,
                    faction = excluded.faction;"""
        c.execute(query, (this_key, this_member, data["ID"]))
    conn.commit()
    c.close()
    conn.close()


if __name__ == '__main__':
    url = "https://api.torn.com/faction/?selections={},{},{}&key={}".format("fundsnews", "basic", "donations",
                                                                            random.choice(api_keys))
    print(url)
    user_agent = 'Relentlessbot/0.1 (+https://lt.relentless.pw/bot.html)'
    headers = {'User-Agent': user_agent, }
    req = urllib.request.Request(url, None, headers)
    with urllib.request.urlopen(req) as val:
        data = json.loads(val.read().decode())
        # Faction data
        store_faction_data(data["ID"], data["name"])
        # Member data
        store_all_members_data(data['members'])
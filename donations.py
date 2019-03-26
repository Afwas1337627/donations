import json
import random
import re
import sqlite3
import time
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
    query = """INSERT INTO members(member, member_name, faction)
        VALUES(?, ?, ?)
        ON CONFLICT(member) DO UPDATE SET 
            member_name = excluded.member_name,
            faction = excluded.faction;"""
    for this_key, this_member in all_members.items():
        c.execute(query, (this_key, this_member["name"], data["ID"]))
    conn.commit()
    c.close()
    conn.close()


def get_members(faction_id):
    query = """SELECT member FROM members
        WHERE faction = ?;"""
    conn = sqlite3.connect('donations.sqlite')
    c = conn.cursor()
    r = c.execute(query, (faction_id,))
    all_members = set()
    for member in r.fetchall():
        all_members.add(member)
    return all_members


def store_bank_data(storing_donations):
    conn = sqlite3.connect('donations.sqlite')
    c = conn.cursor()
    query = """INSERT INTO bank(stored_timestamp, member, money_balance, point_balance)
        VALUES(?, ?, ?, ?)
        ON CONFLICT(member) DO UPDATE SET 
            money_balance = excluded.money_balance,
            point_balance = excluded.point_balance,
            stored_timestamp = excluded.stored_timestamp;"""
    for this_key, this_donation in storing_donations.items():
        c.execute(query, (
            int(time.time()), this_key, this_donation["money_balance"],
            this_donation["points_balance"]))
    conn.commit()
    c.close()
    conn.close()


def analyze_donations(raw_donations):
    this_donations = []
    for this_donation in raw_donations:
        pattern = r'XID=(\d+).*?>|$'
        needles = re.search(pattern, raw_donations[this_donation]["news"])
        this_member = 0
        if needles:
            this_member = needles.group(1)
        pattern = r'\$([\d,])+|$'
        needles = re.search(pattern, raw_donations[this_donation]["news"])
        this_monies = 0
        if needles:
            this_monies = needles.group(1).replace(',', '')
        this_timestamp = raw_donations[this_donation]["timestamp"]
        this_direction = "withdrawn"
        if "deposited" in raw_donations[this_donation]["news"]:
            this_direction = "deposited"
        elif "was given" in raw_donations[this_donation]["news"]:
            pass
        else:
            print("Unknown direction in `{}`".format(raw_donations[this_donation]["news"]))
        this_full_donation = {
            "member": this_member,
            "donation": this_monies,
            "timestamp": this_timestamp,
            "direction": this_direction
        }
        this_donations.append(this_full_donation)
    return this_donations


def get_timestamp(this_member):
    query = """SELECT money_balance, stored_timestamp FROM bank
        WHERE member = ?;"""
    conn = sqlite3.connect('donations.sqlite')
    c = conn.cursor()
    r = c.execute(query, (this_member,))
    res = r.fetchone()

    return res


def store_final_donation(this_timestamp, this_member, this_amount):
    conn = sqlite3.connect('donations.sqlite')
    c = conn.cursor()
    query = """INSERT INTO bank(stored_timestamp, member, money_balance)
        VALUES(?, ?, ?)
        ON CONFLICT(member) DO UPDATE SET 
            money_balance = excluded.money_balance,
            point_balance = excluded.point_balance,
            stored_timestamp = excluded.stored_timestamp;"""
    for this_key, this_donation in all_donations.items():
        c.execute(query, (this_timestamp, this_member, this_amount))


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
        members = set()
        for key in data['members']:
            members.add(key)
        database_members = get_members(8336)
        new_members = members - database_members
        old_members = database_members - members

        store_bank_data(data["donations"])
        donations = []
        all_donations = analyze_donations(data["donationnews"])
        for donation in all_donations:
            if donation["member"] in old_members:
                # Since old_members are in database this should
                # always return a valid result
                last_available_data = get_timestamp(donation["member"])
                last_available_money = last_available_data[0]
                last_available_timestamp = last_available_data[1]
                posthumously_withdrawals = []
                this_withdrawal = {}
                if last_available_timestamp < donations["timestamp"]:
                    this_withdrawal["timestamp"] = donation["timestamp"]
                    this_withdrawal["final_deposit"] = last_available_timestamp
                    this_withdrawal["member"] = donation["member"]
                    this_withdrawal["direction"] = donation["direction"]
                    this_withdrawal["donation"] = donation["donation"]
                    posthumously_withdrawals.append(this_withdrawal)

                for this_withdrawal in posthumously_withdrawals:
                    if this_withdrawal["direction"] == "withdrawn":
                        this_withdrawal["donation"] = 0 - this_withdrawal["donation"]
                    last_available_money += this_withdrawal["donation"]
                    store_final_donation(this_withdrawal["member"], last_available_money)

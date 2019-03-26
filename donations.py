import json
import random
import re
import sqlite3
import time
import urllib.request
# from pprint import pprint

import passwords


def store_faction_data(this_id, this_name):
    """
    Store data for a single faction in table factions
    :param this_id:
    :param this_name:
    :return:
    """
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
    """
    Store data for all members in the table members
    :param all_members:
    :return:
    """
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
    """
    Return a set with ids for all members in the members table
    :param faction_id:
    :return all_members:
    """
    query = """SELECT member FROM members
        WHERE faction = ?;"""
    conn = sqlite3.connect('donations.sqlite')
    c = conn.cursor()
    r = c.execute(query, (faction_id,))
    all_members = set()
    for member in r.fetchall():
        all_members.add(str(member[0]))
    c.close()
    conn.close()
    return all_members


def store_bank_data(storing_donations):
    """
    Store data for all bank accounts in the table bank
    :param storing_donations:
    :return:
    """
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
    """
    Analyze the raw donation data and filter out member ID,
    the amount that was deposited or taken and the operation
    (withdrawal or deposited)
    :param raw_donations:
    :return this_donations:
    """
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
    """
    Retrieve the latest bank account balance for given member
    :param this_member:
    :return res:
    """
    query = """SELECT money_balance, stored_timestamp FROM bank
        WHERE member = ?;"""
    conn = sqlite3.connect('donations.sqlite')
    c = conn.cursor()
    r = c.execute(query, (this_member,))
    res = r.fetchone()
    c.close()
    conn.close()
    return res


def store_final_donation(this_timestamp, this_member, this_amount):
    """
    For a member that has left the faction store the updated bank
    account balance
    :param this_timestamp:
    :param this_member:
    :param this_amount:
    :return:
    """
    conn = sqlite3.connect('donations.sqlite')
    c = conn.cursor()
    query = """INSERT INTO bank(stored_timestamp, member, money_balance)
        VALUES(?, ?, ?)
        ON CONFLICT(member) DO UPDATE SET 
            money_balance = excluded.money_balance,
            point_balance = excluded.point_balance,
            stored_timestamp = excluded.stored_timestamp;"""
    c.execute(query, (this_timestamp, this_member, this_amount))
    conn.commit()
    c.close()
    conn.close()


def get_new_faction_for_old_member(this_member):
    this_url = "https://api.torn.com/user/{}?selections=&key={}".format(this_member, random.choice(api_keys))
    # this_user_agent = 'Relentlessbot/0.1 (+https://lt.relentless.pw/bot.html)'
    # this_headers = {'User-Agent': this_user_agent, }
    this_req = urllib.request.Request(this_url, None, headers)
    with urllib.request.urlopen(this_req) as this_val:
        this_data = json.loads(this_val.read().decode())
        faction_id = this_data["faction"]["faction_id"]
        faction_name = this_data["faction"]["faction_name"]
        print("{} [{}] is member of {} [{}]".format(
            this_data["name"],
            this_data["player_id"],
            faction_id,
            faction_name
        ))
        conn = sqlite3.connect('donations.sqlite')
        c = conn.cursor()

        query = """INSERT INTO factions(faction, faction_name)
            VALUES(?, ?)
            ON CONFLICT(faction) DO UPDATE SET 
            faction_name = excluded.faction_name;"""
        c.execute(query, (faction_id, faction_name))
        conn.commit()

        query = """UPDATE members 
            SET faction = ?,
                member_name = ?
            WHERE member = ?;"""
        c.execute(query, (faction_id, this_data["name"], this_data["player_id"]))
        conn.commit()

        c.close()
        conn.close()


def prune_database():
    conn = sqlite3.connect('donations.sqlite')
    c = conn.cursor()
    query = """DELETE FROM bank
        WHERE money_balance = 0
        AND point_balance = 0
        AND member IN (
            SELECT member FROM members WHERE faction != ?);"""
    c.execute(query, (my_faction,))
    conn.commit()
    c.close()
    conn.close()


if __name__ == '__main__':
    my_faction = 8336
    # File passwords.py not in git
    api_keys = passwords.api_keys
    url = "https://api.torn.com/faction/?selections={},{},{}&key={}".format("fundsnews", "basic", "donations",
                                                                            random.choice(api_keys))
    user_agent = 'Relentlessbot/0.1 (+https://lt.relentless.pw/bot.html)'
    headers = {'User-Agent': user_agent, }
    req = urllib.request.Request(url, None, headers)
    with urllib.request.urlopen(req) as val:
        data = json.loads(val.read().decode())
        # Faction data
        store_faction_data(data["ID"], data["name"])
        # Member data
        store_all_members_data(data['members'])
        # Compare database with list from API
        members = set()
        for key in data['members']:
            members.add(key)
        database_members = get_members(my_faction)
        new_members = members - database_members
        old_members = database_members - members
        # Bank
        store_bank_data(data["donations"])
        # This section handles members that have left the
        # faction. Final details on their bank account only live
        # in the donationnews from API
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
                if last_available_timestamp < donation["timestamp"]:
                    # It is very possible that there are more than one
                    # withdrawals in the time between the latest API
                    # poll and the time the member left the faction
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
                    store_final_donation(int(time.time()), this_withdrawal["member"], last_available_money)

                get_new_faction_for_old_member(donation["member"])
                prune_database()

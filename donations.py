import json
import random
import re
import sqlite3
import urllib.request
from pprint import pprint


def store_donation(this_key, this_donation):
    member = 'Unknown'
    donation = '0'
    conn = sqlite3.connect('donations.sqlite')
    c = conn.cursor()
    if 'deposited' in this_donation['news']:
        # Player deposited money
        regex = r'XID=(\d+).*?>(\w+)<\/a> deposited \$([\d,]+)$'
        d = re.search(regex, this_donation['news'])
        if d:
            member = d.group(1)
            name = d.group(2)
            donation = d.group(3).replace(',', '')
        print(this_donation['news'])
        print(member)
        print(donation)
        query = """INSERT INTO donations(
                donator, donation_id, donation_timestamp, donation_text, donation_amount) 
                VALUES(?, ?, ?, ?, ?)
                ON CONFLICT(donator, donation_timestamp) DO NOTHING;"""
        c.execute(query, (member, this_key, this_donation['timestamp'], this_donation['news'],
                          donation))
    conn.commit()
    c.close()
    conn.close()


if __name__ == '__main__':
    url = "https://api.torn.com/faction/?selections={},{},{}&key={}".format("fundsnews", "basic", "donations", random.choice(api_keys))
    print(url)
    user_agent = 'Relentlessbot/0.1 (+https://lt.relentless.pw/bot.html)'
    headers = {'User-Agent': user_agent, }
    req = urllib.request.Request(url, None, headers)
    with urllib.request.urlopen(req) as val:
        data = json.loads(val.read().decode())
        pprint(data)
        for key, donation in data["donationnews"].items():
            store_donation(key, donation)
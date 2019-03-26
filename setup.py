import sqlite3


if __name__ == '__main__':
    conn = sqlite3.connect('donations.sqlite')
    c = conn.cursor()

    query = """DROP TABLE IF EXISTS factions;"""
    c.execute(query)
    query = """DROP TABLE IF EXISTS members;"""
    c.execute(query)
    query = """DROP TABLE IF EXISTS bank;"""
    c.execute(query)
    conn.commit()

    query = """CREATE TABLE factions(
        id INTEGER PRIMARY KEY,
        faction INTEGER UNIQUE,
        faction_name TEXT);"""

    c.execute(query)
    conn.commit()

    query = """CREATE TABLE members(
        id INTEGER PRIMARY KEY,
        member INTEGER UNIQUE,
        member_name TEXT,
        faction INTEGER,
        FOREIGN KEY(faction) REFERENCES factions(faction));"""
    c.execute(query)
    conn.commit()

    query = """CREATE TABLE bank(
        id INTEGER PRIMARY KEY,
        stored_timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        member INTEGER UNIQUE,
        money_balance INTEGER,
        point_balance INTEGER,
        FOREIGN KEY (member) REFERENCES members(member));"""
    c.execute(query)
    conn.commit()

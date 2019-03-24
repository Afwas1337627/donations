import sqlite3


if __name__ == '__main__':
    conn = sqlite3.connect('donations.sqlite')
    c = conn.cursor()

    query = """DROP TABLE IF EXISTS factions;"""
    c.execute(query)
    query = """DROP TABLE IF EXISTS members;"""
    c.execute(query)
    query = """DROP TABLE IF EXISTS donations;"""
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
        money_donated INTEGER DEFAULT 0,
        points_donated INTEGER DEFAULT 0,
        FOREIGN KEY(faction) REFERENCES factions(faction));"""
    c.execute(query)
    conn.commit()

    query = """CREATE TABLE donations(
        id INTEGER PRIMARY KEY,
        donation_amount INTEGER,
        donation_timestamp INTEGER,
        donation_id INTEGER,
        donation_text INTEGER,
        banker INTEGER DEFAULT 0,
        donator INTEGER,
        UNIQUE(donator, donation_timestamp),
        FOREIGN KEY(donator) REFERENCES members(member));"""
    c.execute(query)
    conn.commit()

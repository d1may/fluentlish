import sqlite3

def main_db():
    con = sqlite3.connect("dict.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS dictionary (
        user_id INTEGER,
        word TEXT,
        rating INTEGER CHECK(rating BETWEEN 1 AND 10),
        last_seen TIMESTAMP,
        PRIMARY KEY (user_id, word)
    )
    """)
    con.commit()
    con.close()
    
def status_db():
    con = sqlite3.connect("dict.db")
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS vip (
        user_id INTEGER,
        isPremium INTEGER DEFAULT 0,
        start_date TEXT,
        end_date TEXT,
        PRIMARY KEY (user_id)
    )
    """)
    con.commit()
    con.close()
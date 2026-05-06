import json
import sqlite3
import re
import pandas as pd

def parse_text(text):
    # Regex to extract structured data
    ship_match = re.search(r"ship (.*?) sailing", text)
    flag_match = re.search(r"under (.*?) colors", text)
    date_match = re.search(r"Dated ([\d\-]+)", text)

    cargo_items = {}
    for item in ["timber", "tar", "pitch", "hemp"]:
        # Find quantity of each specific item
        item_match = re.search(rf"(\d+) tons of {item}", text)
        if item_match:
            cargo_items[item] = int(item_match.group(1))
        else:
            cargo_items[item] = 0

    flag_hopping = 1 if "Suspicious registry papers" in text else 0

    return {
        "ship_name": ship_match.group(1).strip() if ship_match else "Unknown",
        "flag_state": flag_match.group(1).strip() if flag_match else "Unknown",
        "date": date_match.group(1).strip() if date_match else "Unknown",
        "timber_tons": cargo_items["timber"],
        "tar_tons": cargo_items["tar"],
        "pitch_tons": cargo_items["pitch"],
        "hemp_tons": cargo_items["hemp"],
        "flag_hopping": flag_hopping
    }

def setup_db():
    conn = sqlite3.connect('prize_papers_dataset.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS naval_stores_trade (
        id TEXT PRIMARY KEY,
        ship_name TEXT,
        flag_state TEXT,
        date TEXT,
        timber_tons INTEGER,
        tar_tons INTEGER,
        pitch_tons INTEGER,
        hemp_tons INTEGER,
        flag_hopping INTEGER,
        raw_text TEXT
    )
    ''')
    conn.commit()
    return conn

def main():
    with open('ocr_results.json', 'r') as f:
        records = json.load(f)

    conn = setup_db()
    cursor = conn.cursor()

    for record in records:
        parsed = parse_text(record['raw_text'])
        cursor.execute('''
        INSERT OR REPLACE INTO naval_stores_trade
        (id, ship_name, flag_state, date, timber_tons, tar_tons, pitch_tons, hemp_tons, flag_hopping, raw_text)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record['id'],
            parsed['ship_name'],
            parsed['flag_state'],
            parsed['date'],
            parsed['timber_tons'],
            parsed['tar_tons'],
            parsed['pitch_tons'],
            parsed['hemp_tons'],
            parsed['flag_hopping'],
            record['raw_text']
        ))

    conn.commit()

    # Export to CSV for Antigravity engine
    df = pd.read_sql_query("SELECT * FROM naval_stores_trade", conn)
    df.to_csv("structured_dataset.csv", index=False)

    print(f"Stored {len(records)} records in database and exported to structured_dataset.csv")
    conn.close()

if __name__ == "__main__":
    main()

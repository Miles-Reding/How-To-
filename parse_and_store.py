import json
import sqlite3
import pandas as pd
import os

def setup_db(db_path='prize_papers_dataset.db'):
    conn = sqlite3.connect(db_path)
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
    data_file = 'gemini_extracted_data.json'
    if not os.path.exists(data_file):
        print(f"Warning: Data file {data_file} not found. Please run process_with_gemini.py first.")
        return

    print(f"Loading data from {data_file}")
    with open(data_file, 'r') as f:
        records = json.load(f)

    conn = setup_db()
    cursor = conn.cursor()

    for record in records:
        cursor.execute('''
        INSERT OR REPLACE INTO naval_stores_trade
        (id, ship_name, flag_state, date, timber_tons, tar_tons, pitch_tons, hemp_tons, flag_hopping, raw_text)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.get('id', 'unknown_id'),
            record.get('ship_name', 'Unknown'),
            record.get('flag_state', 'Unknown'),
            record.get('date', 'Unknown'),
            record.get('timber_tons', 0),
            record.get('tar_tons', 0),
            record.get('pitch_tons', 0),
            record.get('hemp_tons', 0),
            record.get('flag_hopping', 0),
            record.get('raw_text', '')
        ))

    conn.commit()

    df = pd.read_sql_query("SELECT * FROM naval_stores_trade", conn)
    df.to_csv("structured_dataset.csv", index=False)

    print(f"Stored {len(records)} records in database and exported to structured_dataset.csv")
    conn.close()

if __name__ == "__main__":
    main()

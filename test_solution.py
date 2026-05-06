import pytest
import sqlite3
import pandas as pd
import os
import json

from parse_and_store import setup_db

def test_database_creation(tmp_path):
    db_path = tmp_path / "test_db.db"
    conn = setup_db(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='naval_stores_trade'")
    assert cursor.fetchone() is not None
    conn.close()

def test_narrative_verification(tmp_path):
    db_path = tmp_path / "test_db.db"
    conn = setup_db(db_path)
    cursor = conn.cursor()

    mock_records = [
        ("id1", "PreBerlin", "Neutral", "1805-01-01", 100, 0, 0, 0, 0, "mock"),
        ("id2", "PostBerlin", "British", "1807-06-01", 0, 100, 0, 0, 1, "mock"),
        ("id3", "PostMilan", "Neutral", "1808-01-01", 0, 0, 100, 0, 0, "mock")
    ]

    cursor.executemany('''
    INSERT INTO naval_stores_trade
    (id, ship_name, flag_state, date, timber_tons, tar_tons, pitch_tons, hemp_tons, flag_hopping, raw_text)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', mock_records)
    conn.commit()
    conn.close()

    import narrative_verification
    csv_path = tmp_path / "test_verified.csv"
    narrative_verification.verify_narrative(db_path=str(db_path), output_csv=str(csv_path))

    assert os.path.exists(csv_path)
    df = pd.read_csv(csv_path)
    assert len(df) == 3

    evasion_row = df[df['id'] == 'id2'].iloc[0]
    assert evasion_row['evasion_tactic_verified'] == True

    normal_row = df[df['id'] == 'id1'].iloc[0]
    assert normal_row['evasion_tactic_verified'] == False

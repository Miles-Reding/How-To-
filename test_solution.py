import pytest
import sqlite3
import pandas as pd
import os

def test_database_exists():
    assert os.path.exists('prize_papers_dataset.db')

def test_database_records():
    conn = sqlite3.connect('prize_papers_dataset.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM naval_stores_trade")
    count = cursor.fetchone()[0]
    assert count > 0, "Database should contain records"
    conn.close()

def test_exported_csv():
    assert os.path.exists('structured_dataset.csv')
    df = pd.read_csv('structured_dataset.csv')
    assert len(df) > 0, "CSV should contain records"
    assert 'timber_tons' in df.columns

def test_verified_dataset():
    assert os.path.exists('verified_dataset.csv')
    df = pd.read_csv('verified_dataset.csv')
    assert 'evasion_tactic_verified' in df.columns
    # Check that boolean column exists
    assert df['evasion_tactic_verified'].dtype == bool

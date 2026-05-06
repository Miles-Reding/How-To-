import pandas as pd
import sqlite3

def verify_narrative(db_path='prize_papers_dataset.db', output_csv='verified_dataset.csv'):
    # Berlin Decree: Nov 21, 1806
    # Milan Decree: Dec 17, 1807

    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM naval_stores_trade", conn)

    # Safely convert to datetime, setting 'Unknown' or invalid strings to NaT
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    berlin_decree_date = pd.to_datetime("1806-11-21")
    milan_decree_date = pd.to_datetime("1807-12-17")

    df['evasion_tactic_verified'] = False

    for idx, row in df.iterrows():
        # Only verify if we have a valid date
        if pd.notna(row['date']):
            # Verify evasion if after Berlin Decree and flag-hopping is true
            if row['date'] > berlin_decree_date and row['flag_hopping'] == 1:
                df.at[idx, 'evasion_tactic_verified'] = True

    print(f"Total records processed: {len(df)}")
    print(f"Evasion tactics identified post-Berlin Decree: {df['evasion_tactic_verified'].sum()}")

    # Analyze Baltic trade volume before and after Berlin Decree
    # Ignore records with unknown dates for this specific aggregation
    df_valid_dates = df.dropna(subset=['date'])
    pre_decree = df_valid_dates[df_valid_dates['date'] <= berlin_decree_date]
    post_berlin = df_valid_dates[(df_valid_dates['date'] > berlin_decree_date) & (df_valid_dates['date'] <= milan_decree_date)]
    post_milan = df_valid_dates[df_valid_dates['date'] > milan_decree_date]

    pre_vol = pre_decree[['timber_tons', 'tar_tons', 'pitch_tons', 'hemp_tons']].sum().sum()
    post_berlin_vol = post_berlin[['timber_tons', 'tar_tons', 'pitch_tons', 'hemp_tons']].sum().sum()
    post_milan_vol = post_milan[['timber_tons', 'tar_tons', 'pitch_tons', 'hemp_tons']].sum().sum()

    print(f"Total Naval Stores Volume Pre-Decree: {pre_vol} tons")
    print(f"Total Naval Stores Volume Post-Berlin: {post_berlin_vol} tons")
    print(f"Total Naval Stores Volume Post-Milan: {post_milan_vol} tons")

    # Re-fill NaT with string 'Unknown' before saving to CSV for readability
    df['date'] = df['date'].dt.strftime('%Y-%m-%d').fillna('Unknown')

    # Update the CSV with the verification flags
    df.to_csv(output_csv, index=False)
    print(f"Verification complete. Exported to {output_csv}")

if __name__ == "__main__":
    verify_narrative()

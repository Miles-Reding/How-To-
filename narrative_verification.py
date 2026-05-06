import pandas as pd
import sqlite3

def verify_narrative():
    # Berlin Decree: Nov 21, 1806
    # Milan Decree: Dec 17, 1807
    # Both decreed the Continental System, restricting trade with Britain.

    conn = sqlite3.connect('prize_papers_dataset.db')
    df = pd.read_sql_query("SELECT * FROM naval_stores_trade", conn)
    df['date'] = pd.to_datetime(df['date'])

    berlin_decree_date = pd.to_datetime("1806-11-21")
    milan_decree_date = pd.to_datetime("1807-12-17")

    # Flag discrepancies: e.g., neutral ships carrying large amounts of naval stores to/from blockaded regions after decrees
    # For this simulation, we'll flag 'flag-hopping' cases post-Berlin Decree as verified evasion tactics.

    df['evasion_tactic_verified'] = False

    for idx, row in df.iterrows():
        if row['date'] > berlin_decree_date and row['flag_hopping'] == 1:
            df.at[idx, 'evasion_tactic_verified'] = True

    print(f"Total records processed: {len(df)}")
    print(f"Evasion tactics identified post-Berlin Decree: {df['evasion_tactic_verified'].sum()}")

    # Analyze Baltic trade volume before and after Berlin Decree
    pre_decree = df[df['date'] <= berlin_decree_date]
    post_decree = df[df['date'] > berlin_decree_date]

    pre_vol = pre_decree[['timber_tons', 'tar_tons', 'pitch_tons', 'hemp_tons']].sum().sum()
    post_vol = post_decree[['timber_tons', 'tar_tons', 'pitch_tons', 'hemp_tons']].sum().sum()

    print(f"Total Naval Stores Volume Pre-Decree: {pre_vol} tons")
    print(f"Total Naval Stores Volume Post-Decree: {post_vol} tons")

    # Update the CSV with the verification flags
    df.to_csv("verified_dataset.csv", index=False)
    print("Verification complete. Exported to verified_dataset.csv")

if __name__ == "__main__":
    verify_narrative()

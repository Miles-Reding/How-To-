import json
import random
from datetime import datetime, timedelta

def generate_mock_manifests(num_records=50):
    ships = ["Flora", "James Lovett", "Merchant of Venice", "Sea Gull", "Baltic Star", "Nordic Wind", "St. Petersburg Trader"]
    flags = ["British", "French", "Neutral (Danish)", "Neutral (Swedish)", "Neutral (American)", "Dutch"]
    goods = ["timber", "tar", "pitch", "hemp", "iron", "wheat"]

    records = []

    start_date = datetime(1806, 1, 1) # Around the time of the Decrees

    for i in range(num_records):
        ship_name = random.choice(ships)
        flag = random.choice(flags)

        # Determine if there's flag hopping (e.g. neutral flag but British ownership hinted)
        flag_hopping = False
        if "Neutral" in flag and random.random() > 0.7:
            flag_hopping = True

        date = start_date + timedelta(days=random.randint(0, 365*4))

        cargo = []
        for _ in range(random.randint(1, 4)):
            item = random.choice(goods)
            quantity = random.randint(50, 500)
            cargo.append(f"{quantity} tons of {item}")

        raw_text = f"Manifest of the ship {ship_name} sailing under {flag} colors. Dated {date.strftime('%Y-%m-%d')}. Cargo consisting of: {', '.join(cargo)}."
        if flag_hopping:
            raw_text += " Note: Suspicious registry papers indicate prior British ownership."

        records.append({
            "id": f"HCA_32_{random.randint(1000, 9999)}",
            "raw_text": raw_text,
            "image_url": "mock_url"
        })

    with open('ocr_results.json', 'w') as f:
        json.dump(records, f, indent=2)

generate_mock_manifests()
print("Mock OCR data generated.")

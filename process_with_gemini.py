import os
import json
import glob
import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, RetryError
from typing_extensions import TypedDict

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY environment variable not set. Running in dummy mode.")

genai.configure(api_key=api_key)

class ManifestData(TypedDict):
    ship_name: str
    flag_state: str
    date: str
    timber_tons: int
    tar_tons: int
    pitch_tons: int
    hemp_tons: int
    flag_hopping: int

def get_dummy_response(img_path):
    return {
        "ship_name": "Mock Star",
        "flag_state": "Neutral (Swedish)",
        "date": "1808-05-12",
        "timber_tons": 100,
        "tar_tons": 50,
        "pitch_tons": 0,
        "hemp_tons": 0,
        "flag_hopping": 1
    }

def process_image_with_retry(img_path, model, max_retries=5):
    if not os.environ.get("GEMINI_API_KEY"):
        return get_dummy_response(img_path)

    print(f"Uploading {img_path} to Gemini...")
    sample_file = genai.upload_file(path=img_path, display_name=os.path.basename(img_path))

    prompt = """
    Analyze this 18th/19th-century ship's cargo manifest or legal document.
    Extract the following information and return it strictly as JSON:
    - ship_name: The name of the ship (string).
    - flag_state: The nationality or flag the ship is sailing under (string).
    - date: The date of the document (YYYY-MM-DD format if possible, or extract the year as a string).
    - timber_tons: The quantity of timber in tons (integer).
    - tar_tons: The quantity of tar in tons (integer).
    - pitch_tons: The quantity of pitch in tons (integer).
    - hemp_tons: The quantity of hemp in tons (integer).
    - flag_hopping: An integer (1 or 0). Set to 1 if there is ANY indication of suspicious registry papers, evasion of blockade, fake neutral colors, or prior ownership by a belligerent nation. Otherwise 0.

    If a specific cargo amount is not found, default to 0. If a string field is not found, use 'Unknown'.
    """

    retries = 0
    while retries < max_retries:
        try:
            print(f"Processing {img_path} with Gemini... (Attempt {retries + 1})")
            response = model.generate_content(
                [sample_file, prompt],
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=ManifestData,
                    temperature=0.1,
                ),
            )
            result = json.loads(response.text)
            genai.delete_file(sample_file.name)
            return result
        except ResourceExhausted:
            wait_time = (2 ** retries) * 10
            print(f"Rate limit exceeded (429). Waiting {wait_time} seconds before retrying...")
            time.sleep(wait_time)
            retries += 1
        except Exception as e:
            print(f"Error processing with Gemini: {e}")
            genai.delete_file(sample_file.name)
            return None

    print(f"Failed to process {img_path} after {max_retries} retries.")
    genai.delete_file(sample_file.name)
    return None

def main():
    model = genai.GenerativeModel('gemini-2.5-flash')

    image_files = glob.glob("downloaded_images/*.jpg")
    if not image_files:
        print("No images found in downloaded_images/. Run download_sample_images.py first.")
        return

    output_file = 'gemini_extracted_data.json'

    # Load existing results to allow resuming a crashed run
    existing_results = {}
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r') as f:
                data = json.load(f)
                for item in data:
                    existing_results[item['id']] = item
            print(f"Loaded {len(existing_results)} existing records. Resuming...")
        except json.JSONDecodeError:
            print("Warning: Could not parse existing JSON file. Starting fresh.")

    results_list = list(existing_results.values())
    processed_count = 0

    for img_path in image_files:
        doc_id = os.path.basename(img_path).replace(".jpg", "")

        # Skip if already processed successfully
        if doc_id in existing_results:
            continue

        data = process_image_with_retry(img_path, model)
        if data:
            data["id"] = doc_id
            data["raw_text"] = "Processed via Gemini Vision API directly to JSON."
            results_list.append(data)
            processed_count += 1

            # Incremental save: save immediately after successful processing
            with open(output_file, 'w') as f:
                json.dump(results_list, f, indent=2)

        # Basic delay to avoid hitting the standard RPM limit too fast
        time.sleep(3)

    print(f"\nRun complete. Processed {processed_count} new documents.")
    print(f"Total dataset size: {len(results_list)} documents saved to {output_file}.")

if __name__ == "__main__":
    main()

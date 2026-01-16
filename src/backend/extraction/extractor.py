from llama_parse import LlamaParse
import json
from pathlib import Path
from src.backend.config.settings import settings

def extract_pdf_to_json(
    pdf_path: str,
    api_key: str,
    output_dir: str = "extracted_output"
):
    print(f"📄 Extracting: {pdf_path}")
    
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"❌ Error: File not found at {pdf_path}")

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # --- UPDATED CONFIGURATION ---
    parser = LlamaParse(
        api_key=api_key,
        result_type="markdown",
        system_prompt=(
            "You are an expert at extracting technical tables from engineering standards. "
            "Extract ALL data tables from the document into a strict JSON format. "
            "For each table, capture the table title and all rows. "
            "Ensure numerical values (like 1.83) are stored as numbers, not strings where possible. "
            "Represent '—' or empty cells as null."
            "Do not skip any rows."
        ),
        premium_mode=True, 
        verbose=True
    )
    
    print("⏳ Extracting...")
    
    # 3. Direct Load (Fixes the empty list issue)
    json_objects = parser.load_data(pdf_path)
    
    # 4. Debugging Empty Result
    if not json_objects:
        print("❌ Error: Parser returned NO data. Check if file has selectable text or valid tables.")
        return []

    # 5. Extract the actual data structure
    # LlamaParse JSON result usually comes as a list of dicts or objects with a 'json_resource' key
    try:
        # If it returns a list of LlamaIndex Document objects, try getting the text
        if hasattr(json_objects[4], 'text'):
            # The 'text' field often contains the JSON string in JSON mode
            final_data = json.loads(json_objects[4].text)
        elif isinstance(json_objects[4], dict):
            final_data = json_objects
        else:
            # Fallback for some API versions
            final_data = [doc.to_dict() for doc in json_objects]
            
    except Exception as e:
        print(f"⚠️ Warning during JSON parse ({e}). Saving raw output.")
        final_data = json_objects

    # Save
    output_file = Path(output_dir) / f"{Path(pdf_path).stem}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved: {output_file}")
    return final_data

if __name__ == "__main__":
    # Use raw string for Windows path
    pdf_file = r"assets/sources/IS-8130-original.pdf"
    
    try:
        data = extract_pdf_to_json(
            pdf_path=pdf_file,
            api_key=settings.llama_cloud_api_key,
            output_dir="extracted_output"
        )
        print("✅ Extraction finished successfully.")
    except Exception as e:
        print(f"❌ Failed: {e}")
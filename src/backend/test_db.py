import json
from typing import Dict, Any
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from src.backend.db.database import Base
from src.backend.db.models.conductor_spec_model import ConductorSpec
from src.backend.config.settings import settings



def check_table_and_load_data(json_file_path: str):
    """Check if table is created and load data from JSON file."""
    
    # Setup database
    engine = create_engine(settings.database_url, echo=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    print("="*70)
    print("CONDUCTOR TABLE CHECK & DATA LOAD")
    print("="*70)
    
    # Check if table exists
    print("\n[STEP 1] Checking if table exists...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables in database: {tables}")
    
    if "conductor_specs" in tables:
        print("✓ Table 'conductor_specs' exists")
        
        # Check columns
        columns = inspector.get_columns("conductor_specs")
        print("\nColumns:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    else:
        print("✗ Table 'conductor_specs' does NOT exist")
        return
    
    # Load JSON file
    print(f"\n[STEP 2] Loading JSON from: {json_file_path}")
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        print("✓ JSON file loaded successfully")
    except FileNotFoundError:
        print(f"✗ File not found: {json_file_path}")
        return
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON: {e}")
        return
    
    # Load data into database
    print("\n[STEP 3] Loading data into database...")
   
    try:
        count = load_from_json(json_data, db)
        print(f"✓ Successfully loaded {count} records")
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        db.close()
        return
    
    # Verify data in database
    print("\n[STEP 4] Verifying data in database...")
    total_records = db.query(ConductorSpec).count()
    print(f"Total records in database: {total_records}")
    
    if total_records > 0:
        print("\nFirst 5 records:")
        records = db.query(ConductorSpec).limit(5).all()
        for record in records:
            print(f"  - CSA: {record.csa_mm2} mm² | Cu: {record.max_resistance_cu_plain} Ω/km | Al: {record.max_resistance_al} Ω/km")
    
    # Check specific CSA
    print("\n[STEP 5] Testing specific CSA lookup...")
    test_csa = 10.0
    spec = db.query(ConductorSpec).filter(ConductorSpec.csa_mm2 == test_csa).first()
    
    if spec:
        print(f"✓ Found specification for {test_csa} mm²:")
        print(f"  - Min wires (Cu circular): {spec.min_wires_cu_circular}")
        print(f"  - Max resistance (Cu plain): {spec.max_resistance_cu_plain} Ω/km")
        print(f"  - Max resistance (Al): {spec.max_resistance_al} Ω/km")
    else:
        print(f"✗ No specification found for {test_csa} mm²")
    
    print("\n" + "="*70)
    print("TABLE CHECK & DATA LOAD COMPLETE")
    print("="*70)
    
    db.close()


def load_from_json(json_data: Dict[str, Any], db: Session) -> int:
    count = 0
        
    try:
        for table in json_data.get("tables", []):
            rows = table.get("rows", [])
                
            for row in rows:
                spec = ConductorSpec(
                    csa_mm2=float(row["nominal_cross_sectional_area"]),
                        
                    min_wires_cu_circular=row.get("min_wires_circular_cu"),
                    min_wires_cu_compacted=row.get("min_wires_compacted_cu"),
                    max_resistance_cu_plain=row.get("max_resistance_cu_plain"),
                    max_resistance_cu_tinned=row.get("max_resistance_cu_tinned"),
                        
                    min_wires_al_circular=row.get("min_wires_circular_al") if isinstance(row.get("min_wires_circular_al"), int) else None,
                    min_wires_al_compacted=row.get("min_wires_compacted_al"),
                    max_resistance_al=row.get("max_resistance_al"),
                    note=row.get("note")
                )
                db.add(spec)
                count += 1
            
        db.commit()
        return count
    except Exception as e:
        db.rollback()
        raise e

if __name__ == "__main__":
    # Replace with your JSON file path
    json_file_path = "extracted_output/conductor_v1.json"
    check_table_and_load_data(json_file_path)



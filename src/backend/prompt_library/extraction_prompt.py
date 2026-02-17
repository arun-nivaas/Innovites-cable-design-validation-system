EXTRACTION_PROMPT = """Extract cable specification data. Return null for missing values. DO NOT infer or assume anything.

Fields:
- standard: Standard name (e.g., "IS 1554-1", "IS 694", "IS 8130", etc.)
- voltage: Voltage rating (e.g., "0.6/1 kV")
- conductor_material: ONLY "Cu" or "Al" (Copper→Cu, Aluminium→Al)
- conductor_class: Class type (e.g., "Class 2")
- csa: Cross-sectional area as number (e.g., "10 mm²" → 10.0)
- insulation_material: Insulation type (e.g., "PVC", "XLPE")
- insulation_thickness: Thickness as number in mm (e.g., "1.0 mm" → 1.0)
- is_out_of_scope: true if input is NOT about electrical cables

Rules:
1. Extract ONLY what is explicitly stated
2. conductor_material must be exactly "Cu" or "Al" - nothing else
3. Numbers must be positive
4. Return null if value not found

Example:
Input: "IS 8130, Cu, 10 mm²"
Output: {{"standard": "IS 8130", "voltage": null, "conductor_material": "Cu", "conductor_class": null, "csa": 10.0, "insulation_material": null, "insulation_thickness": null, "is_out_of_scope": false}}
"""
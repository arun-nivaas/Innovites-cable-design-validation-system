import streamlit as st
import requests
import pandas as pd

# Page config
st.set_page_config(page_title="Cable Design Validator",page_icon="⚡",layout="wide")

# Minimal CSS
st.markdown("""
    <style>
    .main {padding: 2rem;}
    .stButton>button {width: 100%; height: 3em; font-weight: 600;}
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'result' not in st.session_state:
    st.session_state.result = None

# Title
st.title("⚡ Cable Design Validator")
st.divider()

st.subheader("📝 Input")
tab1, tab2 = st.tabs(["Free Text", "Form"])

# Free Text Input
with tab1:
    free_text = st.text_area(
        "Design Specification",
        height=200,
        placeholder="IEC 60502-1 cable, 16 sqmm Cu Class 2, PVC insulation 0.9 mm",
        key="free_text"
    )
    validate_free = st.button("🔍 Validate", type="primary", key="btn_free")
    user_input = free_text if validate_free else None
    
# Structured Form
with tab2:
    standard = st.text_input("Standard", "IEC 60502-1")
    voltage = st.text_input("Voltage", "0.6/1 kV")
        
    col_a, col_b = st.columns(2)
    with col_a:
        csa = st.number_input("CSA (mm²)", 1.5, 1000.0, 16.0)
        material = st.selectbox("Material", ["Cu", "Al"])
    with col_b:
        conductor_class = st.selectbox("Class", ["Class 1", "Class 2"])
        insulation = st.text_input("Insulation", "PVC")
        
    thickness = st.number_input("Thickness (mm)", 0.1, 10.0, 0.9)
        
    validate_form = st.button("🔍 Validate", type="primary", key="btn_form")
        
    if validate_form:
        user_input = f"{standard}, {voltage}, {material}, {conductor_class}, {csa} mm², {insulation}, {thickness} mm"
    elif not validate_free:
        user_input = None


st.subheader("📊 Validation Results")
    
    # Validate API call
if user_input and user_input.strip():
    with st.spinner("Validating..."):
        try:
            response = requests.post(
                "http://localhost:8000/design/validate",
                json={"input": user_input},
                timeout=50
            )
                
            if response.status_code == 200:
                st.session_state.result = response.json()
            else:
                st.error(f"API Error: {response.status_code}")
                    
        except requests.exceptions.ConnectionError:
            st.error("🔌 Backend not running on port 8000")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    # Display Results Table
if st.session_state.result:
    result = st.session_state.result
        
    # FIX: Check as boolean, not string. Handle the correct key for explanation.
    if result.get("is_out_of_scope") is True:
        st.error("⚠️ OUT OF SCOPE")
        # FIX: Key name matches your JSON structure
        explanation = result.get("out_of_scope_explanation", "This input is not a cable design.")
        st.info(explanation)
        
    else:
        validation_items = result.get("validation", [])
            
        if validation_items:
            # Build table data
            table_data = []
            for item in validation_items:
                field_name = item.get("field", "")
                # Get provided value from fields
                provided = result.get("fields", {}).get(field_name, "—")
                    
                table_data.append({
                    "Attribute": field_name.replace("_", " ").title(),
                    "Provided": str(provided) if provided is not None else "—",
                    "Expected": item.get("expected", "—"),
                    "Status": item.get("status", ""),
                    "Comment": item.get("comment", "")
                })
                
            df = pd.DataFrame(table_data)
                
            # Apply color coding
            def color_status(val):
                if val == "PASS":
                    return "background-color: #d4edda; color: #155724; font-weight: bold;"
                elif val == "WARN":
                    return "background-color: #fff3cd; color: #856404; font-weight: bold;"
                elif val == "FAIL":
                    return "background-color: #f8d7da; color: #721c24; font-weight: bold;"
                return ""
                
            # Use map instead of applymap (deprecated in newer Pandas)
            styled_df = df.style.map(color_status, subset=['Status'])
                
            # Display table
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.info("No validation results")
    
else:
    st.info("👈 Enter design specification and click Validate")


        

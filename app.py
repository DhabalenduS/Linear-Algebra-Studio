import streamlit as st
import importlib
import traceback

# --- Page Configuration (Must be the first Streamlit command) ---
st.set_page_config(
    page_title="Linear Algebra Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Safe Module Import Helper ---
def load_module(module_name):
    try:
        return importlib.import_module(module_name)
    except Exception as e:
        st.error(f"⚠️ Error loading module `{module_name}`:")
        st.code(traceback.format_exc(), language="python")
        return None

# Dynamically import Unit1_systems module safely
Unit1_systems = load_module("modules.Unit1_systems")

# --- Custom Styling ---
st.markdown("""
    <style>
    .centered-header {
        text-align: center;
        font-size: 3.5rem !important;
        font-weight: 800;
        color: #1E3A8A;
        margin-top: 10px;
        margin-bottom: 0px;
    }
    .centered-subheader {
        text-align: center;
        color: #4B5563;
        font-size: 1.25rem;
        margin-bottom: 5px;
    }
    .author-by {
        text-align: center;
        color: #6B7280;
        font-size: 1rem;
        margin-bottom: 0px;
    }
    .author-name {
        text-align: center;
        color: #1E3A8A;
        font-size: 1.75rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .author-credentials {
        text-align: center;
        color: #4B5563;
        font-size: 0.9rem;
        font-weight: 500;
        margin-bottom: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Query Parameters & Session State Sync ---
query_params = st.query_params

if "unit" in query_params:
    unit_val = str(query_params["unit"])
    mapping = {
        "1": "Unit-I", "2": "Unit-II", "3": "Unit-III",
        "4": "Unit-IV", "5": "Unit-V", "6": "Unit-VI"
    }
    if unit_val in mapping:
        st.session_state.active_unit = mapping[unit_val]
elif "active_unit" not in st.session_state:
    st.session_state.active_unit = "Home"

# --- GLOBAL HEADER (Always visible across all views & deep links) ---
st.markdown('<p class="centered-header">Linear Algebra Studio</p>', unsafe_allow_html=True)
st.markdown('<p class="centered-subheader">Interactive workspace for UG/PG Students</p>', unsafe_allow_html=True)
st.markdown('<p class="author-by">by</p>', unsafe_allow_html=True)
st.markdown('<p class="author-name">Dr. Dhabalendu Samanta</p>', unsafe_allow_html=True)
st.markdown('<p class="author-credentials">PhD(Math), IIT Delhi, India | 10 Years Experience @ STMicroelectronics Pvt Ltd | 5 Patents (USPTO) | 16 Years Teaching Exp. | Multiple Single Author SCIE Q2 Pure Math Publications</p>', unsafe_allow_html=True)

# --- Navigation Check ---
if st.session_state.active_unit != "Home":
    if st.button("⬅️ Back to Course Units Dashboard", type="secondary"):
        st.session_state.active_unit = "Home"
        st.query_params.clear()
        st.rerun()
    st.divider()

# --- Unit Hub Dashboard ---
if st.session_state.active_unit == "Home":
    st.markdown("### 📚 Course Units Dashboard")
    st.write("Select a unit below to enter its interactive workspace:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📦 **Unit-I**\n\nSystems of Linear Equations & Matrices", use_container_width=True, key="u1"):
            st.session_state.active_unit = "Unit-I"
            st.query_params["unit"] = "1"
            st.query_params["tab"] = "0"
            st.rerun()
        if st.button("📦 **Unit-IV**\n\nInner Product Spaces & Orthogonality", use_container_width=True, key="u4"):
            st.session_state.active_unit = "Unit-IV"
            st.query_params["unit"] = "4"
            st.rerun()

    with col2:
        if st.button("📦 **Unit-II**\n\nVector Spaces & Subspaces", use_container_width=True, key="u2"):
            st.session_state.active_unit = "Unit-II"
            st.query_params["unit"] = "2"
            st.rerun()
        if st.button("📦 **Unit-V**\n\nEigenvalues & Eigenvectors", use_container_width=True, key="u5"):
            st.session_state.active_unit = "Unit-V"
            st.query_params["unit"] = "5"
            st.rerun()

    with col3:
        if st.button("📦 **Unit-III**\n\nLinear Transformations", use_container_width=True, key="u3"):
            st.session_state.active_unit = "Unit-III"
            st.query_params["unit"] = "3"
            st.rerun()
        if st.button("📦 **Unit-VI**\n\nReal-World Applications", use_container_width=True, key="u6"):
            st.session_state.active_unit = "Unit-VI"
            st.query_params["unit"] = "6"
            st.rerun()

# --- RENDER ACTIVE MODULE CONTENT ---
elif st.session_state.active_unit == "Unit-I":
    if Unit1_systems and hasattr(Unit1_systems, "render"):
        Unit1_systems.render()
    else:
        st.error("The `Unit1_systems` module could not be loaded or lacks a `render()` function. Please inspect `modules/Unit1_systems.py`.")

elif st.session_state.active_unit == "Unit-II":
    st.header("Unit-II: Vector Spaces")
    st.info("Sub-modules for Subspaces, Linear Independence, and Basis/Dimension are under development.")

elif st.session_state.active_unit == "Unit-III":
    st.header("Unit-III: Linear Transformations")
    st.info("Sub-modules for Range, Kernel, and Matrix Representations are under development.")

elif st.session_state.active_unit == "Unit-IV":
    st.header("Unit-IV: Inner Product Spaces")
    st.info("Sub-modules for Gram-Schmidt Orthogonalization and Projections are under development.")

elif st.session_state.active_unit == "Unit-V":
    st.header("Unit-V: Eigenvalues & Eigenvectors")
    st.info("Sub-modules for Characteristic Equations and Diagonalization are under development.")

elif st.session_state.active_unit == "Unit-VI":
    st.header("Unit-VI: Applications")
    st.info("Sub-modules for SVD, PCA, and Differential Equations are under development.")

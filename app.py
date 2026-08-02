import streamlit as st
from modules import Unit1_systems

# --- Page Configuration (No icon passed) ---
st.set_page_config(
    page_title="Linear Algebra Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        margin-bottom: 40px;
    }
    .unit-card {
        border: 2px solid #E5E7EB;
        border-radius: 12px;
        padding: 30px 20px;
        text-align: center;
        background-color: #F9FAFB;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        margin-bottom: 20px;
        cursor: pointer;
    }
    .unit-card:hover {
        border-color: #3B82F6;
        background-color: #F0Fdf4;
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.15);
    }
    .unit-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 8px;
    }
    .unit-desc {
        font-size: 0.95rem;
        color: #6B7280;
    }
    </style>
""", unsafe_allow_html=True)

# --- Session State Management ---
if 'active_unit' not in st.session_state:
    st.session_state.active_unit = "Home"

# --- Header Section ---
st.markdown('<p class="centered-header">Linear Algebra Studio</p>', unsafe_allow_html=True)
st.markdown('<p class="centered-subheader">Interactive workspace for UG/PG Students</p>', unsafe_allow_html=True)

# --- Navigation Check ---
if st.session_state.active_unit != "Home":
    if st.button("⬅️ Back to Course Units Dashboard", type="secondary"):
        st.session_state.active_unit = "Home"
        st.rerun()
    st.divider()

# --- Unit Hub Dashboard ---
if st.session_state.active_unit == "Home":
    st.markdown("### 📚 Course Units Dashboard")
    st.write("Click on any unit box below to enter its interactive workspace:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("### Unit-I\nSystems of Linear Equations & Matrices", use_container_width=True, key="btn_u1"):
            st.session_state.active_unit = "Unit-I"
            st.rerun()
            
        if st.button("### Unit-IV\nInner Product Spaces & Orthogonality", use_container_width=True, key="btn_u4"):
            st.session_state.active_unit = "Unit-IV"
            st.rerun()

    with col2:
        if st.button("### Unit-II\nVector Spaces & Subspaces", use_container_width=True, key="btn_u2"):
            st.session_state.active_unit = "Unit-II"
            st.rerun()
            
        if st.button("### Unit-V\nEigenvalues & Eigenvectors", use_container_width=True, key="btn_u5"):
            st.session_state.active_unit = "Unit-V"
            st.rerun()

    with col3:
        if st.button("### Unit-III\nLinear Transformations", use_container_width=True, key="btn_u3"):
            st.session_state.active_unit = "Unit-III"
            st.rerun()
            
        if st.button("### Unit-VI\nReal-World Applications", use_container_width=True, key="btn_u6"):
            st.session_state.active_unit = "Unit-VI"
            st.rerun()

# --- RENDER ACTIVE MODULE CONTENT ---
elif st.session_state.active_unit == "Unit-I":
    Unit1_systems.render()

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

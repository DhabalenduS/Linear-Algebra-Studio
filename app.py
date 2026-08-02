import streamlit as st
from modules import Unit1_systems

# --- Page Configuration ---
st.set_page_config(
    page_title="Linear Algebra Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling for Center Alignment & Unit Cards ---
st.markdown("""
    <style>
    /* Remove default anchor link icons */
    .st-emotion-cache-16idsys p { font-size: 1.1rem; }
    
    .centered-header {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0px;
    }
    .centered-subheader {
        text-align: center;
        color: #4B5563;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
    .unit-card {
        border: 2px solid #E5E7EB;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        background-color: #F9FAFB;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        margin-bottom: 20px;
    }
    .unit-card:hover {
        border-color: #3B82F6;
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.15);
    }
    </style>
""", unsafe_allow_html=True)

# --- Session State Management for Navigation ---
if 'active_unit' not in st.session_state:
    st.session_state.active_unit = "Home"

# --- Header Section (Centered) ---
st.markdown('<p class="centered-header">📐 Linear Algebra Studio</p>', unsafe_allow_html=True)
st.markdown('<p class="centered-subheader">Interactive undergraduate workspace mapped directly to course curriculum.</p>', unsafe_allow_html=True)

# --- Navigation Check ---
if st.session_state.active_unit != "Home":
    if st.button("⬅️ Back to All Units Dashboard", type="secondary"):
        st.session_state.active_unit = "Home"
        st.rerun()
    st.divider()

# --- Unit Hub or Workspace Selection ---
if st.session_state.active_unit == "Home":
    st.markdown("### 📚 Course Units Dashboard")
    st.write("Select a unit below to enter its interactive workspace:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="unit-card"><h4>Unit-I</h4><p>Systems of Linear Equations & Matrices</p></div>', unsafe_allow_html=True)
        if st.button("Open Unit-I", use_container_width=True, key="btn_u1"):
            st.session_state.active_unit = "Unit-I"
            st.rerun()
            
        st.markdown('<div class="unit-card" style="margin-top:20px;"><h4>Unit-IV</h4><p>Inner Product Spaces & Orthogonality</p></div>', unsafe_allow_html=True)
        if st.button("Open Unit-IV", use_container_width=True, key="btn_u4"):
            st.session_state.active_unit = "Unit-IV"
            st.rerun()

    with col2:
        st.markdown('<div class="unit-card"><h4>Unit-II</h4><p>Vector Spaces & Subspaces</p></div>', unsafe_allow_html=True)
        if st.button("Open Unit-II", use_container_width=True, key="btn_u2"):
            st.session_state.active_unit = "Unit-II"
            st.rerun()
            
        st.markdown('<div class="unit-card" style="margin-top:20px;"><h4>Unit-V</h4><p>Eigenvalues & Eigenvectors</p></div>', unsafe_allow_html=True)
        if st.button("Open Unit-V", use_container_width=True, key="btn_u5"):
            st.session_state.active_unit = "Unit-V"
            st.rerun()

    with col3:
        st.markdown('<div class="unit-card"><h4>Unit-III</h4><p>Linear Transformations</p></div>', unsafe_allow_html=True)
        if st.button("Open Unit-III", use_container_width=True, key="btn_u3"):
            st.session_state.active_unit = "Unit-III"
            st.rerun()
            
        st.markdown('<div class="unit-card" style="margin-top:20px;"><h4>Unit-VI</h4><p>Real-World Applications</p></div>', unsafe_allow_html=True)
        if st.button("Open Unit-VI", use_container_width=True, key="btn_u6"):
            st.session_state.active_unit = "Unit-VI"
            st.rerun()

# --- RENDER ACTIVE MODULE CONTENT ---
elif st.session_state.active_unit == "Unit-I":
    Unit1_systems.render()

elif st.session_state.active_unit == "Unit-II":
    st.header("Unit-II: Vector Spaces")
    st.info("Sub-modules for Subspaces, Linear Independence, and Basis/Dimension are coming up next.")

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

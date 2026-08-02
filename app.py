import streamlit as st
from modules import Unit1_systems

# --- Page Configuration ---
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
        font-size: 1.75rem; /* Increased size for greater prominence */
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

# --- Session State Management ---
if 'active_unit' not in st.session_state:
    st.session_state.active_unit = "Home"

# --- Header Section ---
st.markdown('<p class="centered-header">Linear Algebra Studio</p>', unsafe_allow_html=True)
st.markdown('<p class="centered-subheader">Interactive workspace for UG/PG Students</p>', unsafe_allow_html=True)
st.markdown('<p class="author-by">by</p>', unsafe_allow_html=True)
st.markdown('<p class="author-name">Dr. Dhabalendu Samanta</p>', unsafe_allow_html=True)
st.markdown('<p class="author-credentials">PhD(Math), IIT Delhi, India | 10 Years Experience @ STMicroelectronics Pvt Ltd | 5 Patents (USPTO) | 16 Years Teaching Exp. | Multiple Single Author SCIE Q2 Pure Math Publications</p>', unsafe_allow_html=True)

# --- Navigation Check ---
if st.session_state.active_unit != "Home":
    if st.button("⬅️ Back to Course Units Dashboard", type="secondary"):
        st.session_state.active_unit = "Home"
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
            st.rerun()
        if st.button("📦 **Unit-IV**\n\nInner Product Spaces & Orthogonality", use_container_width=True, key="u4"):
            st.session_state.active_unit = "Unit-IV"
            st.rerun()

    with col2:
        if st.button("📦 **Unit-II**\n\nVector Spaces & Subspaces", use_container_width=True, key="u2"):
            st.session_state.active_unit = "Unit-II"
            st.rerun()
        if st.button("📦 **Unit-V**\n\nEigenvalues & Eigenvectors", use_container_width=True, key="u5"):
            st.session_state.active_unit = "Unit-V"
            st.rerun()

    with col3:
        if st.button("📦 **Unit-III**\n\nLinear Transformations", use_container_width=True, key="u3"):
            st.session_state.active_unit = "Unit-III"
            st.rerun()
        if st.button("📦 **Unit-VI**\n\nReal-World Applications", use_container_width=True, key="u6"):
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

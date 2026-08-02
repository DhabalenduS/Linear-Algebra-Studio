import streamlit as st
from modules import Unit1_systems

# --- Page Configuration ---
st.set_page_config(
    page_title="Linear Algebra Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Executive Styling ---
st.markdown("""
    <style>
    .main-title {
        font-size: 2.8rem !important;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0rem;
    }
    .sub-text {
        color: #4B5563;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- Main Application Header ---
st.markdown('<p class="main-title">📐 Linear Algebra Studio</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Interactive workspace for undergraduate linear algebra, mapped directly to course curriculum.</p>', unsafe_allow_html=True)

# --- MAIN 6-UNIT TABS ---
main_tabs = st.tabs([
    "Unit-I: Systems of Linear Equations",
    "Unit-II: Vector Spaces",
    "Unit-III: Linear Transformations",
    "Unit-IV: Inner Product Spaces",
    "Unit-V: Eigenvalues & Eigenvectors",
    "Unit-VI: Applications"
])

# --- UNIT-I WORKSPACE ---
with main_tabs[0]:
    Unit1_systems.render()

# --- UNIT-II WORKSPACE ---
with main_tabs[1]:
    st.header("Unit-II: Vector Spaces")
    st.info("Sub-tabs for Subspaces, Linear Independence, and Basis/Dimension under development.")

# --- UNIT-III WORKSPACE ---
with main_tabs[2]:
    st.header("Unit-III: Linear Transformations")
    st.info("Sub-tabs for Range, Kernel, and Matrix Representations under development.")

# --- UNIT-IV WORKSPACE ---
with main_tabs[3]:
    st.header("Unit-IV: Inner Product Spaces")
    st.info("Sub-tabs for Gram-Schmidt Orthogonalization and Projections under development.")

# --- UNIT-V WORKSPACE ---
with main_tabs[4]:
    st.header("Unit-V: Eigenvalues & Eigenvectors")
    st.info("Sub-tabs for Characteristic Equations and Diagonalization under development.")

# --- UNIT-VI WORKSPACE ---
with main_tabs[5]:
    st.header("Unit-VI: Applications")
    st.info("Sub-tabs for SVD, PCA, and Differential Equations under development.")

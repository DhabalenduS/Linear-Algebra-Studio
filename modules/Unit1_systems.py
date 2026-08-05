import streamlit as st
import numpy as np
import re
from fractions import Fraction
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# Optional PDF generator support
try:
    from fpdf import FPDF
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

def format_matrix_latex(mat):
    latex_rows = []
    for row in mat:
        row_elems = []
        for val in row:
            try:
                f = Fraction(val).limit_denominator()
                if f.denominator == 1:
                    row_elems.append(str(f.numerator))
                else:
                    row_elems.append(f"\\frac{{{f.numerator}}}{{{f.denominator}}}")
            except:
                row_elems.append(str(val))
        latex_rows.append(" & ".join(row_elems))
    return "\\begin{bmatrix}\n" + " \\\\\n".join(latex_rows) + "\n\\end{bmatrix}"

def format_augmented_matrix_latex(mat):
    """Formats an augmented matrix using \mid for a standard mathematical augmented vertical separator inside bmatrix."""
    latex_rows = []
    ncols = mat.shape[1]
    for row in mat:
        row_elems = []
        for idx, val in enumerate(row):
            try:
                f = Fraction(val).limit_denominator()
                if f.denominator == 1:
                    val_str = str(f.numerator)
                else:
                    val_str = f"\\frac{{{f.numerator}}}{{{f.denominator}}}"
            except:
                val_str = str(val)
            
            if idx == ncols - 2:
                row_elems.append(f"{val_str} \\mid")
            else:
                row_elems.append(val_str)
        latex_rows.append(" & ".join(row_elems))
    
    return "\\begin{bmatrix}\n" + " \\\\\n".join(latex_rows) + "\n\\end{bmatrix}"

def perform_row_operation(A, op_str):
    op_str = op_str.replace(" ", "")
    swap_match = re.match(r"R(\d+)<->R(\d+)", op_str)
    if swap_match:
        r1 = int(swap_match.group(1)) - 1
        r2 = int(swap_match.group(2)) - 1
        if not (0 <= r1 < len(A) and 0 <= r2 < len(A)):
            raise ValueError(f"Row index out of range. Matrix has {len(A)} rows.")
        new_A = A.copy()
        new_A[[r1, r2]] = new_A[[r2, r1]]
        return new_A

    match = re.match(r"R(\d+)->(.*)", op_str)
    if not match:
        raise ValueError("Invalid format. Use 'R1 <-> R2' for swaps or 'R2 -> R2 - 3*R1' for replacement.")

    target_idx = int(match.group(1)) - 1
    expr = match.group(2)

    if not (0 <= target_idx < len(A)):
        raise ValueError(f"Target row index out of range. Matrix has {len(A)} rows.")

    new_A = A.copy()
    def replace_row(m):
        r_num = int(m.group(1)) - 1
        return f"A[{r_num}]"

    python_expr = re.sub(r"R(\d+)", replace_row, expr)
    try:
        new_A[target_idx] = eval(python_expr, {"A": A, "np": np, "Fraction": Fraction})
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {e}.")
    return new_A

def matrix_to_pretty_string(mat):
    rows_str = []
    for row in mat:
        row_vals = []
        for val in row:
            try:
                f = Fraction(val).limit_denominator()
                row_vals.append(str(f) if f.denominator == 1 else f"{f.numerator}/{f.denominator}")
            except:
                row_vals.append(str(val))
        rows_str.append("[ " + "  ".join(row_vals) + " ]")
    return "\n".join(rows_str)

def render():
    st.markdown("""
        <style>
        div.stButton > button {
            width: auto !important;
            display: inline-block !important;
            flex: unset !important;
            padding: 0.35rem 1rem !important;
            font-size: 0.9rem !important;
            border-radius: 4px;
        }
        div.stTextInput input {
            max-width: 160px !important;
        }
        div.stNumberInput {
            max-width: 180px !important;
        }
        div.stSelectbox {
            max-width: 250px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("### Unit-I: Systems of Linear Equations & Matrices")
    
    tab_names = [
        "Row Operations", 
        "System of Linear Equations", 
        "LU Decomposition (Lecture 5)",
        "Inverse of a Matrix"
    ]
    
    try:
        query_tab = int(st.query_params.get("tab", 0))
    except ValueError:
        query_tab = 0
        
    if not (0 <= query_tab < len(tab_names)):
        query_tab = 0

    dynamic_key = f"u1_sub_tabs_key_{query_tab}"

    selected_tab = st.radio(
        "Select Sub-Topic", 
        tab_names, 
        index=query_tab, 
        horizontal=True, 
        label_visibility="collapsed",
        key=dynamic_key
    )
    
    current_tab_idx = tab_names.index(selected_tab)
    if query_tab != current_tab_idx:
        st.query_params["unit"] = "1"
        st.query_params["tab"] = str(current_tab_idx)
        st.rerun()
    
    st.divider()
    
    # --- TAB 0: ROW OPERATIONS ---
    if selected_tab == "Row Operations":
        st.markdown("#### Interactive Matrix Row Operations & RREF Practice")
        st.markdown("Practice elementary row transformations, echelon forms, and matrix reduction.")

        if "matrix_history" not in st.session_state:
            st.session_state.matrix_history = []
        if "current_matrix" not in st.session_state:
            st.session_state.current_matrix = None
        if "original_matrix" not in st.session_state:
            st.session_state.original_matrix = None

        col_set1, col_set2 = st.columns([1, 1])
        with col_set1:
            rows = st.number_input("Rows", min_value=1, max_value=20, value=3, step=1, key="u1_rows")
        with col_set2:
            cols = st.number_input("Columns", min_value=1, max_value=20, value=4, step=1, key="u1_cols")
            
        if st.button("Reset Workspace", key="u1_reset"):
            st.session_state.matrix_history = []
            st.session_state.current_matrix = None
            st.session_state.original_matrix = None
            st.rerun()

        if st.session_state.original_matrix is None:
            st.markdown("##### Step 1: Define Matrix Entries (by space separated entries)")

            entered_rows = []
            valid_input = True
            input_warnings = []
            has_empty_inputs = False

            example_placeholder = "e.g. " + " ".join(str(j) for j in range(1, cols + 1))

            temp_inputs = []
            for i in range(rows):
                c_lbl, c_inp, c_space = st.columns([0.06, 0.3, 0.64])
                with c_lbl:
                    st.markdown(f"**R{i+1}**")
                with c_inp:
                    row_input = st.text_input(
                        f"Row {i+1} entries", 
                        value="", 
                        placeholder=example_placeholder, 
                        key=f"row_{i}", 
                        label_visibility="collapsed"
                    )
                temp_inputs.append(row_input)

            for i, row_input in enumerate(temp_inputs):
                stripped = row_input.strip()
                if not stripped:
                    has_empty_inputs = True
                    valid_input = False
                    continue
                try:
                    row_vals = [Fraction(x) for x in stripped.split()]
                    if len(row_vals) > cols:
                        valid_input = False
                        input_warnings.append(f"Row {i+1} has {len(row_vals)} elements, but only {cols} columns are allowed.")
                    elif len(row_vals) < cols:
                        valid_input = False
                        input_warnings.append(f"Row {i+1} has {len(row_vals)} elements, but {cols} columns are required.")
                    entered_rows.append(row_vals)
                except Exception:
                    valid_input = False
                    input_warnings.append(f"Row {i+1} contains invalid numeric entries or formatting.")

            if not has_empty_inputs and input_warnings:
                st.markdown("")
                for warn in input_warnings:
                    st.warning(f"⚠️ {warn}")

            st.markdown("")
            init_btn = st.button("Initialize Matrix & Start Practice", type="primary", key="u1_init")
            
            if init_btn:
                if has_empty_inputs:
                    st.error("Please fill in all row entries before initializing.")
                elif valid_input:
                    mat = np.array(entered_rows, dtype=object)
                    st.session_state.original_matrix = mat.copy()
                    st.session_state.current_matrix = mat.copy()
                    st.session_state.matrix_history = []
                    st.rerun()
                else:
                    st.error("Please resolve the column size discrepancies highlighted above.")
        else:
            st.markdown("---")
            m_col1, m_col2 = st.columns(2)
            with m_col1:
                st.markdown("##### 📌 Initial Given Matrix")
                st.latex(format_matrix_latex(st.session_state.original_matrix))
            with m_col2:
                st.markdown("##### 🔄 Current Matrix State")
                st.latex(format_matrix_latex(st.session_state.current_matrix))
            st.markdown("---")

            col_left, col_right = st.columns([1.2, 1])
            with col_left:
                st.markdown("##### 🛠️ Apply Row Operation")
                st.markdown("*Syntax:* `R1 <-> R2` | `R1 -> 3*R1` | `R2 -> R2 - 2*R1`")
                op_input = st.text_input("Enter Operation", placeholder="e.g., R2 -> R2 - 2*R1", key="u1_op_input")
                
                c1, c2 = st.columns(2)
                with c1:
                    apply_btn = st.button("Execute Operation", type="primary", key="u1_exec")
                with c2:
                    undo_btn = st.button("Undo Last Step", key="u1_undo")
                    
                if apply_btn and op_input:
                    try:
                        updated = perform_row_operation(st.session_state.current_matrix, op_input)
                        st.session_state.matrix_history.append({"operation": op_input, "matrix": updated.copy()})
                        st.session_state.current_matrix = updated
                        st.success(f"Successfully applied: {op_input}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                        
                if undo_btn:
                    if st.session_state.matrix_history:
                        st.session_state.matrix_history.pop()
                        if st.session_state.matrix_history:
                            st.session_state.current_matrix = st.session_state.matrix_history[-1]["matrix"].copy()
                        else:
                            st.session_state.current_matrix = st.session_state.original_matrix.copy()
                        st.info("Reverted last operation.")
                        st.rerun()
                    else:
                        st.warning("No operations to undo.")

            with col_right:
                if st.session_state.matrix_history:
                    st.markdown("##### 📥 Export History")
                    
                    history_text = f"Initial Matrix:\n{matrix_to_pretty_string(st.session_state.original_matrix)}\n\n"
                    for idx, item in enumerate(st.session_state.matrix_history):
                        history_text += f"Step {idx+1}: {item['operation']}\n{matrix_to_pretty_string(item['matrix'])}\n\n"
                    history_text += f"Final Current Matrix:\n{matrix_to_pretty_string(st.session_state.current_matrix)}"
                    
                    st.download_button(
                        label="📄 Download Text (.txt)",
                        data=history_text,
                        file_name="matrix_practice_history.txt",
                        mime="text/plain",
                        key="download_history_txt"
                    )

                    if PDF_AVAILABLE:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Courier", size=11)
                        pdf.cell(200, 10, txt="Matrix Row Operations - Practice History", ln=True, align='C')
                        pdf.ln(10)
                        
                        for line in history_text.split('\n'):
                            pdf.cell(200, 6, txt=line, ln=True)
                            
                        pdf_bytes = bytes(pdf.output())
                        st.download_button(
                            label="📥 Download PDF (.pdf)",
                            data=pdf_bytes,
                            file_name="matrix_practice_history.pdf",
                            mime="application/pdf",
                            key="download_history_pdf"
                        )

            if st.session_state.matrix_history:
                st.markdown("---")
                st.markdown("##### 📚 Step-by-Step Practice History")
                for idx, item in enumerate(st.session_state.matrix_history):
                    with st.expander(f"Step {idx+1}: {item['operation']}"):
                        st.latex(format_matrix_latex(item['matrix']))

    # --- TAB 1: SYSTEM OF LINEAR EQUATIONS ---
    elif selected_tab == "System of Linear Equations":
        st.markdown("#### System of Linear Equations Solver")
        st.markdown("Solve $AX = B$ using Gauss Elimination or check system consistency and rank.")
        
        method_choice = st.selectbox(
            "Select Solution Technique", 
            ["Gauss Elimination", "Rank & System Consistency"]
        )
        
        n_vars = st.number_input("Number of equations", min_value=1, max_value=20, value=3, step=1, key="sys_n")
        
        st.markdown("##### Enter Coefficient Matrix A (space separated)")
        
        example_placeholder = "e.g. " + " ".join(str(j+1) for j in range(n_vars))
        A_rows = []
        for i in range(n_vars):
            c_lbl, c_inp, c_space = st.columns([0.06, 0.3, 0.64])
            with c_lbl:
                st.markdown(f"**R{i+1}**")
            with c_inp:
                r_val = st.text_input(
                    f"R{i+1}", 
                    value="", 
                    placeholder=example_placeholder, 
                    key=f"gauss_a_{i}", 
                    label_visibility="collapsed"
                )
            row_content = r_val.strip() if r_val.strip() else " ".join(str(j+1) for j in range(n_vars))
            A_rows.append([float(x) for x in row_content.split()])
            
        st.markdown("##### Constant vector B (space separated)")
        c_lbl_b, c_inp_b, c_space_b = st.columns([0.06, 0.3, 0.64])
        with c_lbl_b:
            st.markdown("**B**")
        with c_inp_b:
            b_val = st.text_input("Constant vector B", value="", placeholder="e.g. " + " ".join([str(j+1) for j in range(n_vars)]), key="gauss_b", label_visibility="collapsed")
        b_content = b_val.strip() if b_val.strip() else " ".join([str(j+1) for j in range(n_vars)])
        b_vec = [float(x) for x in b_content.split()]
        
        if method_choice == "Gauss Elimination":
            gauss_mode = st.selectbox(
                "Select Gauss Solver Mode",
                ["(i) Automated Gauss Solver", "(ii) Manual Gauss Solver"]
            )
            
            if gauss_mode == "(i) Automated Gauss Solver":
                if st.button("Run Automated Gauss Solver", type="primary", key="run_gauss"):
                    A_mat = np.array(A_rows, dtype=float)
                    b_col = np.array(b_vec, dtype=float)
                    aug = np.column_stack((A_mat, b_col))
                    
                    st.markdown("##### Automated Execution Steps")
                    
                    st.markdown("Step 0 Augmented matrix:")
                    st.latex(f"[A|B] = {format_augmented_matrix_latex(aug)}")
                    
                    curr = aug.copy()
                    step_count = 1
                    
                    for i in range(n_vars):
                        if curr[i, i] == 0:
                            for r in range(i+1, n_vars):
                                if curr[r, i] != 0:
                                    op_desc = f"R_{{ {i+1} }} \\leftrightarrow R_{{ {r+1} }}"
                                    curr[[i, r]] = curr[[r, i]]
                                    st.markdown(f"Step {step_count} Applying ${op_desc}$")
                                    st.latex(f"\\sim {format_augmented_matrix_latex(curr)}")
                                    step_count += 1
                                    break
                        for j in range(i+1, n_vars):
                            if curr[i, i] != 0 and curr[j, i] != 0:
                                factor = curr[j, i] / curr[i, i]
                                f_frac = Fraction(factor).limit_denominator()
                                if f_frac.denominator == 1:
                                    f_str = str(f_frac.numerator)
                                else:
                                    f_str = f"\\frac{{{f_frac.numerator}}}{{{f_frac.denominator}}}"
                                
                                op_desc = f"R_{{ {j+1} }} \\rightarrow R_{{ {j+1} }} - {f_str}R_{{ {i+1} }}"
                                curr[j] = curr[j] - factor * curr[i]
                                st.markdown(f"Step {step_count} Applying ${op_desc}$")
                                st.latex(f"\\sim {format_augmented_matrix_latex(curr)}")
                                step_count += 1
                    
                    st.markdown("---")
                    st.markdown("##### Back-Substitution Steps")
                    
                    rank_A = np.linalg.matrix_rank(curr[:, :-1])
                    rank_aug = np.linalg.matrix_rank(curr)
                    num_rows, num_cols = curr.shape
                    num_vars_local = num_cols - 1
                    
                    if rank_A < rank_aug:
                        st.error("The system is inconsistent (No solution exists).")
                    elif rank_A < num_vars_local:
                        st.warning("The system has infinitely many solutions.")
                    else:
                        x = np.zeros(n_vars)
                        for i in range(n_vars - 1, -1, -1):
                            sub_sum = 0
                            sub_terms = []
                            for k in range(i + 1, n_vars):
                                val_k = curr[i, k]
                                if not np.isclose(val_k, 0):
                                    sub_sum += val_k * x[k]
                                    f_sub = Fraction(val_k).limit_denominator()
                                    f_sub_str = str(f_sub) if f_sub.denominator == 1 else f"\\frac{{{f_sub.numerator}}}{{{f_sub.denominator}}}"
                                    sub_terms.append(f"{f_sub_str} x_{{ {k+1} }}")
                            
                            rhs_val = curr[i, -1]
                            diag_val = curr[i, i]
                            numer = rhs_val - sub_sum
                            x[i] = numer / diag_val
                            
                            f_diag = Fraction(diag_val).limit_denominator()
                            f_rhs = Fraction(rhs_val).limit_denominator()
                            f_diag_str = str(f_diag) if f_diag.denominator == 1 else f"\\frac{{{f_diag.numerator}}}{{{f_diag.denominator}}}"
                            f_rhs_str = str(f_rhs) if f_rhs.denominator == 1 else f"\\frac{{{f_rhs.numerator}}}{{{f_rhs.denominator}}}"
                            
                            step_eq = f"x_{{ {i+1} }} = \\frac{{{f_rhs_str}"
                            if sub_terms:
                                step_eq += " - " + " - ".join(sub_terms)
                            step_eq += f"}} {{{f_diag_str}}} = {x[i]:.4g}"
                            st.latex(step_eq)
                            
                        st.success(f"Final Solution Vector X: {x}")
            else:
                st.markdown("##### Manual Gauss Elimination Workspace")
                if "manual_gauss_history" not in st.session_state:
                    st.session_state.manual_gauss_history = []
                if "manual_gauss_orig" not in st.session_state:
                    st.session_state.manual_gauss_orig = None
                if "manual_gauss_curr" not in st.session_state:
                    st.session_state.manual_gauss_curr = None

                c_init1, c_init2 = st.columns(2)
                with c_init1:
                    if st.button("Load Augmented Matrix Into Manual Workspace", type="primary", key="load_manual_aug"):
                        A_mat = np.array(A_rows, dtype=float)
                        b_col = np.array(b_vec, dtype=float)
                        aug = np.column_stack((A_mat, b_col))
                        st.session_state.manual_gauss_orig = aug.copy()
                        st.session_state.manual_gauss_curr = aug.copy()
                        st.session_state.manual_gauss_history = []
                        st.rerun()
                with c_init2:
                    if st.button("Reset Manual Workspace", key="reset_manual_aug"):
                        st.session_state.manual_gauss_orig = None
                        st.session_state.manual_gauss_curr = None
                        st.session_state.manual_gauss_history = []
                        st.rerun()

                if st.session_state.manual_gauss_curr is not None:
                    st.markdown("---")
                    mg_col1, mg_col2 = st.columns(2)
                    with mg_col1:
                        st.markdown("##### 📌 Initial Augmented Matrix $[A | B]$")
                        st.latex(format_augmented_matrix_latex(st.session_state.manual_gauss_orig))
                    with mg_col2:
                        st.markdown("##### 🔄 Current Augmented Matrix State")
                        st.latex(format_augmented_matrix_latex(st.session_state.manual_gauss_curr))
                    st.markdown("---")

                    m_op_input = st.text_input("Enter Row Operation", placeholder="e.g., R2 -> R2 - 2*R1", key="manual_op_input")
                    mc1, mc2 = st.columns(2)
                    with mc1:
                        m_apply_btn = st.button("Execute Step", type="primary", key="manual_exec")
                    with mc2:
                        m_undo_btn = st.button("Undo Last Step", key="manual_undo")
                        
                    if m_apply_btn and m_op_input:
                        try:
                            updated = perform_row_operation(st.session_state.manual_gauss_curr, m_op_input)
                            st.session_state.manual_gauss_history.append({"operation": m_op_input, "matrix": updated.copy()})
                            st.session_state.manual_gauss_curr = updated
                            st.success(f"Successfully applied: {m_op_input}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                            
                    if m_undo_btn:
                        if st.session_state.manual_gauss_history:
                            st.session_state.manual_gauss_history.pop()
                            if st.session_state.manual_gauss_history:
                                st.session_state.manual_gauss_curr = st.session_state.manual_gauss_history[-1]["matrix"].copy()
                            else:
                                st.session_state.manual_gauss_curr = st.session_state.manual_gauss_orig.copy()
                            st.info("Reverted last operation.")
                            st.rerun()
                        else:
                            st.warning("No operations to undo.")
        else:
            if st.button("Check Rank & Consistency", type="primary", key="calc_rank_sys"):
                try:
                    mat_a = np.array(A_rows, dtype=float)
                    vec_b = np.array(b_vec, dtype=float)
                    aug_mat = np.column_stack((mat_a, vec_b))
                    
                    r_a = np.linalg.matrix_rank(mat_a)
                    r_aug = np.linalg.matrix_rank(aug_mat)
                    
                    st.markdown(f"* Rank of Coefficient Matrix A: **{r_a}**")
                    st.markdown(f"* Rank of Augmented Matrix [A|B]: **{r_aug}**")
                    
                    if r_a != r_aug:
                        st.error("The system is **Inconsistent** (No solutions).")
                    elif r_a == r_aug and r_a == n_vars:
                        st.success("The system is **Consistent** with a **Unique Solution**.")
                    else:
                        st.warning("The system is **Consistent** with **Infinitely Many Solutions**.")
                except Exception as e:
                    st.error(f"Error calculating rank: {e}")

    # --- TAB 2: LU DECOMPOSITION (LECTURE 5) ---
    elif selected_tab == "LU Decomposition (Lecture 5)":
        st.markdown("#### Lecture 5: LU Decomposition (Doolittle & Crout Methods)")
        st.markdown("Factorize matrix $A = LU$ and solve non-homogeneous linear systems $AX = B$ using triangular decomposition and forward/back-substitution.")
        
        lu_method = st.selectbox(
            "Select Factorization Method",
            ["Doolittle’s Method ($l_{ii} = 1$)", "Crout’s Method ($u_{ii} = 1$)"]
        )
        
        lu_n = st.number_input("Matrix dimension (n x n)", min_value=2, max_value=5, value=3, step=1, key="lu_dim")
        
        st.markdown("##### Enter Square Matrix A")
        lu_rows_input = []
        for i in range(lu_n):
            c_lbl, c_inp, c_space = st.columns([0.06, 0.3, 0.64])
            with c_lbl:
                st.markdown(f"**R{i+1}**")
            with c_inp:
                r_val = st.text_input(
                    f"LU_R{i+1}", 
                    value="", 
                    placeholder="e.g. " + " ".join(str(j+1) for j in range(lu_n)), 
                    key=f"lu_a_{i}", 
                    label_visibility="collapsed"
                )
            row_content = r_val.strip() if r_val.strip() else " ".join(str(j+1) for j in range(lu_n))
            lu_rows_input.append([float(x) for x in row_content.split()])

        st.markdown("##### Enter Constant Vector B (for solving $AX = B$)")
        c_lbl_lub, c_inp_lub, c_space_lub = st.columns([0.06, 0.3, 0.64])
        with c_lbl_lub:
            st.markdown("**B**")
        with c_inp_lub:
            lub_val = st.text_input("Constant vector B for LU", value="", placeholder="e.g. " + " ".join([str(j+1) for j in range(lu_n)]), key="lu_b_vec", label_visibility="collapsed")
        lub_content = lub_val.strip() if lub_val.strip() else " ".join([str(j+1) for j in range(lu_n)])
        lub_vec = [float(x) for x in lub_content.split()]

        if st.button("Perform Complete LU Decomposition & Solve System", type="primary", key="run_lecture_lu"):
            try:
                A_mat = np.array(lu_rows_input, dtype=float)
                B_vec = np.array(lub_vec, dtype=float)
                n = lu_n
                
                L = np.zeros((n, n))
                U = np.zeros((n, n))
                
                is_doolittle = "Doolittle" in lu_method
                
                st.markdown("---")
                st.markdown("##### Step 1: Factorization Process ($A = LU$)")
                
                if is_doolittle:
                    st.markdown("*Using **Doolittle’s Normalization** ($l_{ii} = 1$)*")
                    for i in range(n):
                        L[i, i] = 1.0
                        for j in range(i, n):
                            s = sum(L[i, k] * U[k, j] for k in range(i))
                            U[i, j] = A_mat[i, j] - s
                        for j in range(i + 1, n):
                            s = sum(L[j, k] * U[k, i] for k in range(i))
                            L[j, i] = (A_mat[j, i] - s) / U[i, i]
                else:
                    st.markdown("*Using **Crout’s Normalization** ($u_{ii} = 1$)*")
                    for i in range(n):
                        U[i, i] = 1.0
                        for j in range(i, n):
                            s = sum(L[j, k] * U[k, i] for k in range(i))
                            L[j, i] = A_mat[j, i] - s
                        for j in range(i + 1, n):
                            s = sum(L[i, k] * U[k, j] for k in range(i))
                            U[i, j] = (A_mat[i, j] - s) / L[i, i]

                col_res_l, col_res_u = st.columns(2)
                with col_res_l:
                    st.markdown("**Lower Triangular Matrix ($L$)**")
                    st.latex(f"L = {format_matrix_latex(L)}")
                with col_res_u:
                    st.markdown("**Upper Triangular Matrix ($U$)**")
                    st.latex(f"U = {format_matrix_latex(U)}")

                st.markdown("---")
                st.markdown("##### Step 2: Forward Substitution ($LY = B$)")
                Y_vec = np.zeros(n)
                for i in range(n):
                    s = sum(L[i, k] * Y_vec[k] for k in range(i))
                    Y_vec[i] = (B_vec[i] - s) / L[i, i]
                st.latex(f"Y = \\begin{{bmatrix}} " + " \\\\ ".join([f"{val:.4g}" for val in Y_vec]) + " \\end{bmatrix}")

                st.markdown("---")
                st.markdown("##### Step 3: Back Substitution ($UX = Y$)")
                X_vec = np.zeros(n)
                for i in range(n - 1, -1, -1):
                    s = sum(U[i, k] * X_vec[k] for k in range(i + 1, n))
                    X_vec[i] = (Y_vec[i] - s) / U[i, i]
                st.latex(f"X = \\begin{{bmatrix}} " + " \\\\ ".join([f"{val:.4g}" for val in X_vec]) + " \\end{bmatrix}")
                st.success("LU Decomposition and system solution computed successfully according to Lecture 5 specs!")
            except Exception as e:
                st.error(f"Error during LU decomposition: {e}")

    # --- TAB 3: INVERSE OF A MATRIX ---
    elif selected_tab == "Inverse of a Matrix":
        st.markdown("#### Matrix Multiplication & Invertible Matrices Practice")
        st.info("Interactive workspace for testing matrix products, determinants, and finding matrix inverses ($A^{-1}$), plus elementary matrix properties.")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("##### Matrix A Input Validation")
            a_input = st.text_area("Row-by-row values for A (comma separated rows)", value="1, 2\n3, 4", key="mat_a_val")
        with col_m2:
            st.markdown("##### Matrix B Input Validation")
            b_input = st.text_area("Row-by-row values for B (comma separated rows)", value="5, 6\n7, 8", key="mat_b_val")
            
        if st.button("Compute Products & Inverses", type="primary", key="calc_mult"):
            try:
                A = np.array([[float(x) for x in r.split(",")] for r in a_input.strip().split("\n")], dtype=float)
                B = np.array([[float(x) for x in r.split(",")] for r in b_input.strip().split("\n")], dtype=float)
                
                st.markdown("##### Results:")
                col_res1, col_res2, col_res3 = st.columns(3)
                with col_res1:
                    st.markdown("**Matrix Product ($A \\times B$)**")
                    st.latex(format_matrix_latex(np.dot(A, B)))
                with col_res2:
                    st.markdown("**Inverse of A ($A^{-1}$)**")
                    if A.shape[0] == A.shape[1] and np.linalg.det(A) != 0:
                        st.latex(format_matrix_latex(np.linalg.inv(A)))
                    else:
                        st.warning("Matrix A is not square or is non-invertible (singular).")
                with col_res3:
                    st.markdown("**Inverse of B ($B^{-1}$)**")
                    if B.shape[0] == B.shape[1] and np.linalg.det(B) != 0:
                        st.latex(format_matrix_latex(np.linalg.inv(B)))
                    else:
                        st.warning("Matrix B is not square or is non-invertible (singular).")
            except Exception as e:
                st.error(f"Computation error: {e}. Check input dimensions.")

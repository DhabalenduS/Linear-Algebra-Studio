import streamlit as st
import numpy as np

def format_matrix_latex(mat):
    """Helper to format a numpy matrix into LaTeX bmatrix string."""
    if mat.ndim == 1:
        mat = mat.reshape(1, -1)
    lines = []
    for row in mat:
        formatted_row = " & ".join([f"{val:g}" for val in row])
        lines.append(formatted_row)
    return "\\begin{bmatrix} " + " \\\\ ".join(lines) + " \\end{bmatrix}"

def format_augmented_matrix_latex(mat, n_div):
    """Helper to format an augmented matrix [A | I] with a vertical divider line."""
    lines = []
    for row in mat:
        left_part = " & ".join([f"{val:g}" for val in row[:n_div]])
        right_part = " & ".join([f"{val:g}" for val in row[n_div:]])
        lines.append(f"{left_part} \\mid & {right_part}")
    return "\\begin{bmatrix} " + " \\\\ ".join(lines) + " \\end{bmatrix}"

def perform_row_operation(mat, op_str):
    """Parses and performs an elementary row operation on a copy of the matrix."""
    m = mat.copy()
    op_clean = op_str.replace(" ", "").upper()
    
    # Example: R1<->R2
    if "<->" in op_clean:
        parts = op_clean.split("<->")
        r1 = int(parts[0].replace("R", "")) - 1
        r2 = int(parts[1].replace("R", "")) - 1
        m[[r1, r2]] = m[[r2, r1]]
        return m
        
    # Example: R1->3*R1 or R2->R2-2*R1
    elif "->" in op_clean:
        lhs, rhs = op_clean.split("->")
        target_row = int(lhs.replace("R", "")) - 1
        
        # Simple scalar multiplication: R1->3*R1 or R1->-R1
        if "*" in rhs and "+" not in rhs and "-" not in rhs:
            parts = rhs.split("*")
            factor = float(parts[0]) if parts[0] != "-" else -1.0
            if parts[0] == "-":
                factor = -1.0
            src_row = int(parts[1].replace("R", "")) - 1
            m[target_row] = factor * m[src_row]
            return m
            
        # Row addition/subtraction combination: R2->R2-2*R1
        # We can safely evaluate standard algebraic row expressions
        # Let's write a robust parser for standard formats like R2-2*R1 or R2+R1
        import re
        # Evaluate using custom line combination parsing
        # For safety/simplicity in standard formats: target = target ± scalar * source
        match = re.match(r"R(\d+)([\+\-])([\d\.]*)\*?R(\d+)", rhs)
        if match:
            sign = match.group(2)
            scalar_str = match.group(3)
            scalar = float(scalar_str) if scalar_str else 1.0
            src_row = int(match.group(4)) - 1
            if sign == "+":
                m[target_row] = m[target_row] + scalar * m[src_row]
            else:
                m[target_row] = m[target_row] - scalar * m[src_row]
            return m
            
    raise ValueError("Invalid row operation format. Please check syntax examples.")

def render():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Unit 1 Navigation")
    selected_tab = st.sidebar.radio(
        "Select Section:",
        options=[
            "System of Linear Equations",
            "Inverse of a Matrix",
            "Rank & Consistency",
            "Eigenvalues & Eigenvectors"
        ],
        key="unit1_sub_navigation"
    )

    if selected_tab == "System of Linear Equations":
        st.markdown("#### System of Linear Equations Workspace")
        st.info("Explore solutions to linear systems using Gaussian Elimination and Gauss-Jordan methods.")
        # Placeholder for other tabs if needed

    # --- TAB 2: INVERSE OF A MATRIX ---
    elif selected_tab == "Inverse of a Matrix":
        st.markdown("#### Inverse of a Matrix Workspace")
        st.markdown("Find the inverse of a matrix using different methods and explore automated vs. manual practice modes.")
        
        c_ta1, c_ta2 = st.columns([1, 3])
        with c_ta1:
            st.markdown("**Enter Matrix A**\n*(Row-by-row, space separated rows)*:")
        with c_ta2:
            matrix_input_str = st.text_area(
                "Enter Matrix A (Row-by-row, space separated rows):",
                value="1 0 2\n0 1 0\n1 0 3",
                help="Example:\n1 0 2\n0 1 0\n1 0 3",
                key="inverse_matrix_input",
                label_visibility="collapsed",
                height=90
            )

        try:
            rows_input = matrix_input_str.strip().split("\n")
            matrix_data = [[float(val) for val in r.replace(',', ' ').split()] for r in rows_input if r.strip()]
            A = np.array(matrix_data, dtype=float)
        except Exception as e:
            st.error(f"Invalid matrix format: {e}")
            A = np.array([[1.0, 0.0, 2.0], [0.0, 1.0, 0.0], [1.0, 0.0, 3.0]], dtype=float)

        c_m_lbl, c_m_inp = st.columns([1, 3])
        with c_m_lbl:
            st.markdown("**Select Method:**")
        with c_m_inp:
            method_choice = st.selectbox(
                "Select Method:",
                options=["Adjoint Formula", "Gauss-Jordan Elimination"],
                key="inverse_method_dropdown",
                label_visibility="collapsed"
            )

        c_mod_lbl, c_mod_inp = st.columns([1, 3])
        with c_mod_lbl:
            st.markdown("**Select Mode:**")
        with c_mod_inp:
            mode_choice = st.selectbox(
                "Select Mode:",
                options=["Automated", "Manual"],
                help="Manual: Students perform steps on their own.\nAutomated: Solves with full step-by-step details.",
                key="inverse_mode_dropdown",
                label_visibility="collapsed"
            )

        st.markdown("---")

        if mode_choice == "Automated":
            compute_clicked = st.button("Compute Inverse", type="primary", key="inverse_compute_btn")
            if compute_clicked:
                st.subheader(f"Automated Solution via {method_choice}")
                
                if A.shape[0] != A.shape[1]:
                    st.error("Matrix must be square to find an inverse.")
                else:
                    det_A = np.linalg.det(A)
                    if np.isclose(det_A, 0):
                        st.warning("Matrix is singular (determinant is 0), so it has no inverse.")
                    else:
                        if method_choice == "Adjoint Formula":
                            st.markdown(f"**1. Determinant of A:** $\\det(A) = {det_A:.4g}$")
                            
                            n = A.shape[0]
                            if n == 2:
                                adj = np.array([[A[1, 1], -A[0, 1]], [-A[1, 0], A[0, 0]]])
                                st.markdown("**2. Adjoint Matrix:**")
                                st.latex(f"\\text{{adj}}(A) = {format_matrix_latex(adj)}")
                                inv_A = adj / det_A
                                st.markdown("**3. Inverse Matrix ($A^{-1} = \\frac{1}{\\det(A)} \\text{{adj}}(A)$):**")
                                st.latex(f"A^{{-1}} = {format_matrix_latex(inv_A)}")
                            else:
                                cofactors = np.zeros((n, n))
                                for i in range(n):
                                    for j in range(n):
                                        submat = np.delete(np.delete(A, i, axis=0), j, axis=1)
                                        cofactors[i, j] = ((-1)**(i + j)) * np.linalg.det(submat)
                                adj = cofactors.T
                                st.markdown("**2. Adjoint Matrix (Transpose of Cofactor Matrix):**")
                                st.latex(f"\\text{{adj}}(A) = {format_matrix_latex(adj)}")
                                inv_A = adj / det_A
                                st.markdown("**3. Inverse Matrix:**")
                                st.latex(f"A^{{-1}} = {format_matrix_latex(inv_A)}")
                                
                        else:  # Gauss-Jordan Elimination
                            st.markdown("Using Gauss-Jordan Elimination on $[A \\mid I]$ to reduce to $[I \\mid A^{-1}]$:")
                            n = A.shape[0]
                            identity = np.eye(n)
                            augmented = np.column_stack((A, identity))
                            
                            st.latex(f"\\text{{Initial Augmented Matrix: }} [A \\mid I] = {format_augmented_matrix_latex(augmented, n_div=n)}")
                            
                            curr_aug = augmented.copy()
                            step_num = 1
                            
                            for i in range(n):
                                pivot = curr_aug[i, i]
                                if np.isclose(pivot, 0):
                                    for r in range(i+1, n):
                                        if not np.isclose(curr_aug[r, i], 0):
                                            curr_aug[[i, r]] = curr_aug[[r, i]]
                                            st.markdown(f"Step {step_num}: Swap Row {i+1} with Row {r+1}")
                                            st.latex(f"\\sim {format_augmented_matrix_latex(curr_aug, n_div=n)}")
                                            step_num += 1
                                            pivot = curr_aug[i, i]
                                            break
                                if not np.isclose(pivot, 0) and not np.isclose(pivot, 1):
                                    curr_aug[i] = curr_aug[i] / pivot
                                    st.markdown(f"Step {step_num}: Normalize Row {i+1} ($R_{{{i+1}}} \\to \\frac{{1}}{{{pivot:.2g}}} R_{{{i+1}}}$)")
                                    st.latex(f"\\sim {format_augmented_matrix_latex(curr_aug, n_div=n)}")
                                    step_num += 1
                                
                                for j in range(n):
                                    if j != i and not np.isclose(curr_aug[j, i], 0):
                                        factor = curr_aug[j, i]
                                        curr_aug[j] = curr_aug[j] - factor * curr_aug[i]
                                        st.markdown(f"Step {step_num}: Eliminate Row {j+1} ($R_{{{j+1}}} \\to R_{{{j+1}}} - ({factor:.2g})R_{{{i+1}}}$)")
                                        st.latex(f"\\sim {format_augmented_matrix_latex(curr_aug, n_div=n)}")
                                        step_num += 1
                                        
                            inv_mat = curr_aug[:, n:]
                            st.success("Successfully reduced to Reduced Row Echelon Form!")
                            st.markdown("**Final Inverse Matrix $A^{-1}$:**")
                            st.latex(f"A^{{-1}} = {format_matrix_latex(inv_mat)}")
        else:
            st.subheader(f"Manual Practice Mode ({method_choice})")
            
            if method_choice == "Gauss-Jordan Elimination":
                st.markdown("Perform elementary row-operations step-by-step on the augmented matrix $[A \\mid I]$ to calculate the inverse matrix $A^{-1}$.")
                
                if "manual_inv_history" not in st.session_state:
                    st.session_state.manual_inv_history = []
                if "manual_inv_orig" not in st.session_state:
                    st.session_state.manual_inv_orig = None
                if "manual_inv_curr" not in st.session_state:
                    st.session_state.manual_inv_curr = None

                c_pload1, c_pload2, c_pload3 = st.columns([1, 1, 2])
                with c_pload1:
                    load_manual_btn = st.button("Load Matrix", type="primary", key="load_manual_inv", use_container_width=True)
                with c_pload2:
                    reset_manual_btn = st.button("Reset", key="reset_manual_inv", use_container_width=True)

                if load_manual_btn:
                    if A.shape[0] != A.shape[1]:
                        st.error("Matrix must be square to find an inverse.")
                    else:
                        n_dim = A.shape[0]
                        aug_inv = np.column_stack((A, np.eye(n_dim)))
                        st.session_state.manual_inv_orig = aug_inv.copy()
                        st.session_state.manual_inv_curr = aug_inv.copy()
                        st.session_state.manual_inv_history = []
                        st.rerun()

                if reset_manual_btn:
                    st.session_state.manual_inv_orig = None
                    st.session_state.manual_inv_curr = None
                    st.session_state.manual_inv_history = []
                    st.rerun()

                if st.session_state.manual_inv_curr is not None:
                    n_dim = A.shape[0]
                    st.markdown("---")
                    mi_col1, mi_col2 = st.columns(2)
                    with mi_col1:
                        st.markdown("##### 📌 Initial Augmented Matrix $[A \\mid I]$")
                        st.latex(format_augmented_matrix_latex(st.session_state.manual_inv_orig, n_div=n_dim))
                    with mi_col2:
                        st.markdown("##### 🔄 Current Augmented Matrix State")
                        st.latex(format_augmented_matrix_latex(st.session_state.manual_inv_curr, n_div=n_dim))
                    st.markdown("---")

                    st.markdown("##### 🛠️ Apply Row Operation")
                    st.markdown("*Syntax:* `R1 <-> R2` | `R1 -> 3*R1` | `R2 -> R2 - 2*R1`")
                    inv_op_input = st.text_input("Enter Row Operation", placeholder="e.g., R3 -> R3 - R1", key="manual_inv_op_input")
                    
                    mic1, mic2, mic3 = st.columns([1, 1, 2])
                    with mic1:
                        inv_apply_btn = st.button("Execute Step", type="primary", key="manual_inv_exec", use_container_width=True)
                    with mic2:
                        inv_undo_btn = st.button("Undo Step", key="manual_inv_undo", use_container_width=True)
                        
                    if inv_apply_btn and inv_op_input:
                        try:
                            updated_inv = perform_row_operation(st.session_state.manual_inv_curr, inv_op_input)
                            st.session_state.manual_inv_history.append({"operation": inv_op_input, "matrix": updated_inv.copy()})
                            st.session_state.manual_inv_curr = updated_inv
                            st.success(f"Successfully applied: {inv_op_input}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                            
                    if inv_undo_btn:
                        if st.session_state.manual_inv_history:
                            st.session_state.manual_inv_history.pop()
                            if st.session_state.manual_inv_history:
                                st.session_state.manual_inv_curr = st.session_state.manual_inv_history[-1]["matrix"].copy()
                            else:
                                st.session_state.manual_inv_curr = st.session_state.manual_inv_orig.copy()
                            st.info("Reverted last operation.")
                            st.rerun()
                        else:
                            st.warning("No operations to undo.")

                    if st.session_state.manual_inv_history:
                        st.markdown("---")
                        st.markdown("##### 📚 Manual Step-by-Step History")
                        for idx, item in enumerate(st.session_state.manual_inv_history):
                            with st.expander(f"Step {idx+1}: {item['operation']}"):
                                st.latex(f"\\sim {format_augmented_matrix_latex(item['matrix'], n_div=n_dim)}")
                                
                    st.markdown("---")
                    if st.button("Check Result", key="check_manual_inv_result", type="primary"):
                        current_right_block = st.session_state.manual_inv_curr[:, n_dim:]
                        try:
                            actual_inv = np.linalg.inv(A)
                            if np.allclose(current_right_block, actual_inv, atol=1e-2):
                                st.success("🎉 Congratulations! You have successfully reduced the left block to Identity and correctly derived $A^{-1}$ on the right block!")
                                st.latex(f"A^{{-1}} = {format_matrix_latex(current_right_block)}")
                            else:
                                st.warning("⚠️ The right-hand block does not match the true inverse matrix yet. Keep performing row operations to achieve $[I \\mid A^{-1}]$!")
                        except Exception as err:
                            st.error(f"Verification error: {err}")
                else:
                    st.caption("Click the button above to load your matrix's augmented $[A \mid I]$ state into the manual practice workspace.")
            else:
                st.info("Perform the matrix inverse steps on your own scratchpad. You can use the verification block below to check your final calculated inverse matrix values.")
                
                user_ans_str = st.text_area("Enter your calculated inverse matrix values (row-by-row, comma or space separated):", value="1 0 0\n0 1 0\n0 0 1", key="user_manual_inverse_input")
                
                verify_clicked = st.button("Verify Result", key="verify_manual_inverse", type="primary")

                if verify_clicked:
                    try:
                        rows_ans = user_ans_str.strip().split("\n")
                        user_data = [[float(val) for val in r.replace(',', ' ').split()] for r in rows_ans if r.strip()]
                        User_Inv = np.array(user_data, dtype=float)
                        
                        actual_inv = np.linalg.inv(A)
                        
                        if User_Inv.shape == actual_inv.shape and np.allclose(User_Inv, actual_inv, atol=1e-2):
                            st.success("🎉 Excellent! Your calculated inverse matrix is correct.")
                            st.latex(f"\\text{{Your Answer}} = {format_matrix_latex(User_Inv)}")
                        else:
                            st.error("❌ Your matrix does not match the correct inverse. Please review your steps and try again.")
                            st.markdown("**Expected Correct Inverse for comparison:**")
                            st.latex(f"A^{{-1}} = {format_matrix_latex(actual_inv)}")
                    except Exception as err:
                        st.error(f"Error parsing your matrix input: {err}")

    elif selected_tab == "Rank & Consistency":
        st.markdown("#### Rank & Consistency Workspace")
    elif selected_tab == "Eigenvalues & Eigenvectors":
        st.markdown("#### Eigenvalues & Eigenvectors Workspace")

import streamlit as st
import numpy as np
import re
from fractions import Fraction

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

def render():
    st.markdown("### Unit-I: Systems of Linear Equations & Matrices")
    
    tab_names = [
        "Row Operations & RREF", 
        "Matrix Arithmetic & Inverses", 
        "Gaussian Elimination & LU", 
        "Rank & Solutions"
    ]
    
    default_tab_idx = getattr(st.session_state, "active_tab", 0)
    if not (0 <= default_tab_idx < len(tab_names)):
        default_tab_idx = 0

    selected_tab = st.radio(
        "Select Sub-Topic", 
        tab_names, 
        index=default_tab_idx, 
        horizontal=True, 
        label_visibility="collapsed",
        key="u1_sub_tabs"
    )
    
    st.divider()
    
    # --- TAB 0: ROW OPERATIONS & RREF ---
    if selected_tab == "Row Operations & RREF":
        st.markdown("#### Interactive Matrix Row Operations & RREF Practice")
        st.markdown("Practice elementary row transformations, echelon forms, and matrix reduction.")

        if "matrix_history" not in st.session_state:
            st.session_state.matrix_history = []
        if "current_matrix" not in st.session_state:
            st.session_state.current_matrix = None
        if "original_matrix" not in st.session_state:
            st.session_state.original_matrix = None

        col_set1, col_set2 = st.columns(2)
        with col_set1:
            rows = st.number_input("Rows", min_value=2, max_value=6, value=3, step=1, key="u1_rows")
        with col_set2:
            cols = st.number_input("Columns", min_value=2, max_value=6, value=3, step=1, key="u1_cols")
            
        if st.button("Reset Workspace", key="u1_reset"):
            st.session_state.matrix_history = []
            st.session_state.current_matrix = None
            st.session_state.original_matrix = None
            st.rerun()

        if st.session_state.original_matrix is None:
            st.markdown("##### Step 1: Define Matrix Entries")
            entered_rows = []
            valid_input = True
            for i in range(rows):
                row_input = st.text_input(f"Row {i+1}", value=" ".join(["1" if j==i else "0" for j in range(cols)]), key=f"row_{i}")
                try:
                    row_vals = [Fraction(x) for x in row_input.strip().split()]
                    if len(row_vals) != cols:
                        valid_input = False
                    entered_rows.append(row_vals)
                except:
                    valid_input = False
                    
            if st.button("Initialize Matrix & Start Practice", type="primary", key="u1_init"):
                if valid_input:
                    mat = np.array(entered_rows, dtype=object)
                    st.session_state.original_matrix = mat.copy()
                    st.session_state.current_matrix = mat.copy()
                    st.session_state.matrix_history = []
                    st.rerun()
                else:
                    st.error(f"Ensure every row contains exactly {cols} numbers/fractions.")
        else:
            col_left, col_right = st.columns([1.2, 1])
            with col_left:
                st.markdown("##### 🛠️ Apply Row Operation")
                st.markdown("*Syntax:* `R1 <-> R2` | `R1 -> 3*R1` | `R2 -> R2 - 2*R1`")
                op_input = st.text_input("Enter Operation", placeholder="e.g., R2 -> R2 - 2*R1", key="u1_op_input")
                
                c1, c2 = st.columns(2)
                with c1:
                    apply_btn = st.button("Execute Operation", type="primary", use_container_width=True, key="u1_exec")
                with c2:
                    undo_btn = st.button("Undo Last Step", use_container_width=True, key="u1_undo")
                    
                if apply_btn and op_input:
                    try:
                        updated = perform_row_operation(st.session_state.current_matrix, op_input)
                        st.session_state.matrix_history.append({"operation": op_input, "matrix": st.session_state.current_matrix.copy()})
                        st.session_state.current_matrix = updated
                        st.success(f"Successfully applied: {op_input}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                        
                if undo_btn:
                    if st.session_state.matrix_history:
                        last_state = st.session_state.matrix_history.pop()
                        st.session_state.current_matrix = last_state["matrix"]
                        st.info("Reverted last operation.")
                        st.rerun()
                    else:
                        st.warning("No operations to undo.")

            with col_right:
                st.markdown("##### 📊 Current Matrix State")
                st.latex(format_matrix_latex(st.session_state.current_matrix))

            if st.session_state.matrix_history:
                st.markdown("---")
                st.markdown("##### 📜 Step-by-Step Practice History")
                for idx, item in enumerate(st.session_state.matrix_history):
                    with st.expander(f"Step {idx+1}: {item['operation']}"):
                        st.latex(format_matrix_latex(item['matrix']))

    # --- TAB 1: MATRIX ARITHMETIC & INVERSES ---
    elif selected_tab == "Matrix Arithmetic & Inverses":
        st.markdown("#### Matrix Multiplication & Invertible Matrices Practice")
        st.info("Interactive workspace for testing matrix products, determinants, and finding matrix inverses ($A^{-1}$).")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("##### Matrix A Input")
            a_input = st.text_area("Row-by-row values for A (comma separated rows)", value="1, 2\n3, 4", key="mat_a_val")
        with col_m2:
            st.markdown("##### Matrix B Input")
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

    # --- TAB 2: GAUSSIAN ELIMINATION & LU DECOMPOSITION ---
    elif selected_tab == "Gaussian Elimination & LU":
        st.markdown("#### System of Linear Equations Solver")
        st.markdown("Solve $Ax = b$ using Gauss Elimination (Manual/Automated) or LU Factorization (Doolittle's / Crout's methods).")
        
        method_choice = st.selectbox(
            "Select Solution Technique", 
            ["Gauss Elimination", "Doolittle's Method (LU)", "Crout's Method (LU)"]
        )
        
        n_vars = st.number_input("Number of Variables / Equations ($n$)", min_value=2, max_value=5, value=3, step=1, key="sys_n")
        
        st.markdown("##### Enter Coefficient Matrix A and Vector b")
        A_rows = []
        for i in range(n_vars):
            r_val = st.text_input(f"Row {i+1} coefficients (space separated)", value=" ".join(["1" if j==i else "0" for j in range(n_vars)]), key=f"gauss_a_{i}")
            A_rows.append([float(x) for x in r_val.split()])
            
        b_val = st.text_input("Constant vector b (space separated)", value=" ".join(["1"] * n_vars), key="gauss_b")
        b_vec = [float(x) for x in b_val.split()]
        
        if method_choice == "Gauss Elimination":
            mode = st.radio("Select Mode", ["Automated Step-by-Step", "Manual Practice Mode"])
            if st.button("Run Solver", type="primary", key="run_gauss"):
                A_mat = np.array(A_rows, dtype=float)
                b_col = np.array(b_vec, dtype=float)
                aug = np.column_stack((A_mat, b_col))
                
                if mode == "Automated Step-by-Step":
                    st.markdown("##### Automated Execution Steps")
                    steps = [aug.copy()]
                    curr = aug.copy()
                    for i in range(n_vars):
                        if curr[i, i] == 0:
                            for r in range(i+1, n_vars):
                                if curr[r, i] != 0:
                                    curr[[i, r]] = curr[[r, i]]
                                    steps.append(curr.copy())
                                    break
                        for j in range(i+1, n_vars):
                            if curr[i, i] != 0:
                                factor = curr[j, i] / curr[i, i]
                                curr[j] = curr[j] - factor * curr[i]
                                steps.append(curr.copy())
                    
                    for idx, step_mat in enumerate(steps):
                        st.markdown(f"**Step {idx} Matrix:**")
                        st.latex(format_matrix_latex(step_mat))
                        
                    # Back substitution solution
                    x = np.zeros(n_vars)
                    for i in range(n_vars - 1, -1, -1):
                        x[i] = (curr[i, -1] - np.dot(curr[i, i+1:n_vars], x[i+1:n_vars])) / curr[i, i]
                    st.success(f"Final Solution Vector x: {x}")
                else:
                    st.info("Switch to Tab 0 (Row Operations & RREF) for full hands-on manual row operation validation on this matrix system.")
                    
        else:
            # LU Decomposition (Doolittle / Crout)
            lu_type = "doolittle" if "Doolittle" in method_choice else "crout"
            sub_option = st.selectbox(
                "LU Breakdown View", 
                ["(i) Show L and U Matrices (Factorization)", "(ii) Show Intermediate Steps (Solving Ly = b)", "(iii) Final Solution Vector (x)"]
            )
            
            if st.button("Compute LU Decomposition", type="primary", key="run_lu"):
                A = np.array(A_rows, dtype=float)
                b = np.array(b_vec, dtype=float)
                n = len(b)
                L = np.zeros((n, n))
                U = np.zeros((n, n))
                
                if lu_type == "doolittle":
                    for i in range(n):
                        L[i, i] = 1.0
                        for j in range(i, n):
                            s = sum(L[i, k] * U[k, j] for k in range(i))
                            U[i, j] = A[i, j] - s
                        for j in range(i + 1, n):
                            s = sum(L[j, k] * U[k, i] for k in range(i))
                            L[j, i] = (A[j, i] - s) / U[i, i]
                else:
                    for i in range(n):
                        U[i, i] = 1.0
                        for j in range(i, n):
                            s = sum(L[j, k] * U[k, i] for k in range(i))
                            L[j, i] = A[j, i] - s
                        for j in range(i + 1, n):
                            s = sum(L[i, k] * U[k, j] for k in range(i))
                            U[i, j] = (A[i, j] - s) / L[i, i]
                
                # Solve Ly = b
                y = np.zeros(n)
                for i in range(n):
                    s = sum(L[i, k] * y[k] for k in range(i))
                    y[i] = (b[i] - s) / L[i, i]
                    
                # Solve Ux = y
                x = np.zeros(n)
                for i in range(n - 1, -1, -1):
                    s = sum(U[i, k] * x[k] for k in range(i + 1, n))
                    x[i] = (y[i] - s) / U[i, i]

                if "(i)" in sub_option:
                    col_l1, col_l2 = st.columns(2)
                    with col_l1:
                        st.markdown("**Lower Triangular Matrix L**")
                        st.latex(format_matrix_latex(L))
                    with col_l2:
                        st.markdown("**Upper Triangular Matrix U**")
                        st.latex(format_matrix_latex(U))
                elif "(ii)" in sub_option:
                    st.markdown("**Intermediate Solution Vector (y solving Ly = b)**")
                    st.write(y)
                else:
                    st.markdown("**Final Solution Vector (x solving Ux = y)**")
                    st.write(x)

    # --- TAB 4: RANK & SOLUTIONS ---
    elif selected_tab == "Rank & Solutions":
        st.markdown("#### Rank of a Matrix & System Consistency")
        st.info("Check matrix rank, column/row space dimensions, and consistency conditions for linear equation sets.")
        
        matrix_text = st.text_area("Enter matrix rows (comma separated values)", value="1, 2, 3\n2, 4, 6\n1, 1, 1", key="rank_mat")
        if st.button("Calculate Rank", type="primary", key="calc_rank"):
            try:
                mat = np.array([[float(x) for x in r.split(",")] for r in matrix_text.strip().split("\n")], dtype=float)
                rank = np.linalg.matrix_rank(mat)
                st.success(f"The rank of the matrix is: **{rank}**")
            except Exception as e:
                st.error(f"Error parsing matrix: {e}")

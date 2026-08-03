import streamlit as st
import numpy as np
import re
from fractions import Fraction
import matplotlib.pyplot as plt

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
        "Row Operations", 
        "System of Linear Equations", 
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

    # --- TAB 1: SYSTEM OF LINEAR EQUATIONS ---
    elif selected_tab == "System of Linear Equations":
        st.markdown("#### System of Linear Equations Solver")
        st.markdown("Solve $Ax = b$ using Gauss Elimination, LU Factorization, or check system consistency and rank.")
        
        method_choice = st.selectbox(
            "Select Solution Technique", 
            ["Gauss Elimination", "Doolittle's Method (LU)", "Crout's Method (LU)", "Rank & System Consistency"]
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
            if st.button("Run Gauss Solver", type="primary", key="run_gauss"):
                A_mat = np.array(A_rows, dtype=float)
                b_col = np.array(b_vec, dtype=float)
                aug = np.column_stack((A_mat, b_col))
                
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
                    
                x = np.zeros(n_vars)
                for i in range(n_vars - 1, -1, -1):
                    x[i] = (curr[i, -1] - np.dot(curr[i, i+1:n_vars], x[i+1:n_vars])) / curr[i, i]
                st.success(f"Final Solution Vector x: {x}")
                st.session_state['last_solved_system'] = (A_mat, b_col)
                
        elif "LU" in method_choice:
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
                
                y = np.zeros(n)
                for i in range(n):
                    s = sum(L[i, k] * y[k] for k in range(i))
                    y[i] = (b[i] - s) / L[i, i]
                    
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
                st.session_state['last_solved_system'] = (A, b)
        else:
            if st.button("Check Rank & Consistency", type="primary", key="calc_rank_sys"):
                try:
                    mat_a = np.array(A_rows, dtype=float)
                    vec_b = np.array(b_vec, dtype=float)
                    aug_mat = np.column_stack((mat_a, vec_b))
                    
                    r_a = np.linalg.matrix_rank(mat_a)
                    r_aug = np.linalg.matrix_rank(aug_mat)
                    
                    st.markdown(f"* Rank of Coefficient Matrix A: **{r_a}**")
                    st.markdown(f"* Rank of Augmented Matrix [A|b]: **{r_aug}**")
                    
                    if r_a != r_aug:
                        st.error("The system is **Inconsistent** (No solutions).")
                    elif r_a == r_aug and r_a == n_vars:
                        st.success("The system is **Consistent** with a **Unique Solution**.")
                    else:
                        st.warning("The system is **Consistent** with **Infinitely Many Solutions**.")
                    st.session_state['last_solved_system'] = (mat_a, vec_b)
                except Exception as e:
                    st.error(f"Error calculating rank: {e}")

        # --- OPTIONAL GEOMETRICAL VISUALIZATION SECTION ---
        if n_vars in [2, 3] and 'last_solved_system' in st.session_state:
            st.markdown("---")
            with st.expander("📈 Optional Geometrical Visualization (View Intersection of Lines/Planes)"):
                st.markdown("Visualize how the equations geometrically intersect in space (2D lines or 3D planes).")
                if st.button("Generate Geometry Plot", key="gen_geom_plot"):
                    A_plot, b_plot = st.session_state['last_solved_system']
                    if A_plot.shape[0] >= 2 and A_plot.shape[1] == 2:
                        # 2D Plot: Lines intersection
                        fig, ax = plt.subplots(figsize=(6, 6))
                        x_vals = np.linspace(-10, 10, 400)
                        for i in range(len(b_plot)):
                            a1, a2 = A_plot[i, 0], A_plot[i, 1]
                            c = b_plot[i]
                            if a2 != 0:
                                y_vals = (c - a1 * x_vals) / a2
                                ax.plot(x_vals, y_vals, label=f"Eq {i+1}: {a1}x + {a2}y = {c}")
                            else:
                                if a1 != 0:
                                    x_const = c / a1
                                    ax.axvline(x=x_const, label=f"Eq {i+1}: x = {x_const}")
                        ax.axhline(0, color='black', linewidth=1)
                        ax.axvline(0, color='black', linewidth=1)
                        ax.set_xlim(-10, 10)
                        ax.set_ylim(-10, 10)
                        ax.grid(True, linestyle='--', alpha=0.6)
                        ax.legend()
                        ax.set_title("Geometrical Interpretation (2D Lines)")
                        st.pyplot(fig)
                        
                    elif A_plot.shape[0] >= 3 and A_plot.shape[1] == 3:
                        # 3D Plot: Planes intersection
                        fig = plt.figure(figsize=(8, 6))
                        ax = fig.add_subplot(111, projection='3d')
                        xx, yy = np.meshgrid(np.linspace(-5, 5, 10), np.linspace(-5, 5, 10))
                        for i in range(min(3, len(b_plot))):
                            a, b, c = A_plot[i, 0], A_plot[i, 1], A_plot[i, 2]
                            d = b_plot[i]
                            if c != 0:
                                zz = (d - a * xx - b * yy) / c
                                ax.plot_surface(xx, yy, zz, alpha=0.5, label=f"Plane {i+1}")
                        ax.set_xlabel("X-axis")
                        ax.set_ylabel("Y-axis")
                        ax.set_zlabel("Z-axis")
                        ax.set_title("Geometrical Interpretation (3D Planes)")
                        st.pyplot(fig)
                    else:
                        st.warning("Visualization is optimized for 2 or 3 variable systems.")

    # --- TAB 2: INVERSE OF A MATRIX ---
    elif selected_tab == "Inverse of a Matrix":
        st.markdown("#### Matrix Multiplication & Invertible Matrices Practice")
        st.info("Interactive workspace for testing matrix products, determinants, and finding matrix inverses ($A^{-1}$), plus elementary matrix properties.")
        
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

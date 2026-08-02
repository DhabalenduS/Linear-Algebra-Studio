import streamlit as st
import numpy as np
import re
from fractions import Fraction

def format_matrix_latex(mat):
    latex_rows = []
    for row in mat:
        row_elems = []
        for val in row:
            f = Fraction(val).limit_denominator()
            if f.denominator == 1:
                row_elems.append(str(f.numerator))
            else:
                row_elems.append(f"\\frac{{{f.numerator}}}{{{f.denominator}}}")
        latex_rows.append(" & ".join(row_elems))
    return "\\begin{bmatrix}\n" + " \\\\\n".join(latex_rows) + "\n\\end{bmatrix}"

def perform_row_operation(A, op_str):
    op_str = op_str.replace(" ", "")
    
    # 1. Row Swap: e.g., R1<->R2
    swap_match = re.match(r"R(\d+)<->R(\d+)", op_str)
    if swap_match:
        r1 = int(swap_match.group(1)) - 1
        r2 = int(swap_match.group(2)) - 1
        if not (0 <= r1 < len(A) and 0 <= r2 < len(A)):
            raise ValueError(f"Row index out of range. Matrix has {len(A)} rows.")
        new_A = A.copy()
        new_A[[r1, r2]] = new_A[[r2, r1]]
        return new_A

    # 2. Row Replacement/Scaling: e.g., R2->R2-3*R1
    match = re.match(r"R(\d+)->(.*)", op_str)
    if not match:
        raise ValueError("Invalid format. Use 'R1 <-> R2' for swaps or 'R2 -> R2 - 3*R1' for replacement.")

    target_idx = int(match.group(1)) - 1
    expr = match.group(2)

    if not (0 <= target_idx < len(A)):
        raise ValueError(f"Target row index out of range. Matrix has {len(A)} rows.")

    if re.fullmatch(r"R\d+", expr):
        raise ValueError(f"Invalid replacement: '{op_str}'. Did you mean to use '<->'?")

    new_A = A.copy()

    def replace_row(m):
        r_num = int(m.group(1)) - 1
        if not (0 <= r_num < len(A)):
            raise ValueError(f"Referenced row R{r_num + 1} is out of range.")
        return f"A[{r_num}]"

    python_expr = re.sub(r"R(\d+)", replace_row, expr)

    try:
        new_A[target_idx] = eval(python_expr, {"A": A, "np": np, "Fraction": Fraction})
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {e}.")

    return new_A

def render():
    st.markdown("### Unit-I: Systems of Linear Equations")
    
    # Sub-tabs for Unit I
    sub_tab_1, sub_tab_2, sub_tab_3, sub_tab_4 = st.tabs([
        "Row Operations & RREF", 
        "Matrix Arithmetic & Inverses", 
        "Gaussian Elimination & LU", 
        "Rank & Solutions"
    ])
    
    with sub_tab_1:
        st.markdown("#### Interactive Matrix Row Operations")
        st.markdown("Professional workspace for linear algebra reduction and elementary row transformations.")

        # Session State Initialization (scoped or global)
        if "matrix_history" not in st.session_state:
            st.session_state.matrix_history = []
        if "current_matrix" not in st.session_state:
            st.session_state.current_matrix = None
        if "original_matrix" not in st.session_state:
            st.session_state.original_matrix = None

        # Sidebar controls for Matrix setup inside Unit 1
        st.markdown("---")
        col_set1, col_set2 = st.columns(2)
        with col_set1:
            rows = st.number_input("Rows", min_value=2, max_value=6, value=4, step=1, key="u1_rows")
        with col_set2:
            cols = st.number_input("Columns", min_value=2, max_value=6, value=3, step=1, key="u1_cols")
            
        reset_btn = st.button("Reset Workspace", key="u1_reset")
        if reset_btn:
            st.session_state.matrix_history = []
            st.session_state.current_matrix = None
            st.session_state.original_matrix = None
            st.rerun()

        # Step 1: Input Matrix Entries
        if st.session_state.original_matrix is None:
            st.markdown("##### Step 1: Define Matrix Entries")
            st.info(f"Enter space-separated numerical values for each row ({cols} values per row).")
            
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
                    
            if st.button("Initialize Matrix & Start Studio", type="primary", key="u1_init"):
                if valid_input:
                    mat = np.array(entered_rows, dtype=object)
                    st.session_state.original_matrix = mat.copy()
                    st.session_state.current_matrix = mat.copy()
                    st.session_state.matrix_history = []
                    st.rerun()
                else:
                    st.error(f"Ensure every row contains exactly {cols} valid numbers/fractions separated by spaces.")
        else:
            # Step 2: Interactive Workspace & Dashboard
            col_left, col_right = st.columns([1.2, 1])
            
            with col_left:
                st.markdown("##### 🛠️ Apply Row Operation")
                st.markdown("*Syntax:* `R1 <-> R2` | `R1 -> 3*R1` | `R2 -> R2 - 3*R1`")
                op_input = st.text_input("Enter Operation", placeholder="e.g., R2 -> R2 - 2*R1", key="u1_op_input")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    apply_btn = st.button("Execute Operation", type="primary", use_container_width=True, key="u1_exec")
                with col_btn2:
                    undo_btn = st.button("Undo Last Step", use_container_width=True, key="u1_undo")
                    
                if apply_btn and op_input:
                    try:
                        updated = perform_row_operation(st.session_state.current_matrix, op_input)
                        st.session_state.matrix_history.append({
                            "operation": op_input,
                            "matrix": st.session_state.current_matrix.copy()
                        })
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
                st.markdown("##### 📊 Current Matrix")
                st.latex(format_matrix_latex(st.session_state.current_matrix))

            # Step 3: Execution Audit Trail
            if st.session_state.matrix_history:
                st.markdown("---")
                st.markdown("##### 📜 Execution History & Summary Audit")
                for idx, item in enumerate(st.session_state.matrix_history):
                    with st.expander(f"Step {idx+1}: {item['operation']}"):
                        st.latex(format_matrix_latex(item['matrix']))

    with sub_tab_2:
        st.subheader("Matrix Arithmetic & Inverses")
        st.info("Module under development for Matrix Multiplication and Inverses.")

    with sub_tab_3:
        st.subheader("Gaussian Elimination & LU Decomposition")
        st.info("Module under development for Matrix Factorization.")

    with sub_tab_4:
        st.subheader("Rank & System Solutions")
        st.info("Module under development for consistency checks and solution sets.")

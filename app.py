import streamlit as st
import numpy as np
import re
from fractions import Fraction

# --- Page Config ---
st.set_page_config(page_title="Interactive Row-Operation Interface", layout="centered")

st.title("Interactive Elementary Row Operation Tool")
st.markdown("Practice Row Operations")
# --- Helper Functions ---
def format_matrix_display(mat):
    cleaned_rows = []
    for row in mat:
        cleaned_row = []
        for val in row:
            f = Fraction(val).limit_denominator()
            if f.denominator == 1:
                cleaned_row.append(str(f.numerator))
            else:
                cleaned_row.append(f"{f.numerator}/{f.denominator}")
        cleaned_rows.append(cleaned_row)
    return cleaned_rows

def perform_row_operation(A, op_str):
    op_str = op_str.replace(" ", "")

    # 1. Check for Row Swap: e.g., R1<->R2
    swap_match = re.match(r"R(\d+)<->R(\d+)", op_str)
    if swap_match:
        r1 = int(swap_match.group(1)) - 1
        r2 = int(swap_match.group(2)) - 1

        if not (0 <= r1 < len(A) and 0 <= r2 < len(A)):
            raise ValueError(f"Row index out of range. Matrix has {len(A)} rows.")

        new_A = A.copy()
        new_A[[r1, r2]] = new_A[[r2, r1]]
        return new_A

    # 2. Check for Row Replacement/Scaling: e.g., R2->R2-3*R1, R1->3*R1
    match = re.match(r"R(\d+)->(.*)", op_str)
    if not match:
        raise ValueError(
            "Invalid operation format! "
            "Use '<->' for swaps (e.g., R1 <-> R2) "
            "or '->' for replacement/scaling (e.g., R2 -> R2 - 3*R1)."
        )

    target_idx = int(match.group(1)) - 1
    expr = match.group(2)

    if not (0 <= target_idx < len(A)):
        raise ValueError(f"Target row index out of range. Matrix has {len(A)} rows.")

    if re.fullmatch(r"R\d+", expr):
        raise ValueError(
            f"Invalid replacement: '{op_str}'. "
            "Did you mean to use a swap '<->' instead of '->'?"
        )

    new_A = A.copy()

    def replace_row(m):
        r_num = int(m.group(1)) - 1
        if not (0 <= r_num < len(A)):
            raise ValueError(f"Referenced row R{r_num + 1} is out of range. Matrix has {len(A)} rows.")
        return f"A[{r_num}]"

    python_expr = re.sub(r"R(\d+)", replace_row, expr)

    try:
        new_A[target_idx] = eval(python_expr, {"A": A, "np": np, "Fraction": Fraction})
    except Exception as e:
        raise ValueError(f"Error evaluating expression: {e}. Check your math syntax.")

    return new_A

# --- Session State Initialization ---
if "initialized" not in st.session_state:
    st.session_state.initialized = False

# --- Step 1: Input Setup Form ---
if not st.session_state.initialized:
    st.subheader("Step 1: Define Matrix Dimensions and Entries")
    
    rows = st.number_input("Number of rows for Matrix A:", min_value=1, max_value=10, value=4, step=1)
    cols = st.number_input("Number of columns for Matrix A:", min_value=1, max_value=10, value=3, step=1)

    st.markdown("Enter matrix entries row by row (space-separated values, e.g., `3 3 2`):")
    
    default_rows = ["3 3 2", "1 2 0", "0 10 3", "2 -3 -1"]
    row_inputs = []
    for i in range(rows):
        default_val = default_rows[i] if i < len(default_rows) else "0 " * cols
        val = st.text_input(f"Row {i+1}", value=default_val.strip(), key=f"row_input_{i}")
        row_inputs.append(val)

    if st.button("Initialize Matrix"):
        try:
            A_list = []
            for r_str in row_inputs:
                row_vals = [Fraction(x) for x in r_str.strip().split()]
                if len(row_vals) != cols:
                    raise ValueError(f"Each row must contain exactly {cols} elements.")
                A_list.append(row_vals)
            
            st.session_state.original_matrix = np.array(A_list, dtype=object)
            st.session_state.current_matrix = st.session_state.original_matrix.copy()
            st.session_state.history = []
            st.session_state.step_count = 1
            st.session_state.initialized = True
            st.rerun()
        except Exception as e:
            st.error(f"Error parsing matrix input: {e}")

# --- Step 2: Interactive Operation Interface ---
else:
    st.subheader("Current Matrix State")
    
    current_display = format_matrix_display(st.session_state.current_matrix)
    st.table(current_display)

    st.markdown("---")
    st.markdown("**Examples of Operations:** `R1 <-> R2` (Swap) | `R1 -> 3*R1` (Scaling) | `R2 -> R2 - 3*R1` (Replacement)")
    
    op_input = st.text_input("Enter row operation:", placeholder="e.g., R2 -> R2 - 3*R1")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Apply Operation"):
            try:
                if not op_input.strip():
                    st.warning("Please enter a valid row operation.")
                else:
                    updated_matrix = perform_row_operation(st.session_state.current_matrix, op_input)
                    
                    st.session_state.history.append({
                        "step": st.session_state.step_count,
                        "operation": op_input,
                        "matrix": updated_matrix.copy()
                    })

                    st.session_state.current_matrix = updated_matrix
                    st.session_state.step_count += 1
                    
                    st.success(f"Successfully applied: {op_input}")
                    st.rerun()
            except ValueError as ve:
                st.warning(f"WARNING: {ve}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

    with col2:
        if st.button("Reset / Start Over"):
            st.session_state.initialized = False
            st.rerun()

    # --- History & Summary Section ---
    if st.session_state.history:
        with st.expander("View Execution History & Summary"):
            st.write("**Original Matrix:**")
            st.table(format_matrix_display(st.session_state.original_matrix))
            
            for item in st.session_state.history:
                st.write(f"**Step {item['step']} (Operation: `{item['operation']}`)**")
                st.table(format_matrix_display(item['matrix']))

import streamlit as st
import numpy as np

def adjoint_method_module():
    st.subheader("Inverse via Adjoint Method")
    
    # Select Mode
    mode = st.selectbox("Select Mode", ["Automated", "Manual"])
    
    # Sample matrix B from Lecture No 6 - Problem 2
    # B = [[2, -1, 1], [1, 2, 3], [3, -2, 4]]
    B = np.array([[2, -1, 1], 
                  [1, 2, 3], 
                  [3, -2, 4]], dtype=float)
    
    st.write("**Target Matrix B:**")
    st.write(B)
    
    if mode == "Automated":
        st.markdown("### Automated Solution via Adjoint Formula")
        
        # 1. Determinant
        det_B = np.linalg.det(B)
        det_rounded = round(det_B)
        st.write(f"**1. Determinant of B:** $\\det(B) = {det_rounded}$")
        
        if det_rounded == 0:
            st.error("Matrix is singular (determinant is zero). Inverse does not exist.")
            return

        # 2. Cofactor Matrix C
        # C_ij = (-1)**(i+j) * det(M_ij)
        cofactor_matrix = np.zeros_like(B)
        rows, cols = B.shape
        for i in range(rows):
            for j in range(cols):
                minor = np.delete(np.delete(B, i, axis=0), j, axis=1)
                cofactor_matrix[i, j] = ((-1) ** (i + j)) * round(np.linalg.det(minor))
                
        st.write("**2. Cofactor Matrix (C):**")
        st.write(cofactor_matrix)
        
        # 3. Adjoint Matrix (Transpose of Cofactor Matrix)
        adj_B = cofactor_matrix.T
        st.write("**3. Adjoint Matrix ($\\operatorname{adj}(B) = C^T$):**")
        st.write(adj_B)
        
        # 4. Inverse Matrix B^(-1) = (1 / det(B)) * adj(B)
        inv_B = adj_B / det_rounded
        st.write("**4. Inverse Matrix ($B^{-1} = \\frac{1}{\\det(B)}\\operatorname{adj}(B)$):**")
        st.write(inv_B)

    elif mode == "Manual":
        st.markdown("### Manual Practice Mode (Adjoint Formula)")
        st.write("Perform the steps sequentially to compute the inverse via the adjoint method[cite: 3].")
        
        # Step 1: Determinant input check
        st.markdown("#### Step 1: Compute Determinant $\\det(B)$")
        user_det = st.number_input("Enter $\\det(B)$:", value=0.0)
        
        actual_det = round(np.linalg.det(B))
        if st.button("Verify Determinant"):
            if abs(user_det - actual_det) < 1e-5:
                st.success("Correct determinant!")
            else:
                st.error(f"Incorrect. The correct determinant is {actual_det}.")
                
        # Step 2 & 3: Adjoint Matrix check
        st.markdown("#### Step 2 & 3: Enter Adjoint Matrix $\\operatorname{adj}(B)$")
        st.write("Provide elements for the 3x3 adjoint matrix:")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            adj_00 = st.number_input("adj[0,0]", value=0.0)
            adj_10 = st.number_input("adj[1,0]", value=0.0)
            adj_20 = st.number_input("adj[2,0]", value=0.0)
        with col2:
            adj_01 = st.number_input("adj[0,1]", value=0.0)
            adj_11 = st.number_input("adj[1,1]", value=0.0)
            adj_21 = st.number_input("adj[2,1]", value=0.0)
        with col3:
            adj_02 = st.number_input("adj[0,2]", value=0.0)
            adj_12 = st.number_input("adj[1,2]", value=0.0)
            adj_22 = st.number_input("adj[2,2]", value=0.0)
            
        user_adj = np.array([[adj_00, adj_01, adj_02],
                             [adj_10, adj_11, adj_12],
                             [adj_20, adj_21, adj_22]])
        
        cofactor_matrix = np.zeros_like(B)
        for i in range(3):
            for j in range(3):
                minor = np.delete(np.delete(B, i, axis=0), j, axis=1)
                cofactor_matrix[i, j] = ((-1) ** (i + j)) * round(np.linalg.det(minor))
        actual_adj = cofactor_matrix.T
        
        if st.button("Verify Adjoint Matrix"):
            if np.allclose(user_adj, actual_adj):
                st.success("Excellent! The adjoint matrix is correct.")
            else:
                st.error("The adjoint matrix contains errors. Please recheck your cofactor transpose steps[cite: 3].")

if __name__ == "__main__":
    st.title("Linear Algebra Studio")
    adjoint_method_module()

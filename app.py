import streamlit as st
import pandas as pd
import joblib
import base64
from io import BytesIO
import streamlit_authenticator as stauth

# --- AUTHENTICATION ---
names = ["Sayeda Rehmat"]
usernames = ["sayeda"]
passwords = ["autoneuro123"]
hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(names, usernames, hashed_passwords, "auto_neuro_app", "abcdef", cookie_expiry_days=1)
name, auth_status, username = authenticator.login("Login", "main")

if auth_status == False:
    st.error("Username/password is incorrect")
elif auth_status == None:
    st.warning("Please enter your username and password")
elif auth_status:

    st.title("🧠 AutoNeuro Pro")
    st.write(f"Welcome, **{name}** 👋")

    model = joblib.load("gene_classifier.pkl")

    st.subheader("🔬 Predict from Gene Name")
    gene_input = st.text_input("Enter Gene Name:")
    if st.button("Predict"):
        if gene_input.strip():
            pred = model.predict([gene_input])[0]
            st.success(f"Prediction: {pred}")

    st.subheader("📂 Predict from Uploaded VCF (Sample Format Required)")
    uploaded_file = st.file_uploader("Upload a .vcf file (with GENE info in INFO column)", type="vcf")
    if uploaded_file:
        vcf_lines = uploaded_file.getvalue().decode("utf-8").splitlines()
        results = []
        for line in vcf_lines:
            if line.startswith("#"):
                continue
            cols = line.strip().split("\t")
            if len(cols) < 8:
                continue
            info_field = cols[7]
            gene = "Unknown"
            for item in info_field.split(";"):
                if item.startswith("GENE="):
                    gene = item.replace("GENE=", "").strip()
                    break
            if gene != "Unknown":
                try:
                    pred = model.predict([gene])[0]
                    results.append({"Gene": gene, "Prediction": pred})
                except:
                    results.append({"Gene": gene, "Prediction": "Error"})
        df = pd.DataFrame(results)
        if not df.empty:
            st.dataframe(df)
            csv = df.to_csv(index=False).encode()
            st.download_button("📥 Download CSV", csv, "predictions.csv", "text/csv")

            pdf = BytesIO()
            pdf.write(df.to_string().encode())
            st.download_button("📄 Download PDF", pdf.getvalue(), "predictions.pdf", "application/pdf")
        else:
            st.warning("No valid GENE= entries found in the uploaded VCF.")

    st.markdown("---")
    st.markdown("👩‍💻 Created by **Sayeda Rehmat**")

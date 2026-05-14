import streamlit as st
import pandas as pd
from faker import Faker
import io
from sqlalchemy import create_engine, inspect

fake = Faker()

st.set_page_config(page_title="SafeSandbox Pro", page_icon="🔒", layout="wide")
st.title("🔒 SafeSandbox Pro: Data Anonymizer")
# Create a professional pricing sidebar panel
with st.sidebar:
    st.header("👑 Go Premium")
    st.write("Unlock unlimited database record scrubbing, multi-table syncing, and production environment exports.")
    
    # Your live Gumroad payment checkout link
   st.link_button("🚀 Upgrade to Pro ($29/mo)", "https://casmir34.gumroad.com/l/safesandbox-pro")
    
    st.divider()
    st.info("💡 Standard Workspace Session Mode.")


tab1, tab2 = st.tabs(["📁 File Upload Mode", "🗄️ Live Cloud Database Mode"])

def anonymize_dataframe(df):
    for col in df.columns:
        col_lower = str(col).lower()
        if 'name' in col_lower:
            df[col] = df[col].apply(lambda x: fake.name() if pd.notnull(x) else x)
        elif 'email' in col_lower:
            df[col] = df[col].apply(lambda x: fake.unique.email() if pd.notnull(x) else x)
        elif 'phone' in col_lower:
            df[col] = df[col].apply(lambda x: fake.phone_number() if pd.notnull(x) else x)
    return df

# TRACK 1: FILE UPLOADS
with tab1:
    uploaded_file = st.file_uploader("Upload CSV or Excel production logs", type=["csv", "xlsx"])
    if uploaded_file is not None:
        filename = uploaded_file.name
        df = pd.read_excel(uploaded_file) if filename.endswith(('.xlsx', '.xls')) else pd.read_csv(uploaded_file, encoding='utf-8', errors='ignore')
        
        st.success("File pulled successfully!")
        df_clean = anonymize_dataframe(df)
        st.dataframe(df_clean.head(5))
        
        output = io.BytesIO()
        df_clean.to_csv(output, index=False)
        st.download_button("📥 Download Anonymised File", data=output.getvalue(), file_name=f"clean_{filename}", mime="text/csv")

# TRACK 2: LIVE DATABASES (Supabase / Postgres)
with tab2:
    st.write("Connect directly to your live cloud database tables to scrub them in place.")
    db_uri = st.text_input(
        "Enter your Connection String (URI)", 
        placeholder="postgresql://postgres:password@db.supabase.co:5432/postgres",
        type="password"
    )
    
    if db_uri:
        try:
            engine = create_engine(db_uri)
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            selected_table = st.selectbox("🎯 Select a database table to anonymise:", tables)
            
            if st.button("⚡ Fetch & Anonymise Database Table"):
                with st.spinner("Streaming records from database..."):
                    df_db = pd.read_sql_table(selected_table, engine)
                    df_db_clean = anonymize_dataframe(df_db)
                    st.success(f"Cleaned table metadata generated for: {selected_table}")
                    st.dataframe(df_db_clean.head(10))
                    
                    csv_data = df_db_clean.to_csv(index=False).encode('utf-8')
                    st.download_button("📥 Export Clean Table as CSV", data=csv_data, file_name=f"clean_{selected_table}.csv")
        except Exception as e:
            st.error(f"🔌 Connection failed: {e}")

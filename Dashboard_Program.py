import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

conn = sqlite3.connect("mlb_history.db")

tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
table_list = tables["name"].tolist()

selected_table = st.selectbox("Select Year & Table", table_list)

df = pd.read_sql_query(f"SELECT * FROM `{selected_table}`", conn)

numeric_cols = df.select_dtypes(include='number').columns
if not numeric_cols.empty:
    col = st.selectbox("Choose a numeric column to filter", numeric_cols)
    min_val, max_val = int(df[col].min()), int(df[col].max())
    user_range = st.slider(f"Filter {col}", min_val, max_val, (min_val, max_val))
    df = df[(df[col] >= user_range[0]) & (df[col] <= user_range[1])]


st.dataframe(df.head())

# Bar chart
st.subheader("Bar Chart of Selected Numeric Column")
st.bar_chart(df[numeric_cols[0]])

# Line chart
st.subheader("Line Chart of Same Column (if applicable)")
st.line_chart(df[numeric_cols[0]])

# Heatmap
if len(numeric_cols) >= 2:
    st.subheader("Correlation Heatmap")
    fig, ax = plt.subplots()
    sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)
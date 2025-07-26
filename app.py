import streamlit as st
import pandas as pd
import os

DATA_FILE = r"C:\Users\ChristaTaylor\OneDrive - dottba.com\code\data\prem_list.csv"

@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Load and initialize
df = load_data()
if "saved_by" not in df.columns:
    df["saved_by"] = ""
if "Keep for Dish" not in df.columns:
    df["Keep for Dish"] = False

st.title("📱 Mobile Premium List")

# Track user
username = st.text_input("Enter your name to track edits:", key="user_input")
if not username:
    st.warning("Please enter your name above to enable editing.")

# Search + Pagination
# Search + Filters
st.markdown("### 🔍 Filter Results")

search_term = st.text_input("Search keywords:")

col1, col2, col3, col4 = st.columns(4)

with col1:
    length_filter = st.selectbox("Length", options=["All"] + sorted(df["length"].dropna().unique().astype(str)), index=0)
with col3:
    keep_filter = st.selectbox("Keep for Dish", options=["All", "Yes", "No"], index=0)
with col4:
    saved_by_filter = st.selectbox("Saved By", options=["All"] + sorted(df["saved_by"].dropna().unique()), index=0)

# Apply filters
filtered = df.copy()

if search_term:
    filtered = filtered[filtered["keyword"].str.contains(search_term, case=False, na=False)]
if length_filter != "All":
    filtered = filtered[filtered["length"].astype(str) == length_filter]
if keep_filter == "Yes":
    filtered = filtered[filtered["Keep for Dish"] == True]
elif keep_filter == "No":
    filtered = filtered[filtered["Keep for Dish"] == False]
if saved_by_filter != "All":
    filtered = filtered[filtered["saved_by"] == saved_by_filter]

page = st.number_input("Page", min_value=1, value=1, step=1)
page_size = 50
start = (page - 1) * page_size
end = start + page_size
page_df = filtered.iloc[start:end].copy()


# Add CSS for zebra striping
st.markdown("""
<style>
div[data-testid="column"] > div:nth-child(even) {
    background-color: #f9f9f9;
}
</style>
""", unsafe_allow_html=True)

# Table Headers
header_cols = st.columns([0.1, 0.5, 0.2, 0.2])
with header_cols[0]: st.markdown("**Keep**")
with header_cols[1]: st.markdown("**Keyword**")
with header_cols[2]: st.markdown("**Length**")
with header_cols[3]: st.markdown("**Comments**")

# Table Rows
for i, row in page_df.iterrows():
    cols = st.columns([0.1, 0.5, 0.2, 0.2])
    with cols[0]:
        checked = st.checkbox("", key=f"cb_{i}", value=row.get("Keep for Dish", False), disabled=not username)
    with cols[1]:
        st.write(row["keyword"])
    with cols[2]:
        st.write(row.get("length", ""))
    with cols[3]:
        st.write(row.get("comments", ""))

    # Auto-save if checkbox changed
    if checked != row.get("Keep for Dish", False) and username:
        df.at[i, "Keep for Dish"] = checked
        df.at[i, "saved_by"] = username if checked else ""
        save_data(df)
        st.session_state[f"saved_{i}"] = True

    # Show save confirmation only once
    if st.session_state.get(f"saved_{i}", False):
        st.success(f"✅ '{row['keyword']}' saved by {username}")



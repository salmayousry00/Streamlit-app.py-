import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Instant Business Data Explorer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Instant Data Intelligence & Business Analytics Platform")
st.markdown("Transform raw CSV/Excel business records into interactive dashboards, KPI metrics, and visual insights in seconds.")

st.sidebar.header("Data Control Panel")
uploaded_file = st.sidebar.file_uploader("Upload Business Dataset (CSV or Excel)", type=["csv", "xlsx"])

@st.cache_data
def load_sample_data():
    np.random.seed(42)
    categories = ["Electronics", "Fashion", "Home & Kitchen", "Books", "Sports"]
    regions = ["North", "South", "East", "West"]
    n_records = 250
    return pd.DataFrame({
        "Transaction_ID": [f"TXN-{1000 + i}" for i in range(n_records)],
        "Region": np.random.choice(regions, n_records),
        "Product_Category": np.random.choice(categories, n_records),
        "Sales_Amount": np.random.uniform(20.0, 500.0, n_records).round(2),
        "Discount_Pct": np.random.uniform(0.0, 30.0, n_records).round(1),
        "Customer_Rating": np.random.randint(1, 6, n_records),
        "Quantity_Sold": np.random.randint(1, 15, n_records)
    })

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.sidebar.success("File uploaded successfully!")
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()
else:
    df = load_sample_data()
    st.sidebar.info("Using embedded demo e-commerce dataset. Upload your file to analyze custom data.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Records", f"{len(df):,}")
with col2:
    st.metric("Total Variables", f"{df.shape[1]}")
with col3:
    st.metric("Missing Values", f"{df.isna().sum().sum()}")
with col4:
    st.metric("Duplicates", f"{df.duplicated().sum()}")

tab1, tab2, tab3, tab4 = st.tabs(["📋 Data Preview", "📈 Numerical Analytics", "📊 Category Analysis", "⚙️ Data Filtering & Export"])

with tab1:
    st.subheader("Dataset Structure & Top Records")
    st.dataframe(df.head(20), use_container_width=True)
    st.subheader("Statistical Summary")
    st.dataframe(df.describe().T, use_container_width=True)

with tab2:
    st.subheader("Numerical Distribution & Correlation")
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) >= 1:
        selected_metric = st.selectbox("Select Metric for Distribution", numeric_cols)
        fig_dist = px.histogram(df, x=selected_metric, nbins=30, marginal="box", color_discrete_sequence=["#1967D2"])
        st.plotly_chart(fig_dist, use_container_width=True)

        if len(numeric_cols) >= 2:
            st.subheader("Correlation Heatmap")
            corr_matrix = df[numeric_cols].corr()
            fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto", color_continuous_scale="Blues")
            st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.warning("No numeric columns found in the dataset.")

with tab3:
    st.subheader("Categorical Breakdown & Aggregations")
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if cat_cols and numeric_cols:
        cat_select = st.selectbox("Group By Category", cat_cols)
        num_select = st.selectbox("Aggregate Value", numeric_cols)
        grouped_df = df.groupby(cat_select)[num_select].sum().reset_index()
        fig_bar = px.bar(grouped_df, x=cat_select, y=num_select, color=num_select, color_continuous_scale="Viridis")
        st.plotly_chart(fig_bar, use_container_width=True)
    elif cat_cols:
        cat_select = st.selectbox("Select Column to Count", cat_cols)
        fig_count = px.bar(df[cat_select].value_counts().reset_index(), x=cat_select, y="count", color_discrete_sequence=["#2b5c8f"])
        st.plotly_chart(fig_count, use_container_width=True)
    else:
        st.warning("No categorical columns available.")

with tab4:
    st.subheader("Filter and Download Processed Records")
    if numeric_cols:
        filter_col = st.selectbox("Filter Metric", numeric_cols, key="filter_metric")
        min_val = float(df[filter_col].min())
        max_val = float(df[filter_col].max())
        val_range = st.slider("Select Range", min_val, max_val, (min_val, max_val))
        filtered_df = df[(df[filter_col] >= val_range[0]) & (df[filter_col] <= val_range[1])]
    else:
        filtered_df = df

    st.write(f"Filtered Records: {len(filtered_df)}")
    st.dataframe(filtered_df.head(10), use_container_width=True)

    csv_data = filtered_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 Download Filtered Dataset as CSV",
        data=csv_data,
        file_name="processed_business_data.csv",
        mime="text/csv"
    )

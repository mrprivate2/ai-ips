import streamlit as st
import pandas as pd
import os
import plotly.express as px
import time

st.set_page_config(layout="wide")

st.title("🧠 AI Model Learning & Training")

DATASET = "logs/live_training_data.csv"


# =============================
# SAFE DATA LOADER (🔥 FIX)
# =============================

def load_dataset_safe(path):
    try:
        df = pd.read_csv(
            path,
            on_bad_lines="skip",   # ✅ skip corrupted rows
            engine="python"
        )

        # remove fully empty rows
        df.dropna(how="all", inplace=True)

        return df

    except Exception as e:
        st.error(f"Dataset load failed: {e}")
        return None


# =============================
# ACTION BUTTONS
# =============================

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Refresh Data"):
        st.rerun()

with col2:
    if st.button("🚀 Retrain Model"):
        st.info("Training started... check terminal output")
        os.system("ai-ips retrain")
        st.success("Model retraining triggered!")


# =============================
# DATASET CHECK
# =============================

if not os.path.exists(DATASET):
    st.info("Training dataset not created yet.")
    st.warning("Model is currently using base trained weights.")
    st.stop()


# =============================
# LOAD DATA (FIXED)
# =============================

df = load_dataset_safe(DATASET)

if df is None:
    st.error("Dataset corrupted beyond recovery.")
    st.stop()

if df.empty:
    st.warning("Dataset exists but contains no usable data.")
    st.stop()


# =============================
# BASIC METRICS
# =============================

total_samples = len(df)

normal_samples = 0
attack_samples = 0

if "label" in df.columns:
    normal_samples = len(df[df["label"].isin([0, "normal", "NORMAL"])])
    attack_samples = total_samples - normal_samples

imbalance_ratio = attack_samples / max(normal_samples, 1)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Samples", total_samples)
c2.metric("Normal", normal_samples)
c3.metric("Attacks", attack_samples)
c4.metric("⚠ Imbalance", round(imbalance_ratio, 2))

if imbalance_ratio > 3:
    st.warning("Dataset is highly imbalanced → model bias risk")

st.divider()


# =============================
# DATA QUALITY CHECK
# =============================

st.subheader("🧪 Data Quality")

missing = df.isnull().sum().sum()
duplicates = df.duplicated().sum()

q1, q2 = st.columns(2)

q1.metric("Missing Values", int(missing))
q2.metric("Duplicate Rows", int(duplicates))

if missing > 0:
    st.warning("Missing values detected → clean dataset")

if duplicates > 0:
    st.warning("Duplicate samples detected → may affect learning")

st.divider()


# =============================
# DATA GROWTH
# =============================

if "timestamp" in df.columns:

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    growth = (
        df.groupby(pd.Grouper(key="timestamp", freq="5Min"))
        .size()
        .reset_index(name="samples")
    )

    st.subheader("📈 Dataset Growth")

    fig_growth = px.line(
        growth,
        x="timestamp",
        y="samples",
        template="plotly_dark"
    )

    st.plotly_chart(fig_growth, use_container_width=True)

st.divider()


# =============================
# LABEL DISTRIBUTION
# =============================

if "label" in df.columns:

    st.subheader("📊 Label Distribution")

    label_counts = df["label"].astype(str).value_counts().reset_index()
    label_counts.columns = ["label", "count"]

    fig = px.bar(
        label_counts,
        x="label",
        y="count",
        template="plotly_dark",
        color="label"
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()


# =============================
# FEATURE CORRELATION
# =============================

st.subheader("🔬 Feature Correlation")

numeric_df = df.select_dtypes(include=["int64", "float64"])

if not numeric_df.empty:

    corr = numeric_df.corr()

    fig_corr = px.imshow(
        corr,
        text_auto=True,
        template="plotly_dark"
    )

    st.plotly_chart(fig_corr, use_container_width=True)

    high_corr = (corr.abs() > 0.9).sum().sum() - len(corr)

    if high_corr > 0:
        st.warning("Highly correlated features detected → redundancy possible")

else:
    st.info("Not enough numeric data for correlation analysis.")

st.divider()


# =============================
# FEATURE PREVIEW
# =============================

st.subheader("📦 Feature Columns")

st.code(list(df.columns))


# =============================
# RECENT DATA
# =============================

st.subheader("🧾 Recent Samples")

st.dataframe(df.tail(20), use_container_width=True)

st.divider()


# =============================
# MODEL STATUS
# =============================

st.subheader("🤖 Model Status")

model_path = "src/models/saved/supervised_model.pkl"

if os.path.exists(model_path):

    modified_time = time.ctime(os.path.getmtime(model_path))

    st.success(f"Model available ✅\nLast trained: {modified_time}")

else:
    st.error("Model not found ❌")
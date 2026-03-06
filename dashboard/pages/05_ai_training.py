import streamlit as st
import pandas as pd
import os
import plotly.express as px

st.set_page_config(layout="wide")

st.title("🧠 AI Model Self-Learning")

# =============================
# REFRESH BUTTON
# =============================

if st.button("🔄 Refresh Training Data"):
    st.rerun()

DATASET = "logs/live_training_data.csv"

# =============================
# DATASET NOT FOUND
# =============================

if not os.path.exists(DATASET):

    st.info("Training dataset not created yet.")
    st.warning("AI model is currently using the base trained model.")
    st.stop()

# =============================
# LOAD DATASET
# =============================

try:
    df = pd.read_csv(DATASET)
except Exception:
    st.error("Training dataset corrupted.")
    st.stop()

# =============================
# EMPTY DATASET
# =============================

if df.empty:
    st.info("Training dataset exists but no samples collected yet.")
    st.stop()

# =============================
# TRAINING METRICS
# =============================

total_samples = len(df)

normal_samples = 0
attack_samples = 0

if "label" in df.columns:

    # Support numeric OR text labels
    normal_samples = len(df[df["label"].isin([0, "normal", "NORMAL"])])
    attack_samples = len(df) - normal_samples

c1, c2, c3 = st.columns(3)

c1.metric("Training Samples", total_samples)
c2.metric("Normal Traffic", normal_samples)
c3.metric("Attack Samples", attack_samples)

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
        color="label",
        labels={
            "label": "Traffic Type",
            "count": "Samples"
        }
    )

    st.plotly_chart(fig, width="stretch")

else:
    st.info("No label column found in dataset.")

st.divider()

# =============================
# RECENT TRAINING DATA
# =============================

st.subheader("🧾 Recent Training Samples")

st.dataframe(
    df.tail(20),
    width="stretch"
)

st.divider()

# =============================
# FEATURE PREVIEW
# =============================

st.subheader("🔬 Feature Preview")

st.write("Dataset Columns:")

st.code(list(df.columns))
import pandas as pd


def top_attackers(df):

    # ============================
    # VALIDATION
    # ============================

    if df.empty or "source_ip" not in df.columns:
        return pd.DataFrame()

    df = df.copy()

    # ============================
    # SAFE COLUMNS
    # ============================

    if "attack_type" not in df.columns:
        df["attack_type"] = "UNKNOWN"

    if "risk_level" not in df.columns:
        df["risk_level"] = "LOW"

    # ============================
    # SEVERITY RANKING
    # ============================

    severity_rank = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4
    }

    df["severity_score"] = df["risk_level"].map(severity_rank).fillna(1)

    # ============================
    # GROUP DATA (OPTIMIZED)
    # ============================

    grouped = df.groupby("source_ip")

    leaderboard = grouped.agg(
        Attacks=("source_ip", "size"),
        Top_Attack=("attack_type", lambda x: x.value_counts().index[0]),
        Max_Severity=("severity_score", "max")
    ).reset_index()

    # ============================
    # ANOMALY DETECTION
    # ============================

    anomaly_ips = []

    if "attack_type" in df.columns:
        anomaly_ips = df[df["attack_type"] == "UNKNOWN_THREAT"]["source_ip"].unique()

    leaderboard["Anomaly"] = leaderboard["source_ip"].isin(anomaly_ips)

    # ============================
    # THREAT SCORE (IMPROVED)
    # ============================

    leaderboard["Threat Score"] = (
        leaderboard["Attacks"] * 0.5 +
        leaderboard["Max_Severity"] * 2 +
        leaderboard["Anomaly"].astype(int) * 3
    )

    # ============================
    # SEVERITY LABEL
    # ============================

    reverse_severity = {v: k for k, v in severity_rank.items()}

    leaderboard["Severity"] = leaderboard["Max_Severity"].map(
        reverse_severity
    ).fillna("LOW")

    # ============================
    # SORTING
    # ============================

    leaderboard = leaderboard.sort_values(
        ["Threat Score", "Attacks"],
        ascending=False
    ).head(10)

    # ============================
    # FINAL FORMAT
    # ============================

    leaderboard = leaderboard.rename(columns={
        "source_ip": "Source IP",
        "Top_Attack": "Top Attack Type"
    })

    leaderboard = leaderboard[[
        "Source IP",
        "Attacks",
        "Top Attack Type",
        "Severity",
        "Anomaly",
        "Threat Score"
    ]]

    return leaderboard
import pandas as pd


def top_attackers(df):

    # ============================
    # VALIDATION
    # ============================

    if df.empty or "source_ip" not in df.columns:
        return pd.DataFrame()

    df = df.copy()

    # ============================
    # SAFE COLUMN HANDLING
    # ============================

    if "attack_type" not in df.columns:
        df["attack_type"] = "Unknown"

    if "risk_level" not in df.columns:
        df["risk_level"] = "Unknown"

    # ============================
    # AGGREGATE ATTACK DATA
    # ============================

    grouped = df.groupby("source_ip")

    leaderboard = pd.DataFrame({

        "Source IP": grouped.size(),

        "Attacks": grouped.size(),

        "Top Attack Type": grouped["attack_type"].agg(
            lambda x: x.value_counts().index[0] if not x.empty else "Unknown"
        ),

        "Highest Severity": grouped["risk_level"].agg(
            lambda x: x.value_counts().index[0] if not x.empty else "Unknown"
        )

    }).reset_index(drop=True)

    leaderboard = leaderboard.sort_values(
        "Attacks",
        ascending=False
    ).head(10)

    # ============================
    # FINAL CLEANUP
    # ============================

    leaderboard = leaderboard[[
        "Source IP",
        "Attacks",
        "Top Attack Type",
        "Highest Severity"
    ]]

    return leaderboard



# =============================
# REQUIRED KEYS
# =============================

REQUIRED_MODEL_CONFIG_KEYS = {
    "supervised_model_path": "Path to the supervised ML model (.pkl)",
    "unsupervised_model_path": "Path to the anomaly detection model (.pkl)",
    "scaler_path": "Path to the feature scaler (.pkl)",
    "weight_supervised": "Weight for supervised model score (0.0 - 1.0)",
    "weight_anomaly": "Weight for anomaly model score (0.0 - 1.0)",
    "warning_threshold": "Risk score threshold for WARNING events",
    "block_threshold": "Risk score threshold for BLOCKING an IP",
    "anomaly_threshold": "Anomaly score threshold for flagging as unknown threat",
}

REQUIRED_APP_CONFIG_KEYS = {
    "network_interface": "Network interface to monitor (e.g. en0, eth0)",
    "whitelist": "List of IP prefixes to ignore (e.g. 192.168.)",
    "debug": "Enable/disable debug logging (true/false)",
    "block_ttl": "How long to keep IPs blocked (seconds)",
    "log_file": "Path to the security events log file",
}


# =============================
# VALIDATE CONFIG
# =============================

def validate_config(config: dict, required_keys: dict, config_name: str) -> bool:
    """
    Validate that a config dict contains all required keys.
    Prints clear error messages for missing keys.
    Returns True if valid, False otherwise.
    """
    missing = []

    for key, description in required_keys.items():
        if key not in config:
            missing.append(f"  ❌ '{key}' — {description}")

    if missing:
        print(f"\n❌ [{config_name}] Missing required configuration keys:")
        for msg in missing:
            print(msg)
        print(f"\n👉 Add the missing keys to configs/{config_name.replace(' ', '_').lower()}.json")
        return False

    return True


def validate_model_config(config: dict) -> bool:
    """Validate model_config.json has all required keys."""
    return validate_config(config, REQUIRED_MODEL_CONFIG_KEYS, "model_config.json")


def validate_app_config(config: dict) -> bool:
    """Validate app_config.json has all required keys."""
    return validate_config(config, REQUIRED_APP_CONFIG_KEYS, "app_config.json")


# =============================
# THRESHOLD SANITY CHECKS
# =============================

def validate_thresholds(config: dict):
    """Validate that threshold values are sane (0-1 range, warning < block)."""
    warnings = []

    warning_threshold = config.get("warning_threshold", 0)
    block_threshold = config.get("block_threshold", 1)

    if not (0 <= warning_threshold <= 1):
        warnings.append(f"  ⚠️  warning_threshold ({warning_threshold}) should be between 0 and 1")

    if not (0 <= block_threshold <= 1):
        warnings.append(f"  ⚠️  block_threshold ({block_threshold}) should be between 0 and 1")

    if warning_threshold >= block_threshold:
        warnings.append(
            f"  ⚠️  warning_threshold ({warning_threshold}) should be < "
            f"block_threshold ({block_threshold})"
        )

    if warnings:
        print("\n⚠️  [model_config.json] Threshold warnings:")
        for msg in warnings:
            print(msg)
        # Warnings don't fail validation, just alert

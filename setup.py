from setuptools import setup, find_packages

setup(
    name="ai-ips",
    version="0.1.0",
    description="AI-powered Intrusion Prevention System",
    author="Sawan Yaduvanshi",

    packages=find_packages(),

    include_package_data=True,

    install_requires=[
        "streamlit",
        "scapy",
        "pandas",
        "numpy",
        "plotly",
        "requests",
        "psutil",
        "scikit-learn",
        "joblib",
        "typer"
    ],

    entry_points={
        "console_scripts": [
            "ai-ips=src.cli.cli:app"
        ]
    },

    python_requires=">=3.9",
)
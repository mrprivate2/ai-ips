from setuptools import setup, find_packages

setup(
    name="ai-ips",
    version="0.1.0",
    description="AI-powered Intrusion Prevention System (Real-time Network Security + ML Detection)",
    author="Sawan Yaduvanshi",
    license="MIT",

    packages=find_packages(exclude=("tests", "docs")),

    include_package_data=True,
    zip_safe=False,

    python_requires=">=3.9",

    install_requires=[
        "streamlit>=1.30.0",
        "scapy>=2.5.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "plotly>=5.18.0",
        "requests>=2.31.0",
        "psutil>=5.9.0",
        "scikit-learn>=1.3.0",
        "joblib>=1.3.0",
        "typer>=0.9.0",
        "fastapi>=0.110.0",
        "uvicorn>=0.27.0"
    ],

    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8"
        ]
    },

    entry_points={
        "console_scripts": [
            "ai-ips=src.cli.cli:app"
        ]
    },

    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: System :: Networking",
        "Intended Audience :: Developers",
    ],
)
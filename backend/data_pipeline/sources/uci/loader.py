from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[3]

UCI_V1_PATH = BASE_DIR / "online_retail_v1.csv"
UCI_V2_PATH = BASE_DIR / "online_retail_v2.csv"


def load_uci_online_retail() -> pd.DataFrame:
    """
    Load the two existing UCI Online Retail II source files.

    The original source files are read-only inputs.
    """

    if not UCI_V1_PATH.exists():
        raise FileNotFoundError(
            f"Missing source file: {UCI_V1_PATH}"
        )

    if not UCI_V2_PATH.exists():
        raise FileNotFoundError(
            f"Missing source file: {UCI_V2_PATH}"
        )

    df_v1 = pd.read_csv(UCI_V1_PATH)
    df_v2 = pd.read_csv(UCI_V2_PATH)

    return pd.concat(
        [df_v1, df_v2],
        ignore_index=True,
    )
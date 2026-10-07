from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[4]

UCI_RAW_DIR = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "raw"
    / "uci"
)

UCI_FILE_1 = UCI_RAW_DIR / "online_retail_v1.csv"
UCI_FILE_2 = UCI_RAW_DIR / "online_retail_v2.csv"


def read_uci_transactions() -> pd.DataFrame:
    """
    Read the two original UCI files.

    The original files are never modified.
    """

    missing_files = [
        str(path)
        for path in [UCI_FILE_1, UCI_FILE_2]
        if not path.exists()
    ]

    if missing_files:
        raise FileNotFoundError(
            "Required UCI files were not found: "
            + ", ".join(missing_files)
        )

    df1 = pd.read_csv(
        UCI_FILE_1,
        encoding="ISO-8859-1",
    )

    df2 = pd.read_csv(
        UCI_FILE_2,
        encoding="ISO-8859-1",
    )

    return pd.concat(
        [df1, df2],
        ignore_index=True,
    )

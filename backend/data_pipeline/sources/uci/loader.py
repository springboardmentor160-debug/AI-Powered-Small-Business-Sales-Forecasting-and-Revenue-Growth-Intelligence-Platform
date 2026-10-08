from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[4]

UCI_RAW_DIR = PROJECT_ROOT / "backend" / "data" / "raw" / "uci"
UCI_FILE_1 = UCI_RAW_DIR / "online_retail_v1.csv"
UCI_FILE_2 = UCI_RAW_DIR / "online_retail_v2.csv"


def read_uci_transactions() -> pd.DataFrame:
    """
    Read the two original UCI files without modifying them.

    Each row receives:
    - _source_row_id: stable row identifier
    - _source_system: source system identifier
    - _source_file: original source filename
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

    df1["_source_system"] = "UCI"
    df1["_source_file"] = UCI_FILE_1.name

    df2["_source_system"] = "UCI"
    df2["_source_file"] = UCI_FILE_2.name

    df = pd.concat(
        [df1, df2],
        ignore_index=True,
    )

    df["_source_row_id"] = range(len(df))

    return df
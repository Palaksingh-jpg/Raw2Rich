import pandas as pd
import os
import re
from datetime import datetime


def profile_suspicious_columns(df):
    """Find suspicious columns without changing the dataframe."""
    findings = []

    for col in df.columns:
        name = str(col).strip()
        normalized = name.lower()

        reasons = []

        if re.match(r"^unnamed(?::\s*\d+)?$", normalized):
            reasons.append(
                "Looks like an automatically generated index column"
            )

        if re.match(r"^unnamed_column_\d+$", normalized):
            reasons.append(
                "Looks like an automatically generated/unnamed column"
            )

        if normalized in {"index", "level_0"}:
            reasons.append(
                "Looks like a dataframe index column"
            )

        non_null = df[col].dropna()

        if (
            len(non_null) > 0
            and non_null.nunique(dropna=False) == 1
        ):
            reasons.append(
                "Contains only one unique value"
            )

        if reasons:
            findings.append({
                "column": name,
                "reasons": reasons,
                "sample_values": non_null.head(5).tolist(),
                "unique_values": int(
                    non_null.nunique(dropna=False)
                ),
            })

    return findings


def clean_data(
    filepath,
    output_dir=".",
    excluded_columns=None,
    rename_map=None
):
    """
    Clean a CSV after the user reviews suspicious columns.

    excluded_columns:
        Columns the user explicitly chose to exclude.

    rename_map:
        Dictionary containing:
        original column name -> new column name
    """

    excluded_columns = excluded_columns or []
    rename_map = rename_map or {}

    log = []

    log.append(
        f"Cleaning report for: {filepath}"
    )

    log.append(
        f"Generated on: "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )

    # ---------------------------------------------------------
    # STEP 1: LOAD CSV
    # ---------------------------------------------------------

    try:
        df = pd.read_csv(
            filepath,
            encoding="utf-8"
        )

        log.append(
            "Loaded file using UTF-8 encoding."
        )

    except UnicodeDecodeError:

        df = pd.read_csv(
            filepath,
            encoding="latin-1"
        )

        log.append(
            "UTF-8 failed. Loaded file using Latin-1 encoding instead."
        )

    raw_shape = df.shape

    log.append(
        f"Raw dataset shape: "
        f"{raw_shape[0]} rows, "
        f"{raw_shape[1]} columns\n"
    )

    # ---------------------------------------------------------
    # STEP 2: APPLY USER DECISIONS
    # ---------------------------------------------------------

    existing_excluded = [
        column
        for column in excluded_columns
        if column in df.columns
    ]

    if existing_excluded:

        df = df.drop(
            columns=existing_excluded
        )

        log.append(
            f"USER DECISION - Excluded columns: "
            f"{existing_excluded}"
        )

    else:

        log.append(
            "USER DECISION - Excluded columns: none"
        )

    valid_renames = {
        old: new.strip()
        for old, new in rename_map.items()
        if old in df.columns
        and str(new).strip()
    }

    if valid_renames:

        df = df.rename(
            columns=valid_renames
        )

        log.append(
            f"USER DECISION - Renamed columns: "
            f"{valid_renames}"
        )

    else:

        log.append(
            "USER DECISION - Renamed columns: none"
        )

    # ---------------------------------------------------------
    # STEP 3: HANDLE UNUSUAL COLUMN NAMES
    # ---------------------------------------------------------

    suspicious_cols = [
        col
        for col in df.columns
        if not str(col).isascii()
    ]

    if suspicious_cols:

        safe_names = {
            col: f"unnamed_column_{i + 1}"
            for i, col in enumerate(suspicious_cols)
        }

        df = df.rename(
            columns=safe_names
        )

        log.append(
            f"Renamed non-standard column names "
            f"for safety: {safe_names}"
        )

    else:

        log.append(
            "No non-standard column names found."
        )

    # ---------------------------------------------------------
    # STEP 4: STANDARDIZE COLUMN NAMES
    # ---------------------------------------------------------

    original_cols = list(df.columns)

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(
            r"[.\s]+",
            "_",
            regex=True
        )
        .str.replace(
            r"[^a-z0-9_]",
            "",
            regex=True
        )
    )

    log.append(
        "Standardized column names "
        "to lowercase_with_underscores."
    )

    log.append(
        f"Before: {original_cols}"
    )

    log.append(
        f"After: {list(df.columns)}\n"
    )

    # ---------------------------------------------------------
    # STEP 5: REMOVE DUPLICATES
    # ---------------------------------------------------------

    duplicates = int(
        df.duplicated().sum()
    )

    df = df.drop_duplicates()

    log.append(
        f"Duplicate rows found and removed: "
        f"{duplicates}"
    )

    # ---------------------------------------------------------
    # STEP 6: TRIM TEXT
    # ---------------------------------------------------------

    text_cols = (
        df.select_dtypes(
            include="object"
        ).columns
    )

    for col in text_cols:

        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
        )

    log.append(
        f"Trimmed extra whitespace in "
        f"{len(text_cols)} text column(s)."
    )

    # ---------------------------------------------------------
    # STEP 7: CONVERT DATE COLUMNS
    # ---------------------------------------------------------

    date_cols = []

    for col in df.columns:

        if "date" in col.lower():

            converted = pd.to_datetime(
                df[col],
                errors="coerce"
            )

            if (
                converted.notna().sum()
                > 0.5 * len(df)
            ):

                df[col] = converted

                date_cols.append(col)

    log.append(
        "Converted to proper date format: "
        f"{date_cols if date_cols else 'none found'}"
    )

    # ---------------------------------------------------------
    # STEP 8: CONVERT NUMBERS STORED AS TEXT
    # ---------------------------------------------------------

    numeric_fixed = []

    for col in text_cols:

        if (
            col not in date_cols
            and col in df.columns
        ):

            converted = pd.to_numeric(
                df[col],
                errors="coerce"
            )

            if (
                converted.notna().sum()
                > 0.9 * len(df)
            ):

                df[col] = converted

                numeric_fixed.append(col)

    log.append(
        "Converted text to numbers: "
        f"{numeric_fixed if numeric_fixed else 'none found'}"
    )

    # ---------------------------------------------------------
    # STEP 9: HANDLE MISSING VALUES
    # ---------------------------------------------------------

    missing_before = df.isna().sum()

    missing_cols = (
        missing_before[
            missing_before > 0
        ]
    )

    for col in missing_cols.index:

        if pd.api.types.is_numeric_dtype(
            df[col]
        ):

            fill_value = df[col].median()

            df[col] = df[col].fillna(
                fill_value
            )

            log.append(
                f"Filled missing values in "
                f"'{col}' with median: "
                f"{fill_value}"
            )

        elif pd.api.types.is_datetime64_any_dtype(
            df[col]
        ):

            log.append(
                f"Left missing dates in "
                f"'{col}' blank because a "
                f"date cannot safely be guessed."
            )

        else:

            df[col] = df[col].fillna(
                "Unknown"
            )

            log.append(
                f"Filled missing values in "
                f"'{col}' with 'Unknown'"
            )

    if len(missing_cols) == 0:

        log.append(
            "No missing values found."
        )

    # ---------------------------------------------------------
    # STEP 10: STANDARDIZE CATEGORIES
    # ---------------------------------------------------------

    for col in text_cols:

        if (
            col in df.columns
            and df[col].nunique() < 50
        ):

            df[col] = (
                df[col]
                .astype(str)
                .str.title()
            )

    log.append(
        "Standardized capitalization "
        "in likely categorical columns.\n"
    )

    # ---------------------------------------------------------
    # STEP 11: SAVE CLEANED FILE
    # ---------------------------------------------------------

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    base_name = os.path.splitext(
        os.path.basename(filepath)
    )[0]

    output_path = os.path.join(
        output_dir,
        f"{base_name}_cleaned.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    clean_shape = df.shape

    log.append(
        f"Final cleaned shape: "
        f"{clean_shape[0]} rows, "
        f"{clean_shape[1]} columns"
    )

    log.append(
        f"Cleaned file saved as: "
        f"{output_path}"
    )

    # ---------------------------------------------------------
    # STEP 12: SAVE CLEANING REPORT
    # ---------------------------------------------------------

    report_path = os.path.join(
        output_dir,
        f"{base_name}_cleaning_report.txt"
    )

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n".join(log)
        )

    return (
        df,
        output_path,
        report_path,
        log
    )
import pandas as pd
import sys
import os
from datetime import datetime

def clean_data(filepath):
    """
    Cleans ANY CSV file automatically — no manual editing required.
    Generates:
      1. A cleaned CSV file
      2. A documentation report of what was done
    """

    log = []  # collects every action for the documentation report
    log.append(f"Cleaning report for: {filepath}")
    log.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # ---- Step 1: Load the file (auto-detect encoding) ----
    try:
        df = pd.read_csv(filepath, encoding="utf-8")
        log.append("Loaded file using UTF-8 encoding.")
    except UnicodeDecodeError:
        df = pd.read_csv(filepath, encoding="latin-1")
        log.append("UTF-8 failed. Loaded file using Latin-1 encoding instead.")

    raw_shape = df.shape
    log.append(f"Raw dataset shape: {raw_shape[0]} rows, {raw_shape[1]} columns\n")

    # ---- Step 2: Flag columns with unusual/unreadable names (do NOT auto-delete) ----
    suspicious_cols = [col for col in df.columns if not str(col).isascii()]
    if suspicious_cols:
        log.append(f"WARNING: Found column(s) with non-standard characters in their name: {suspicious_cols}")
        log.append("These were NOT deleted. Review them manually — they may contain valid data.")
        # Rename them to something safe and traceable instead of deleting
        rename_map = {col: f"unnamed_column_{i+1}" for i, col in enumerate(suspicious_cols)}
        df = df.rename(columns=rename_map)
        log.append(f"Renamed for safety: {rename_map}")
    else:
        log.append("No columns with unusual names found.")

    # ---- Step 3: Standardize column names ----
    original_cols = list(df.columns)
    df.columns = (df.columns.astype(str).str.strip()
                  .str.lower()
                  .str.replace(r"[.\s]+", "_", regex=True)
                  .str.replace(r"[^a-z0-9_]", "", regex=True))
    log.append("Standardized column names to lowercase_with_underscores.")
    log.append(f"  Before: {original_cols}")
    log.append(f"  After:  {list(df.columns)}\n")

    # ---- Step 4: Remove duplicate rows ----
    dupes = df.duplicated().sum()
    df = df.drop_duplicates()
    log.append(f"Duplicate rows found and removed: {dupes}")

    # ---- Step 5: Trim whitespace from all text columns ----
    text_cols = df.select_dtypes(include="object").columns
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()
    log.append(f"Trimmed extra whitespace in {len(text_cols)} text column(s).")

    # ---- Step 6: Auto-detect and convert date columns ----
    date_cols = []
    for col in df.columns:
        if "date" in col.lower():
            converted = pd.to_datetime(df[col], errors="coerce")
            if converted.notna().sum() > 0.5 * len(df):
                df[col] = converted
                date_cols.append(col)
    log.append(f"Converted to proper date format: {date_cols if date_cols else 'none found'}")

    # ---- Step 7: Auto-detect numbers stored as text ----
    numeric_fixed = []
    for col in text_cols:
        if col not in date_cols:
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.notna().sum() > 0.9 * len(df):
                df[col] = converted
                numeric_fixed.append(col)
    log.append(f"Converted text to numbers: {numeric_fixed if numeric_fixed else 'none found'}")

    # ---- Step 8: Handle missing values ----
    missing_before = df.isna().sum()
    missing_cols = missing_before[missing_before > 0]

    for col in missing_cols.index:
        if pd.api.types.is_numeric_dtype(df[col]):
            fill_value = df[col].median()
            df[col] = df[col].fillna(fill_value)
            log.append(f"Filled missing values in '{col}' (numeric) with median: {fill_value}")
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            log.append(f"Left missing dates in '{col}' as blank (cannot guess a date).")
        else:
            df[col] = df[col].fillna("Unknown")
            log.append(f"Filled missing values in '{col}' (text) with 'Unknown'")

    if len(missing_cols) == 0:
        log.append("No missing values found.")

    # ---- Step 9: Standardize text casing in likely categorical columns ----
    for col in text_cols:
        if col in df.columns and df[col].nunique() < 50:
            df[col] = df[col].astype(str).str.title()
    log.append("Standardized capitalization in likely categorical columns.\n")

    # ---- Step 10: Save cleaned file ----
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    output_path = f"{base_name}_cleaned.csv"
    df.to_csv(output_path, index=False)

    clean_shape = df.shape
    log.append(f"Final cleaned shape: {clean_shape[0]} rows, {clean_shape[1]} columns")
    log.append(f"Cleaned file saved as: {output_path}")

    # ---- Save the documentation report ----
    report_path = f"{base_name}_cleaning_report.txt"
    with open(report_path, "w") as f:
        f.write("\n".join(log))

    print("\n".join(log))
    print(f"\nDocumentation report saved as: {report_path}")

    return df


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        filepath = sys.argv[1]
    else:
        filepath = input("Enter the CSV file name to clean (must be in this same folder): ").strip()
    clean_data(filepath)
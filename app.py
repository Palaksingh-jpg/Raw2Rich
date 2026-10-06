import os
import tempfile

import pandas as pd
import streamlit as st

from clean import (
    clean_data,
    profile_suspicious_columns
)


# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="Raw2Rich",
    page_icon="🚀",
    layout="wide"
)


# =========================================================
# HEADER
# =========================================================

st.title("🚀 Raw2Rich")

st.subheader(
    "Turn messy CSV data into trusted insights"
)

st.write(
    "Upload a messy CSV. Raw2Rich profiles the file first, "
    "flags potential data-quality issues, and lets you "
    "review them before cleaning."
)


# =========================================================
# UPLOAD
# =========================================================

uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)


if uploaded_file is not None:

    # =====================================================
    # READ FILE FOR INITIAL PROFILING
    # =====================================================

    try:

        uploaded_file.seek(0)

        try:

            raw_df = pd.read_csv(
                uploaded_file,
                encoding="utf-8"
            )

        except UnicodeDecodeError:

            uploaded_file.seek(0)

            raw_df = pd.read_csv(
                uploaded_file,
                encoding="latin-1"
            )

    except Exception as e:

        st.error(
            f"Could not read this CSV: {e}"
        )

        st.stop()


    st.success(
        f"File uploaded: {uploaded_file.name}"
    )


    # =====================================================
    # DATA QUALITY REVIEW
    # =====================================================

    findings = profile_suspicious_columns(
        raw_df
    )

    st.divider()

    st.header(
        "🔍 Data Quality Review"
    )

    excluded_columns = []

    rename_map = {}


    # =====================================================
    # SUSPICIOUS COLUMN FOUND
    # =====================================================

    if findings:

        st.warning(
            f"Raw2Rich found {len(findings)} "
            f"potentially suspicious column(s). "
            f"Please review them before cleaning."
        )

        st.info(
            "Raw2Rich will NOT automatically delete "
            "suspicious columns. You decide what should "
            "happen to them."
        )


        for i, finding in enumerate(findings):

            column = finding["column"]


            with st.container(
                border=True
            ):

                st.markdown(
                    f"### ⚠️ Suspicious column: `{column}`"
                )


                st.write(
                    "**Why was it flagged?**"
                )


                for reason in finding["reasons"]:

                    st.write(
                        f"- {reason}"
                    )


                st.write(
                    f"**Unique values:** "
                    f"{finding['unique_values']}"
                )


                sample_text = ", ".join(
                    repr(value)
                    for value
                    in finding["sample_values"]
                )


                st.write(
                    f"**Sample values:** "
                    f"{sample_text}"
                )


                # -----------------------------------------
                # USER DECISION
                # -----------------------------------------

                choice = st.radio(
                    "What should Raw2Rich do with this column?",
                    [
                        "Keep column",
                        "Exclude column",
                        "Rename column"
                    ],
                    key=f"decision_{i}"
                )


                # -----------------------------------------
                # EXCLUDE
                # -----------------------------------------

                if choice == "Exclude column":

                    excluded_columns.append(
                        column
                    )


                # -----------------------------------------
                # RENAME
                # -----------------------------------------

                elif choice == "Rename column":

                    new_name = st.text_input(
                        "Enter the new column name",
                        value=column,
                        key=f"rename_{i}"
                    ).strip()


                    if new_name:

                        rename_map[
                            column
                        ] = new_name


    # =====================================================
    # NO SUSPICIOUS COLUMN
    # =====================================================

    else:

        st.success(
            "✅ No obvious suspicious columns were detected."
        )


    # =====================================================
    # CLEAN BUTTON
    # =====================================================

    st.divider()


    if st.button(
        "🚀 Continue with Cleaning",
        type="primary"
    ):


        # =================================================
        # VALIDATE RENAME DECISIONS
        # =================================================

        for old_name, new_name in rename_map.items():

            if old_name == new_name:

                st.error(
                    f"Please enter a different name "
                    f"for `{old_name}`."
                )

                st.stop()


        rename_targets = list(
            rename_map.values()
        )


        if len(rename_targets) != len(
            set(rename_targets)
        ):

            st.error(
                "Two columns cannot be renamed "
                "to the same name."
            )

            st.stop()


        # =================================================
        # TEMPORARY FILE
        # =================================================

        with tempfile.TemporaryDirectory() as temp_dir:

            input_path = os.path.join(
                temp_dir,
                uploaded_file.name
            )


            uploaded_file.seek(0)


            with open(
                input_path,
                "wb"
            ) as f:

                f.write(
                    uploaded_file.getbuffer()
                )


            # =============================================
            # CLEAN DATA
            # =============================================

            with st.spinner(
                "Cleaning and validating your data..."
            ):

                try:

                    (
                        cleaned_df,
                        cleaned_path,
                        report_path,
                        log
                    ) = clean_data(
                        input_path,
                        output_dir=temp_dir,
                        excluded_columns=excluded_columns,
                        rename_map=rename_map
                    )


                except Exception as e:

                    st.error(
                        f"Cleaning failed: {e}"
                    )

                    st.stop()


        # =================================================
        # SAVE RESULTS IN SESSION
        # =================================================

        st.session_state[
            "cleaned_df"
        ] = cleaned_df


        st.session_state[
            "cleaned_bytes"
        ] = (
            cleaned_df
            .to_csv(index=False)
            .encode("utf-8")
        )


        st.session_state[
            "cleaning_report"
        ] = (
            "\n".join(log)
            .encode("utf-8")
        )


        st.session_state[
            "excluded_columns"
        ] = excluded_columns


        st.session_state[
            "rename_map"
        ] = rename_map


        st.success(
            "✅ Data cleaning completed successfully!"
        )


    # =====================================================
    # RESULTS
    # =====================================================

    if "cleaned_df" in st.session_state:

        df = st.session_state[
            "cleaned_df"
        ]


        st.header(
            "✅ Data Quality"
        )


        col1, col2, col3 = st.columns(3)


        col1.metric(
            "Rows",
            f"{len(df):,}"
        )


        col2.metric(
            "Columns",
            f"{len(df.columns):,}"
        )


        col3.metric(
            "Missing Values",
            f"{int(df.isna().sum().sum()):,}"
        )


        # =================================================
        # DOWNLOADS
        # =================================================

        download_col1, download_col2 = st.columns(2)


        with download_col1:

            st.download_button(
                "⬇️ Download Cleaned CSV",
                data=st.session_state[
                    "cleaned_bytes"
                ],
                file_name="raw2rich_cleaned.csv",
                mime="text/csv"
            )


        with download_col2:

            st.download_button(
                "📄 Download Cleaning Report",
                data=st.session_state[
                    "cleaning_report"
                ],
                file_name="raw2rich_cleaning_report.txt",
                mime="text/plain"
            )


        # =================================================
        # USER DECISIONS
        # =================================================

        st.subheader(
            "📋 Cleaning Decisions"
        )


        excluded = st.session_state[
            "excluded_columns"
        ]


        renamed = st.session_state[
            "rename_map"
        ]


        if excluded:

            st.write(
                "**Excluded:** "
                + ", ".join(
                    f"`{column}`"
                    for column in excluded
                )
            )

        else:

            st.write(
                "**Excluded:** None"
            )


        if renamed:

            st.write(
                "**Renamed:** "
                + ", ".join(
                    f"`{old}` → `{new}`"
                    for old, new
                    in renamed.items()
                )
            )

        else:

            st.write(
                "**Renamed:** None"
            )


        # =================================================
        # DASHBOARD
        # =================================================

        st.divider()

        st.header(
            "📊 Raw2Rich Dashboard"
        )


        required_columns = {
            "sales",
            "profit",
            "quantity",
            "order_id"
        }


        if required_columns.issubset(
            df.columns
        ):


            # =============================================
            # KPI CALCULATIONS
            # =============================================

            total_sales = df[
                "sales"
            ].sum()


            total_profit = df[
                "profit"
            ].sum()


            total_quantity = df[
                "quantity"
            ].sum()


            total_orders = df[
                "order_id"
            ].nunique()


            # =============================================
            # KPI CARDS
            # =============================================

            col1, col2, col3, col4 = st.columns(4)


            col1.metric(
                "Total Sales",
                f"{total_sales:,.0f}"
            )


            col2.metric(
                "Total Profit",
                f"{total_profit:,.0f}"
            )


            col3.metric(
                "Total Quantity",
                f"{total_quantity:,.0f}"
            )


            col4.metric(
                "Total Orders",
                f"{total_orders:,.0f}"
            )


            # =============================================
            # SALES BY CATEGORY
            # =============================================

            if "category" in df.columns:

                st.subheader(
                    "Sales by Category"
                )


                category_sales = (
                    df.groupby(
                        "category"
                    )["sales"]
                    .sum()
                    .sort_values(
                        ascending=False
                    )
                )


                st.bar_chart(
                    category_sales
                )


            # =============================================
            # SALES BY REGION
            # =============================================

            if "region" in df.columns:

                st.subheader(
                    "Sales by Region"
                )


                region_sales = (
                    df.groupby(
                        "region"
                    )["sales"]
                    .sum()
                    .sort_values(
                        ascending=False
                    )
                )


                st.bar_chart(
                    region_sales
                )


            # =============================================
            # PROFIT BY CATEGORY
            # =============================================

            if "category" in df.columns:

                st.subheader(
                    "Profit by Category"
                )


                category_profit = (
                    df.groupby(
                        "category"
                    )["profit"]
                    .sum()
                    .sort_values(
                        ascending=False
                    )
                )


                st.bar_chart(
                    category_profit
                )


        else:

            st.info(
                "This dataset does not contain the "
                "Superstore KPI columns. The cleaned "
                "dataset is still available for download."
            )


        # =================================================
        # CLEANED DATA PREVIEW
        # =================================================

        st.subheader(
            "🧹 Cleaned Data Preview"
        )


        st.dataframe(
            df.head(20),
            use_container_width=True
        )
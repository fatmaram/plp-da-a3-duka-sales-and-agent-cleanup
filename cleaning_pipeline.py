import pandas as pd


def clean_agent_data(txns, agents):
    """Clean the mobile money transaction extract and merge the agent register.

    Rules applied in order:
      1. Standardise text fields (trim spaces, fix case)
      2. Remove duplicate transactions (exact copies, then repeated txn_id)
      3. Standardise txn_type to Deposit or Withdrawal
      4. Convert amount to numeric (missing and invalid values become NaN)
      5. Convert txn_date to datetime (slashes become dashes first)
      6. Flag outliers with the IQR method on observed amounts
      7. Flag and impute missing amounts with the median of observed amounts
      8. Left join the agent register (validate many_to_one)

    Parameters
    ----------
    txns : DataFrame with txn_id, agent_id, txn_type, amount, txn_date
    agents : DataFrame with agent_id, county, onboarded

    Returns
    -------
    (clean_df, log) : the clean DataFrame and a list of log lines.
    """
    log = []
    out = txns.copy()
    reg = agents.copy()
    log.append(f"Start: {len(out)} transaction rows and {len(reg)} agents")

    # 1. Standardise text fields
    out["agent_id"] = out["agent_id"].astype(str).str.strip().str.upper()
    out["txn_id"] = out["txn_id"].astype(str).str.strip()
    reg["agent_id"] = reg["agent_id"].astype(str).str.strip().str.upper()

    # 2. Duplicates: exact copies first, then repeated txn_id with different details
    before = len(out)
    out = out.drop_duplicates()
    log.append(f"Removed {before - len(out)} exact duplicate rows")

    before = len(out)
    out["_known"] = out["agent_id"].isin(reg["agent_id"])
    out = (out.sort_values("_known", ascending=False, kind="stable")
              .drop_duplicates(subset="txn_id", keep="first")
              .sort_index()
              .drop(columns="_known"))
    log.append(f"Removed {before - len(out)} repeated txn_id rows (kept the copy with a known agent)")

    # 3. Consistency: txn_type
    cleaned_type = out["txn_type"].astype(str).str.strip().str.lower()
    mapping = {"deposit": "Deposit", "withdrawal": "Withdrawal"}
    standard = cleaned_type.map(mapping)
    n_fixed = (standard != out["txn_type"]).sum()
    n_unmapped = standard.isna().sum()
    out["txn_type"] = standard
    log.append(f"Standardised {n_fixed} txn_type values to Deposit or Withdrawal ({n_unmapped} unmapped)")

    # 4. Validity: amount to numeric
    n_missing = out["amount"].isna().sum()
    text = out["amount"].astype(str).str.replace(",", "", regex=False).str.strip()
    numeric = pd.to_numeric(text, errors="coerce")
    n_invalid = (out["amount"].notna() & numeric.isna()).sum()
    out["amount"] = numeric
    log.append(f"Amount: {n_missing} missing (includes N/A read as missing) and {n_invalid} invalid text values set to NaN")

    # 5. Validity: txn_date to datetime
    raw_dates = out["txn_date"].astype(str).str.strip()
    n_slash = raw_dates.str.contains("/", regex=False).sum()
    out["txn_date"] = pd.to_datetime(raw_dates.str.replace("/", "-", regex=False),
                                     format="%Y-%m-%d", errors="coerce")
    n_bad_dates = out["txn_date"].isna().sum()
    log.append(f"Dates: converted {n_slash} slash dates to ISO format ({n_bad_dates} unreadable)")

    # 6. Outliers: IQR fences on observed amounts only
    q1, q3 = out["amount"].quantile([0.25, 0.75])
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    out["is_outlier"] = (out["amount"] < low) | (out["amount"] > high)
    log.append(f"Outliers: fences {low:,.0f} to {high:,.0f}, flagged {out['is_outlier'].sum()} rows for review")

    # 7. Completeness: flag first, then impute with the median
    out["amount_imputed"] = out["amount"].isna()
    median_amount = out["amount"].median()
    out["amount"] = out["amount"].fillna(median_amount)
    log.append(f"Imputed {out['amount_imputed'].sum()} amounts with the median {median_amount:,.2f} and set amount_imputed to True")

    # 8. Merge with the agent register
    rows_before = len(out)
    merged = out.merge(reg[["agent_id", "county", "onboarded"]], on="agent_id",
                       how="left", validate="many_to_one", indicator=True)
    merged["agent_known"] = merged["_merge"] == "both"
    merged = merged.drop(columns="_merge")
    n_unknown = (~merged["agent_known"]).sum()
    merged["county"] = merged["county"].fillna("Unknown")
    log.append(f"Merge: {rows_before} rows before and {len(merged)} after a left join; {n_unknown} rows have an unknown agent (county set to Unknown)")

    merged = merged.reset_index(drop=True)
    log.append(f"Finish: {len(merged)} clean rows")
    return merged, log
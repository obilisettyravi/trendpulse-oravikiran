"""
TrendPulse — Task 2: Clean the Data & Save as CSV
==================================================
Loads the JSON file produced by Task 1, applies a series of cleaning
steps, and saves the result as a tidy CSV file.

Pipeline:
  1. Load the latest JSON from data/ into a Pandas DataFrame
  2. Remove duplicates → drop nulls → fix types → filter low scores → strip whitespace
  3. Save cleaned data to data/trends_clean.csv and print a summary

Author : Obilisetti Ravi Kiran
"""

from __future__ import annotations

import glob
import os
import pandas as pd


# ── Step 1: Find and load the JSON file ───────────────────────────────────────

def find_latest_json(data_dir: str = "data") -> str:
    """
    Scan the data/ folder for files matching trends_*.json and return the
    path of the most recently dated one (sorted lexicographically — works
    because the filename format is YYYYMMDD).
    """
    pattern = os.path.join(data_dir, "trends_*.json")
    matches = sorted(glob.glob(pattern))  # sort ascending; last entry is newest
    if not matches:
        raise FileNotFoundError(
            f"No trends_*.json file found in '{data_dir}/'. "
            "Run task1_data_collection.py first."
        )
    return matches[-1]  # return the most recent file


def load_json(file_path: str) -> pd.DataFrame:
    """
    Load a JSON file (list of story dicts) into a Pandas DataFrame.
    Prints the number of rows loaded.
    """
    df = pd.read_json(file_path)
    print(f"Loaded {len(df)} stories from {file_path}")
    return df


# ── Step 2: Clean the DataFrame ───────────────────────────────────────────────

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply four cleaning steps in order and print the row count after each:

    1. Remove duplicate rows (same post_id).
    2. Drop rows where post_id, title, or score is missing/null.
    3. Cast score and num_comments to int (they may arrive as floats).
    4. Remove stories with score < 5 (low-quality / test posts).
    5. Strip leading/trailing whitespace from the title column.
    """

    # ── 2a. Remove duplicates on post_id ──────────────────────────────────
    df = df.drop_duplicates(subset="post_id")
    print(f"\nAfter removing duplicates: {len(df)}")

    # ── 2b. Drop rows with null post_id, title, or score ──────────────────
    df = df.dropna(subset=["post_id", "title", "score"])
    print(f"After removing nulls: {len(df)}")

    # ── 2c. Ensure numeric columns are proper integers ─────────────────────
    # Use Int64 (nullable integer) so any remaining NaN in num_comments
    # doesn't raise an error; then convert to plain int via fillna(0).
    df["score"]        = df["score"].fillna(0).astype(int)
    df["num_comments"] = df["num_comments"].fillna(0).astype(int)

    # ── 2d. Filter out stories with score < 5 ─────────────────────────────
    df = df[df["score"] >= 5]
    print(f"After removing low scores: {len(df)}")

    # ── 2e. Strip whitespace from the title column ────────────────────────
    df["title"] = df["title"].str.strip()

    return df


# ── Step 3: Save to CSV and print summary ─────────────────────────────────────

def save_to_csv(df: pd.DataFrame, output_path: str = "data/trends_clean.csv") -> None:
    """
    Save the cleaned DataFrame to a CSV file (no row index).
    Print a confirmation message and a per-category story count.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write CSV without the auto-generated integer row index
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\nSaved {len(df)} rows to {output_path}")

    # ── Per-category summary ───────────────────────────────────────────────
    print("\nStories per category:")
    counts = df["category"].value_counts()
    for category, count in counts.items():
        # Left-align category name in a 15-char column for neat formatting
        print(f"  {category:<15} {count}")


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Step 1 — load
    json_path = find_latest_json("data")
    df = load_json(json_path)

    # Step 2 — clean
    df = clean_data(df)

    # Step 3 — save
    save_to_csv(df, "data/trends_clean.csv")

"""
TrendPulse — Task 3: Analysis with Pandas & NumPy
==================================================
Loads the cleaned CSV from Task 2, explores the data, computes statistics
using NumPy, adds two derived columns, and saves the result as a new CSV
ready for visualisation in Task 4.

Pipeline:
  1. Load data/trends_clean.csv and print a basic overview
  2. Compute mean / median / std / max / min of score with NumPy
  3. Add 'engagement' and 'is_popular' columns
  4. Save the enriched DataFrame to data/trends_analysed.csv

Author : Obilisetti Ravi Kiran
"""

from __future__ import annotations

import numpy as np
import pandas as pd

INPUT_FILE  = "data/trends_clean.csv"
OUTPUT_FILE = "data/trends_analysed.csv"


# ── Step 1: Load and explore ───────────────────────────────────────────────────

def load_and_explore(file_path: str) -> pd.DataFrame:
    """
    Load the cleaned CSV into a DataFrame and print a quick overview:
    shape, first 5 rows, and overall average score / comment count.
    """
    df = pd.read_csv(file_path)

    print(f"Loaded data: {df.shape}")          # (rows, columns)

    print("\nFirst 5 rows:")
    print(df.head())                            # preview the data

    # Use pandas mean() for the summary averages
    avg_score    = df["score"].mean()
    avg_comments = df["num_comments"].mean()
    print(f"\nAverage score   : {avg_score:,.0f}")
    print(f"Average comments: {avg_comments:,.0f}")

    return df


# ── Step 2: NumPy statistics ───────────────────────────────────────────────────

def numpy_stats(df: pd.DataFrame) -> None:
    """
    Use NumPy functions to compute descriptive statistics on the score column
    and answer specific questions about the dataset.
    """
    scores = df["score"].to_numpy()             # convert Series to NumPy array

    mean_score   = np.mean(scores)
    median_score = np.median(scores)
    std_score    = np.std(scores)
    max_score    = np.max(scores)
    min_score    = np.min(scores)

    print("\n--- NumPy Stats ---")
    print(f"Mean score   : {mean_score:,.0f}")
    print(f"Median score : {median_score:,.0f}")
    print(f"Std deviation: {std_score:,.0f}")
    print(f"Max score    : {max_score:,.0f}")
    print(f"Min score    : {min_score:,.0f}")

    # Category with the most stories
    top_category       = df["category"].value_counts().idxmax()
    top_category_count = df["category"].value_counts().max()
    print(f"\nMost stories in: {top_category} ({top_category_count} stories)")

    # Story with the most comments
    most_commented_idx   = df["num_comments"].idxmax()
    most_commented_story = df.loc[most_commented_idx]
    print(
        f'\nMost commented story: "{most_commented_story["title"]}"'
        f'  — {most_commented_story["num_comments"]:,} comments'
    )


# ── Step 3: Add new columns ────────────────────────────────────────────────────

def add_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive two new columns:

    engagement — ratio of comments to (score + 1).
                 Adding 1 avoids division-by-zero for zero-score stories.
                 A high value means the story sparked lots of discussion
                 relative to its upvote count.

    is_popular — boolean flag; True when a story's score exceeds the
                 dataset-wide mean score.
    """
    avg_score = df["score"].mean()

    # How much discussion each upvote generates
    df["engagement"] = df["num_comments"] / (df["score"] + 1)

    # True / False whether the story is above-average in score
    df["is_popular"] = df["score"] > avg_score

    return df


# ── Step 4: Save to CSV ────────────────────────────────────────────────────────

def save_analysed(df: pd.DataFrame, output_path: str) -> None:
    """
    Save the enriched DataFrame (original 7 columns + 2 new ones) to CSV.
    """
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\nSaved to {output_path}")


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Step 1 — load and explore
    df = load_and_explore(INPUT_FILE)

    # Step 2 — NumPy statistics
    numpy_stats(df)

    # Step 3 — add derived columns
    df = add_columns(df)

    # Step 4 — save result
    save_analysed(df, OUTPUT_FILE)

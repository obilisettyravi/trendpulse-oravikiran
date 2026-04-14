"""
TrendPulse — Task 4: Visualizations
=====================================
Loads the analysed CSV from Task 3 and produces 4 PNG files:
  chart1_top_stories.png  — horizontal bar: top 10 stories by score
  chart2_categories.png   — bar chart: story count per category
  chart3_scatter.png      — scatter: score vs comments (popular vs not)
  dashboard.png           — all 3 charts combined in one figure (bonus)

Author : Obilisetti Ravi Kiran
"""

from __future__ import annotations

import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# Use non-interactive backend so no GUI window is required when saving PNGs
matplotlib.use("Agg")

INPUT_FILE = "data/trends_analysed.csv"
OUTPUT_DIR = "outputs"

# Consistent colour palette used across charts
CATEGORY_COLOURS = {
    "technology":    "#4C72B0",
    "worldnews":     "#DD8452",
    "sports":        "#55A868",
    "science":       "#C44E52",
    "entertainment": "#8172B2",
}


# ── Step 1: Setup ──────────────────────────────────────────────────────────────

def load_data(file_path: str) -> pd.DataFrame:
    """Load the analysed CSV and return a DataFrame."""
    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} rows from {file_path}")
    return df


def setup_output_dir(directory: str) -> None:
    """Create the outputs/ folder if it doesn't exist."""
    os.makedirs(directory, exist_ok=True)
    print(f"Output folder ready: {directory}/")


# ── Step 2: Chart 1 — Top 10 Stories by Score ─────────────────────────────────

def chart1_top_stories(df: pd.DataFrame) -> None:
    """
    Horizontal bar chart of the top 10 stories ranked by score.
    Titles longer than 50 characters are truncated with '…' so they
    fit neatly on the y-axis.
    """
    # Select the 10 highest-scoring stories, sorted ascending so the best
    # story appears at the top of the chart (matplotlib draws bottom-up)
    top10 = (
        df.nlargest(10, "score")
          .sort_values("score", ascending=True)
    )

    # Truncate long titles to keep the chart readable
    labels = [
        t if len(t) <= 50 else t[:47] + "…"
        for t in top10["title"]
    ]

    fig, ax = plt.subplots(figsize=(12, 6))

    # Map each bar's colour to the story's category
    colours = [CATEGORY_COLOURS.get(cat, "#888888") for cat in top10["category"]]
    bars = ax.barh(labels, top10["score"], color=colours)

    # Add score labels at the end of each bar for quick reading
    for bar, score in zip(bars, top10["score"]):
        ax.text(
            bar.get_width() + 5,
            bar.get_y() + bar.get_height() / 2,
            str(score),
            va="center", fontsize=8,
        )

    ax.set_title("Top 10 HackerNews Stories by Score", fontsize=14, fontweight="bold")
    ax.set_xlabel("Score (upvotes)")
    ax.set_ylabel("Story Title")
    ax.margins(x=0.12)          # leave room for the score labels on the right
    plt.tight_layout()

    out_path = os.path.join(OUTPUT_DIR, "chart1_top_stories.png")
    plt.savefig(out_path, dpi=150)   # save BEFORE show (required by the spec)
    plt.close(fig)
    print(f"Saved {out_path}")


# ── Step 3: Chart 2 — Stories per Category ────────────────────────────────────

def chart2_categories(df: pd.DataFrame) -> None:
    """
    Vertical bar chart showing how many stories belong to each category.
    Each bar gets a distinct colour from the shared palette.
    """
    counts = df["category"].value_counts().sort_index()   # alphabetical order

    fig, ax = plt.subplots(figsize=(8, 5))

    colours = [CATEGORY_COLOURS.get(cat, "#888888") for cat in counts.index]
    bars = ax.bar(counts.index, counts.values, color=colours)

    # Display the exact count above every bar
    for bar, count in zip(bars, counts.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.3,
            str(count),
            ha="center", fontsize=10,
        )

    ax.set_title("Number of Stories per Category", fontsize=14, fontweight="bold")
    ax.set_xlabel("Category")
    ax.set_ylabel("Number of Stories")
    ax.set_ylim(0, counts.max() + 3)   # headroom for count labels
    ax.tick_params(axis="x", rotation=15)
    plt.tight_layout()

    out_path = os.path.join(OUTPUT_DIR, "chart2_categories.png")
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved {out_path}")


# ── Step 4: Chart 3 — Score vs Comments (scatter) ─────────────────────────────

def chart3_scatter(df: pd.DataFrame) -> None:
    """
    Scatter plot of score (x) vs num_comments (y).
    Popular stories (is_popular == True) are plotted in a contrasting colour
    so the viewer can instantly see whether high-scoring stories also get
    more discussion.
    """
    popular     = df[df["is_popular"] == True]   # noqa: E712
    not_popular = df[df["is_popular"] == False]  # noqa: E712

    fig, ax = plt.subplots(figsize=(9, 6))

    # Plot non-popular stories first (background layer)
    ax.scatter(
        not_popular["score"], not_popular["num_comments"],
        color="#AEC6CF", alpha=0.7, edgecolors="white", linewidths=0.5,
        label="Not popular (score ≤ avg)",
    )

    # Popular stories on top so they're not hidden
    ax.scatter(
        popular["score"], popular["num_comments"],
        color="#FF6B6B", alpha=0.9, edgecolors="white", linewidths=0.5,
        label="Popular (score > avg)",
    )

    ax.set_title("Score vs Number of Comments", fontsize=14, fontweight="bold")
    ax.set_xlabel("Score (upvotes)")
    ax.set_ylabel("Number of Comments")
    ax.legend(title="Popularity")
    plt.tight_layout()

    out_path = os.path.join(OUTPUT_DIR, "chart3_scatter.png")
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved {out_path}")


# ── Bonus: Dashboard — all 3 charts side by side ──────────────────────────────

def chart_dashboard(df: pd.DataFrame) -> None:
    """
    Combines all three charts into a single 1×3 figure saved as dashboard.png.
    Each sub-plot is drawn independently using the same data and styling as the
    individual charts so the dashboard is self-contained.
    """
    fig, axes = plt.subplots(1, 3, figsize=(22, 7))
    fig.suptitle("TrendPulse Dashboard", fontsize=18, fontweight="bold", y=1.01)

    # ── Sub-plot 1: top 10 stories (horizontal bar) ────────────────────────
    ax1 = axes[0]
    top10 = (
        df.nlargest(10, "score")
          .sort_values("score", ascending=True)
    )
    labels  = [t if len(t) <= 40 else t[:37] + "…" for t in top10["title"]]
    colours = [CATEGORY_COLOURS.get(cat, "#888888") for cat in top10["category"]]
    ax1.barh(labels, top10["score"], color=colours)
    ax1.set_title("Top 10 Stories by Score", fontweight="bold")
    ax1.set_xlabel("Score")
    ax1.set_ylabel("Story Title")

    # ── Sub-plot 2: stories per category (vertical bar) ───────────────────
    ax2 = axes[1]
    counts  = df["category"].value_counts().sort_index()
    colours2 = [CATEGORY_COLOURS.get(cat, "#888888") for cat in counts.index]
    ax2.bar(counts.index, counts.values, color=colours2)
    ax2.set_title("Stories per Category", fontweight="bold")
    ax2.set_xlabel("Category")
    ax2.set_ylabel("Count")
    ax2.tick_params(axis="x", rotation=15)

    # ── Sub-plot 3: score vs comments scatter ─────────────────────────────
    ax3 = axes[2]
    popular     = df[df["is_popular"] == True]   # noqa: E712
    not_popular = df[df["is_popular"] == False]  # noqa: E712
    ax3.scatter(
        not_popular["score"], not_popular["num_comments"],
        color="#AEC6CF", alpha=0.7, label="Not popular",
    )
    ax3.scatter(
        popular["score"], popular["num_comments"],
        color="#FF6B6B", alpha=0.9, label="Popular",
    )
    ax3.set_title("Score vs Comments", fontweight="bold")
    ax3.set_xlabel("Score")
    ax3.set_ylabel("Comments")
    ax3.legend()

    plt.tight_layout()

    out_path = os.path.join(OUTPUT_DIR, "dashboard.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {out_path}")


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Step 1 — load data and prepare output folder
    df = load_data(INPUT_FILE)
    setup_output_dir(OUTPUT_DIR)

    # Step 2 — Chart 1: top 10 stories by score
    chart1_top_stories(df)

    # Step 3 — Chart 2: stories per category
    chart2_categories(df)

    # Step 4 — Chart 3: score vs comments scatter
    chart3_scatter(df)

    # Bonus — combined dashboard
    chart_dashboard(df)

    print("\nAll charts saved to outputs/")

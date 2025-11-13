import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------
# Step 1: Load and Prepare Data
# ---------------------------------------------------

def load_datasets(path_2021, path_2025):
    df_2021_full = pd.read_csv(path_2021)
    df_2021 = df_2021_full.sort_values(by='BayesAvgRating', ascending=False).head(500)
    df_2025 = pd.read_csv(path_2025)

    return df_2021, df_2025


# ---------------------------------------------------
# Step 2: Perform Data Quality Checks
# ---------------------------------------------------

def perform_quality_checks(df, label="Dataset"):
    print(f"\n=== {label} Data Quality Checks ===")

    # Identify relevant rating column (flexible for 2021 or 2025)
    rating_col = None
    for col in ['BayesAvgRating', 'Rating_2021', 'Rating_2025']:
        if col in df.columns:
            rating_col = col
            break

    if rating_col is None:
        print("No rating column found for quality checks.")
        return

    # Basic missing value check
    missing_ratings = df[rating_col].isna().sum()
    print(f"Missing values in {rating_col}: {missing_ratings}")

    # Rating summary
    print(f"\n{rating_col} Summary Statistics:")
    print(df[rating_col].describe())

    # Check for extreme values (based on 0–10 scale)
    out_of_range = df[(df[rating_col] < 0) | (df[rating_col] > 10)]
    if not out_of_range.empty:
        print(f"\nOut-of-range ratings in {rating_col} (< 0 or > 10):")
        print(out_of_range[['BGGId', rating_col]])

    # Optional: suspiciously low/high for 2021
    if rating_col in ['BayesAvgRating', 'Rating_2021']:
        low = df[df[rating_col] <= 5.0]
        high = df[df[rating_col] >= 9.5]

        if not low.empty:
            print(f"\nSuspiciously low ratings (<= 5.0) in {label}:")
            print(low[['BGGId', 'Name', rating_col]])

        if not high.empty:
            print(f"\nSuspiciously high ratings (>= 9.5) in {label}:")
            print(high[['BGGId', 'Name', rating_col]])

    # Duplicates
    duplicate_ids = df['BGGId'].duplicated().sum()
    print(f"\nDuplicated BGGIds in {label}: {duplicate_ids}")

    # Missing BGGIds
    missing_ids = df['BGGId'].isna().sum()
    print(f"Missing BGGIds in {label}: {missing_ids}")


# ---------------------------------------------------
# Step 3: Merge and Compare Ratings
# ---------------------------------------------------

def merge_datasets(df_2021, df_2025):
    df_2021_clean = df_2021[['BGGId', 'Name', 'BayesAvgRating']].copy()
    df_2021_clean.rename(columns={'BayesAvgRating': 'Rating_2021'}, inplace=True)

    df_merged = df_2021_clean.merge(df_2025, on='BGGId', how='inner')
    df_merged['rating_change'] = df_merged['Rating_2025'] - df_merged['Rating_2021']
    return df_merged

def check_merged_data(df):
    print("\n=== Merged Data Quality Checks ===")
    print("Missing values per column:")
    print(df.isna().sum())

    duplicates = df['BGGId'].duplicated().sum()
    print(f"\nDuplicated BGGIds in Merged Data: {duplicates}")

    print("\nRating Change Summary:")
    print(df['rating_change'].describe())

    extreme = df[df['rating_change'].abs() > 1.0]
    print(f"\nGames with extreme rating changes (>|1.0|): {len(extreme)}")
    if not extreme.empty:
        print(extreme[['BGGId', 'Name', 'Rating_2021', 'Rating_2025', 'rating_change']])

# ---------------------------------------------------
# Step 4: Visualization
# ---------------------------------------------------

def plot_top_rating_changes(df, top_n=5, ascending=False, title=""):
    sorted_df = df.sort_values(by='rating_change', ascending=ascending).head(top_n)

    x = np.arange(len(sorted_df))
    width = 0.35

    fig, ax = plt.subplots(figsize=(max(10, top_n * 1.5), 6))
    ax.bar(x - width / 2, sorted_df['Rating_2021'], width, label='Rating 2021')
    ax.bar(x + width / 2, sorted_df['Rating_2025'], width, label='Rating 2025')

    ax.set_ylabel('BayesAvgRating')
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(sorted_df['Name'], rotation=45, ha='right')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    for i in range(len(sorted_df)):
        change = sorted_df.iloc[i]['rating_change']
        ax.annotate(f"{change:+.2f}",
                    xy=(x[i], max(sorted_df.iloc[i]['Rating_2021'], sorted_df.iloc[i]['Rating_2025']) + 0.02),
                    ha='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.show()


# ---------------------------------------------------
# Step 5: Main Execution
# ---------------------------------------------------

def main():
    path_2021 = "games.csv"
    path_2025 = "games_2025_parsed.csv"

    df_2021, df_2025 = load_datasets(path_2021, path_2025)

    perform_quality_checks(df_2021, label="Top 500 Games (2021)")
    perform_quality_checks(df_2025, label="Parsed Ratings (2025)")

    df_merged = merge_datasets(df_2021, df_2025)
    check_merged_data(df_merged)

    df_merged.to_csv("top500_games_2021_vs_2025_cleaned.csv", index=False)
    print("\nMerged data saved to 'top500_games_2021_vs_2025_cleaned.csv'")

    while True:
        user_input = input("\nEnter the number of top rating changes to visualize (or 'q' to quit): ").strip()

        if user_input.lower() in ['q', 'quit', 'exit']:
            print("Exiting plot viewer.")
            break

        try:
            top_n = int(user_input)

            if top_n <= 0:
                print("Please enter a number greater than 0.")
                continue

            # Positive changes
            plot_top_rating_changes(
                df_merged,
                top_n=top_n,
                ascending=False,
                title=f"Top {top_n} Games with Biggest Positive Rating Change"
            )

            # Negative changes
            plot_top_rating_changes(
                df_merged,
                top_n=top_n,
                ascending=True,
                title=f"Top {top_n} Games with Biggest Negative Rating Change"
            )

        except ValueError:
            print("Invalid input. Please enter a whole number or 'q' to quit.")


if __name__ == "__main__":
    main()

# Board Game Ratings Analysis (2021 vs 2025)

This project analyzes changes in board game popularity by comparing the Bayes Average Ratings of the top 500 games from 2021 to 2025 using data from BoardGameGeek.

## Files
- `fetch_2025_data.py`: Pulls 2025 data via BGG API
- `analyze_ratings.py`: Cleans and compares the datasets
- `games.csv`: Source 2021 data
- `games_2025_raw_XML.csv`: Raw XML from API
- `games_2025_parsed.csv`: Parsed 2025 ratings
- `top500_games_2021_vs_2025_cleaned.csv`: Final merged dataset

## Requirements
- Python 3.10+
- pandas, numpy, matplotlib, requests

## Notes
API calls are authenticated using a token provided by BGG. Script includes 3-second delay to comply with their policies.

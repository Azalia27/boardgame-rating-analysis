import pandas as pd
import requests
import xml.etree.ElementTree as ET
import time

# ---------------------------------------------------
# Step 1: Load Top 500 BGG IDs from 2021 dataset
# ---------------------------------------------------

def get_top_500_bgg_ids(csv_path_2021):
    df_2021 = pd.read_csv(csv_path_2021)
    top_500 = df_2021.sort_values(by="BayesAvgRating", ascending=False).head(500)
    return top_500["BGGId"].tolist()

# ---------------------------------------------------
# Step 2: Fetch Raw XML Data for Each BGGId
# ---------------------------------------------------

def fetch_raw_xml_data(bgg_ids, save_path="games_2025_raw_XML.csv"):
    bgg_api_url = "https://boardgamegeek.com/xmlapi2/thing?id={}&stats=1"
    games_2025_raw_data = []

    for idx, bgg_id in enumerate(bgg_ids):
        try:
            headers = {
                "User-Agent": "BoardGameRatingsAnalyzer/1.0",
                "Authorization": "Bearer 7bfd9d15-f868-4fc8-83a5-3dd14013949b"
            }
            response = requests.get(bgg_api_url.format(bgg_id), headers=headers)

            if response.status_code == 200:
                xml_string = response.content.decode("utf-8", errors="replace")
            else:
                print(f"Warning: BGGId {bgg_id} returned status {response.status_code}")
                xml_string = ""

            games_2025_raw_data.append({
                "BGGId": bgg_id,
                "XMLResponse": xml_string
            })

            if (idx + 1) % 25 == 0:
                print(f"Fetched board game #{idx + 1}")

            time.sleep(3)

        except Exception as e:
            print(f"Failed to fetch BGGId {bgg_id}: {e}")
            games_2025_raw_data.append({
                "BGGId": bgg_id,
                "XMLResponse": ""
            })

    df_raw = pd.DataFrame(games_2025_raw_data)
    df_raw.to_csv(save_path, index=False)
    print(f"\nRaw XML data saved to {save_path}")
    return df_raw

# ---------------------------------------------------
# Step 3: Parse XML to Extract Bayes Average Rating
# ---------------------------------------------------

def parse_bayes_average(df_raw):
    parsed_games_data = []

    for idx, row in df_raw.iterrows():
        bgg_id = row['BGGId']
        xml_content = row['XMLResponse']

        try:
            root = ET.fromstring(xml_content)
            bayes_avg_element = root.find(".//bayesaverage")

            if bayes_avg_element is not None:
                bayes_avg_rating = float(bayes_avg_element.attrib.get('value'))
            else:
                bayes_avg_rating = None

            parsed_games_data.append({
                'BGGId': bgg_id,
                'Rating_2025': bayes_avg_rating
            })

        except Exception as e:
            print(f"Error parsing BGGId {bgg_id}: {e}")
            parsed_games_data.append({
                'BGGId': bgg_id,
                'Rating_2025': None
            })

    df_parsed = pd.DataFrame(parsed_games_data)
    print("\nXML parsing complete.")
    return df_parsed

# ---------------------------------------------------
# Step 4: Main Execution
# ---------------------------------------------------

def main():
    csv_2021_path = "games.csv"

    top_bgg_ids = get_top_500_bgg_ids(csv_2021_path)

    df_raw = fetch_raw_xml_data(top_bgg_ids)

    # Optional reload
    df_raw = pd.read_csv("games_2025_raw_XML.csv")

    df_parsed = parse_bayes_average(df_raw)

    df_parsed.to_csv("games_2025_parsed.csv", index=False)
    print("Parsed data saved as 'games_2025_parsed.csv'")

    print(df_parsed.head())

if __name__ == "__main__":
    main()

import requests
import pandas as pd

# Team Table fields can be found here: https://lol.fandom.com/wiki/Special:CargoTables/Teams
def convert_to_image_url(filename):
    base = "https://lol.fandom.com/wiki/Special:Redirect/file/"
    return base + filename if pd.notna(filename) and filename else None

def fetch_all_cargo_data(base_url, table, fields, where=None):
    all_data = []
    offset = 0
    limit = 500

    while True:
        params = {
            "action": "cargoquery",
            "format": "json",
            "tables": table,
            "fields": ",".join(fields),
            "limit": str(limit),
            "offset": str(offset)
        }
        if where:
            params["where"] = where

        response = requests.get(base_url, params=params)
        response.raise_for_status()
        results = response.json().get("cargoquery", [])

        if not results:
            break  # Done paging

        all_data.extend(entry["title"] for entry in results)
        offset += limit

    df = pd.DataFrame(all_data)

    # Fix image field if present
    if "Image" in df.columns:
        df["Image"] = df["Image"].apply(convert_to_image_url)

    return df

# Example usage
url = "https://lol.fandom.com/api.php"
fields = [
    "Name", "Region", "Image", "IsDisbanded",
    "RenamedTo", "IsLowercase", "Short", "OverviewPage"
]

df_teams = fetch_all_cargo_data(url, "Teams", fields)
df_teams.to_csv("all_teams.csv", index=False)
print("Exported all teams to all_teams.csv")

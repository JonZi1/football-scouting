"""
FBref Player Data Scraper

Scrapes player statistics from FBref.com for top European leagues.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
import time

# League URLs from FBref
LEAGUES = {
    "Premier League": "https://fbref.com/en/comps/9/stats/Premier-League-Stats",
    "La Liga": "https://fbref.com/en/comps/12/stats/La-Liga-Stats",
    "Bundesliga": "https://fbref.com/en/comps/20/stats/Bundesliga-Stats",
    "Serie A": "https://fbref.com/en/comps/11/stats/Serie-A-Stats",
    "Ligue 1": "https://fbref.com/en/comps/13/stats/Ligue-1-Stats",
}

OUTPUT_DIR = Path(__file__).parent / "data"


def scrape_league(league_name: str, url: str) -> pd.DataFrame:
    """Scrape player stats from a single league."""
    print(f"Scraping {league_name}...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    # Find the standard stats table
    table = soup.find("table", {"id": "stats_standard"})

    if not table:
        print(f"  Could not find stats table for {league_name}")
        return pd.DataFrame()

    # Parse table
    rows = []
    tbody = table.find("tbody")

    if not tbody:
        return pd.DataFrame()

    for tr in tbody.find_all("tr"):
        # Skip header rows
        if tr.get("class") and "thead" in tr.get("class"):
            continue

        cells = tr.find_all(["th", "td"])

        if len(cells) < 10:
            continue

        try:
            player_cell = cells[0]
            player_name = player_cell.get_text(strip=True)

            row = {
                "player": player_name,
                "nation": cells[1].get_text(strip=True) if len(cells) > 1 else "",
                "position": cells[2].get_text(strip=True) if len(cells) > 2 else "",
                "team": cells[3].get_text(strip=True) if len(cells) > 3 else "",
                "age": cells[4].get_text(strip=True).split("-")[0] if len(cells) > 4 else "",
                "matches": cells[6].get_text(strip=True) if len(cells) > 6 else "",
                "starts": cells[7].get_text(strip=True) if len(cells) > 7 else "",
                "minutes": cells[8].get_text(strip=True).replace(",", "") if len(cells) > 8 else "",
                "goals": cells[10].get_text(strip=True) if len(cells) > 10 else "",
                "assists": cells[11].get_text(strip=True) if len(cells) > 11 else "",
                "league": league_name,
            }
            rows.append(row)
        except (IndexError, AttributeError) as e:
            continue

    df = pd.DataFrame(rows)

    # Convert numeric columns
    numeric_cols = ["age", "matches", "starts", "minutes", "goals", "assists"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    print(f"  Found {len(df)} players")
    return df


def scrape_all_leagues() -> pd.DataFrame:
    """Scrape all configured leagues."""
    all_data = []

    for league_name, url in LEAGUES.items():
        try:
            df = scrape_league(league_name, url)
            all_data.append(df)
            # Be nice to the server
            time.sleep(3)
        except Exception as e:
            print(f"  Error scraping {league_name}: {e}")

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return pd.DataFrame()


def main():
    """Main entry point."""
    print("Starting FBref scraper...")
    print("=" * 50)

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Scrape all leagues
    df = scrape_all_leagues()

    if df.empty:
        print("No data scraped!")
        return

    # Save to CSV
    output_file = OUTPUT_DIR / "players.csv"
    df.to_csv(output_file, index=False)

    print("=" * 50)
    print(f"Saved {len(df)} players to {output_file}")
    print(f"Leagues: {df['league'].unique().tolist()}")


if __name__ == "__main__":
    main()

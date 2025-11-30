# Football Player Scouting Dashboard

A Streamlit app to help scout and compare football players using data from FBref.

## Features

- **Filter players** by position, league, age, and minutes played
- **Search** for specific players
- **Compare players** side-by-side with radar charts
- Data from top 5 European leagues (Premier League, La Liga, Bundesliga, Serie A, Ligue 1)

## Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Scrape player data
python scraper.py

# Run the app
streamlit run app.py
```

## Data Source

Player statistics are scraped from [FBref.com](https://fbref.com).

## Tech Stack

- Python
- Streamlit
- pandas
- Plotly
- BeautifulSoup

## Author

Built by Jon Zisi

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# App config
st.set_page_config(
    page_title="Football Player Scouting Dashboard",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Football Player Scouting Dashboard")
st.caption("Compare and analyze Premier League players using FPL data (2025-26 season)")

# Check if data exists
DATA_FILE = Path(__file__).parent / "data" / "players.csv"

if not DATA_FILE.exists():
    st.warning("No player data found. Run `python scraper.py` first to fetch data.")
    st.stop()

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    # Map team IDs to names if needed
    team_map = {
        1: "Arsenal", 2: "Aston Villa", 3: "Bournemouth", 4: "Brentford",
        5: "Brighton", 6: "Chelsea", 7: "Crystal Palace", 8: "Everton",
        9: "Fulham", 10: "Ipswich", 11: "Leicester", 12: "Liverpool",
        13: "Man City", 14: "Man Utd", 15: "Newcastle", 16: "Nott'm Forest",
        17: "Southampton", 18: "Spurs", 19: "West Ham", 20: "Wolves"
    }
    if df["team"].dtype in ["int64", "float64"]:
        df["team"] = df["team"].map(team_map)
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Position filter
positions = ["All"] + sorted(df["position"].dropna().unique().tolist())
selected_position = st.sidebar.selectbox("Position", positions)

# Team filter
teams = ["All"] + sorted(df["team"].dropna().unique().tolist())
selected_team = st.sidebar.selectbox("Team", teams)

# Price range filter
if "price" in df.columns:
    min_price, max_price = float(df["price"].min()), float(df["price"].max())
    price_range = st.sidebar.slider("Price Range (£m)", min_price, max_price, (min_price, max_price), step=0.5)

# Minutes played filter
min_minutes = st.sidebar.number_input("Minimum Minutes Played", min_value=0, value=90)

# Apply filters
filtered_df = df.copy()

if selected_position != "All":
    filtered_df = filtered_df[filtered_df["position"] == selected_position]

if selected_team != "All":
    filtered_df = filtered_df[filtered_df["team"] == selected_team]

if "price" in df.columns:
    filtered_df = filtered_df[
        (filtered_df["price"] >= price_range[0]) &
        (filtered_df["price"] <= price_range[1])
    ]

filtered_df = filtered_df[filtered_df["minutes"] >= min_minutes]

# Main content
tab1, tab2, tab3 = st.tabs(["📋 Player List", "📊 Compare Players", "📈 Analytics"])

with tab1:
    st.header(f"Players ({len(filtered_df)} found)")

    # Search
    search = st.text_input("Search player name")
    if search:
        filtered_df = filtered_df[filtered_df["player"].str.contains(search, case=False, na=False)]

    # Display table
    display_cols = ["player", "position", "team", "price", "total_points", "minutes", "goals", "assists", "form"]
    available_cols = [c for c in display_cols if c in filtered_df.columns]

    # Sort options
    sort_col = st.selectbox("Sort by", available_cols, index=available_cols.index("total_points") if "total_points" in available_cols else 0)
    sort_order = st.checkbox("Ascending", value=False)

    st.dataframe(
        filtered_df[available_cols].sort_values(sort_col, ascending=sort_order),
        use_container_width=True,
        hide_index=True
    )

with tab2:
    st.header("Compare Players")

    col1, col2 = st.columns(2)

    player_list = sorted(filtered_df["player"].dropna().unique().tolist())

    with col1:
        player1 = st.selectbox("Player 1", [""] + player_list, key="p1")

    with col2:
        player2 = st.selectbox("Player 2", [""] + player_list, key="p2")

    if player1 and player2:
        # Get player stats
        p1_stats = filtered_df[filtered_df["player"] == player1].iloc[0]
        p2_stats = filtered_df[filtered_df["player"] == player2].iloc[0]

        # FPL-specific metrics for radar chart
        radar_metrics = ["influence", "creativity", "threat", "ict_index", "form", "points_per_game"]
        radar_labels = ["Influence", "Creativity", "Threat", "ICT Index", "Form", "Pts/Game"]
        available_metrics = [m for m in radar_metrics if m in df.columns and df[m].notna().any()]
        available_labels = [radar_labels[i] for i, m in enumerate(radar_metrics) if m in available_metrics]

        if available_metrics:
            # Normalize stats for radar chart (0-100 scale)
            max_vals = df[available_metrics].max()

            p1_values = [(p1_stats[m] / max_vals[m] * 100) if pd.notna(p1_stats[m]) and max_vals[m] > 0 else 0 for m in available_metrics]
            p2_values = [(p2_stats[m] / max_vals[m] * 100) if pd.notna(p2_stats[m]) and max_vals[m] > 0 else 0 for m in available_metrics]

            # Create radar chart
            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=p1_values + [p1_values[0]],
                theta=available_labels + [available_labels[0]],
                fill='toself',
                name=player1,
                opacity=0.7
            ))

            fig.add_trace(go.Scatterpolar(
                r=p2_values + [p2_values[0]],
                theta=available_labels + [available_labels[0]],
                fill='toself',
                name=player2,
                opacity=0.7
            ))

            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                title="Player Comparison (Normalized to 100)"
            )

            st.plotly_chart(fig, use_container_width=True)

        # Side by side stats
        st.subheader("Stats Comparison")

        compare_metrics = ["total_points", "minutes", "goals", "assists", "clean_sheets", "yellow_cards", "bonus", "price", "form", "points_per_game"]
        compare_labels = ["Total Points", "Minutes", "Goals", "Assists", "Clean Sheets", "Yellow Cards", "Bonus", "Price (£m)", "Form", "Pts/Game"]

        compare_data = []
        for label, metric in zip(compare_labels, compare_metrics):
            if metric in df.columns:
                v1 = p1_stats.get(metric, "N/A")
                v2 = p2_stats.get(metric, "N/A")
                compare_data.append({"Stat": label, player1: v1, player2: v2})

        compare_df = pd.DataFrame(compare_data)
        st.dataframe(compare_df, use_container_width=True, hide_index=True)
    else:
        st.info("Select two players to compare")

with tab3:
    st.header("Analytics")

    col1, col2 = st.columns(2)

    with col1:
        # Top scorers
        st.subheader("Top Scorers")
        top_scorers = filtered_df.nlargest(10, "goals")[["player", "team", "goals", "minutes"]]
        st.dataframe(top_scorers, use_container_width=True, hide_index=True)

    with col2:
        # Top assists
        st.subheader("Top Assists")
        top_assists = filtered_df.nlargest(10, "assists")[["player", "team", "assists", "minutes"]]
        st.dataframe(top_assists, use_container_width=True, hide_index=True)

    # Value analysis: Points per million
    st.subheader("Best Value Players (Points per £m)")
    if "price" in filtered_df.columns and "total_points" in filtered_df.columns:
        value_df = filtered_df[filtered_df["price"] > 0].copy()
        value_df["value"] = value_df["total_points"] / value_df["price"]
        best_value = value_df.nlargest(15, "value")[["player", "team", "position", "price", "total_points", "value"]]
        best_value["value"] = best_value["value"].round(2)
        st.dataframe(best_value, use_container_width=True, hide_index=True)

    # Scatter plot: Price vs Points
    st.subheader("Price vs Total Points")
    if "price" in filtered_df.columns and "total_points" in filtered_df.columns:
        fig = px.scatter(
            filtered_df[filtered_df["minutes"] > 0],
            x="price",
            y="total_points",
            color="position",
            hover_data=["player", "team"],
            labels={"price": "Price (£m)", "total_points": "Total Points"},
            title="Player Value Analysis"
        )
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.divider()
st.caption("Data source: Fantasy Premier League API (2025-26 season) | Built by Jon Zisi")

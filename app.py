import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# App config
st.set_page_config(
    page_title="Football Player Scouting Dashboard",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Football Player Scouting Dashboard")
st.caption("Compare and analyze players using FBref data")

# Check if data exists
DATA_FILE = Path(__file__).parent / "data" / "players.csv"

if not DATA_FILE.exists():
    st.warning("No player data found. Run `python scraper.py` first to fetch data.")
    st.stop()

# Load data
@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

df = load_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Position filter
positions = ["All"] + sorted(df["position"].dropna().unique().tolist())
selected_position = st.sidebar.selectbox("Position", positions)

# League filter
leagues = ["All"] + sorted(df["league"].dropna().unique().tolist())
selected_league = st.sidebar.selectbox("League", leagues)

# Age filter
min_age, max_age = int(df["age"].min()), int(df["age"].max())
age_range = st.sidebar.slider("Age Range", min_age, max_age, (min_age, max_age))

# Minutes played filter
min_minutes = st.sidebar.number_input("Minimum Minutes Played", min_value=0, value=500)

# Apply filters
filtered_df = df.copy()

if selected_position != "All":
    filtered_df = filtered_df[filtered_df["position"] == selected_position]

if selected_league != "All":
    filtered_df = filtered_df[filtered_df["league"] == selected_league]

filtered_df = filtered_df[
    (filtered_df["age"] >= age_range[0]) &
    (filtered_df["age"] <= age_range[1]) &
    (filtered_df["minutes"] >= min_minutes)
]

# Main content
tab1, tab2 = st.tabs(["📋 Player List", "📊 Compare Players"])

with tab1:
    st.header(f"Players ({len(filtered_df)} found)")

    # Search
    search = st.text_input("Search player name")
    if search:
        filtered_df = filtered_df[filtered_df["player"].str.contains(search, case=False, na=False)]

    # Display table
    display_cols = ["player", "position", "team", "league", "age", "minutes", "goals", "assists"]
    available_cols = [c for c in display_cols if c in filtered_df.columns]

    st.dataframe(
        filtered_df[available_cols].sort_values("player"),
        use_container_width=True,
        hide_index=True
    )

with tab2:
    st.header("Compare Players")

    col1, col2 = st.columns(2)

    player_list = filtered_df["player"].dropna().unique().tolist()

    with col1:
        player1 = st.selectbox("Player 1", [""] + player_list, key="p1")

    with col2:
        player2 = st.selectbox("Player 2", [""] + player_list, key="p2")

    if player1 and player2:
        # Get player stats
        p1_stats = filtered_df[filtered_df["player"] == player1].iloc[0]
        p2_stats = filtered_df[filtered_df["player"] == player2].iloc[0]

        # Define metrics for radar chart (adjust based on available columns)
        radar_metrics = ["goals", "assists", "shots", "passes", "tackles", "interceptions"]
        available_metrics = [m for m in radar_metrics if m in df.columns]

        if available_metrics:
            # Normalize stats for radar chart (0-100 scale)
            max_vals = df[available_metrics].max()

            p1_values = [(p1_stats[m] / max_vals[m] * 100) if max_vals[m] > 0 else 0 for m in available_metrics]
            p2_values = [(p2_stats[m] / max_vals[m] * 100) if max_vals[m] > 0 else 0 for m in available_metrics]

            # Create radar chart
            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=p1_values + [p1_values[0]],
                theta=available_metrics + [available_metrics[0]],
                fill='toself',
                name=player1,
                opacity=0.7
            ))

            fig.add_trace(go.Scatterpolar(
                r=p2_values + [p2_values[0]],
                theta=available_metrics + [available_metrics[0]],
                fill='toself',
                name=player2,
                opacity=0.7
            ))

            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                title="Player Comparison"
            )

            st.plotly_chart(fig, use_container_width=True)

        # Side by side stats
        st.subheader("Stats Comparison")

        compare_df = pd.DataFrame({
            "Stat": available_metrics if available_metrics else ["No stats available"],
            player1: [p1_stats.get(m, "N/A") for m in available_metrics] if available_metrics else ["N/A"],
            player2: [p2_stats.get(m, "N/A") for m in available_metrics] if available_metrics else ["N/A"]
        })

        st.dataframe(compare_df, use_container_width=True, hide_index=True)
    else:
        st.info("Select two players to compare")

# Footer
st.divider()
st.caption("Data source: FBref.com | Built by Jon Zisi")

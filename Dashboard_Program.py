import streamlit as st
import pandas as pd
import os
import plotly.express as px

DATA_DIR = "mlb_yearly_data"

@st.cache_data
def load_data():
    dfs = []
    for fname in os.listdir(DATA_DIR):
        if fname.endswith(".csv") and "table" in fname:
            year = int(fname.split("_")[1])
            path = os.path.join(DATA_DIR, fname)
            df = pd.read_csv(path)

            # Drop rows with mostly NaNs or bad headers
            df = df.dropna(how='all').dropna(axis=1, how='all')
            if "Name(s)" in df.columns and "Team(s)" in df.columns and "#" in df.columns:
                df = df.rename(columns={"Name(s)": "Player", "Team(s)": "Team", "#": "Value"})
                df["Year"] = year
                dfs.append(df)

    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

def main():
    # Initialize session state for navigation
    if 'page' not in st.session_state:
        st.session_state.page = 'main'
    if 'selected_player' not in st.session_state:
        st.session_state.selected_player = None
    if 'selected_stat' not in st.session_state:
        st.session_state.selected_stat = None
    if 'selected_year' not in st.session_state:
        st.session_state.selected_year = None

    df = load_data()
    if df.empty:
        st.error("No data available.")
        return

    stat_types = df['Statistic'].dropna().unique()
    years = sorted(df['Year'].dropna().unique())
    teams = df['Team'].dropna().unique()

    if st.session_state.page == 'main':
        st.title("MAJOR LEAGUE BASEBALL STATS")
        st.markdown("Explore raw historical baseball stats scraped from Baseball Almanac. Choose stats, teams, or years below.")

        # Sidebar filters
        st.sidebar.header("Filters")
        selected_stat = st.sidebar.selectbox("Select Statistic", stat_types)
        selected_year = st.sidebar.slider("Select Year", min_value=min(years), max_value=max(years), value=min(years))
        selected_team = st.sidebar.selectbox("Filter by Team (optional)", ["All"] + list(teams))

        st.session_state.selected_stat = selected_stat
        st.session_state.selected_year = selected_year

        # Filter DataFrame for the selected stat, year, and optional team
        df_filtered = df[(df["Statistic"] == selected_stat) & (df["Year"] == selected_year)]
        if selected_team != "All":
            df_filtered = df_filtered[df_filtered["Team"] == selected_team]

        df_filtered["Value"] = pd.to_numeric(df_filtered["Value"], errors="coerce")
        df_filtered = df_filtered.dropna(subset=["Value"])

        st.subheader(f"Top Players for {selected_stat} in {selected_year}")

        if df_filtered.empty:
            st.warning("No data for selected options.")
        else:
            # Sort descending by value
            top_players_df = df_filtered.sort_values(by="Value", ascending=False).head(10)

            # Show player buttons
            for i, row in top_players_df.iterrows():
                player = row["Player"]
                team = row["Team"]
                value = row["Value"]
                player_label = f"{player} ({team}): {value}"

                if st.button(player_label, key=f"player_{i}"):
                    st.session_state.selected_player = player
                    st.session_state.page = 'player_detail'
                    st.rerun()


    elif st.session_state.page == 'player_detail':
        selected_player = st.session_state.selected_player
        selected_stat = st.session_state.selected_stat

        st.title(f"{selected_player}'s {selected_stat} Over Time")
        if st.button("Back to Main Page"):
            st.session_state.page = 'main'
            st.session_state.selected_player = None
            st.rerun()


        # Filter for player's stat over all years
        player_all_years_data = df[(df["Player"] == selected_player) & (df["Statistic"] == selected_stat)]
        player_all_years_data["Value"] = pd.to_numeric(player_all_years_data["Value"], errors="coerce")
        player_all_years_data = player_all_years_data.dropna(subset=["Year", "Value"]).sort_values(by="Year")

        if player_all_years_data.empty:
            st.warning(f"No {selected_stat} data available for {selected_player}.")
        else:
            fig = px.line(
                player_all_years_data,
                x="Year",
                y="Value",
                markers=True,
                labels={"Value": selected_stat, "Year": "Year"},
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig)

    df_filtered["Value"] = pd.to_numeric(df_filtered["Value"], errors="coerce")
    df_filtered = df_filtered.dropna(subset=["Value"])

    st.subheader(f"Top Player for {selected_stat} in {selected_year}")

    if df_filtered.empty:
        st.warning("No data for selected options.")
        top_player = None
    else:
        # Get the top player (highest value)
        top_player_df = df_filtered.sort_values(by="Value", ascending=False).head(1)

        top_player = top_player_df.iloc[0]["Player"]
        top_value = top_player_df.iloc[0]["Value"]

        st.write(f"**{top_player}** from team **{top_player_df.iloc[0]['Team']}** with {top_value} {selected_stat}.")

        # Optionally, show a single bar for the top player
        fig = px.bar(top_player_df, x="Player", y="Value",
                    title=f"Top Player for {selected_stat} in {selected_year}",
                    labels={"Value": selected_stat, "Player": "Player"})
        st.plotly_chart(fig)

    # Player selection dropdown from top player for stat over time visualization
    if top_player:
        selected_player = st.selectbox("Selected Top Player to See Their Stats Over Time", [top_player])
    else:
        # fallback to all players if no top player available
        available_players = sorted(df["Player"].dropna().unique())
        selected_player = st.selectbox("Select a Player to See Their Stats Over Time", available_players)


    # Player stat over all years
    st.subheader(f"{selected_player}'s {selected_stat} Over Time")

    player_data = df[(df["Player"] == selected_player) & (df["Statistic"] == selected_stat)]
    if player_data.empty:
        st.warning(f"No {selected_stat} data available for {selected_player}.")
    else:
        player_data = player_data.dropna(subset=["Year", "Value"]).sort_values(by="Year")
        fig2 = px.line(
            player_data,
            x="Year",
            y="Value",
            markers=True,
            title=f"{selected_player}'s {selected_stat} Over Time",
            labels={"Value": selected_stat, "Year": "Year"}
        )
        fig2.update_layout(height=500)
        st.plotly_chart(fig2)

    # Stat Trends Over Time for top players overall
    st.subheader("Stat Trends Over Time")
    trend_stat = st.selectbox("Choose Stat to Trend", stat_types, key="trend_stat")
    df_trend = df[df["Statistic"] == trend_stat]
    df_trend["Value"] = pd.to_numeric(df_trend["Value"], errors="coerce")
    df_trend = df_trend.dropna(subset=["Value"])

    top_players_overall = df_trend["Player"].value_counts().head(5).index
    df_top_trend = df_trend[df_trend["Player"].isin(top_players_overall)]

    fig3 = px.line(df_top_trend, x="Year", y="Value", color="Player",
                   title=f"Top Players Over Time: {trend_stat}")
    st.plotly_chart(fig3)


if __name__ == "__main__":
    main()

from django.shortcuts import render
from django.conf import settings
import pandas as pd
import os
import plotly.express as px


def home(request):
    # ---------------------------------------------------
    # LOAD CLEANED DATASETS
    # ---------------------------------------------------
    base_dir = settings.BASE_DIR

    df_auto = pd.read_csv(os.path.join(base_dir, "data", "clean_naic_auto_insurance.csv"))
    df_home = pd.read_csv(os.path.join(base_dir, "data", "clean_nerdwallet_home.csv"))
    df_fema = pd.read_csv(os.path.join(base_dir, "data", "clean_fema_weather.csv"), low_memory=False)

    # ---------------------------------------------------
    # INSURANCE TYPE (Auto or Home)
    # ---------------------------------------------------
    insurance_types = ["Auto", "Home"]
    selected_insurance = request.GET.get("insurance", "Auto").capitalize()
    if selected_insurance not in insurance_types:
        selected_insurance = "Auto"

    # ---------------------------------------------------
    # CLEAN STATE CODES
    # Ensure only 2-letter state codes are used
    # ---------------------------------------------------
    def clean_states(df):
        df = df[df["state"].notna()]
        df["state"] = df["state"].astype(str).str.strip().str.upper()
        return df[df["state"].str.len() == 2].copy()

    df_auto = clean_states(df_auto)
    df_home = clean_states(df_home)
    df_fema = clean_states(df_fema)

    # ---------------------------------------------------
    # YEAR HANDLING
    # Auto = selectable 2018–2022
    # Home = always "Current (2025)"
    # ---------------------------------------------------
    auto_years = list(range(2018, 2023))
    selected_year = request.GET.get("year", auto_years[-1])

    if selected_insurance == "Auto":
        selected_year = int(selected_year)
        states = sorted(df_auto["state"].unique().tolist())
    else:
        selected_year = "Current (2025)"     # UI label only
        states = sorted(df_home["state"].unique().tolist())

    selected_state = request.GET.get("state", states[0])

    # ---------------------------------------------------
    # BUILD INSURANCE DATAFRAME (df_ins)
    # ---------------------------------------------------
    if selected_insurance == "Auto":
        year_col = f"avg_{selected_year}"

        df_ins = (
            df_auto[["state", year_col]]
            .rename(columns={year_col: "Average Premium"})
            .groupby("state", as_index=False)
            .agg({"Average Premium": "mean"})
        )

    else:  # HOME
        df_ins = (
            df_home.rename(columns={"avg_annual_usd": "Average Premium"})
            .groupby("state", as_index=False)
            .agg({"Average Premium": "mean"})
        )

    # ---------------------------------------------------
    # FEMA DISASTER COUNTS (ONE PER STATE)
    # ---------------------------------------------------
    df_fema["declarationDate"] = pd.to_datetime(df_fema["declarationDate"], errors="coerce")

    fema_counts = (
        df_fema.groupby("state", as_index=False)
        .agg(disaster_count=("state", "count"))
    )

    # ---------------------------------------------------
    # MERGE INSURANCE + FEMA
    # ---------------------------------------------------
    merged_df = df_ins.merge(fema_counts, on="state", how="left")
    merged_df["disaster_count"] = merged_df["disaster_count"].fillna(0)

    # ---------------------------------------------------
    # BUILD INDEXES + FINAL RISK SCORE
    # ---------------------------------------------------
    merged_df["Premium Index"] = merged_df["Average Premium"] / merged_df["Average Premium"].mean()

    disaster_avg = merged_df["disaster_count"].mean()
    merged_df["Disaster Index"] = (
        merged_df["disaster_count"] / disaster_avg if disaster_avg > 0 else 0
    )

    merged_df["Risk Score"] = (
        0.6 * merged_df["Premium Index"] +
        0.4 * merged_df["Disaster Index"]
    )

    selected_risk = round(
        merged_df.loc[merged_df["state"] == selected_state, "Risk Score"].values[0],
        2
    )

    # ---------------------------------------------------
    # AUTO TREND CHART (INDEXED TO 2018)
    # ---------------------------------------------------
    trend_chart = None

    if selected_insurance == "Auto":
        base_year = auto_years[0]  # 2018 baseline

        trend_rows = []

        # National trend
        nat_base = df_auto[f"avg_{base_year}"].mean()

        for y in auto_years:
            trend_rows.append({
                "Year": int(y),
                "Premium Index": df_auto[f"avg_{y}"].mean() / nat_base,
                "Series": "National Avg"
            })

        # State trend
        state_row = df_auto[df_auto["state"] == selected_state].iloc[0]
        state_base = state_row[f"avg_{base_year}"]

        for y in auto_years:
            trend_rows.append({
                "Year": int(y),
                "Premium Index": state_row[f"avg_{y}"] / state_base,
                "Series": selected_state
            })

        trend_df = pd.DataFrame(trend_rows).sort_values("Year")

        trend_fig = px.line(
            trend_df,
            x="Year",
            y="Premium Index",
            color="Series",
            markers=True,
            title="Auto Insurance Premium Trend (Indexed to 2018 = 1.00)"
        )

        trend_fig.add_hline(
            y=1.0,
            line_dash="dash",
            annotation_text="2018 Baseline"
        )

        trend_fig.update_layout(
            xaxis=dict(
                tickmode="array",
                tickvals=auto_years
            ),
            yaxis_title="Premium Index (Base Year = 1.00)",
            xaxis_title="Year",
            yaxis_tickformat=".2f",
            template="plotly_white",
            legend_title_text=""
        )

        trend_chart = trend_fig.to_html(full_html=False)

    # ---------------------------------------------------
    # BAR CHART
    # ---------------------------------------------------
    bar_chart = px.bar(
        merged_df.sort_values("Premium Index"),
        x="Premium Index",
        y="state",
        orientation="h",
        template="plotly_white"
    ).to_html(full_html=False)

    # ---------------------------------------------------
    # MAP (STATE RISK SCORE)
    # ---------------------------------------------------
    us_map = px.choropleth(
        merged_df,
        locations="state",
        locationmode="USA-states",
        color="Risk Score",
        scope="usa",
        color_continuous_scale=px.colors.sequential.Blues,
        template="plotly_white"
    ).to_html(full_html=False)

    # ---------------------------------------------------
    # TABLE (FINAL ORDER)
    # ---------------------------------------------------
    table_df = (
        merged_df
        .rename(columns={
            "state": "State",
            "disaster_count": "Average Annual Disaster"
        })
        .sort_values("Risk Score", ascending=False)
    )

    table_df["Risk Score"] = table_df["Risk Score"].round(2)
    table_df["Premium Index"] = table_df["Premium Index"].round(2)
    table_df["Average Premium"] = table_df["Average Premium"].map(lambda x: f"${x:,.0f}")

    naic_preview = table_df[
        ["State", "Risk Score", "Average Annual Disaster", "Average Premium", "Premium Index"]
    ].to_html(index=False, classes="table table-striped table-sm")

    # ---------------------------------------------------
    # RETURN PAGE
    # ---------------------------------------------------
    return render(request, "home.html", {
        "insurance_types": insurance_types,
        "selected_insurance": selected_insurance,
        "states": states,
        "years": auto_years,
        "selected_state": selected_state,
        "selected_year": selected_year,
        "risk_score": selected_risk,
        "trend_chart": trend_chart,
        "state_bar_chart": bar_chart,
        "us_map": us_map,
        "naic_preview": naic_preview,
    })

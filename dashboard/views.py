from django.shortcuts import render
from django.conf import settings
import pandas as pd
import os
import plotly.express as px
import numpy as np


def home(request):
    # ---------------------------------------------------
    # LOAD DATA
    # ---------------------------------------------------
    naic_path = os.path.join(settings.BASE_DIR, "data", "clean_naic_auto_insurance.csv")
    fema_path = os.path.join(settings.BASE_DIR, "data", "fema_weather.csv")

    df_naic = pd.read_csv(naic_path)
    df_fema = pd.read_csv(fema_path, low_memory=False)

    # Remove invalid state rows
    df_naic = df_naic[
        df_naic["state"].notna() &
        (df_naic["state"].str.len() == 2)
    ]

    # ---------------------------------------------------
    # NORMALIZE FEMA DATA
    # ---------------------------------------------------
    df_fema["declarationDate"] = pd.to_datetime(
        df_fema["declarationDate"],
        errors="coerce"
    )
    df_fema["year"] = df_fema["declarationDate"].dt.year

    if "state" not in df_fema.columns and "stateCode" in df_fema.columns:
        df_fema["state"] = df_fema["stateCode"]

    fema_counts = (
        df_fema
        .dropna(subset=["year"])
        .groupby(["state", "year"])
        .size()
        .reset_index(name="disaster_count")
    )

    # ---------------------------------------------------
    # FILTER DIMENSIONS
    # ---------------------------------------------------
    years = list(range(2018, 2023))
    states = sorted(df_naic["state"].unique().tolist())

    selected_year = int(request.GET.get("year", years[-1]))
    selected_state = request.GET.get("state", states[0])

    # ---------------------------------------------------
    # STATE vs NATIONAL TREND (INDEXED)
    # ---------------------------------------------------
    national_raw = [df_naic[f"avg_{y}"].mean() for y in years]
    state_row = df_naic[df_naic["state"] == selected_state].iloc[0]
    state_raw = [state_row[f"avg_{y}"] for y in years]

    national_trend = [v / national_raw[0] for v in national_raw]
    state_trend = [v / state_raw[0] for v in state_raw]

    trend_df = pd.DataFrame({
        "Year": years + years,
        "Premium Index": state_trend + national_trend,
        "Type": [selected_state] * len(years) + ["National Avg"] * len(years)
    })

    trend_fig = px.line(
        trend_df,
        x="Year",
        y="Premium Index",
        color="Type",
        markers=True,
        title=f"{selected_state} vs National Premium Trend (Indexed)"
    )

    trend_fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Premium Index (2018 = 1.00)",
        yaxis_tickformat=".2f",
        template="plotly_white",
        legend_title_text=""
    )

    trend_chart = trend_fig.to_html(full_html=False)

    # ---------------------------------------------------
    # PREMIUM + FEMA MERGE
    # ---------------------------------------------------
    year_col = f"avg_{selected_year}"

    premium_df = df_naic[["state", year_col]].rename(
        columns={year_col: "Average Premium"}
    )

    national_avg = premium_df["Average Premium"].mean()
    premium_df["Premium Index"] = premium_df["Average Premium"] / national_avg

    fema_year = fema_counts[fema_counts["year"] == selected_year]

    merged_df = premium_df.merge(
        fema_year,
        on="state",
        how="left"
    )

    merged_df["disaster_count"] = merged_df["disaster_count"].fillna(0)

    disaster_avg = merged_df["disaster_count"].mean()
    merged_df["Disaster Index"] = (
        merged_df["disaster_count"] / disaster_avg if disaster_avg > 0 else 0
    )

    # ---------------------------------------------------
    # COMPOSITE RISK SCORE (TRUE VALUE)
    # ---------------------------------------------------
    merged_df["Risk Score"] = (
        0.6 * merged_df["Premium Index"] +
        0.4 * merged_df["Disaster Index"]
    )

    selected_risk = round(
        merged_df.loc[
            merged_df["state"] == selected_state, "Risk Score"
        ].values[0],
        2
    )

    # ---------------------------------------------------
    # MAP-ONLY LOG SCALE (FOR VISUAL HONESTY)
    # ---------------------------------------------------
    merged_df["Risk Score (Map)"] = np.log1p(merged_df["Risk Score"])

    # ---------------------------------------------------
    # STATE PREMIUM INDEX BAR CHART
    # ---------------------------------------------------
    bar_df = merged_df.sort_values("Premium Index", ascending=True)

    bar_df["Highlight"] = bar_df["state"].apply(
        lambda x: selected_state if x == selected_state else "Other"
    )

    bar_fig = px.bar(
        bar_df,
        x="Premium Index",
        y="state",
        orientation="h",
        color="Highlight",
        color_discrete_map={
            selected_state: "#d62728",
            "Other": "#1f77b4"
        },
        title=f"State Premium Index ({selected_year})",
        hover_data={
            "Average Premium": ":$,.0f",
            "Premium Index": ":.2f",
            "disaster_count": True,
            "Risk Score": ":.2f"
        }
    )

    bar_fig.add_vline(
        x=1.0,
        line_dash="dash",
        line_color="black",
        annotation_text="National Avg"
    )

    bar_fig.update_layout(
        xaxis_title="Premium Index (1.00 = National Average)",
        yaxis_title="State",
        template="plotly_white",
        legend_title_text=""
    )

    state_bar_chart = bar_fig.to_html(full_html=False)

    # ---------------------------------------------------
    # US MAP (LOG-SCALED COLOR, TRUE VALUE ON HOVER)
    # ---------------------------------------------------
    map_fig = px.choropleth(
        merged_df,
        locations="state",
        locationmode="USA-states",
        color="Risk Score (Map)",
        scope="usa",
        color_continuous_scale=px.colors.sequential.Turbo,
        title=f"Composite Risk Score by State ({selected_year})",
        hover_data={
            "Risk Score": ":.2f"
        }
    )

    map_fig.update_coloraxes(
        colorbar=dict(
            title="Relative Risk (Log Scaled)",
            tickformat=".2f"
        )
    )

    map_fig.update_layout(
        template="plotly_white"
    )

    us_map = map_fig.to_html(full_html=False)

    # ---------------------------------------------------
    # TABLE (ALL STATES, SORTED, FORMATTED)
    # ---------------------------------------------------
    rename_map = {f"avg_{y}": str(y) for y in years}
    display_df = df_naic.rename(columns=rename_map)
    display_df = display_df[["state"] + [str(y) for y in years]]

    for y in years:
        display_df[str(y)] = display_df[str(y)] / 1_000_000_000

    display_df = display_df.sort_values(
        by=str(selected_year),
        ascending=False
    )

    national_row = {"state": "National Avg"}
    for y in years:
        national_row[str(y)] = display_df[str(y)].mean()

    display_df = pd.concat(
        [display_df, pd.DataFrame([national_row])],
        ignore_index=True
    )

    for y in years:
        display_df[str(y)] = display_df[str(y)].map(lambda x: f"${x:,.2f}B")

    display_df = display_df.rename(columns={"state": "State"})

    table_html = display_df.to_html(
        index=False,
        classes="table table-striped table-sm",
        escape=False
    )

    table_html = (
        table_html
        .replace("<th>", "<th style='text-align:right;'>")
        .replace("<th>State</th>", "<th style='text-align:left;'>State</th>")
        .replace("<td>", "<td style='text-align:right;'>")
    )

    for s in display_df["State"].unique():
        table_html = table_html.replace(
            f"<td>{s}</td>",
            f"<td style='text-align:left;'>{s}</td>"
        )

    # ---------------------------------------------------
    # CONTEXT
    # ---------------------------------------------------
    context = {
        "states": states,
        "years": years,
        "selected_state": selected_state,
        "selected_year": selected_year,
        "risk_score": selected_risk,
        "trend_chart": trend_chart,
        "state_bar_chart": state_bar_chart,
        "us_map": us_map,
        "naic_preview": table_html,
    }

    return render(request, "home.html", context)

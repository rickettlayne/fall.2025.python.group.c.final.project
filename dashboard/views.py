from django.shortcuts import render
import pandas as pd
import os
from django.conf import settings
import plotly.express as px


def home(request):
    # ---------------------------------------------------
    # Load datasets
    # ---------------------------------------------------
    naic_path = os.path.join(settings.BASE_DIR, "data", "clean_naic_auto_insurance.csv")
    fema_path = os.path.join(settings.BASE_DIR, "data", "fema_weather.csv")

    df_naic = pd.read_csv(naic_path)
    df_naic = df_naic[df_naic["state"].notna()]
    df_fema = pd.read_csv(fema_path, low_memory=False)

    # ---------------------------------------------------
    # NORMALIZE FEMA DATA
    # ---------------------------------------------------
    # Expect a declaration date column
    if "declarationDate" not in df_fema.columns:
        raise ValueError("FEMA file missing declarationDate column")

    df_fema["declarationDate"] = pd.to_datetime(
        df_fema["declarationDate"],
        errors="coerce"
    )

    df_fema["year"] = df_fema["declarationDate"].dt.year

    # Normalize state column
    if "state" not in df_fema.columns:
        if "stateCode" in df_fema.columns:
            df_fema["state"] = df_fema["stateCode"]
        else:
            raise ValueError("FEMA file missing state column")

    # Count disasters by state and year
    fema_counts = (
        df_fema
        .dropna(subset=["year"])
        .groupby(["state", "year"])
        .size()
        .reset_index(name="disaster_count")
    )

    # ---------------------------------------------------
    # Dimensions
    # ---------------------------------------------------
    states = sorted(df_naic["state"].dropna().unique().tolist())
    years = list(range(2018, 2023))

    selected_state = request.GET.get("state", states[0])
    selected_year = int(request.GET.get("year", years[-1]))

    # ---------------------------------------------------
    # STATE vs NATIONAL TREND
    # ---------------------------------------------------
    national_trend = [df_naic[f"avg_{y}"].mean() for y in years]
    state_row = df_naic[df_naic["state"] == selected_state].iloc[0]
    state_trend = [state_row[f"avg_{y}"] for y in years]

    trend_df = pd.DataFrame({
        "Year": years + years,
        "Average Premium": state_trend + national_trend,
        "Type": [selected_state] * len(years) + ["National Avg"] * len(years)
    })

    trend_fig = px.line(
        trend_df,
        x="Year",
        y="Average Premium",
        color="Type",
        markers=True,
        title=f"{selected_state} vs National Auto Insurance Premium Trend"
    )

    trend_fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Average Premium (USD)",
        yaxis_tickprefix="$",
        yaxis_tickformat=",.0f",
        template="plotly_white",
        legend_title_text=""
    )

    trend_chart = trend_fig.to_html(full_html=False)

    # ---------------------------------------------------
    # PREMIUM INDEX
    # ---------------------------------------------------
    year_col = f"avg_{selected_year}"

    index_df = df_naic[["state", year_col]].rename(
        columns={year_col: "Average Premium"}
    )

    national_avg = index_df["Average Premium"].mean()
    index_df["Premium Index"] = index_df["Average Premium"] / national_avg

    # ---------------------------------------------------
    # FEMA DISASTER INDEX
    # ---------------------------------------------------
    fema_year = fema_counts[fema_counts["year"] == selected_year]

    merged_df = index_df.merge(
        fema_year,
        on="state",
        how="left"
    )

    merged_df["disaster_count"] = merged_df["disaster_count"].fillna(0)

    national_disaster_avg = merged_df["disaster_count"].mean()

    merged_df["Disaster Index"] = (
        merged_df["disaster_count"] / national_disaster_avg
        if national_disaster_avg > 0
        else 0
    )

    # ---------------------------------------------------
    # COMPOSITE RISK SCORE
    # ---------------------------------------------------
    merged_df["Risk Score"] = (
        0.6 * merged_df["Premium Index"] +
        0.4 * merged_df["Disaster Index"]
    )

    # ---------------------------------------------------
    # STATE PREMIUM INDEX CHART
    # ---------------------------------------------------
    chart_df = merged_df.sort_values("Premium Index", ascending=False)

    chart_df["Highlight"] = chart_df["state"].apply(
        lambda x: selected_state if x == selected_state else "Other"
    )

    index_fig = px.bar(
        chart_df,
        x="Premium Index",
        y="state",
        orientation="h",
        color="Highlight",
        color_discrete_map={
            selected_state: "#d62728",
            "Other": "#1f77b4"
        },
        title=f"State Auto Insurance Premium Index ({selected_year})",
        hover_data={
            "Average Premium": ":$,.0f",
            "Premium Index": ":.2f",
            "disaster_count": True,
            "Risk Score": ":.2f"
        }
    )

    index_fig.add_vline(
        x=1.0,
        line_dash="dash",
        line_color="black",
        annotation_text="National Avg"
    )

    index_fig.update_layout(
        xaxis_title="Premium Index (1.00 = National Average)",
        yaxis_title="State",
        template="plotly_white",
        legend_title_text=""
    )

    state_comparison_chart = index_fig.to_html(full_html=False)

    # ---------------------------------------------------
    # US MAP (RISK SCORE)
    # ---------------------------------------------------
    map_fig = px.choropleth(
        merged_df,
        locations="state",
        locationmode="USA-states",
        color="Risk Score",
        scope="usa",
        color_continuous_scale="Reds",
        title=f"Composite Insurance & Disaster Risk Score ({selected_year})"
    )

    map_fig.update_layout(
        coloraxis_colorbar=dict(
            title="Risk Score",
            tickformat=".2f"
        ),
        template="plotly_white"
    )

    us_map = map_fig.to_html(full_html=False)

    # ---------------------------------------------------
    # RISK SCORE CARD
    # ---------------------------------------------------
    selected_risk = (
        merged_df[merged_df["state"] == selected_state]["Risk Score"]
        .values[0]
    )

    # ---------------------------------------------------
    # TABLE PREVIEW (ALL STATES, SORTED, FORMATTED)
    # ---------------------------------------------------
    rename_map = {f"avg_{y}": str(y) for y in years}
    display_df = df_naic.rename(columns=rename_map)

    display_df = display_df[["state"] + [str(y) for y in years]]

    # Convert to billions and format
    for y in years:
        display_df[str(y)] = display_df[str(y)] / 1_000_000_000

    # Sort by selected year descending
    display_df = display_df.sort_values(
        by=str(selected_year),
        ascending=False
    )

    # Add National Average row
    national_row = {"state": "National Avg"}
    for y in years:
        national_row[str(y)] = display_df[str(y)].mean()

    display_df = pd.concat(
        [display_df, pd.DataFrame([national_row])],
        ignore_index=True
    )

    # Format display values
    for y in years:
        display_df[str(y)] = display_df[str(y)].map(lambda x: f"${x:,.2f}B")

    # Capitalize State header
    display_df = display_df.rename(columns={"state": "State"})

    table_html = display_df.to_html(
        index=False,
        classes="table table-striped table-sm",
        escape=False
    )

    # Align headers and cells
    table_html = (
        table_html
        .replace("<th>", "<th style='text-align:right;'>")
        .replace("<th>State</th>", "<th style='text-align:left;'>State</th>")
        .replace("<td>", "<td style='text-align:right;'>")
    )

    # Left-align State column cells
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
        "trend_chart": trend_chart,
        "state_bar_chart": state_comparison_chart,
        "us_map": us_map,
        "naic_preview": table_html,
        "risk_score": round(selected_risk, 2)
    }

    return render(request, "home.html", context)

from django.shortcuts import render
import pandas as pd
import os
from django.conf import settings
import plotly.express as px


def home(request):
    # ---------------------------------------------------
    # Load cleaned NAIC auto insurance data
    # ---------------------------------------------------
    naic_path = os.path.join(
        settings.BASE_DIR,
        "data",
        "clean_naic_auto_insurance.csv"
    )
    df = pd.read_csv(naic_path)

    # ---------------------------------------------------
    # Dimensions
    # ---------------------------------------------------
    states = sorted(df["state"].dropna().unique().tolist())
    years = list(range(2018, 2023))

    selected_state = request.GET.get("state", states[0])
    selected_year = int(request.GET.get("year", years[-1]))

    # ---------------------------------------------------
    # STATE vs NATIONAL TREND
    # ---------------------------------------------------
    national_trend = [df[f"avg_{y}"].mean() for y in years]
    state_row = df[df["state"] == selected_state].iloc[0]
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
    # STATE COMPARISON (SCATTER WITH LOG SCALE)
    # ---------------------------------------------------
    year_col = f"avg_{selected_year}"

    scatter_df = df[["state", year_col]].rename(
        columns={year_col: "Average Premium"}
    )

    scatter_df = scatter_df.sort_values("Average Premium", ascending=False)

    scatter_df["Highlight"] = scatter_df["state"].apply(
        lambda x: selected_state if x == selected_state else "Other"
    )

    scatter_fig = px.scatter(
        scatter_df,
        x="Average Premium",
        y="state",
        color="Highlight",
        color_discrete_map={
            selected_state: "#d62728",
            "Other": "#1f77b4"
        },
        title=f"Auto Insurance Premiums by State ({selected_year})",
        hover_data={
            "Average Premium": ":$,.0f"
        }
    )

    scatter_fig.update_layout(
        xaxis_title="Total Premiums (USD, Log Scale)",
        yaxis_title="State",
        xaxis_type="log",
        template="plotly_white",
        legend_title_text=""
    )

    state_comparison_chart = scatter_fig.to_html(full_html=False)

    # ---------------------------------------------------
    # US MAP
    # ---------------------------------------------------
    map_fig = px.choropleth(
        scatter_df,
        locations="state",
        locationmode="USA-states",
        color="Average Premium",
        scope="usa",
        color_continuous_scale="Blues",
        title=f"Average Auto Insurance Premiums by State ({selected_year})"
    )

    selected_state_df = scatter_df[scatter_df["state"] == selected_state]

    map_fig.add_choropleth(
        locations=selected_state_df["state"],
        locationmode="USA-states",
        z=[selected_state_df["Average Premium"].values[0]],
        colorscale=[[0, "#d62728"], [1, "#d62728"]],
        showscale=False,
        marker_line_color="black",
        marker_line_width=2
    )

    map_fig.update_layout(
        coloraxis_colorbar=dict(
            title="Premium (USD)",
            tickprefix="$",
            tickformat=",.0f"
        ),
        template="plotly_white"
    )

    us_map = map_fig.to_html(full_html=False)

    # ---------------------------------------------------
    # TABLE PREVIEW
    # ---------------------------------------------------
    rename_map = {f"avg_{y}": str(y) for y in years}
    display_df = df.rename(columns=rename_map)
    display_df = display_df[["state"] + [str(y) for y in years]]

    table_html = display_df.head().to_html(
        index=False,
        classes="table table-striped table-sm"
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
        "naic_preview": table_html
    }

    return render(request, "home.html", context)

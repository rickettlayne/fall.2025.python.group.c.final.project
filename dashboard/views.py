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
    # NATIONAL vs STATE TREND (line chart)
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
        yaxis_title="Average Premium (USD)",
        xaxis_title="Year",
        template="plotly_white",
        legend_title_text=""
    )

    trend_chart = trend_fig.to_html(full_html=False)

    # ---------------------------------------------------
    # STATE COMPARISON BAR CHART (selected year)
    # ---------------------------------------------------
    year_col = f"avg_{selected_year}"

    bar_df = df[["state", year_col]].rename(
        columns={year_col: "Average Premium"}
    )

    bar_fig = px.bar(
        bar_df,
        x="state",
        y="Average Premium",
        title=f"Auto Insurance Premiums by State ({selected_year})"
    )

    bar_fig.update_layout(
        xaxis_title="State",
        yaxis_title="Average Premium (USD)",
        template="plotly_white"
    )

    state_bar_chart = bar_fig.to_html(full_html=False)

    # ---------------------------------------------------
    # TABLE PREVIEW (rename avg_YYYY -> YYYY)
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
        "naic_preview": table_html,
        "trend_chart": trend_chart,
        "state_bar_chart": state_bar_chart
    }

    return render(request, "home.html", context)

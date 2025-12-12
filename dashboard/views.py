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
    # Compute national averages by year
    # ---------------------------------------------------
    year_avgs = {}
    for year in years:
        col = f"avg_{year}"
        if col in df.columns:
            year_avgs[year] = round(df[col].mean(), 2)

    # ---------------------------------------------------
    # Build national trend dataframe
    # ---------------------------------------------------
    trend_df = pd.DataFrame({
        "Year": list(year_avgs.keys()),
        "Average Premium": list(year_avgs.values())
    })

    # ---------------------------------------------------
    # Create Plotly line chart
    # ---------------------------------------------------
    fig = px.line(
        trend_df,
        x="Year",
        y="Average Premium",
        markers=True,
        title="National Average Auto Insurance Premium Trend"
    )

    fig.update_layout(
        yaxis_title="Average Premium (USD)",
        xaxis_title="Year",
        template="plotly_white"
    )

    trend_chart = fig.to_html(full_html=False)

    # ---------------------------------------------------
    # Prepare table for display
    # ---------------------------------------------------
    rename_map = {f"avg_{y}": str(y) for y in years}
    display_df = df.rename(columns=rename_map)
    display_df = display_df[["state"] + [str(y) for y in years]]

    table_html = display_df.head().to_html(
        index=False,
        classes="table table-striped table-sm"
    )

    # ---------------------------------------------------
    # Context
    # ---------------------------------------------------
    context = {
        "states": states,
        "years": years,
        "selected_state": selected_state,
        "selected_year": selected_year,
        "year_avgs": year_avgs,
        "naic_preview": table_html,
        "trend_chart": trend_chart
    }

    return render(request, "home.html", context)

from django.shortcuts import render
from django.conf import settings
import pandas as pd
import os
import plotly.express as px


def home(request):
    base_dir = settings.BASE_DIR

    # ---------------------------------------------------
    # LOAD DATA
    # ---------------------------------------------------
    df_auto = pd.read_csv(os.path.join(base_dir, "data", "clean_naic_auto_insurance.csv"))
    df_home = pd.read_csv(os.path.join(base_dir, "data", "clean_nerdwallet_home.csv"))
    df_fema = pd.read_csv(os.path.join(base_dir, "data", "clean_fema_weather.csv"), low_memory=False)
    df_noaa = pd.read_csv(os.path.join(base_dir, "data", "clean_noaa_weather.csv"))

    # ---------------------------------------------------
    # BASIC CLEANUP
    # ---------------------------------------------------
    def clean_states(df, col="state"):
        if col not in df.columns:
            return df.iloc[0:0].copy()
        out = df[df[col].notna()].copy()
        out[col] = (
            out[col]
            .astype(str)
            .str.strip()
            .str.upper()
            .str.replace(".", "", regex=False)
        )
        # keep two character codes only
        out = out[out[col].str.len() == 2]
        return out

    df_auto = clean_states(df_auto, "state")
    df_home = clean_states(df_home, "state")
    df_fema = clean_states(df_fema, "state")
    df_noaa = clean_states(df_noaa, "state")

    # try to force numeric where relevant
    for col in df_auto.columns:
        if col.startswith("avg_"):
            df_auto[col] = pd.to_numeric(df_auto[col], errors="coerce")

    if "avg_annual_usd" in df_home.columns:
        df_home["avg_annual_usd"] = pd.to_numeric(df_home["avg_annual_usd"], errors="coerce")

    # ---------------------------------------------------
    # INSURANCE TYPE AND YEAR SELECTION
    # ---------------------------------------------------
    insurance_types = ["Auto", "Home"]
    selected_insurance = request.GET.get("insurance", "Auto").capitalize()
    if selected_insurance not in insurance_types:
        selected_insurance = "Auto"

    auto_years = list(range(2018, 2023))
    selected_year_param = request.GET.get("year", str(auto_years[-1]))

    if selected_insurance == "Auto":
        try:
            selected_year = int(selected_year_param)
        except ValueError:
            selected_year = auto_years[-1]
        states = sorted(df_auto["state"].unique().tolist())
    else:
        # Home data is effectively a single snapshot year
        selected_year = "Current (2025)"
        states = sorted(df_home["state"].unique().tolist())

    if not states:
        states = ["TX"]

    selected_state = request.GET.get("state", states[0])
    if selected_state not in states:
        selected_state = states[0]

    # ---------------------------------------------------
    # BUILD INSURANCE DATAFRAME: df_ins
    # ---------------------------------------------------
    if selected_insurance == "Auto":
        year_col = f"avg_{selected_year}"
        if year_col not in df_auto.columns:
            # fail safe, default to last known year
            year_col = "avg_2022"

        df_ins = (
            df_auto[["state", year_col]]
            .rename(columns={year_col: "Average Premium"})
            .groupby("state", as_index=False)
            .agg({"Average Premium": "mean"})
        )
    else:
        # Home: single snapshot
        df_ins = (
            df_home
            .rename(columns={"avg_annual_usd": "Average Premium"})
            .groupby("state", as_index=False)
            .agg({"Average Premium": "mean"})
        )

    # drop states with missing premium
    df_ins = df_ins.dropna(subset=["Average Premium"])

    # ---------------------------------------------------
    # FEMA: DISASTER COUNTS AND SEVERITY
    # ---------------------------------------------------
    if "declarationDate" in df_fema.columns:
        df_fema["declarationDate"] = pd.to_datetime(
            df_fema["declarationDate"], errors="coerce"
        )

    # basic frequency by state
    fema_counts = (
        df_fema
        .groupby("state", as_index=False)
        .agg(disaster_count=("state", "count"))
    )

    # severity by incident type
    if "incidentType" in df_fema.columns:
        tmp = df_fema.dropna(subset=["incidentType"]).copy()
        tmp["incidentTypeClean"] = tmp["incidentType"].astype(str).str.upper()

        def map_incident(cat):
            if "HURRICANE" in cat or "TROPICAL" in cat:
                return "Hurricane"
            if "FLOOD" in cat:
                return "Flood"
            if "FIRE" in cat or "WILDFIRE" in cat:
                return "Fire"
            if "STORM" in cat or "TORNADO" in cat or "WIND" in cat or "HAIL" in cat:
                return "Severe Storm"
            if "SNOW" in cat or "BLIZZARD" in cat or "FREEZE" in cat or "WINTER" in cat or "ICE" in cat:
                return "Winter"
            return "Other"

        tmp["incident_group"] = tmp["incidentTypeClean"].apply(map_incident)

        grp = (
            tmp.groupby(["state", "incident_group"])
            .size()
            .reset_index(name="count")
        )

        # weight by perceived severity
        severity_weights = {
            "Hurricane": 2.0,
            "Flood": 1.7,
            "Fire": 1.8,
            "Severe Storm": 1.4,
            "Winter": 1.2,
            "Other": 1.0,
        }

        grp["weight"] = grp["incident_group"].map(severity_weights).fillna(1.0)
        grp["severity_score_part"] = grp["count"] * grp["weight"]

        fema_severity = (
            grp.groupby("state", as_index=False)
            .agg(severity_score=("severity_score_part", "sum"))
        )
    else:
        fema_severity = pd.DataFrame({"state": df_ins["state"].unique(), "severity_score": 1.0})

    # ---------------------------------------------------
    # NOAA WEATHER INDEX
    # ---------------------------------------------------
    weather_index_df = None
    if not df_noaa.empty:
        if "year" in df_noaa.columns:
            df_noaa["year"] = pd.to_numeric(df_noaa["year"], errors="coerce")

        numeric_cols = [
            c for c in df_noaa.columns
            if c not in ["state", "year"] and pd.api.types.is_numeric_dtype(df_noaa[c])
        ]

        if numeric_cols:
            noaa_state = (
                df_noaa
                .groupby("state", as_index=False)[numeric_cols]
                .mean()
            )
            noaa_state["weather_score_raw"] = noaa_state[numeric_cols].mean(axis=1)
            w_mean = noaa_state["weather_score_raw"].mean()
            if w_mean and w_mean != 0:
                noaa_state["Weather Index"] = noaa_state["weather_score_raw"] / w_mean
            else:
                noaa_state["Weather Index"] = 1.0
            weather_index_df = noaa_state[["state", "Weather Index"]]
        else:
            weather_index_df = pd.DataFrame(
                {"state": df_ins["state"].unique(), "Weather Index": 1.0}
            )
    else:
        weather_index_df = pd.DataFrame(
            {"state": df_ins["state"].unique(), "Weather Index": 1.0}
        )

    # ---------------------------------------------------
    # MERGE INSURANCE, FEMA, NOAA
    # ---------------------------------------------------
    merged_df = df_ins.merge(fema_counts, on="state", how="left")
    merged_df = merged_df.merge(fema_severity, on="state", how="left")
    merged_df = merged_df.merge(weather_index_df, on="state", how="left")

    merged_df["disaster_count"] = merged_df["disaster_count"].fillna(0)
    merged_df["severity_score"] = merged_df["severity_score"].fillna(
        merged_df["severity_score"].mean() if not merged_df["severity_score"].isna().all() else 1.0
    )
    merged_df["Weather Index"] = merged_df["Weather Index"].fillna(1.0)

    # ---------------------------------------------------
    # PREMIUM INDEX AND COMPONENT INDICES
    # ---------------------------------------------------
    merged_df["Premium Index"] = merged_df["Average Premium"] / merged_df["Average Premium"].mean()

    disaster_mean = merged_df["disaster_count"].mean()
    if disaster_mean and disaster_mean != 0:
        merged_df["Disaster Index"] = merged_df["disaster_count"] / disaster_mean
    else:
        merged_df["Disaster Index"] = 1.0

    severity_mean = merged_df["severity_score"].mean()
    if severity_mean and severity_mean != 0:
        merged_df["Severity Index"] = merged_df["severity_score"] / severity_mean
    else:
        merged_df["Severity Index"] = 1.0

    if "Weather Index" not in merged_df.columns:
        merged_df["Weather Index"] = 1.0

    # ---------------------------------------------------
    # FINAL RISK SCORE
    # ---------------------------------------------------
    merged_df["Risk Score"] = (
        0.5 * merged_df["Premium Index"]
        + 0.3 * merged_df["Severity Index"]
        + 0.2 * merged_df["Weather Index"]
    )

    # risk score for header card
    if selected_state in merged_df["state"].values:
        selected_risk = round(
            merged_df.loc[merged_df["state"] == selected_state, "Risk Score"].values[0],
            2,
        )
    else:
        selected_risk = 1.0

    # ---------------------------------------------------
    # TREND CHART (AUTO ONLY)
    # ---------------------------------------------------
    trend_chart = None

    if selected_insurance == "Auto":
        base_year = auto_years[0]

        trend_rows = []

        nat_base = df_auto[f"avg_{base_year}"].mean()

        for y in auto_years:
            nat_val = df_auto[f"avg_{y}"].mean()
            trend_rows.append(
                {
                    "Year": int(y),
                    "Premium Index": nat_val / nat_base if nat_base else 1.0,
                    "Series": "National Avg",
                }
            )

        # if state exists in df_auto
        if selected_state in df_auto["state"].values:
            state_row = df_auto[df_auto["state"] == selected_state].iloc[0]
            state_base = state_row[f"avg_{base_year}"]
            for y in auto_years:
                val = state_row[f"avg_{y}"]
                trend_rows.append(
                    {
                        "Year": int(y),
                        "Premium Index": val / state_base if state_base else 1.0,
                        "Series": selected_state,
                    }
                )

        trend_df = pd.DataFrame(trend_rows)
        trend_df["Year"] = trend_df["Year"].astype(int)
        trend_df = trend_df.sort_values("Year")

        trend_fig = px.line(
            trend_df,
            x="Year",
            y="Premium Index",
            color="Series",
            markers=True,
            title="Auto Insurance Premium Trend, indexed to base year",
        )

        trend_fig.add_hline(
            y=1.0,
            line_dash="dash",
            annotation_text=f"{base_year} baseline",
        )

        trend_fig.update_layout(
            xaxis=dict(
                type="linear",
                tickmode="array",
                tickvals=auto_years,
            ),
            yaxis_title="Premium Index",
            xaxis_title="Year",
            yaxis_tickformat=".2f",
            template="plotly_white",
            legend_title_text="",
        )

        trend_chart = trend_fig.to_html(full_html=False)

    # ---------------------------------------------------
    # NOAA WEATHER TREND CHART (STATE vs NATIONAL)
    # ---------------------------------------------------
    weather_trend_chart = None
    try:
        noaa_state = df_noaa[df_noaa["state"] == selected_state].copy()
        if not noaa_state.empty and "year" in noaa_state.columns:
            noaa_state["year"] = pd.to_numeric(noaa_state["year"], errors="coerce")
            numeric_cols = [
                c for c in noaa_state.columns
                if c not in ["state", "year"] and pd.api.types.is_numeric_dtype(noaa_state[c])
            ]

            if numeric_cols:
                metric = numeric_cols[0]

                state_series = (
                    noaa_state
                    .groupby("year", as_index=False)[metric]
                    .mean()
                    .rename(columns={metric: "State Value"})
                )

                nat_series = (
                    df_noaa
                    .groupby("year", as_index=False)[metric]
                    .mean()
                    .rename(columns={metric: "National Value"})
                )

                joined = state_series.merge(nat_series, on="year", how="inner")
                melted = joined.melt(
                    id_vars="year",
                    value_vars=["State Value", "National Value"],
                    var_name="Series",
                    value_name="Value",
                )

                weather_fig = px.line(
                    melted,
                    x="year",
                    y="Value",
                    color="Series",
                    markers=True,
                    title=f"NOAA weather trend for {selected_state}",
                )

                weather_fig.update_layout(
                    xaxis_title="Year",
                    yaxis_title=metric,
                    template="plotly_white",
                    legend_title_text="",
                )

                weather_trend_chart = weather_fig.to_html(full_html=False)
    except Exception:
        weather_trend_chart = None

    # ---------------------------------------------------
    # FEMA BREAKDOWN CHART FOR SELECTED STATE
    # ---------------------------------------------------
    fema_breakdown_chart = None
    try:
        if "incidentType" in df_fema.columns:
            tmp_state = df_fema[df_fema["state"] == selected_state].copy()
            if not tmp_state.empty:
                tmp_state["incidentTypeClean"] = tmp_state["incidentType"].astype(str).str.upper()

                def map_incident_chart(cat):
                    if "HURRICANE" in cat or "TROPICAL" in cat:
                        return "Hurricane"
                    if "FLOOD" in cat:
                        return "Flood"
                    if "FIRE" in cat or "WILDFIRE" in cat:
                        return "Fire"
                    if "STORM" in cat or "TORNADO" in cat or "WIND" in cat or "HAIL" in cat:
                        return "Severe Storm"
                    if "SNOW" in cat or "BLIZZARD" in cat or "FREEZE" in cat or "WINTER" in cat or "ICE" in cat:
                        return "Winter"
                    return "Other"

                tmp_state["incident_group"] = tmp_state["incidentTypeClean"].apply(map_incident_chart)

                grp_state = (
                    tmp_state.groupby("incident_group")
                    .size()
                    .reset_index(name="count")
                )

                fema_fig = px.pie(
                    grp_state,
                    names="incident_group",
                    values="count",
                    title=f"FEMA disaster mix for {selected_state}",
                )

                fema_fig.update_layout(template="plotly_white")
                fema_breakdown_chart = fema_fig.to_html(full_html=False)
    except Exception:
        fema_breakdown_chart = None

    # ---------------------------------------------------
    # CORRELATION SCATTER: DISASTER vs PREMIUM INDEX
    # ---------------------------------------------------
    correlation_chart = None
    try:
        corr_df = merged_df.dropna(subset=["disaster_count", "Premium Index"]).copy()
        if not corr_df.empty:
            corr_fig = px.scatter(
                corr_df,
                x="disaster_count",
                y="Premium Index",
                hover_name="state",
                title="Relation between disaster frequency and premium index",
            )
            corr_fig.update_layout(
                xaxis_title="Total FEMA disasters",
                yaxis_title="Premium Index",
                template="plotly_white",
            )
            correlation_chart = corr_fig.to_html(full_html=False)
    except Exception:
        correlation_chart = None

    # ---------------------------------------------------
    # STATE BAR CHART (PREMIUM INDEX)
    # ---------------------------------------------------
    bar_df = merged_df.sort_values("Premium Index", ascending=True).copy()
    bar_df["Highlight"] = bar_df["state"].apply(
        lambda s: selected_state if s == selected_state else "Other"
    )

    bar_fig = px.bar(
        bar_df,
        x="Premium Index",
        y="state",
        orientation="h",
        color="Highlight",
        color_discrete_map={
            selected_state: "#d62728",
            "Other": "#1f77b4",
        },
        title=f"{selected_insurance} premium index by state",
        hover_data={
            "Average Premium": ":$,.0f",
            "Premium Index": ":.2f",
            "disaster_count": True,
            "Risk Score": ":.2f",
        },
    )

    bar_fig.add_vline(
        x=1.0,
        line_dash="dash",
        line_color="black",
        annotation_text="National average",
    )

    bar_fig.update_layout(
        xaxis_title="Premium Index",
        yaxis_title="State",
        template="plotly_white",
        legend_title_text="",
    )

    state_bar_chart = bar_fig.to_html(full_html=False)

    # ---------------------------------------------------
    # TABLE: RISK VIEW BY STATE
    # ---------------------------------------------------
    table_df = (
        merged_df
        .rename(columns={
            "state": "State",
            "disaster_count": "Average Annual Disaster",
        })
        .sort_values("Risk Score", ascending=False)
    )

    table_df["Risk Score"] = table_df["Risk Score"].round(2)
    table_df["Premium Index"] = table_df["Premium Index"].round(2)
    table_df["Severity Index"] = table_df["Severity Index"].round(2)
    table_df["Weather Index"] = table_df["Weather Index"].round(2)
    table_df["Average Premium"] = table_df["Average Premium"].map(lambda x: f"${x:,.0f}")

    table_df = table_df[
        [
            "State",
            "Risk Score",
            "Average Annual Disaster",
            "Average Premium",
            "Premium Index",
            "Severity Index",
            "Weather Index",
        ]
    ]

    naic_preview = table_df.to_html(
        index=False,
        classes="table table-striped table-sm",
        escape=False,
    )

    # ---------------------------------------------------
    # CONTEXT
    # ---------------------------------------------------
    context = {
        "insurance_types": insurance_types,
        "selected_insurance": selected_insurance,
        "states": states,
        "years": auto_years,
        "selected_state": selected_state,
        "selected_year": selected_year,
        "risk_score": selected_risk,
        "trend_chart": trend_chart,
        "weather_trend_chart": weather_trend_chart,
        "fema_breakdown_chart": fema_breakdown_chart,
        "correlation_chart": correlation_chart,
        "state_bar_chart": state_bar_chart,
        "us_map": px.choropleth(
            merged_df,
            locations="state",
            locationmode="USA-states",
            color="Risk Score",
            scope="usa",
            color_continuous_scale=px.colors.sequential.Blues,
            template="plotly_white",
        ).to_html(full_html=False),
        "naic_preview": naic_preview,
    }

    return render(request, "home.html", context)

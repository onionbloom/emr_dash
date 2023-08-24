from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash_bootstrap_templates import load_figure_template
from dateutil.relativedelta import relativedelta
from plotly.subplots import make_subplots

from dataframes import get_deps, get_df, get_dr

template = load_figure_template("minty")
colseq = list(px.colors.qualitative.Set3) + list(px.colors.qualitative.Pastel)


def get_x_period(period):
    if period == "W":
        x0 = datetime.now() - relativedelta(days=+32)
        x1 = datetime.now() + relativedelta(days=+28)
    elif period == "M":
        x0 = datetime.now() - relativedelta(months=+3)
        x1 = datetime.now() + relativedelta(months=+3)

    x_period = [x0.strftime("%Y-%m-%d"), x1.strftime("%Y-%m-%d")]

    return x_period


def plotMonFH(period=3, regs=[]):
    """
    This function plots the monthly FH summary
    """

    # Get the dataframe
    df = get_df("ac_util.csv")
    df["Start"] = pd.to_datetime(df["Start"])
    df["TAH/Diff"] = df["TAH/Diff"].round(2)
    df = df.rename(columns={"A/C": "ac_reg"})

    # Filter
    queryPeriod = (df["Start"].dt.month > datetime.now().month - period) & (
        df["Start"].dt.year == datetime.now().year
    )
    queryRegs = df["ac_reg"].isin(regs)
    df = (
        df[queryPeriod & queryRegs]
        .drop(columns=["A/C Group", "End"])
        .sort_values("ac_reg")
    )

    # Create figure
    fig = px.bar(
        df,
        x="Start",
        y="TAH/Diff",
        color="ac_reg",
        color_discrete_sequence=colseq,
        template=template,
        barmode="group",
        text="ac_reg",
        labels={"TAH/Diff": "Flight Hours"},
        hover_data={"ac_reg": False, "Start": False},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
        xaxis=dict(title="Month", dtick="M1"),
        yaxis=dict(title="Flight Hours"),
        title_text=f"{period}-month Period Flying Hours",
        title_xanchor="center",
        title_x=0.5,
        title_y=0.95,
        modebar=dict(orientation="v", remove=["zoom", "lasso", "autoscale"]),
    )

    return fig


# Plot previous month's new HIL's by ATA
def plotMEL(period=3):
    raw = get_df("mel_use.csv")
    raw["Start"] = pd.to_datetime(raw["Start"])
    df = raw[
        (raw["Start"].dt.month > datetime.now().month - period)
        & (raw["Start"].dt.year == datetime.now().year)
    ].drop(columns=["A/C Group", "End", "Usage %"])

    fig = px.bar(df, x="Start", y="MEL W/Os", color="MEL Code", barmode="group")
    fig.update_layout(
        title_text=f"Previous {period}-Month MEL Use",
        title_xanchor="center",
        title_yanchor="top",
        title_x=0.5,
        title_y=0.95,
        xaxis=dict(title="Month", type="date", dtick="M1"),
        yaxis=dict(title="MEL Raised"),
        modebar=dict(orientation="v", remove=["zoom", "lasso", "autoscale"]),
    )

    return fig


# Plot country map
def plotCountry(period, regs):
    # Get the dataframe
    df = get_deps(period, regs)

    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lng",
        color="Serv.Type",
        text="city",
        size="Serv.Type",
        scope="asia",
        hover_data={"lat": False, "lng": False},
        labels={"Serv.Type": "Rev. Flights"},
    )
    fig.update_traces(hovertemplate="%{marker.size} departures")
    fig.update_geos(
        fitbounds="locations", resolution=50, visible=False, showcountries=True
    )
    fig.update_layout(
        title_text=f"{period}-month Period Departure Counts",
        title_xanchor="center",
        title_x=0.5,
        title_y=0.95,
    )

    return fig


# Plot monthly tech. DR
def plotTechDR(period):
    # Get the monthly tech DR df
    df = get_dr(period=period)
    subfig = make_subplots(
        specs=[[{"secondary_y": True}]]
    )  # make a figure with secondary y axis

    fig0 = px.line(
        df,
        x=df.index.to_timestamp("M", "s"),
        y=["dr"],
        template=template,
        line_shape="spline",
        markers=True,
    )
    fig0.update_traces(
        yaxis="y2",
        hovertemplate="<br>Period: %{x} <br>Tech DR: %{y}",
        textposition="bottom center",
    )

    fig1 = px.bar(
        df,
        x=df.index.to_timestamp("M", "s"),
        y=["TAC acc."],
        template=template,
    )
    fig1.update_traces(
        hovertemplate="<br>Period: %{x} <br>Revenue Flights: %{y}",
        marker_line_width=0,
        width=86400000 * 20,  # Width of the bars in miliseconds times days
        marker_color="#6CC3D4",
    )

    subfig.add_traces(fig1.data + fig0.data)  # Combine the figures
    newnames = {"dr": "Technical DR", "TAC acc.": "Cycles"}
    subfig.for_each_trace(
        lambda x: x.update(
            name=newnames[x.name],
            legendgroup=newnames[x.name],
            hovertemplate=x.hovertemplate.replace(
                x.name,
                newnames[x.name],
            ),
        )
    )
    subfig.update_layout(
        title_text=f"{period}-Month Dispatch Reliability and Utilization",
        title_xanchor="center",
        title_x=0.5,
        xaxis=dict(
            title="Month",
            type="date",
            dtick="M1",
            ticks="outside",
            ticklen=10,
            tickformat="%b \n%Y",
        ),
        yaxis=dict(
            title="Flight Cycles",
            dtick=200,
            range=[600, 1000],
            tickmode="linear",
        ),
        yaxis2=dict(
            title="Tech. DR",
            range=[90, 100],
            dtick=2,
            tickmode="linear",
        ),
        hovermode="x unified",
        showlegend=False,
    )

    return subfig

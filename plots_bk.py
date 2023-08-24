from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash_bootstrap_templates import load_figure_template
from dateutil.relativedelta import relativedelta
from plotly.subplots import make_subplots


from dataframes import get_deps, get_df

util_df = get_util_df()
oil_consum = get_fluids_df()

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


def plotMonFC(period="1M"):
    """
    This function plots the monthly FC summary
    """

    if period == "0":
        period = "1M"
    else:
        period = period + "M"

    # Get the dataframe and filter the last 'period' months
    df = get_mon_util_df().last(period).groupby("AC").sum()
    annotTAH = df["TAC_PERIOD"].round(2)
    fig = px.bar(df, x=df.index, y=["TAC_PERIOD"], template=template, text=annotTAH)
    fig.update_traces(
        hovertemplate="%{y}",
        marker_line_width=0,
        width=0.97,
        marker_color="#6CC3D4",
        textposition="outside",
    )
    newnames = {"TAC_PERIOD": f"Cycles for {period} Period"}
    fig.for_each_trace(
        lambda x: x.update(
            name=newnames[x.name],
            legendgroup=newnames[x.name],
            hovertemplate=x.hovertemplate.replace(x.name, newnames[x.name]),
        )
    )
    fig.update_layout(
        title_text=f"Revenue Cycles For a {period} Period",
        title_xanchor="center",
        title_x=0.5,
        xaxis=dict(title="Registration"),
        yaxis=dict(title="Total Cycles", period=[80, 300]),
        modebar=dict(orientation="v", remove=["zoom", "lasso", "autoscale"]),
        title_yanchor="top",
        title_y=0.95,
        hovermode="x unified",
        legend_x=0.7,
    )

    return fig


def plotAvgFhDay(period="1M"):
    """
    This function plots the daily flight hour average for each aircraft.
    """

    if period == "0":
        period = "1M"
    else:
        period = period + "M"

    # Get the dataframe and filter the last 'period' months
    df = get_mon_util_df().last(period).groupby("AC").sum()
    df["AVG_HRS_PER_DAY"] = df["TAH_PERIOD"] / df["OP_DAYS"]
    annot = df["AVG_HRS_PER_DAY"].round(2)
    fig = px.bar(df, x=df.index, y=["AVG_HRS_PER_DAY"], template=template, text=annot)
    fig.update_traces(
        hovertemplate="%{y}",
        marker_line_width=0,
        width=0.97,
        marker_color="#6CC3D4",
        textposition="outside",
    )
    newnames = {"AVG_HRS_PER_DAY": "Daily FH Average"}
    fig.for_each_trace(
        lambda x: x.update(
            name=newnames[x.name],
            legendgroup=newnames[x.name],
            hovertemplate=x.hovertemplate.replace(x.name, newnames[x.name]),
        )
    )
    fig.update_layout(
        title_text=f"Daily Average Hours For a {period} Period",
        title_xanchor="center",
        title_x=0.5,
        xaxis=dict(title="Registration"),
        yaxis=dict(title="Average Hours", period=[0, 10]),
        modebar=dict(orientation="v", remove=["zoom", "lasso", "autoscale"]),
        title_yanchor="top",
        title_y=0.95,
        hovermode="x unified",
        legend_x=0.7,
    )

    return fig


def plotAvgFcDay(period="1M"):
    """
    This function plots the daily flight hour average for each aircraft.
    """

    if period == "0":
        period = "1M"
    else:
        period = period + "M"

    # Get the dataframe and filter the last 'period' months
    df = get_mon_util_df().last(period).groupby("AC").sum()
    df["AVG_CYC_PER_DAY"] = df["TAC_PERIOD"] / df["OP_DAYS"]
    annot = df["AVG_CYC_PER_DAY"].round(2)
    fig = px.bar(df, x=df.index, y=["AVG_CYC_PER_DAY"], template=template, text=annot)
    fig.update_traces(
        hovertemplate="%{y}",
        marker_line_width=0,
        width=0.97,
        marker_color="#6CC3D4",
        textposition="outside",
    )
    newnames = {"AVG_CYC_PER_DAY": "Daily FC Average"}
    fig.for_each_trace(
        lambda x: x.update(
            name=newnames[x.name],
            legendgroup=newnames[x.name],
            hovertemplate=x.hovertemplate.replace(x.name, newnames[x.name]),
        )
    )
    fig.update_layout(
        title_text=f"Daily Average Cycles For a {period} Period",
        title_xanchor="center",
        title_x=0.5,
        xaxis=dict(title="Registration"),
        yaxis=dict(title="Average Cycles", period=[0, 10]),
        modebar=dict(orientation="v", remove=["zoom", "lasso", "autoscale"]),
        title_yanchor="top",
        title_y=0.95,
        hovermode="x unified",
        legend_x=0.7,
    )

    return fig


# Plots the monthly FC utilization summary
def plotFl(weekly):
    """
    This function plots the dispatch reliability and utilization in cycles. Can show weekly or monthly plot depending on the state of the selector in the app.
    """

    if weekly:
        # Create dataframe for weekly DR
        df = util_df.groupby(pd.Grouper(key="TO_DATETIME", freq="W-WED"))[
            ["CYC", "DELAY", "IMPACT_DEL"]
        ].sum()
        df["DR"] = (df["CYC"] - df["DELAY"]) * 100 / df["CYC"]

        subfig = make_subplots(specs=[[{"secondary_y": True}]])
        dr_target = [97.00, 97.00]

        annotDR = df["DR"].round(decimals=2)  # Y annotations for the DR line plot
        fig2 = px.line(
            df,
            x=df.index,
            y=["DR"],
            template=template,
            line_shape="spline",
            markers=True,
            text=annotDR,
        )
        fig2.add_trace(
            go.Scatter(
                x=["2020-05-01", "2030-05-01"],
                y=dr_target,
                name="DR Target",
                line=dict(color="#F3969A", dash="dash", width=1),
            )
        )
        fig2.update_traces(
            yaxis="y2",
            hovertemplate="<br>Up to: %{x} <br>Dispatch Reliability: %{y}",
            textposition="bottom center",
        )
        annotCycles = df["CYC"].astype("int")  # Y annotations for the cycles bar plot
        fig = px.bar(df, x=df.index, y=["CYC"], template=template, text=annotCycles)
        fig.update_traces(
            hovertemplate="<br>Up to: %{x} <br>Revenue Flights: %{y}",
            marker_line_width=0,
            width=86400000 * 6,
            marker_color="#6CC3D4",
            textposition="outside",
        )

        subfig.add_traces(fig.data + fig2.data)
        newnames = {
            "DR": "Dispatch Reliability",
            "CYC": "Cycles",
            "DR Target": "DR Target",
        }
        subfig.for_each_trace(
            lambda x: x.update(
                name=newnames[x.name],
                legendgroup=newnames[x.name],
                hovertemplate=x.hovertemplate.replace(x.name, newnames[x.name]),
            )
        )
        subfig.update_layout(
            title_text="Weekly Dispatch Reliability and Utilization",
            title_xanchor="center",
            title_x=0.5,
            xaxis=dict(
                title="Month",
                type="date",
                dtick="M1",
                period=get_x_period("W"),
                ticklabelmode="period",
                ticks="outside",
                ticklen=10,
                minor=dict(
                    ticklen=4,
                    dtick=1000 * 60 * 60 * 24 * 7,
                ),
            ),
            yaxis=dict(
                title="Number of Flights", dtick=60, tickmode="linear", period=[0, 240]
            ),
            yaxis2=dict(
                title="Dispatch Reliability",
                tick0=85,
                dtick=5,
                period=[85, 105],
                tickmode="linear",
            ),
            modebar=dict(orientation="v", remove=["zoom", "lasso", "autoscale"]),
            title_yanchor="top",
            title_y=0.95,
            hovermode="x unified",
            legend_x=0.7,
        )
    else:
        # Create dataframe for Monthly DR
        df = util_df.groupby(pd.Grouper(key="TO_DATETIME", freq="M"))[
            ["CYC", "DELAY", "IMPACT_DEL"]
        ].sum()
        df["DR"] = (df["CYC"] - df["DELAY"]) * 100 / df["CYC"]

        subfig = make_subplots(specs=[[{"secondary_y": True}]])
        dr_target = [98.00, 98.00]

        annotDR = df["DR"].round(decimals=2)  # Y annotations for the DR line plot
        fig2 = px.line(
            df,
            x=df.index,
            y=["DR"],
            template=template,
            line_shape="spline",
            markers=True,
            text=annotDR,
        )
        fig2.add_trace(
            go.Scatter(
                x=["2020-05-01", "2030-05-01"],
                y=dr_target,
                name="DR Target",
                line=dict(color="#F3969A", dash="dash", width=1),
            )
        )
        fig2.update_traces(
            yaxis="y2",
            hovertemplate="<br>Period: %{x} <br>Dispatch Reliability: %{y}",
            textposition="bottom center",
        )

        annotCycles = df["CYC"].astype("int")  # Y annotations for the cycles bar plot
        fig = px.bar(df, x=df.index, y=["CYC"], template=template, text=annotCycles)
        fig.update_traces(
            hovertemplate="<br>Period: %{x} <br>Revenue Flights: %{y}",
            marker_line_width=0,
            width=86400000 * 20,
            marker_color="#6CC3D4",
            textposition="outside",
        )

        subfig.add_traces(fig.data + fig2.data)
        newnames = {
            "DR": "Dispatch Reliability",
            "CYC": "Cycles",
            "DR Target": "DR Target",
        }
        subfig.for_each_trace(
            lambda x: x.update(
                name=newnames[x.name],
                legendgroup=newnames[x.name],
                hovertemplate=x.hovertemplate.replace(x.name, newnames[x.name]),
            )
        )
        subfig.update_layout(
            title_text="Monthly Dispatch Reliability and Utilization",
            title_xanchor="center",
            title_x=0.5,
            xaxis=dict(
                title="Month",
                type="date",
                tick0="2022-01-30",
                dtick="M1",
                ticks="outside",
                ticklen=10,
                period=get_x_period("M"),
                tickformat="%b \n%Y",
            ),
            yaxis=dict(
                title="Number of Flights",
                tick0=220,
                dtick=100,
                tickmode="linear",
                period=[120, 1020],
            ),
            yaxis2=dict(
                title="Dispatch Reliability",
                tick0=96,
                dtick=2,
                period=[94, 100.2],
                tickmode="linear",
            ),
            modebar=dict(orientation="v", remove=["zoom", "lasso", "autoscale"]),
            title_yanchor="top",
            title_y=0.95,
            hovermode="x unified",
        )

    return subfig


# Plots the top 5 unscheduled removals
def plotRem():
    """
    Function that returns the plot figure for top 5 unscheduled removals
    """

    # Read csv
    rem_raw = pd.read_csv("./csv_data_files/UNSCHED_REM.csv", low_memory=False)
    rem_raw["REM_DATE"] = pd.to_datetime(rem_raw["REM_DATE"], format="%m/%d/%Y")

    # Count the removals for each ATA, sort, and get the top 5
    count = rem_raw.groupby("ATA")["PN"].count()
    df = count.sort_values(ascending=False).head(5)

    fig = px.bar(df, x=df.index, y=df.values, template=template)
    fig.update_layout(
        title_text="Top 5 Removals by ATA Chapter",
        title_x=0.5,
        title_xanchor="center",
        xaxis=dict(title="ATA Chapter", dtick=1),
        yaxis=dict(
            title="Number of Removals",
            tick0=0,
            dtick=5,
            periodmode="tozero",
            period=[0, 10],
        ),
        modebar=dict(orientation="v", remove=["zoom", "lasso", "autoscale"]),
    )
    fig.update_traces(hovertemplate="ATA Chapter: %{x} <br>Removals: %{y}")

    return fig


# Plots the fluids consumption
def plotOil(reg="PK-PWA"):
    df1 = oil_consum.loc[reg][["ENG1_OIL_QTZ/FH"]].dropna()
    df2 = oil_consum.loc[reg][["ENG2_OIL_QTZ/FH"]].dropna()
    fig = px.line(
        df1,
        x=df1.index,
        y=["ENG1_OIL_QTZ/FH"],
        line_shape="spline",
        markers=True,
        template=template,
    )
    newnames = {"ENG1_OIL_QTZ/FH": "ENG1"}
    fig.for_each_trace(
        lambda x: x.update(
            name=newnames[x.name],
            legendgroup=newnames[x.name],
            hovertemplate=x.hovertemplate.replace(x.name, newnames[x.name]),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df2.index,
            y=df2["ENG2_OIL_QTZ/FH"],
            line_shape="spline",
            mode="lines+markers",
            name="ENG2",
        )
    )
    consumTgt = [0.6, 0.6]
    fig.add_trace(
        go.Scatter(
            x=["2021-05-01", "2050-05-01"],
            y=consumTgt,
            name="Consumption Limit",
            line=dict(color="#F3969A", dash="dash", width=1),
        )
    )
    fig.update_traces(hovertemplate="<br>Up to: %{x}<br>Consumption: %{y} Quarts/FH")
    fig.update_layout(
        title_text=f"{reg} Engine Oil Consumption",
        title_xanchor="center",
        title_x=0.5,
        xaxis=dict(
            title="Month",
            type="date",
            dtick="M1",
            ticks="outside",
            ticklen=10,
            period=get_x_period("W"),
        ),
        yaxis=dict(
            title="Consumption (Qrt/Hr)",
            tick0=0,
            dtick=0.1,
            tickmode="linear",
            period=[0, 1],
        ),
        modebar=dict(orientation="v", remove=["zoom", "lasso", "autoscale"]),
        hovermode="x unified",
        legend_x=0.03,
    )

    return fig


# Plot the top5 delays by ATA
def plotDel():
    del_raw = pd.read_csv("./csv_data_files/DELAYS.csv")
    del_raw["DATE"] = pd.to_datetime(del_raw["DATE"], format="%Y-%m-%d")
    df = (
        del_raw[del_raw["INC_TYPE"] == "DELAY"]
        .groupby(by="ATA")["FLT_NUM"]
        .count()
        .sort_values(ascending=False)
        .head(5)
    )

    fig = px.bar(df, x=df.index, y=df.values, template=template)
    fig.update_layout(
        title_text="Top 5 Removals by ATA Chapter",
        title_x=0.5,
        title_xanchor="center",
        xaxis=dict(title="ATA Chapter", dtick=1),
        yaxis=dict(
            title="Number of Delays",
            tick0=0,
            dtick=5,
            periodmode="tozero",
            period=[0, 10],
        ),
        modebar=dict(orientation="v", remove=["zoom", "lasso", "autoscale"]),
    )
    fig.update_traces(hovertemplate="ATA Chapter: %{x} <br>Delays: %{y}")

    return fig


# Plot DR and SI
def plotSI(weekly):
    if weekly:
        pass
    else:
        # Create dataframe for Monthly DR
        df = util_df.groupby(pd.Grouper(key="TO_DATETIME", freq="M"))[
            ["CYC", "DELAY", "IMPACT_DEL"]
        ].sum()
        df["DR"] = (df["CYC"] - df["DELAY"]) * 100 / df["CYC"]
        df["COTD"] = (df["DELAY"] + df["IMPACT_DEL"]) / df["CYC"]

        del_raw = pd.read_csv("./csv_data_files/DELAYS.csv")
        del_raw["DATE"] = pd.to_datetime(del_raw["DATE"])
        df_del = (
            del_raw.groupby([pd.Grouper(key="DATE", freq="M"), "INC_TYPE"])[["FLT_NUM"]]
            .count()
            .reset_index()
        )
        conditions = [df_del["INC_TYPE"] == "DELAY2", df_del["INC_TYPE"] == "DELAY3"]

        weights = [2, 3]

        df_del["SUM"] = df_del["FLT_NUM"] * np.select(conditions, weights)
        df_del = df_del.groupby(pd.Grouper(key="DATE", freq="M"))[["SUM"]].sum()
        df_del["Monthly_SI"] = df_del["SUM"] * 100 / df.loc[df_del["SUM"].index]["CYC"]

        subfig = make_subplots(specs=[[{"secondary_y": True}]])
        dr_target = [98.00, 98.00]

        annotDR = df["DR"].round(decimals=2)
        fig2 = px.line(
            df,
            x=df.index,
            y=["DR"],
            template=template,
            line_shape="spline",
            markers=True,
            text=annotDR,
        )
        fig2.add_trace(
            go.Scatter(
                x=["2020-05-01", "2030-05-01"],
                y=dr_target,
                name="DR Target",
                line=dict(color="#F3969A", dash="dash", width=1),
            )
        )
        fig2.update_traces(
            yaxis="y2",
            hovertemplate="Period: %{x} <br>Dispatch Reliability: %{y}",
            textposition="bottom center",
        )

        annotSI = df_del["Monthly_SI"].round(decimals=2)
        fig = px.line(
            df_del,
            x=df_del.index,
            y=["Monthly_SI"],
            template=template,
            line_shape="spline",
            markers=True,
            text=annotSI,
        )
        fig.update_traces(
            hovertemplate="Period %{x} <br>Severity Index: %{y}",
            line_color="#FFCE67",
            textposition="top center",
        )

        subfig.add_traces(fig.data + fig2.data)
        newnames = {
            "DR": "Dispatch Reliability",
            "Monthly_SI": "Severity Index",
            "DR Target": "DR Target",
        }
        subfig.for_each_trace(
            lambda x: x.update(
                name=newnames[x.name],
                legendgroup=newnames[x.name],
                hovertemplate=x.hovertemplate.replace(x.name, newnames[x.name]),
            )
        )

        subfig.update_layout(
            title_text="Monthly Dispatch Reliability and Severity Index",
            title_xanchor="center",
            title_x=0.5,
            xaxis=dict(
                title="Month",
                type="date",
                tick0="2022-01-30",
                dtick="M1",
                ticks="outside",
                ticklen=10,
                period=get_x_period("M"),
                tickformat="%b \n%Y",
            ),
            yaxis=dict(
                title="Severity Index",
                tick0=0,
                dtick=2,
                tickmode="linear",
                periodmode="tozero",
                period=[0, 14],
            ),
            yaxis2=dict(
                title="Dispatch Reliability",
                tick0=95,
                dtick=2,
                period=[94, 101],
                tickmode="linear",
            ),
            modebar=dict(orientation="v", remove=["zoom", "lasso", "autoscale"]),
            title_yanchor="top",
            title_y=0.95,
            hovermode="x unified",
            legend_x=0.7,
        )

    return subfig


# Plot DR and COTD
def plotCOTD(weekly):
    if weekly:
        # Create dataframe for weekly DR
        df = util_df.groupby(pd.Grouper(key="TO_DATETIME", freq="W-WED"))[
            ["CYC", "DELAY", "IMPACT_DEL"]
        ].sum()
        df["DR"] = (df["CYC"] - df["DELAY"]) * 100 / df["CYC"]
        df["COTD"] = (df["DELAY"] + df["IMPACT_DEL"]) / df["CYC"]

        subfig = make_subplots(specs=[[{"secondary_y": True}]])
        dr_target = [97.00, 97.00]

        annotDR = df["DR"].round(decimals=2)
        fig2 = px.line(
            df,
            x=df.index,
            y=["DR"],
            template=template,
            labels={"DR": "Dispatch Reliability"},
            line_shape="spline",
            markers=True,
            text=annotDR,
        )
        fig2.add_trace(
            go.Scatter(
                x=["2020-05-01", "2030-05-01"],
                y=dr_target,
                name="DR Target",
                line=dict(color="#F3969A", dash="dash", width=1),
            )
        )
        fig2.update_traces(
            yaxis="y2",
            hovertemplate="Period: %{x} <br>Dispatch Reliability: %{y}",
            textposition="bottom center",
        )

        annotCOTD = df["COTD"].round(decimals=3)
        fig = px.line(
            df,
            x=df.index,
            y=["COTD"],
            template=template,
            line_shape="spline",
            markers=True,
            text=annotCOTD,
        )
        fig.update_traces(
            hovertemplate="Up to: %{x} <br>COTD: %{y}",
            line_color="#FFCE67",
            textposition="top center",
        )

        subfig.add_traces(fig.data + fig2.data)
        newnames = {
            "DR": "Dispatch Reliability",
            "COTD": "Delay Contribution",
            "DR Target": "DR Target",
        }
        subfig.for_each_trace(
            lambda x: x.update(
                name=newnames[x.name],
                legendgroup=newnames[x.name],
                hovertemplate=x.hovertemplate.replace(x.name, newnames[x.name]),
            )
        )
        subfig.update_layout(
            title_text="Weekly Reliability and Delay Contribution",
            title_xanchor="center",
            title_x=0.5,
            xaxis=dict(
                title="Month",
                type="date",
                dtick="M1",
                period=get_x_period("W"),
                ticklabelmode="period",
                ticks="outside",
                ticklen=10,
                minor=dict(
                    ticklen=4,
                    dtick=1000 * 60 * 60 * 24 * 7,
                ),
            ),
            yaxis=dict(
                title="COTD",
                dtick=0.1,
                tickmode="linear",
                periodmode="tozero",
                period=[0, 0.6],
            ),
            yaxis2=dict(
                title="Dispatch Reliability",
                tick0=85,
                dtick=5,
                period=[75, 105],
                tickmode="linear",
            ),
            modebar=dict(orientation="v", remove=["zoom", "lasso", "autoscale"]),
            title_yanchor="top",
            title_y=0.95,
            hovermode="x unified",
            legend_x=0.7,
        )
    else:
        # Create dataframe for Monthly DR
        df = util_df.groupby(pd.Grouper(key="TO_DATETIME", freq="M"))[
            ["CYC", "DELAY", "IMPACT_DEL"]
        ].sum()
        df["DR"] = (df["CYC"] - df["DELAY"]) * 100 / df["CYC"]
        df["COTD"] = (df["DELAY"] + df["IMPACT_DEL"]) / df["CYC"]

        subfig = make_subplots(specs=[[{"secondary_y": True}]])
        dr_target = [98.00, 98.00]

        annotDR = df["DR"].round(decimals=2)
        fig2 = px.line(
            df,
            x=df.index,
            y=["DR"],
            template=template,
            line_shape="spline",
            markers=True,
            text=annotDR,
        )
        fig2.add_trace(
            go.Scatter(
                x=["2020-05-01", "2030-05-01"],
                y=dr_target,
                name="DR Target",
                line=dict(color="#F3969A", dash="dash", width=1),
            )
        )
        fig2.update_traces(
            yaxis="y2",
            hovertemplate="Period: %{x} <br>Dispatch Reliability: %{y}",
            textposition="bottom center",
        )

        annotCOTD = df["COTD"].round(decimals=3)
        fig = px.line(
            df,
            x=df.index,
            y=["COTD"],
            template=template,
            line_shape="spline",
            markers=True,
            text=annotCOTD,
        )
        fig.update_traces(
            hovertemplate="Period: %{x} <br>COTD: %{y}",
            line_color="#FFCE67",
            textposition="top center",
        )

        subfig.add_traces(fig.data + fig2.data)
        newnames = {
            "DR": "Dispatch Reliability",
            "COTD": "Delay Contribution",
            "DR Target": "DR Target",
        }
        subfig.for_each_trace(
            lambda x: x.update(
                name=newnames[x.name],
                legendgroup=newnames[x.name],
                hovertemplate=x.hovertemplate.replace(x.name, newnames[x.name]),
            )
        )
        subfig.update_layout(
            title_text="Monthly Dispatch Reliability and Delay Contribution",
            title_xanchor="center",
            title_x=0.5,
            xaxis=dict(
                title="Month",
                type="date",
                tick0="2022-01-30",
                dtick="M1",
                ticks="outside",
                ticklen=10,
                period=get_x_period("M"),
                tickformat="%b \n%Y",
            ),
            yaxis=dict(
                title="COTD",
                tick0=0,
                dtick=0.1,
                tickmode="linear",
                periodmode="tozero",
                period=[0, 0.7],
            ),
            yaxis2=dict(
                title="Dispatch Reliability",
                tick0=95,
                dtick=2,
                period=[94, 101],
                tickmode="linear",
            ),
            modebar=dict(orientation="v", remove=["zoom", "lasso", "autoscale"]),
            title_yanchor="top",
            title_y=0.95,
            hovermode="x unified",
        )

    return subfig


# Plot top 5 PIREP
def plot5PIREP():
    df = get_mon_pirep(top5=True)
    fig = px.bar(df, x=df["ATA - Description"], y="Pir.Rate", template=template)
    fig.update_layout(
        title_text="Previous Month PIREP",
        title_xanchor="center",
        title_yanchor="top",
        title_x=0.5,
        title_y=0.95,
        xaxis=dict(title="ATA"),
        yaxis=dict(title="PIREP"),
        modebar=dict(orientation="v", remove=["zoom", "lasso", "autoscale"]),
    )
    return fig


# Plot the pirep history per ATA
def plotPirepPerAta(ata):
    techlog_raw = get_techlog_df()
    df = (
        techlog_raw[techlog_raw["PM"] == "PIREP"]
        .groupby(["ATA", pd.Grouper(key="DATE", freq="M")])[["PM"]]
        .count()
    )

    fig = px.bar(df.loc[ata], x=df.loc[ata].index, y=["PM"], template=template)
    fig.update_traces(
        hovertemplate="ATA: %{x}<br>PIREP Count: %{y}", marker_color="#6CC3D4"
    )

    newnames = {"PM": "PIREP Count"}
    fig.for_each_trace(
        lambda x: x.update(
            name=newnames[x.name],
            legendgroup=newnames[x.name],
            hovertemplate=x.hovertemplate.replace(x.name, newnames[x.name]),
        )
    )

    fig.update_layout(
        title_text="Monthly PIREP History for ATA {ata}".format(ata=ata),
        title_xanchor="center",
        title_x=0.5,
        xaxis=dict(
            title="Month",
            type="date",
            dtick="M1",
            period=get_x_period("M"),
            tickformat="%b\n%Y",
        ),
        yaxis=dict(
            title="PIREP Count",
            tick0=0,
            dtick=1,
            tickmode="linear",
            periodmode="tozero",
        ),
    )

    return fig


# Plot previous month's new HIL's by ATA
def plotMEL(period=3):
    raw = pd.read_csv("db/mel_use.csv")
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

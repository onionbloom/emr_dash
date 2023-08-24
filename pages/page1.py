# Page 1 displays executive summary on fleet utilization, engine ages, APU ratios, and high-level reliability
import dash_bootstrap_components as dbc
from dash import callback, ctx, dash_table, dcc, html
from dash.dash_table.Format import Format, Scheme
from dash.dependencies import Input, Output, State

from cards import card_cotd, card_del, card_dr, card_FC, card_FH, card_status, card_tia
from dataframes import get_df
from plots import plotCountry, plotMonFH, plotTechDR

### LAYOUT
layout = dbc.Container(
    [
        dbc.Row(  # row of cards
            [
                dbc.Col(  # FH card
                    [
                        card_FH,
                        dbc.Tooltip(
                            "YTD Flight Hours",
                            target="card-fh",
                            placement="bottom",
                        ),
                    ],
                    class_name="d-flex justify-content-center",
                    width=3,
                ),
                dbc.Col(  # FC card
                    [
                        card_FC,
                        dbc.Tooltip(
                            "YTD Flight Cycles",
                            target="card-fc",
                            placement="bottom",
                        ),
                    ],
                    class_name="d-flex justify-content-center",
                    width=3,
                ),
                dbc.Col(  # DR card
                    [
                        card_dr,
                        dbc.Tooltip(
                            "YTD Dispatch Reliability",
                            target="card-dr",
                            placement="bottom",
                        ),
                    ],
                    class_name="d-flex justify-content-center",
                    width=3,
                ),
                dbc.Col(
                    [
                        card_del,
                        dbc.Tooltip(
                            "YTD Delays",
                            target="card-del",
                            placement="bottom",
                        ),
                    ],
                    class_name="d-flex justify-content-center",
                    width=3,
                ),
            ],
            class_name="pt-3",
        ),
        dbc.Row(  # row of map graphic
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id="graph-map",
                            config=dict(
                                toImageButtonOptions=dict(
                                    width=1280,
                                    height=720,
                                    filename="dash_map",
                                    format="png",
                                ),
                                displaylogo=False,
                            ),
                        ),
                    ],
                    width=9,
                ),
                dbc.Col(
                    [
                        html.H5(
                            "Graphics Slicer",
                            className="fw-bold text-center",
                            style={"color": "#013764"},
                        ),
                        dbc.Form(
                            [
                                dbc.Label(
                                    "Period", html_for="dropdown-period", width="auto"
                                ),
                                dcc.Dropdown(
                                    id="dropdown-period",
                                    options=[
                                        {"label": "This Month", "value": 1},
                                        {"label": "3 Months", "value": 3},
                                        {"label": "6 Months", "value": 6},
                                        {"label": "12 Months", "value": 12},
                                    ],
                                    value=3,
                                ),
                                dbc.Label(
                                    "Registration",
                                    html_for="dropdown-reg",
                                    width="auto",
                                ),
                                dcc.Dropdown(
                                    id="dropdown-reg",
                                    options=get_df("ac_util.csv")["A/C"]
                                    .sort_values(ascending=True)
                                    .tolist(),
                                    value=get_df("ac_util.csv")["A/C"]
                                    .sort_values(ascending=True)
                                    .tolist(),
                                    multi=True,
                                ),
                            ]
                        ),
                    ],
                    width=3,
                ),
            ],
            class_name="pt-3",
        ),
        dbc.Row(  # row of chart graphic
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id="graph-fleet",
                            config=dict(
                                toImageButtonOptions=dict(
                                    width=1280,
                                    height=720,
                                    filename="dash_graph",
                                    format="png",
                                ),
                                displaylogo=False,
                            ),
                        ),
                    ],
                    width=9,
                ),
                dbc.Col(
                    [
                        html.H5(
                            "Chart Selection",
                            className="fw-bold text-center",
                            style={"color": "#013764"},
                        ),
                        dbc.RadioItems(
                            options=[
                                {
                                    "label": "Utilization Summary",
                                    "value": "util",
                                },
                                {
                                    "label": "Dispatch Reliability",
                                    "value": "dr",
                                },
                                {
                                    "label": "Engines Summary",
                                    "value": "eng",
                                },
                                {
                                    "label": "APU Summary",
                                    "value": "apu",
                                },
                            ],
                            id="engine-radio",
                        ),
                    ]
                ),
            ],
            class_name="pt-3",
        ),
    ],
    fluid=True,
)


### CALLBACKS
@callback(
    Output("graph-fleet", "figure"),
    Output("graph-map", "figure"),
    Input("dropdown-period", "value"),
    Input("dropdown-reg", "value"),
)
def update_graph(period, regs):
    if period:
        fig = plotTechDR(period)
        figMap = plotCountry(period, regs)

    return fig, figMap

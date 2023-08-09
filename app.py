# app.py

import dash_bootstrap_components as dbc
import pandas as pd
from dash import Dash, callback, dcc, html
from dash.dependencies import Input, Output

from pages import page1, page2, page3

### Instantiate Dash
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.MINTY],
    suppress_callback_exceptions=True,
)

server = app.server
LOGO = "./assets/PAS_Logo.png"

### Template Layout
app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Navbar(
                            dbc.Container(
                                [
                                    html.A(
                                        dbc.Row(
                                            [dbc.Col(html.Img(src=LOGO, height="30px"))]
                                        )
                                    ),
                                    dbc.Nav(
                                        [
                                            dbc.NavItem(
                                                dbc.NavLink(
                                                    "Executive Summary",
                                                    id="dash-link",
                                                    href="/dashboard",
                                                )
                                            ),
                                            dbc.NavItem(
                                                dbc.NavLink(
                                                    "Fleet",
                                                    id="fleet-link",
                                                    href="/fleet",
                                                )
                                            ),
                                            dbc.NavItem(
                                                dbc.NavLink(
                                                    "Engines",
                                                    id="pirep-link",
                                                    href="engines",
                                                )
                                            ),
                                            dbc.NavItem(
                                                dbc.NavLink(
                                                    "APU",
                                                    id="apu-link",
                                                    href="apu",
                                                )
                                            ),
                                            dbc.NavItem(
                                                dbc.NavLink(
                                                    "Systems & components",
                                                    id="sys-link",
                                                    href="syscomp",
                                                )
                                            ),
                                        ],
                                        navbar=True,
                                    ),
                                ],
                                fluid=True,
                            ),
                        )
                    ],
                )
            ],
            fluid=True,
        ),
        html.Div(id="page-content"),
    ]
)


### Callback
@callback(
    Output("page-content", "children"),
    Output("dash-link", "active"),
    Output("fleet-link", "active"),
    Input("url", "pathname"),
)
def display_page(pathname):
    if pathname == "/dashboard":
        return page1.layout, True, False
    elif pathname == "/fleet":
        return page2.layout, False, True
    elif pathname == "/engines":
        return page3.layout, False, False
    elif pathname == "/apu":
        pass
    elif pathname == "/syscomp":
        pass
    else:
        return page1.layout, True, False


if __name__ == "__main__":
    app.run_server(debug=True)

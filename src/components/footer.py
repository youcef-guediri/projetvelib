"""
Footer component for the dashboard.
Displays copyright and data source information.
"""

from dash import html
import dash_bootstrap_components as dbc
from datetime import datetime


def create_footer() -> dbc.Container:
    """
    Create the dashboard footer.
    
    Returns:
        Dash Bootstrap Container with footer content
    """
    current_year = datetime.now().year

    footer = dbc.Container(
        [
            html.Hr(style={'marginTop': '40px', 'marginBottom': '20px'}),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.P(
                                [
                                    "© ",
                                    html.Span(str(current_year)),
                                    " - Projet Vélib' Dashboard"
                                ],
                                className="text-center text-muted mb-2"
                            ),
                            html.P(
                                [
                                    "Données fournies par ",
                                    html.A(
                                        "Vélib' Métropole Open Data",
                                        href="https://www.velib-metropole.fr/donnees-open-data-gbfs-du-service-velib-metropole",
                                        target="_blank",
                                        className="text-decoration-none"
                                    )
                                ],
                                className="text-center text-muted mb-2"
                            ),
                            html.P(
                                [
                                    "Développé avec ",
                                    html.A(
                                        "Dash",
                                        href="https://dash.plotly.com/",
                                        target="_blank",
                                        className="text-decoration-none"
                                    ),
                                    " et ",
                                    html.A(
                                        "Plotly",
                                        href="https://plotly.com/",
                                        target="_blank",
                                        className="text-decoration-none"
                                    )
                                ],
                                className="text-center text-muted mb-0"
                            )
                        ],
                        width=12
                    )
                ]
            )
        ],
        fluid=True,
        style={
            'marginTop': 'auto',
            'paddingBottom': '20px'
        }
    )

    return footer


if __name__ == "__main__":
    print("Footer component created successfully")


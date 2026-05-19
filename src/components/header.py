"""
Header component for the dashboard.
Displays the main title and navigation.
"""

from dash import html
import dash_bootstrap_components as dbc

from config import DASHBOARD_TITLE


def create_header() -> dbc.Container:
    """
    Create the dashboard header.
    
    Returns:
        Dash Bootstrap Container with header content
    """
    header = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1(
                                DASHBOARD_TITLE,
                                className="text-center text-white mb-0",
                                style={
                                    'fontWeight': 'bold',
                                    'fontSize': '2.5rem',
                                    'textShadow': '2px 2px 4px rgba(0,0,0,0.3)'
                                }
                            ),
                            html.P(
                                "Analyse en temps réel des stations Vélib' à Paris",
                                className="text-center text-white-50 mb-0",
                                style={'fontSize': '1.1rem'}
                            )
                        ],
                        width=12
                    )
                ],
                className="py-4"
            )
        ],
        fluid=True,
        style={
            'backgroundColor': '#2C3E50',
            'marginBottom': '20px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        }
    )

    return header


if __name__ == "__main__":
    print("Header component created successfully")

# Made with Bob

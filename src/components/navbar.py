"""
Navigation bar component for the dashboard.
Provides navigation between different pages.
"""

import dash_bootstrap_components as dbc


def create_navbar() -> dbc.NavbarSimple:
    """
    Create the navigation bar.
    
    Returns:
        Dash Bootstrap NavbarSimple component
    """
    navbar = dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Accueil", href="/", active="exact")),
            dbc.NavItem(dbc.NavLink("Analyse", href="/analysis", active="exact")),
            dbc.NavItem(dbc.NavLink("Carte", href="/map", active="exact")),
            dbc.NavItem(dbc.NavLink("Insights", href="/insights", active="exact")),
            dbc.NavItem(dbc.NavLink("A propos", href="/about", active="exact")),
        ],
        brand="Vélib' Dashboard",
        brand_href="/",
        color="primary",
        dark=True,
        fluid=True,
        className="mb-3",
        style={'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}
    )

    return navbar


if __name__ == "__main__":
    print("Navbar component created successfully")

# Made with Bob

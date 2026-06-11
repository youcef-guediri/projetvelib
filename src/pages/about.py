"""
About page of the dashboard.
Provides information about the project and data sources.
"""

from dash import html
import dash_bootstrap_components as dbc


def create_about_layout() -> html.Div:
    """
    Create the about page layout.
    
    Returns:
        Dash HTML Div component
    """
    layout = html.Div([
        html.H2("A Propos du Projet", className="text-center mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Objectif du Projet", className="mb-0")),
                    dbc.CardBody([
                        html.P([
                            "Ce dashboard interactif a ete developpe dans le cadre d'un projet de ",
                            html.Strong("Python avance"),
                            " pour analyser et visualiser les donnees du systeme Velib' Metropole a Paris."
                        ]),
                        html.P([
                            "L'objectif est d'eclairer un sujet d'interet public en utilisant des donnees ",
                            html.Strong("Open Data"),
                            " accessibles et non modifiees, conformement aux principes de transparence ",
                            "et de reutilisation des donnees publiques."
                        ])
                    ])
                ], className="mb-4")
            ], xs=12)
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("A Propos de Velib'", className="mb-0")),
                    dbc.CardBody([
                        html.P([
                            "Velib' Metropole est le service de velos en libre-service de la metropole parisienne. ",
                            "Avec plus de 1 400 stations et 20 000 velos (mecaniques et electriques), ",
                            "c'est l'un des plus grands systemes de velos partages au monde."
                        ]),
                        html.Ul([
                            html.Li("Stations disponibles 24h/24 et 7j/7"),
                            html.Li("Velos mecaniques et electriques"),
                            html.Li("Application mobile pour localiser les stations"),
                            html.Li("Systeme de paiement flexible")
                        ])
                    ])
                ], className="mb-4")
            ], xs=12, md=6),

            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Fonctionnalites", className="mb-0")),
                    dbc.CardBody([
                        html.P("Ce dashboard propose plusieurs fonctionnalites :"),
                        html.Ul([
                            html.Li([
                                html.Strong("Accueil : "),
                                "Vue d'ensemble avec statistiques cles et graphiques de synthese"
                            ]),
                            html.Li([
                                html.Strong("Analyse : "),
                                "Visualisations interactives avec filtres dynamiques"
                            ]),
                            html.Li([
                                html.Strong("Carte : "),
                                "Geolocalisation des stations avec informations en temps reel"
                            ]),
                            html.Li([
                                html.Strong("Interactivite : "),
                                "Graphiques dynamiques et filtres personnalisables"
                            ])
                        ])
                    ])
                ], className="mb-4")
            ], xs=12, md=6)
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Sources de Donnees", className="mb-0")),
                    dbc.CardBody([
                        html.P([
                            "Les donnees utilisees proviennent de l'API Open Data de Velib' Metropole, ",
                            "conforme au standard ",
                            html.A(
                                "GBFS (General Bikeshare Feed Specification)",
                                href="https://github.com/NABSA/gbfs",
                                target="_blank",
                                className="text-decoration-none"
                            ),
                            "."
                        ]),
                        html.P("Deux fichiers principaux sont utilises :"),
                        html.Ul([
                            html.Li([
                                html.Strong("station_information.csv : "),
                                "Donnees statiques (nom, localisation, capacite)"
                            ]),
                            html.Li([
                                html.Strong("station_status.csv : "),
                                "Donnees dynamiques (disponibilite en temps reel)"
                            ])
                        ]),
                        html.P([
                            html.A(
                                "Acceder aux donnees Open Data Velib'",
                                href="https://www.velib-metropole.fr/donnees-open-data-gbfs-du-service-velib-metropole",
                                target="_blank",
                                className="text-decoration-none"
                            )
                        ])
                    ])
                ], className="mb-4")
            ], xs=12)
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Technologies Utilisees", className="mb-0")),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.H6("Backend", className="text-primary"),
                                html.Ul([
                                    html.Li("Python 3.11+"),
                                    html.Li("Pandas (manipulation de donnees)"),
                                    html.Li("NumPy (calculs numeriques)")
                                ])
                            ], xs=12, md=4),
                            dbc.Col([
                                html.H6("Visualisation", className="text-primary"),
                                html.Ul([
                                    html.Li("Plotly (graphiques interactifs)"),
                                    html.Li("Plotly Express (graphiques simplifies)"),
                                    html.Li("Dash (framework web)")
                                ])
                            ], xs=12, md=4),
                            dbc.Col([
                                html.H6("Interface", className="text-primary"),
                                html.Ul([
                                    html.Li("Dash Bootstrap Components"),
                                    html.Li("HTML/CSS"),
                                    html.Li("Responsive design")
                                ])
                            ], xs=12, md=4)
                        ])
                    ])
                ], className="mb-4")
            ], xs=12)
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Architecture du Code", className="mb-0")),
                    dbc.CardBody([
                        html.P("Le projet suit une architecture modulaire :"),
                        html.Pre([
                            "projetvelib/\n",
                            "├── config.py              # Configuration\n",
                            "├── main.py                # Point d'entree\n",
                            "├── data/                  # Donnees\n",
                            "│   ├── raw/              # Donnees brutes\n",
                            "│   └── cleaned/          # Donnees nettoyees\n",
                            "├── src/\n",
                            "│   ├── components/       # Composants UI\n",
                            "│   ├── pages/            # Pages du dashboard\n",
                            "│   └── utils/            # Fonctions utilitaires\n",
                            "└── tests/                # Tests unitaires"
                        ], style={
                            'backgroundColor': '#f8f9fa',
                            'padding': '15px',
                            'borderRadius': '5px',
                            'fontSize': '0.9rem'
                        })
                    ])
                ], className="mb-4")
            ], xs=12)
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Copyright", className="mb-0")),
                    dbc.CardBody([
                        html.P([
                            "Je declare sur l'honneur que le code fourni a ete produit par moi-meme, ",
                            "a l'exception des bibliotheques open source utilisees (Dash, Plotly, Pandas, etc.)."
                        ]),
                        html.P([
                            "Ce projet est developpe a des fins educatives dans le cadre d'un cours de ",
                            html.Strong("Python avance"),
                            "."
                        ]),
                        html.P([
                            "Les donnees utilisees sont fournies par Velib' Metropole sous licence ouverte ",
                            "et sont accessibles publiquement."
                        ], className="mb-0")
                    ])
                ], className="mb-4")
            ], xs=12)
        ])
    ])

    return layout


if __name__ == "__main__":
    print("About page layout created successfully")

# Made with Bob

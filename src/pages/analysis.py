"""
Analysis page of the dashboard.
Provides detailed analysis and interactive visualizations.
"""

from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.utils.common_functions import filter_operational_stations
from config import COLORS


def create_analysis_layout(df: pd.DataFrame) -> html.Div:
    """
    Create the analysis page layout.
    
    Args:
        df: DataFrame with station data
        
    Returns:
        Dash HTML Div component
    """
    layout = html.Div([
        html.H2("Analyse Détaillée des Stations", className="text-center mb-4"),

        # Filters
        dbc.Card([
            dbc.CardBody([
                html.H5("Filtres", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Nombre minimum de vélos:"),
                        dcc.Slider(
                            id='min-bikes-slider',
                            min=0,
                            max=50,
                            step=1,
                            value=0,
                            marks={i: str(i) for i in range(0, 51, 10)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        )
                    ], xs=12, md=6),
                    dbc.Col([
                        html.Label("Type de vélo:"),
                        dcc.Dropdown(
                            id='bike-type-dropdown',
                            options=[
                                {'label': 'Tous les vélos', 'value': 'all'},
                                {'label': 'Vélos mécaniques', 'value': 'mechanical'},
                                {'label': 'Vélos électriques', 'value': 'ebike'}
                            ],
                            value='all',
                            clearable=False
                        )
                    ], xs=12, md=6),
                ])
            ])
        ], className="mb-4"),

        # Statistics Summary
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Statistiques Filtrées", className="mb-3"),
                        html.Div(id='filtered-stats')
                    ])
                ])
            ], xs=12)
        ], className="mb-4"),

        # Charts
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='availability-scatter')
                    ])
                ])
            ], xs=12, md=6),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='bike-type-comparison')
                    ])
                ])
            ], xs=12, md=6),
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Graph(id='occupancy-distribution')
                    ])
                ])
            ], xs=12)
        ], className="mb-4"),

        # Store the data
        dcc.Store(id='analysis-data', data=df.to_dict('records'))
    ])

    return layout


@callback(
    [Output('filtered-stats', 'children'),
     Output('availability-scatter', 'figure'),
     Output('bike-type-comparison', 'figure'),
     Output('occupancy-distribution', 'figure')],
    [Input('min-bikes-slider', 'value'),
     Input('bike-type-dropdown', 'value'),
     Input('analysis-data', 'data')]
)
def update_analysis(min_bikes: int, bike_type: str, data: list) -> tuple:
    """
    Update analysis visualizations based on filters.
    
    Args:
        min_bikes: Minimum number of bikes filter
        bike_type: Type of bike filter
        data: Station data
        
    Returns:
        Tuple of (stats_div, scatter_fig, comparison_fig, distribution_fig)
    """
    df = pd.DataFrame(data)
    df_filtered = filter_operational_stations(df)

    # Apply filters
    df_filtered = df_filtered[df_filtered['num_bikes_available'] >= min_bikes]

    if bike_type == 'mechanical':
    # Affiche SEULEMENT les mécaniques
        df_filtered['num_bikes_available'] = df_filtered['mechanical_bikes']
        df_filtered = df_filtered[df_filtered['mechanical_bikes'] > 0]
    elif bike_type == 'ebike':
    # Affiche SEULEMENT les électriques
        df_filtered['num_bikes_available'] = df_filtered['ebikes']
        df_filtered = df_filtered[df_filtered['ebikes'] > 0]

    # Statistics
    stats_div = html.Div([
        dbc.Row([
            dbc.Col([
                html.P([
                    html.Strong("Stations: "),
                    f"{len(df_filtered)}"
                ])
            ], xs=6, md=3),
            dbc.Col([
                html.P([
                    html.Strong("Vélos totaux: "),
                    f"{int(df_filtered['num_bikes_available'].sum())}"
                ])
            ], xs=6, md=3),
            dbc.Col([
                html.P([
                    html.Strong("Mécaniques: "),
                    f"{int(df_filtered['mechanical_bikes'].sum())}"
                ])
            ], xs=6, md=3),
            dbc.Col([
                html.P([
                    html.Strong("Électriques: "),
                    f"{int(df_filtered['ebikes'].sum())}"
                ])
            ], xs=6, md=3),
        ])
    ])

    # Scatter plot: Capacity vs Availability
    scatter_fig = px.scatter(
        df_filtered,
        x='capacity',
        y='num_bikes_available',
        color='availability_rate',
        size='num_bikes_available',
        hover_data=['name', 'mechanical_bikes', 'ebikes'],
        title='Capacité vs Disponibilité',
        labels={
            'capacity': 'Capacité totale',
            'num_bikes_available': 'Vélos disponibles',
            'availability_rate': 'Taux (%)'
        },
        color_continuous_scale='RdYlGn'
    )
    scatter_fig.update_layout(
        title={'x': 0.5, 'xanchor': 'center'},
        height=400
    )

    # Bar chart: Bike type comparison
    bike_comparison_data = pd.DataFrame({
        'Type': ['Mécaniques', 'Électriques'],
        'Nombre': [
            int(df_filtered['mechanical_bikes'].sum()),
            int(df_filtered['ebikes'].sum())
        ]
    })

    comparison_fig = px.bar(
        bike_comparison_data,
        x='Type',
        y='Nombre',
        title='Comparaison des Types de Vélos',
        color='Type',
        color_discrete_map={
            'Mécaniques': COLORS['mechanical'],
            'Électriques': COLORS['ebike']
        }
    )
    comparison_fig.update_layout(
        title={'x': 0.5, 'xanchor': 'center'},
        showlegend=False,
        height=400
    )

    # Box plot: Occupancy distribution
    distribution_fig = go.Figure()
    distribution_fig.add_trace(go.Box(
        y=df_filtered['occupancy_rate'],
        name='Taux d\'occupation',
        marker_color=COLORS['primary'],
        boxmean='sd'
    ))
    distribution_fig.update_layout(
        title={
            'text': 'Distribution du Taux d\'Occupation',
            'x': 0.5,
            'xanchor': 'center'
        },
        yaxis_title='Taux d\'occupation (%)',
        showlegend=False,
        height=400
    )

    return stats_div, scatter_fig, comparison_fig, distribution_fig


if __name__ == "__main__":
    print("Analysis page layout created successfully")


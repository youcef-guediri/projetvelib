"""
Map page of the dashboard.
Displays stations on an interactive map with geolocation.
"""

from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.utils.common_functions import filter_operational_stations
from config import DEFAULT_MAP_CENTER, DEFAULT_MAP_ZOOM


def create_map_layout(df: pd.DataFrame) -> html.Div:
    """
    Create the map page layout.
    
    Args:
        df: DataFrame with station data
        
    Returns:
        Dash HTML Div component
    """
    layout = html.Div([
        html.H2("Carte des Stations Vélib'", className="text-center mb-4"),

        # Map controls
        dbc.Card([
            dbc.CardBody([
                html.H5("Options de la Carte", className="mb-3"),
                dbc.Row([
                    dbc.Col([
                        html.Label("Afficher:"),
                        dcc.Dropdown(
                            id='map-display-dropdown',
                            options=[
                                {'label': 'Toutes les stations', 'value': 'all'},
                                {'label': 'Stations avec vélos disponibles', 'value': 'available'},
                                {'label': 'Stations avec vélos électriques', 'value': 'ebike'},
                                {'label': 'Stations presque vides', 'value': 'low'}
                            ],
                            value='all',
                            clearable=False
                        )
                    ], xs=12, md=4),
                    dbc.Col([
                        html.Label("Taille des marqueurs:"),
                        dcc.RadioItems(
                            id='marker-size-radio',
                            options=[
                                {'label': 'Petit', 'value': 'small'},
                                {'label': 'Moyen', 'value': 'medium'},
                                {'label': 'Grand', 'value': 'large'}
                            ],
                            value='medium',
                            inline=True
                        )
                    ], xs=12, md=4),
                    dbc.Col([
                        html.Label("Coloration:"),
                        dcc.RadioItems(
                            id='color-by-radio',
                            options=[
                                {'label': 'Taux d\'occupation', 'value': 'occupancy'}, 
                                {'label': 'Disponibilité', 'value': 'availability'},
                                {'label': 'Places libres', 'value': 'docks'},
                                {'label': 'Type de vélos', 'value': 'bike_type'}
                            ],
                            value='availability',
                            inline=True
                        )
                    ], xs=12, md=4),
                ])
            ])
        ], className="mb-4"),

        # Map
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-map",
                            type="default",
                            children=dcc.Graph(
                                id='station-map',
                                style={'height': '70vh'}
                            )
                        )
                    ])
                ])
            ], xs=12)
        ]),

        # Store the data
        dcc.Store(id='map-data', data=df.to_dict('records'))
    ])

    return layout


@callback(
    Output('station-map', 'figure'),
    [Input('map-display-dropdown', 'value'),
     Input('marker-size-radio', 'value'),
     Input('color-by-radio', 'value'),
     Input('map-data', 'data')]
)
def update_map(
    display_filter: str,
    marker_size: str,
    color_by: str,
    data: list
) -> go.Figure:
    """
    Update the map based on filters.
    
    Args:
        display_filter: Filter for which stations to display
        marker_size: Size of map markers
        color_by: How to color the markers
        data: Station data
        
    Returns:
        Plotly scatter_mapbox figure
    """
    df = pd.DataFrame(data)
    df_filtered = filter_operational_stations(df)

    # Apply display filter
    if display_filter == 'available':
        df_filtered = df_filtered[df_filtered['num_bikes_available'] > 0]
    elif display_filter == 'ebike':
        df_filtered = df_filtered[df_filtered['ebikes'] > 0]
    elif display_filter == 'low':
        df_filtered = df_filtered[df_filtered['num_bikes_available'] <= 5]

    # Set marker size
    size_map = {'small': 8, 'medium': 12, 'large': 16}
    marker_size_value = size_map.get(marker_size, 12)

    # Calculate occupancy rate safely (avoid division by zero)
    df_filtered = df_filtered.copy()
    df_filtered['occupancy_pct'] = df_filtered.apply(
        lambda row: (row['num_bikes_available'] / row['capacity'] * 100) 
                   if row['capacity'] > 0 else 0,
        axis=1
    )

    # Create hover text (FRANÇAIS uniquement)
    df_filtered['hover_text'] = (
        '<b>' + df_filtered['name'] + '</b><br>' +
        'Vélos disponibles: ' + df_filtered['num_bikes_available'].astype(int).astype(str) + '<br>' +
        'Mécaniques: ' + df_filtered['mechanical_bikes'].astype(int).astype(str) + '<br>' +
        'Électriques: ' + df_filtered['ebikes'].astype(int).astype(str) + '<br>' +
        'Capacité: ' + df_filtered['capacity'].astype(int).astype(str) + '<br>' +
        'Taux d\'occupation: ' + df_filtered['occupancy_pct'].round(1).astype(str) + '%'
    )

    # Determine color column
    if color_by == 'occupancy':
        color_column = 'occupancy_pct'
        color_scale = 'RdYlGn'
        color_label = 'Taux d\'occupation'
    elif color_by == 'availability':
        color_column = 'num_bikes_available'
        color_scale = 'RdYlGn'
        color_label = 'Vélos disponibles'
    elif color_by == 'docks':
        color_column = 'num_docks_available'
        color_scale = 'RdYlGn'
        color_label = 'Places libres'
    else:
        color_column = 'ebike_percentage'
        color_scale = 'Viridis'
        color_label = '% Vélos électriques'

    # Create the map
    fig = px.scatter_mapbox(
        df_filtered,
        lat='lat',
        lon='lon',
        color=color_column,
        size='capacity',
        custom_data=['hover_text'],
        color_continuous_scale=color_scale,
        size_max=marker_size_value,
        zoom=DEFAULT_MAP_ZOOM,
        center={'lat': DEFAULT_MAP_CENTER[0], 'lon': DEFAULT_MAP_CENTER[1]},
        mapbox_style='open-street-map',
        title=f'Carte des Stations Vélib\' - {len(df_filtered)} stations affichées'
    )

    # Utiliser SEULEMENT le hover_text personnalisé (pas de doublon)
    fig.update_traces(
        hovertemplate='%{customdata[0]}<extra></extra>'
    )

    fig.update_layout(
        title={
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'weight': 'bold'}
        },
        margin=dict(t=60, b=20, l=20, r=20),
        coloraxis_colorbar=dict(
            title=color_label,
            thickness=15,
            len=0.7
        )
    )

    return fig


if __name__ == "__main__":
    print("Map page layout created successfully")
    
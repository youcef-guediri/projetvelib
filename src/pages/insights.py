"""
Advanced Insights page - Unique value-added analyses.
Provides deep insights that go beyond basic statistics.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.utils.common_functions import filter_operational_stations


def calculate_station_health_score(row: pd.Series) -> float:
    """
    Calculate a health score for a station (0-100).
    Takes into account: availability, balance, capacity utilization.
    
    Args:
        row: DataFrame row with station data
        
    Returns:
        Health score (0-100)
    """
    # Availability score (40 points)
    availability_score = min(row['availability_rate'], 100) * 0.4

    # Balance score (30 points) - penalize extreme imbalance
    bikes = row['num_bikes_available']
    docks = row['num_docks_available']
    total = bikes + docks
    if total > 0:
        balance = min(bikes, docks) / total
        balance_score = balance * 30
    else:
        balance_score = 0

    # Capacity utilization (30 points) - sweet spot is 50-80%
    if row['capacity'] > 0:
        utilization = (bikes / row['capacity']) * 100
        if 50 <= utilization <= 80:
            utilization_score = 30
        elif utilization < 50:
            utilization_score = (utilization / 50) * 30
        else:
            utilization_score = max(0, 30 - (utilization - 80) * 0.5)
    else:
        utilization_score = 0

    return availability_score + balance_score + utilization_score


def detect_station_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect stations with unusual patterns.
    
    Args:
        df: DataFrame with station data
        
    Returns:
        DataFrame with anomaly flags
    """
    df = df.copy()

    # Empty stations (potential problem)
    df['is_empty'] = (df['num_bikes_available'] == 0) & (df['is_renting'] == 1)

    # Full stations (potential problem)
    df['is_full'] = (df['num_docks_available'] == 0) & (df['is_returning'] == 1)

    # Imbalanced stations (>90% bikes or >90% docks)
    total = df['num_bikes_available'] + df['num_docks_available']
    df['is_imbalanced'] = ((df['num_bikes_available'] / total > 0.9) | 
                           (df['num_docks_available'] / total > 0.9))

    # Low capacity stations (<10 spots)
    df['is_low_capacity'] = df['capacity'] < 10

    # No electric bikes available
    df['no_ebikes'] = (df['ebikes'] == 0) & (df['capacity'] > 0)

    return df


def create_health_score_gauge(score: float, title: str) -> dcc.Graph:
    """
    Create a gauge chart for health score.
    
    Args:
        score: Health score (0-100)
        title: Chart title
        
    Returns:
        Dash Graph component
    """
    # Determine color based on score
    if score >= 80:
        color = "#10B981"  # Green
    elif score >= 60:
        color = "#F59E0B"  # Orange
    else:
        color = "#EF4444"  # Red

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16, 'color': '#0F172A'}},
        delta={'reference': 75, 'increasing': {'color': "#10B981"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#64748B"},
            'bar': {'color': color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#E2E8F0",
            'steps': [
                {'range': [0, 60], 'color': '#FEE2E2'},
                {'range': [60, 80], 'color': '#FEF3C7'},
                {'range': [80, 100], 'color': '#D1FAE5'}
            ],
            'threshold': {
                'line': {'color': "#3B82F6", 'width': 4},
                'thickness': 0.75,
                'value': 75
            }
        }
    ))

    fig.update_layout(
        height=250,
        margin=dict(t=40, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter')
    )

    return dcc.Graph(figure=fig, config={'displayModeBar': False})


def create_anomaly_sunburst(df: pd.DataFrame) -> dcc.Graph:
    """
    Create a sunburst chart showing anomaly distribution.
    
    Args:
        df: DataFrame with anomaly flags
        
    Returns:
        Dash Graph component
    """
    anomaly_data = []

    # Count each type of anomaly
    empty_count = df['is_empty'].sum()
    full_count = df['is_full'].sum()
    imbalanced_count = df['is_imbalanced'].sum()
    no_ebikes_count = df['no_ebikes'].sum()

    # Create hierarchical data
    if empty_count > 0:
        anomaly_data.append({'category': 'Problemes', 'type': 'Stations Vides', 'count': empty_count})
    if full_count > 0:
        anomaly_data.append({'category': 'Problemes', 'type': 'Stations Pleines', 'count': full_count})
    if imbalanced_count > 0:
        anomaly_data.append({'category': 'Attention', 'type': 'Desequilibrees', 'count': imbalanced_count})
    if no_ebikes_count > 0:
        anomaly_data.append({'category': 'Info', 'type': 'Sans Electriques', 'count': no_ebikes_count})

    if not anomaly_data:
        # No anomalies - create a placeholder
        anomaly_data = [{'category': 'Tout va bien', 'type': 'Aucun probleme', 'count': len(df)}]

    df_anomalies = pd.DataFrame(anomaly_data)

    fig = px.sunburst(
        df_anomalies,
        path=['category', 'type'],
        values='count',
        color='count',
        color_continuous_scale='RdYlGn_r',
        title='<b>Repartition des Anomalies</b>'
    )

    fig.update_layout(
        height=400,
        margin=dict(t=60, b=20, l=20, r=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter'),
        title={
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#0F172A'}
        }
    )

    return dcc.Graph(figure=fig, config={'displayModeBar': False})


def create_capacity_efficiency_scatter(df: pd.DataFrame) -> dcc.Graph:
    """
    Create a scatter plot showing capacity vs efficiency.
    
    Args:
        df: DataFrame with station data
        
    Returns:
        Dash Graph component
    """
    df = df.copy()
    df['efficiency'] = (df['num_bikes_available'] / df['capacity'] * 100).fillna(0)

    fig = px.scatter(
        df,
        x='capacity',
        y='efficiency',
        size='num_bikes_available',
        color='ebike_percentage',
        hover_name='name',
        hover_data={
            'capacity': True,
            'efficiency': ':.1f',
            'num_bikes_available': True,
            'ebike_percentage': ':.1f'
        },
        labels={
            'capacity': 'Capacite Totale',
            'efficiency': 'Taux d\'Occupation (%)',
            'ebike_percentage': '% Electriques'
        },
        color_continuous_scale='Viridis',
        title='<b>Efficacite vs Capacite des Stations</b>'
    )

    # Add optimal zone
    fig.add_shape(
        type="rect",
        x0=0, x1=df['capacity'].max(),
        y0=50, y1=80,
        fillcolor="lightgreen",
        opacity=0.1,
        layer="below",
        line_width=0,
    )

    fig.add_annotation(
        x=df['capacity'].max() * 0.8,
        y=65,
        text="Zone Optimale",
        showarrow=False,
        font=dict(size=12, color='#10B981')
    )

    fig.update_layout(
        height=450,
        margin=dict(t=60, b=60, l=60, r=60),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(250,250,250,1)',
        xaxis=dict(gridcolor='#F1F5F9'),
        yaxis=dict(gridcolor='#F1F5F9'),
        font=dict(family='Inter'),
        title={
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#0F172A'}
        }
    )

    return dcc.Graph(figure=fig, config={'displayModeBar': False})


def create_ebike_adoption_map(df: pd.DataFrame) -> dcc.Graph:
    """
    Create a heatmap showing e-bike adoption by area.
    
    Args:
        df: DataFrame with station data
        
    Returns:
        Dash Graph component
    """
    # Create bins for latitude and longitude
    df = df.copy()
    df['lat_bin'] = pd.cut(df['lat'], bins=20)
    df['lon_bin'] = pd.cut(df['lon'], bins=20)

    # Calculate average e-bike percentage per area
    heatmap_data = df.groupby(['lat_bin', 'lon_bin'])['ebike_percentage'].mean().reset_index()

    # Get bin centers
    heatmap_data['lat_center'] = heatmap_data['lat_bin'].apply(lambda x: x.mid)
    heatmap_data['lon_center'] = heatmap_data['lon_bin'].apply(lambda x: x.mid)

    fig = px.density_mapbox(
        heatmap_data,
        lat='lat_center',
        lon='lon_center',
        z='ebike_percentage',
        radius=15,
        center=dict(lat=48.8566, lon=2.3522),
        zoom=11,
        mapbox_style="carto-positron",
        color_continuous_scale='Viridis',
        title='<b>Carte de Chaleur: Adoption des Velos Electriques</b>',
        labels={'ebike_percentage': '% Electriques'}
    )

    fig.update_layout(
        height=500,
        margin=dict(t=60, b=20, l=20, r=20),
        font=dict(family='Inter'),
        title={
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#0F172A'}
        }
    )

    return dcc.Graph(figure=fig, config={'displayModeBar': False})


def create_predictive_alerts(df: pd.DataFrame) -> html.Div:
    """
    Create alert cards for stations needing attention.
    
    Args:
        df: DataFrame with station data
        
    Returns:
        HTML Div with alert cards
    """
    df_anomalies = detect_station_anomalies(df)

    alerts = []

    # Critical: Empty stations
    empty_stations = df_anomalies[df_anomalies['is_empty']].nlargest(3, 'capacity')
    if len(empty_stations) > 0:
        alerts.append(
            dbc.Alert([
                html.H5("ALERTE - Stations Vides Critiques", className="alert-heading"),
                html.P(f"{len(df_anomalies[df_anomalies['is_empty']])} stations sont completement vides."),
                html.Hr(),
                html.Ul([
                    html.Li(f"{row['name']} (Capacite: {row['capacity']})") 
                    for _, row in empty_stations.iterrows()
                ])
            ], color="danger", style={'borderRadius': '12px'})
        )

    # Warning: Full stations
    full_stations = df_anomalies[df_anomalies['is_full']].nlargest(3, 'capacity')
    if len(full_stations) > 0:
        alerts.append(
            dbc.Alert([
                html.H5("ATTENTION - Stations Saturees", className="alert-heading"),
                html.P(f"{len(df_anomalies[df_anomalies['is_full']])} stations sont pleines (aucune place pour retour)."),
                html.Hr(),
                html.Ul([
                    html.Li(f"{row['name']} (Capacite: {row['capacity']})") 
                    for _, row in full_stations.iterrows()
                ])
            ], color="warning", style={'borderRadius': '12px'})
        )

    # Info: No e-bikes
    no_ebike_count = len(df_anomalies[df_anomalies['no_ebikes']])
    if no_ebike_count > 0:
        alerts.append(
            dbc.Alert([
                html.H5("INFO - Stations Sans Velos Electriques", className="alert-heading"),
                html.P(f"{no_ebike_count} stations n'ont aucun velo electrique disponible."),
            ], color="info", style={'borderRadius': '12px'})
        )

    if not alerts:
        alerts.append(
            dbc.Alert([
                html.H5("OK - Tout va bien!", className="alert-heading"),
                html.P("Aucune anomalie critique detectee sur le reseau."),
            ], color="success", style={'borderRadius': '12px'})
        )

    return html.Div(alerts)


def create_insights_layout(df: pd.DataFrame) -> html.Div:
    """
    Create the advanced insights page layout.
    
    Args:
        df: DataFrame with station data
        
    Returns:
        Dash HTML Div component
    """
    df_operational = filter_operational_stations(df)
    df_anomalies = detect_station_anomalies(df_operational)

    # Calculate overall health score
    df_operational['health_score'] = df_operational.apply(calculate_station_health_score, axis=1)
    avg_health_score = df_operational['health_score'].mean()

    # Calculate network efficiency
    total_capacity = df_operational['capacity'].sum()
    total_bikes = df_operational['num_bikes_available'].sum()
    network_efficiency = (total_bikes / total_capacity * 100) if total_capacity > 0 else 0

    # Calculate rebalancing need
    imbalanced_stations = df_anomalies['is_imbalanced'].sum()
    rebalancing_score = 100 - (imbalanced_stations / len(df_operational) * 100)

    layout = html.Div([
        html.Div([
            # Page header
            html.Div([
                html.H1("Insights Avances", style={
                    'fontSize': '2rem',
                    'fontWeight': '700',
                    'color': '#0F172A',
                    'marginBottom': '8px'
                }),
                html.P("Analyses predictives et indicateurs de performance du reseau", style={
                    'fontSize': '1rem',
                    'color': '#64748B',
                    'marginBottom': '0'
                })
            ], style={'marginBottom': '32px'}),

            # Health Scores Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            create_health_score_gauge(avg_health_score, "Sante Globale du Reseau")
                        ])
                    ], style={
                        'border': '1px solid #E2E8F0',
                        'borderRadius': '12px',
                        'backgroundColor': 'white',
                        'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
                    })
                ], xs=12, md=4, className="mb-4"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            create_health_score_gauge(network_efficiency, "Efficacite du Reseau")
                        ])
                    ], style={
                        'border': '1px solid #E2E8F0',
                        'borderRadius': '12px',
                        'backgroundColor': 'white',
                        'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
                    })
                ], xs=12, md=4, className="mb-4"),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            create_health_score_gauge(rebalancing_score, "Score de Reequilibrage")
                        ])
                    ], style={
                        'border': '1px solid #E2E8F0',
                        'borderRadius': '12px',
                        'backgroundColor': 'white',
                        'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
                    })
                ], xs=12, md=4, className="mb-4"),
            ], style={'marginBottom': '40px'}),

            # Predictive Alerts
            html.Div([
                html.H2("Alertes Predictives", style={
                    'fontSize': '1.5rem',
                    'fontWeight': '700',
                    'color': '#0F172A',
                    'marginBottom': '24px'
                }),
                create_predictive_alerts(df_operational)
            ], style={'marginBottom': '40px'}),

            # Advanced Analytics
            html.Div([
                html.H2("Analyses Avancees", style={
                    'fontSize': '1.5rem',
                    'fontWeight': '700',
                    'color': '#0F172A',
                    'marginBottom': '24px'
                }),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                create_anomaly_sunburst(df_anomalies)
                            ])
                        ], style={
                            'border': '1px solid #E2E8F0',
                            'borderRadius': '12px',
                            'backgroundColor': 'white',
                            'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
                        })
                    ], xs=12, md=6, className="mb-4"),
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                create_capacity_efficiency_scatter(df_operational)
                            ])
                        ], style={
                            'border': '1px solid #E2E8F0',
                            'borderRadius': '12px',
                            'backgroundColor': 'white',
                            'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
                        })
                    ], xs=12, md=6, className="mb-4"),
                ]),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                create_ebike_adoption_map(df_operational)
                            ])
                        ], style={
                            'border': '1px solid #E2E8F0',
                            'borderRadius': '12px',
                            'backgroundColor': 'white',
                            'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
                        })
                    ], xs=12, className="mb-4"),
                ])
            ])

        ], style={
            'padding': '32px',
            'maxWidth': '1400px',
            'margin': '0 auto'
        })
    ], style={
        'backgroundColor': '#F8FAFC',
        'minHeight': '100vh',
        'fontFamily': 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    })

    return layout


if __name__ == "__main__":
    print("Advanced insights page created successfully")


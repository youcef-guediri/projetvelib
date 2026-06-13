"""
Home page of the dashboard - Professional Layout.
Displays overview statistics and key metrics with modern design.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from src.utils.common_functions import (
    get_bike_type_distribution,
    format_large_number,
    filter_operational_stations
)


def create_stat_card(title: str, value: str, change: str = "", icon: str = "") -> dbc.Card:
    """
    Create a minimal, professional stat card.
    
    Args:
        title: Card title
        value: Main value to display
        change: Optional change indicator (e.g., "+12%")
        icon: Optional icon
        
    Returns:
        Dash Bootstrap Card component
    """
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.Span(title, style={
                        'fontSize': '0.875rem',
                        'color': '#64748B',
                        'fontWeight': '500',
                        'textTransform': 'uppercase',
                        'letterSpacing': '0.05em'
                    }),
                ]),
                html.Div([
                    html.Span(value, style={
                        'fontSize': '2rem',
                        'fontWeight': '700',
                        'color': '#0F172A',
                        'lineHeight': '1.2'
                    }),
                ], style={'marginTop': '8px', 'marginBottom': '4px'}),
                html.Div([
                    html.Span(change, style={
                        'fontSize': '0.875rem',
                        'color': '#10B981' if change.startswith('+') else '#64748B',
                        'fontWeight': '500'
                    }) if change else None
                ])
            ])
        ], style={'padding': '24px'}),
        style={
            'border': '1px solid #E2E8F0',
            'borderRadius': '12px',
            'backgroundColor': 'white',
            'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
            'transition': 'all 0.2s ease',
            'height': '100%'
        },
        className='stat-card'
    )


def create_section_header(title: str, subtitle: str = "") -> html.Div:
    """
    Create a section header with title and optional subtitle.
    
    Args:
        title: Section title
        subtitle: Optional subtitle
        
    Returns:
        HTML Div component
    """
    return html.Div([
        html.H2(title, style={
            'fontSize': '1.5rem',
            'fontWeight': '700',
            'color': '#0F172A',
            'marginBottom': '4px'
        }),
        html.P(subtitle, style={
            'fontSize': '0.875rem',
            'color': '#64748B',
            'marginBottom': '0'
        }) if subtitle else None
    ], style={'marginBottom': '24px'})


def create_chart_card(title: str, chart: dcc.Graph, subtitle: str = "") -> dbc.Card:
    """
    Create a card wrapper for charts.
    
    Args:
        title: Chart title
        chart: Plotly graph component
        subtitle: Optional subtitle
        
    Returns:
        Dash Bootstrap Card component
    """
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.H3(title, style={
                    'fontSize': '1.125rem',
                    'fontWeight': '600',
                    'color': '#0F172A',
                    'marginBottom': '4px'
                }),
                html.P(subtitle, style={
                    'fontSize': '0.875rem',
                    'color': '#64748B',
                    'marginBottom': '20px'
                }) if subtitle else None
            ]),
            chart
        ], style={'padding': '24px'})
    ], style={
        'border': '1px solid #E2E8F0',
        'borderRadius': '12px',
        'backgroundColor': 'white',
        'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
        'height': '100%'
    })


def create_bike_distribution_chart(df: pd.DataFrame) -> dcc.Graph:
    """
    Create a clean donut chart for bike type distribution.
    
    Args:
        df: DataFrame with bike data
        
    Returns:
        Dash Graph component
    """
    distribution = get_bike_type_distribution(df)

    fig = go.Figure(data=[go.Pie(
        labels=['Mecaniques', 'Electriques'],
        values=[distribution['mechanical'], distribution['electric']],
        hole=0.65,
        marker=dict(
            colors=['#3B82F6', '#10B981'],
            line=dict(color='white', width=2)
        ),
        textinfo='percent',
        textfont=dict(size=14, color='#0F172A', family='Inter'),
        hovertemplate='<b>%{label}</b><br>%{value:,} velos<br>%{percent}<extra></extra>'
    )])

    fig.update_layout(
        showlegend=True,
        height=320,
        margin=dict(t=0, b=0, l=0, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color='#64748B', family='Inter')
        ),
        font=dict(family='Inter')
    )

    return dcc.Graph(figure=fig, config={'displayModeBar': False}, style={'height': '320px'})


def create_availability_histogram(df: pd.DataFrame) -> dcc.Graph:
    """
    Create a clean histogram of bike availability.
    
    Args:
        df: DataFrame with station data
        
    Returns:
        Dash Graph component
    """
    fig = px.histogram(
        df,
        x='num_bikes_available',
        nbins=25,
        labels={'num_bikes_available': 'Velos disponibles', 'count': 'Stations'},
        color_discrete_sequence=['#3B82F6']
    )

    fig.update_traces(
        marker=dict(line=dict(color='white', width=1)),
        hovertemplate='%{x} velos<br>%{y} stations<extra></extra>'
    )

    fig.update_layout(
        showlegend=False,
        height=320,
        margin=dict(t=0, b=40, l=40, r=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            gridcolor='#F1F5F9',
            title=dict(text='Velos disponibles', font=dict(size=12, color='#64748B')),
            tickfont=dict(size=11, color='#64748B')
        ),
        yaxis=dict(
            gridcolor='#F1F5F9',
            title=dict(text='Nombre de stations', font=dict(size=12, color='#64748B')),
            tickfont=dict(size=11, color='#64748B')
        ),
        font=dict(family='Inter')
    )

    return dcc.Graph(figure=fig, config={'displayModeBar': False}, style={'height': '320px'})


def create_capacity_chart(df: pd.DataFrame) -> dcc.Graph:
    """
    Create a clean horizontal bar chart for top stations.
    
    Args:
        df: DataFrame with station data
        
    Returns:
        Dash Graph component
    """
    top_stations = df.nlargest(8, 'capacity')[['name', 'capacity']].copy()

    fig = go.Figure(data=[
        go.Bar(
            x=top_stations['capacity'],
            y=top_stations['name'],
            orientation='h',
            marker=dict(
                color='#3B82F6',
                line=dict(color='white', width=1)
            ),
            text=top_stations['capacity'],
            textposition='outside',
            textfont=dict(size=11, color='#64748B'),
            hovertemplate='<b>%{y}</b><br>%{x} places<extra></extra>'
        )
    ])

    fig.update_layout(
        showlegend=False,
        height=360,
        margin=dict(t=0, b=40, l=200, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            gridcolor='#F1F5F9',
            title=dict(text='Capacite totale', font=dict(size=12, color='#64748B')),
            tickfont=dict(size=11, color='#64748B')
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(size=11, color='#64748B')
        ),
        font=dict(family='Inter')
    )

    return dcc.Graph(figure=fig, config={'displayModeBar': False}, style={'height': '360px'})


def create_home_layout(df: pd.DataFrame) -> html.Div:
    """
    Create the professional home page layout.
    
    Args:
        df: DataFrame with station data
        
    Returns:
        Dash HTML Div component
    """
    # Filter operational stations
    df_operational = filter_operational_stations(df)

    # Calculate metrics
    total_stations = len(df_operational)
    total_bikes = int(df_operational['num_bikes_available'].sum())
    total_ebikes = int(df_operational['ebikes'].sum())
    total_docks = int(df_operational['num_docks_available'].sum())
    avg_availability = df_operational['availability_rate'].mean()

    # Calculate percentages for change indicators
    ebike_percentage = (total_ebikes / total_bikes * 100) if total_bikes > 0 else 0

    layout = html.Div([
        # Main content area with proper spacing
        html.Div([
            # Page header
            html.Div([
                html.H1("Dashboard", style={
                    'fontSize': '2rem',
                    'fontWeight': '700',
                    'color': '#0F172A',
                    'marginBottom': '8px'
                }),
                html.P("Vue d'ensemble des stations Velib' Metropole en temps reel", style={
                    'fontSize': '1rem',
                    'color': '#64748B',
                    'marginBottom': '0'
                })
            ], style={'marginBottom': '32px'}),

            # KPI Grid - 4 columns
            dbc.Row([
                dbc.Col([
                    create_stat_card(
                        "Stations Actives",
                        format_large_number(total_stations),
                        "Operationnelles"
                    )
                ], xs=12, sm=6, lg=3, className="mb-4"),
                dbc.Col([
                    create_stat_card(
                        "Velos Disponibles",
                        format_large_number(total_bikes),
                        f"{avg_availability:.1f}% disponibilite"
                    )
                ], xs=12, sm=6, lg=3, className="mb-4"),
                dbc.Col([
                    create_stat_card(
                        "Velos Electriques",
                        format_large_number(total_ebikes),
                        f"{ebike_percentage:.1f}% du parc"
                    )
                ], xs=12, sm=6, lg=3, className="mb-4"),
                dbc.Col([
                    create_stat_card(
                        "Places Libres",
                        format_large_number(total_docks),
                        "Pour retour"
                    )
                ], xs=12, sm=6, lg=3, className="mb-4"),
            ], style={'marginBottom': '40px'}),

            # Analytics Section
            html.Div([
                create_section_header(
                    "Analyse de la Flotte",
                    "Repartition et disponibilite des velos sur le reseau"
                ),

                # Charts Grid
                dbc.Row([
                    # Left column - 2 smaller charts stacked
                    dbc.Col([
                        dbc.Row([
                            dbc.Col([
                                create_chart_card(
                                    "Repartition par Type",
                                    create_bike_distribution_chart(df_operational),
                                    "Proportion mecaniques vs electriques"
                                )
                            ], xs=12, className="mb-4")
                        ]),
                    ]),
                ]),
            ]),
            # Insights Section
            html.Div([
                create_section_header(
                    "Insights Cles",
                    "Points d'attention et tendances"
                ),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardBody([
                                html.Div([
                                    html.Span("Taux d'electrification", style={
                                        'fontSize': '0.875rem',
                                        'fontWeight': '600',
                                        'color': '#0F172A'
                                    })
                                ], style={'marginBottom': '8px'}),
                                html.P(
                                    f"{ebike_percentage:.1f}% des velos disponibles sont electriques, "
                                    f"soit {format_large_number(total_ebikes)} unites sur le reseau.",
                                    style={
                                        'fontSize': '0.875rem',
                                        'color': '#64748B',
                                        'marginBottom': '0',
                                        'lineHeight': '1.5'
                                    }
                                )
                            ], style={'padding': '20px'})
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
                                html.Div([
                                    html.Span("Disponibilite moyenne", style={
                                        'fontSize': '0.875rem',
                                        'fontWeight': '600',
                                        'color': '#0F172A'
                                    })
                                ], style={'marginBottom': '8px'}),
                                html.P(
                                    f"Le taux de disponibilite moyen est de {avg_availability:.1f}% "
                                    f"sur l'ensemble des {format_large_number(total_stations)} stations actives.",
                                    style={
                                        'fontSize': '0.875rem',
                                        'color': '#64748B',
                                        'marginBottom': '0',
                                        'lineHeight': '1.5'
                                    }
                                )
                            ], style={'padding': '20px'})
                        ], style={
                            'border': '1px solid #E2E8F0',
                            'borderRadius': '12px',
                            'backgroundColor': 'white',
                            'boxShadow': '0 1px 3px 0 rgba(0, 0, 0, 0.1)'
                        })
                    ], xs=12, md=6, className="mb-4"),
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
    print("Professional home page layout created successfully")


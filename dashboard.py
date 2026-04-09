import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, callback_context
import plotly.express as px
import dash_bootstrap_components as dbc

from Processing.analyse_data import load_data, preprocess

app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE], suppress_callback_exceptions=True)

df = load_data()
df = preprocess(df)
df = df[df['Month'].isin(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'])]
df = df[df['Week'] <= 27]

years = sorted(df['Year'].unique())

CARD_STYLE = {"margin-top": "20px", "box-shadow": "0 4px 6px rgba(0,0,0,0.3)"}

app.layout = dbc.Container([
    #header
    dbc.Row([
        dbc.Col(html.H1("ATM Analytics", className="text-center my-4 text-info"), width=12)
    ]),
    dbc.Row([
        dbc.Col(dbc.Card([dbc.CardBody([html.H6("Total Withdrawals"), html.H2(id="total-vol", className="text-info")])]), width=3),
        dbc.Col(dbc.Card([dbc.CardBody([html.H6("Total Cash Out"), html.H2(id="total-val", className="text-success")])]), width=3),
        dbc.Col(dbc.Card([dbc.CardBody([html.H6("Avg Txn Value"), html.H2(id="avg-val", className="text-warning")])]), width=3),
        dbc.Col(dbc.Card([dbc.CardBody([html.H6("Top ATM"), html.H2(id="top-atm", className="text-danger")])]), width=3),
    ], className="mb-4"),

    #Year Dropdown
    dbc.Row([
        dbc.Col([
            dbc.Nav([
                #Yearly Performance
                dbc.DropdownMenu(
                    [dbc.DropdownMenuItem(str(y), id=f"year-{y}", n_clicks=0) for y in years],
                    label="Yearly Performance",
                    nav=True,
                    in_navbar=True,
                    className="text-info",
                    id="yearly-nav-dropdown"
                ),
                #Growth Trends
                dbc.NavLink("Growth Trends", id="growth-link", n_clicks=0, href="#", active=False),
            ], pills=True, className="justify-content-center")
        ], width=12)
    ]),

    #hidden stores to keep track of state
    dcc.Store(id='selected-year', data=years[0]),
    dcc.Store(id='active-tab', data='yearly'),

    #tab Content
    html.Div(id="tab-content")
], fluid=True)

#CALLBACK

@app.callback(
    [Output('selected-year', 'data'),
     Output('active-tab', 'data'),
     Output('yearly-nav-dropdown', 'label')],
    [Input(f"year-{y}", 'n_clicks') for y in years] + [Input('growth-link', 'n_clicks')],
    prevent_initial_call=True
)
def update_state(*args):
    ctx = callback_context
    if not ctx.triggered:
        return years[0], 'yearly', "Yearly Performance"
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'growth-link':
        return years[0], 'growth', "Yearly Performance"
    else:
        selected_year = int(triggered_id.split('-')[1])
        return selected_year, 'yearly', f"Yearly: {selected_year}"

@app.callback(
    [Output("total-vol", "children"),
     Output("total-val", "children"),
     Output("avg-val", "children"),
     Output("top-atm", "children")],
    [Input('selected-year', 'data'),
     Input('active-tab', 'data')]
)
def update_kpis(select_year, active_tab):
    #If on Growth tab, use all data. If on Yearly, filter by year.
    if active_tab == 'growth':
        df_kpi = df.copy()
        label_prefix = "Total " 
    else:
        df_kpi = df[df['Year'] == select_year].copy()
        label_prefix = ""

    if df_kpi.empty:
        return "0", "0", "0", "N/A"

    #Total Withdrawals
    total_vol = df_kpi['No Of Withdrawals'].sum()
    
    #Total Cash Out
    total_val = df_kpi['Total Amount Withdrawn'].sum()
    
    #Avg Txn Value
    safe_df = df_kpi[df_kpi['No Of Withdrawals'] > 0]
    total_txns = safe_df['No Of Withdrawals'].sum()
    avg_val = safe_df['Total Amount Withdrawn'].sum() / total_txns if total_txns > 0 else 0
    
    #Top Performing ATM
    top_atm_name = df_kpi.groupby('ATM Name')['No Of Withdrawals'].sum().idxmax()

    return (
        f"{total_vol:,}", 
        f"₦{total_val:,.0f}", 
        f"₦{avg_val:,.0f}", 
        top_atm_name
    )

#render Content based on State
@app.callback(
    Output('tab-content', 'figure' if False else 'children'),
    [Input('active-tab', 'data'),
     Input('selected-year', 'data')]
)
def render_tab_content(active_tab, select_year):
    template = "plotly_dark"
    
    if active_tab == 'growth':
        #TAB GROWTH TRENDS
        comparison_data = df.pivot_table(
            values='No Of Withdrawals', index='Month', columns='Year', 
            aggfunc='sum', observed=False
        ).reset_index()

        fig_growth = px.bar(
            comparison_data, x='Month', y=comparison_data.columns[1:],
            barmode='group', title="Year-over-Year Monthly Comparison",
            template=template, labels={'value': 'Total Withdrawals', 'variable': 'Year'}
        )
        return dbc.Row([
            dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=fig_growth))], style=CARD_STYLE), width=12)
        ])

    else:
        #TAB YEARLY PERFORMANCE
        df_year = df[df['Year'] == select_year].copy()
        
        # Monthly
        monthly = df_year.groupby('Month', sort=False, observed=False)['No Of Withdrawals'].sum().reset_index()
        fig1 = px.bar(monthly, x='Month', y="No Of Withdrawals", color="Month", title=f"Volume - {select_year}", template=template)
        
        # Weekly
        weekly = df_year.groupby('Week')["No Of Withdrawals"].sum().reset_index()
        fig2 = px.line(weekly, x='Week', y="No Of Withdrawals", title="Weekly Velocity", template=template)

        # ATM
        atm = df_year.groupby('ATM Name')["No Of Withdrawals"].sum().reset_index().sort_values(by="No Of Withdrawals", ascending=False).head(5)
        fig3 = px.bar(atm, x='ATM Name', y="No Of Withdrawals", color="ATM Name", title="Top 5 ATMs", template=template)

        #Card Share
        xyz_col = next((c for c in df_year.columns if 'Xyz' in c), None)
        other_col = next((c for c in df_year.columns if 'Other' in c), None)
        if xyz_col and other_col:
            card_df = pd.DataFrame({'Card': ['XYZ', 'Others'], 'Total': [df_year[xyz_col].sum(), df_year[other_col].sum()]})
            fig4 = px.pie(card_df, values='Total', names='Card', title="Card Share", template=template, hole=0.4)
        else:
            fig4 = px.bar(title="Card Data Missing", template=template)

        #Efficiency
        safe_df = df_year[df_year['No Of Withdrawals'] > 0].copy()
        safe_df['Avg_Txn_Size'] = safe_df['Total Amount Withdrawn'] / safe_df['No Of Withdrawals']
        avg_size = safe_df.groupby('Month', observed=False)['Avg_Txn_Size'].mean().reset_index()
        fig5 = px.area(avg_size, x='Month', y='Avg_Txn_Size', title="Average Withdrawal Size", template=template)

        #Festival
        fest_map = {
            'NH': 'National Holiday',
            'H':  'Hindu Festival',
            'M':  'Muslim Festival',
            'N':  'New Year Period',
            'C':  'Christian Festival'
        }

        #Filter empty/none values and map the codes
        fest_df = df_year[~df_year['Festival Religion'].isin(['None', 'no_festival', 'No Festival', ' ', 'None'])].copy()
        fest_df['Festival Name'] = fest_df['Festival Religion'].map(fest_map).fillna(fest_df['Festival Religion'])

        if not fest_df.empty:
            fest_impact = fest_df.groupby('Festival Name')['Total Amount Withdrawn'].sum().reset_index()
            # Sort by value
            fest_impact = fest_impact.sort_values('Total Amount Withdrawn', ascending=True)

            fig6 = px.bar(
                fest_impact, 
                x='Total Amount Withdrawn', 
                y='Festival Name', 
                orientation='h', 
                color="Festival Name", 
                title="Impact of Festive Periods on Cash Out",
                template=template,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            #text labels on the bars
            fig6.update_traces(texttemplate='₦%{x:,.0s}', textposition='outside')
        else:
            fig6 = px.bar(title="No Festive Impact Detected for this Period", template=template)

        for f in [fig1, fig3, fig6]: f.update_layout(showlegend=False)

        return html.Div([
            dbc.Row([
                dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=fig1))], style=CARD_STYLE), width=6),
                dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=fig2))], style=CARD_STYLE), width=6),
            ]),
            dbc.Row([
                dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=fig5))], style=CARD_STYLE), width=6),
                dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=fig4))], style=CARD_STYLE), width=6),
            ]),
            dbc.Row([
                dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=fig3))], style=CARD_STYLE), width=6),
                dbc.Col(dbc.Card([dbc.CardBody(dcc.Graph(figure=fig6))], style=CARD_STYLE), width=6),
            ])
        ])

if __name__ == '__main__':
    app.run(debug=True)
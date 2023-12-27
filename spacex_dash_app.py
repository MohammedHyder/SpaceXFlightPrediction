# Import required libraries
import pandas as pd
import dash
# import dash_html_components as html
# import dash_core_components as dcc
from dash import html 
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

DEBUG = True 

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
step = 1000

launch_sites_df = spacex_df.groupby('Launch Site', as_index=False).sum()

mark_val = [i for i in range(0, 10000, step)]# range(int(min_payload), int(max_payload), step)]
mark_label = [str(i) for i in range(0, 10000, step)]# i in range(int(min_payload), int(max_payload), step)]
marks = dict(zip(mark_val, mark_label))

dropdown_options = [{'label': row, 'value': row} for row in launch_sites_df['Launch Site']]
dropdown_options.append({'label':'ALL', 'value':'ALL'})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
                    html.H1('SpaceX Launch Records Dashboard',
                            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
                    # TASK 1: Add a dropdown list to enable Launch Site selection
                    # The default select value is for ALL sites
                    dcc.Dropdown(
                        id='site-dropdown', 
                        options=dropdown_options,
                        value='ALL',
                        placeholder='Select a launch site',
                        style={'width':'0.8', 'padding':'3', 'fontSize':'20', 'textAlignLast' : 'center'}),
                    html.Br(),

                    # TASK 2: Add a pie chart to show the total successful launches count for all sites
                    # If a specific launch site was selected, show the Success vs. Failed counts for the site
                    html.Div(dcc.Graph(
                            id='success-pie-chart')
                        ),
                    html.Br(),

                    html.P("Payload range (Kg):"),
                    # TASK 3: Add a slider to select payload range
                    dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=step,
                                    marks=marks,
                                           # {0:'0',
                                           # 100:'100'},
                                    value=[min_payload, max_payload]),
                    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                    html.Div(dcc.Graph(
                        id='success-payload-scatter-chart')
                        ),
                    ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value'))

def get_pie_chart(launch_site):
    filtered_df = spacex_df
    if launch_site == 'ALL':
        success_df = filtered_df[filtered_df['class'] == 1]
        success_launch_df = success_df.groupby('Launch Site', as_index = False).sum() # .reset_index()  # same as as_index = False
        fig = px.pie(success_launch_df, 
                    values='class',
                    names='Launch Site', 
                    title='Total Success Launches by Site')
        return fig
    else:
        launch_site_df = filtered_df[filtered_df['Launch Site'] == launch_site]
        launch_site_df = launch_site_df.value_counts('class').to_frame().reset_index()
        launch_site_df.columns = ['class', 'counts']
        # launch_site_df = filtered_df.groupby('Launch Site', as_index = False).mean()
        # launch_site_df = launch_site_df[launch_site_df['Launch Site'] == launch_site]
        # launch_site_df = launch_site_df.groupby('class', as_index = False).sum()
        fig = px.pie(launch_site_df, 
                    values='counts',
                    names='class', 
                    title='Total Success Launches for site %s' % launch_site)
        return fig 

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(
        Output(component_id='success-payload-scatter-chart', component_property='figure'),
        [Input(component_id='site-dropdown', component_property='value'),
         Input(component_id='payload-slider', component_property='value')
        ])

def update_output(launch_site, payload_range):
    filtered_df = spacex_df 
    min_pay = payload_range[0]
    max_pay = payload_range[1]

    # launch_site_df
    if launch_site == 'ALL':
        filtered_df = filtered_df[filtered_df['Payload Mass (kg)'] < max_pay]
        filtered_df = filtered_df[filtered_df['Payload Mass (kg)'] > min_pay]
        
        fig = px.scatter(filtered_df,
                        x = 'Payload Mass (kg)',
                        y = 'class',
                        color = 'Booster Version Category',
                        title='Correlation between Payload and Success for all Sites'
        ) 
        return fig
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == launch_site]
        filtered_df = filtered_df[filtered_df['Payload Mass (kg)'] < max_pay]
        filtered_df = filtered_df[filtered_df['Payload Mass (kg)'] > min_pay]

        fig = px.scatter(filtered_df,
                        x = 'Payload Mass (kg)',
                        y = 'class',
                        color = 'Booster Version Category',
                        title ='Correlation between Payload and Success for site %s' % launch_site
        ) 
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug = DEBUG)

# Which site has the largest successful launches?
# Which site has the highest launch success rate?
# Which payload range(s) has the highest launch success rate?
# Which payload range(s) has the lowest launch success rate?
# Which F9 Booster version (v1.0, v1.1, FT, B4, B5, etc.) has the highest
# launch success rate?
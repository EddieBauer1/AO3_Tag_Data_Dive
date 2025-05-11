import dash
from dash import dcc, html, Output, Input
import plotly.express as px
from src.processing import create_master_table, sort_years, sort_word_counts, sort_completion, autocorrect
from src.data_prep import check_if_exists, import_data, csv_to_db, preprocess, split_tags

# Ensure data is ready
if not check_if_exists():
    print("Importing Data...")
    import_data()
    print("Creating SQL database...")
    csv_to_db()
    print("Preprocessing...")
    preprocess()
    print("Creating work-tag pairs... (This may take some time, thank you for your patience)")
    split_tags()

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "AO3 Tag Data Dive"

# Layout
app.layout = html.Div([
    html.H1("AO3 Tag Data Dashboard",
            style={
                'backgroundColor': 'maroon',
                'color': 'white',
                'fontFamily': 'Arial, sans-serif',
                'textAlign': 'center',
                'padding': '20px',
                'margin': '0'
                }),
    html.Div([
        dcc.Input(id="tag-input", 
                  type="text", 
                  placeholder="Enter Tag (Any Character, Fandom, Trope, etc.)", 
                  debounce=True,
                  style={
                      'width': '30%'
                  }),
        html.Button("Analyze", id="analyze-button", n_clicks=0)
    ]),
    html.Div(id="output-message", style={"fontFamily": "Arial, sans-serif"}),
    html.Div([
        dcc.Graph(id="year-graph"),
        html.Div(id="year-stats", style={"padding": "10px"})
    ]),
    html.Div([
        dcc.Graph(id="wordcount-graph"),
        html.Div(id="wordcount-stats", style={"padding": "10px"})
    ]),
    html.Div([
        dcc.Graph(id="completion-graph"),
        html.Div(id="completion-stats", style={"padding": "10px"})
    ])
])

# Callback
@app.callback(
    Output("output-message", "children"),
    Output("year-graph", "figure"),
    Output("year-stats", "children"),
    Output("wordcount-graph", "figure"),
    Output("wordcount-stats", "children"),
    Output("completion-graph", "figure"),
    Output("completion-stats", "children"),
    Input("analyze-button", "n_clicks"),
    Input("tag-input", "value")
)

def update_dashboard(n_clicks, tagname):
    if not tagname:
        return "Please enter a tag name.", {}, "", {}, "", {}, ""

    try:
        # Get selected works
        try:
            master_table = create_master_table(tagname)
        except ValueError as no_tag_found:
            options = list(autocorrect(tagname))
            if not options:
                return f"{str(no_tag_found)} No potential matching tags found, sorry!", {}, "", {}, "", {}, ""
            return f"{str(no_tag_found)} Could you mean one of these options instead? {options}", {}, "", {}, "", {}, ""

        # Year graph
        years_table = sort_years()
        year_fig = px.bar(years_table, 
                          x="creation_year", 
                          y="num_works",
                          title=f"Works Containing '{tagname}' Tag by Year", 
                          color_discrete_sequence=['maroon'])
        
        year_fig.update_layout(  
            title_font = dict(family="Arial, sans-serif", size = 24, color = "black"),
            font = dict(family = "Arial, sans-serif", size = 14),
            xaxis_title = "Year",
            yaxis_title = "Number of Works",
            xaxis_title_font = dict(family = "Arial, sans-serif", size = 16),
            yaxis_title_font = dict(family = "Arial, sans-serif", size = 16)
        )
        
        count = sum(years_table['num_works'])
        maximum = years_table[years_table['num_works'] == years_table['num_works'].max()]
        minimum = years_table[years_table['num_works'] == years_table['num_works'].min()]

        year_stats = html.Div([
            html.P(f"Total Works: {count:,}"),
            html.P(f"Most Popular Year: {maximum['creation_year'].iloc[0]} ({(maximum['num_works'].iloc[0]):,} Works)"),
            html.P(f"Least Popular Year: {minimum['creation_year'].iloc[0]} ({(minimum['num_works'].iloc[0]):,} Works)")
        ], style = {"fontFamily": "Arial, sans-serif", "fontSize": "16px", "padding": "10px"})

        # Word count graph
        word_count = sort_word_counts()
        wordcount_fig = px.bar(word_count, 
                        x = "word_bracket", 
                        y = "num_works", 
                        title = f"Works Containing '{tagname}' by Word Count", 
                        color_discrete_sequence = ['maroon']
        )
        
        wordcount_fig.update_layout(  
            title_font = dict(family="Arial, sans-serif", size = 24, color = "black"),
            font = dict(family = "Arial, sans-serif", size = 14),
            xaxis_title = "Word Count",
            yaxis_title = "Number of Works",
            xaxis_title_font = dict(family = "Arial, sans-serif", size = 16),
            yaxis_title_font = dict(family = "Arial, sans-serif", size = 16)
        )
        
        total = int(master_table['word_count'].sum())
        maximum = master_table[master_table['word_count'] == master_table['word_count'].max()]
        average = f"{total / len(master_table):,.1f}"

        wordcount_stats = html.Div([
            html.P(f"Total Word Count: {total:,} Words"),
            html.P(f"Highest Word Count: {int(maximum['word_count'].iloc[0]):,} Words"),
            html.P(f"Average Word Count per Work: {average} Words")
        ], style = {"fontFamily": "Arial, sans-serif", "fontSize": "16px", "padding": "10px"})

        # Completion graph
        completion = sort_completion()
        completion_fig = px.pie(completion,
                        names="complete",  
                        values = "num_works",
                        title = f"Works Containing '{tagname}' by Completion",
                        color = "complete", 
                        color_discrete_map = {'Complete':'maroon',
                                 'Incomplete':'lightgray'}
        )
        
        completion_fig.update_layout(  
            title_font = dict(family="Arial, sans-serif", size = 24, color = "black"),
            font = dict(family = "Arial, sans-serif", size = 14)
        )
        
        complete = int(master_table['complete'].sum())
        incomplete = len(master_table) - complete

        completion_stats = html.Div([
            html.P(f"Number of Complete Works: {complete:,} Works"),
            html.P(f"Number of Incomplete Works: {incomplete:,} Works")
        ], style = {"fontFamily": "Arial, sans-serif", "fontSize": "16px", "padding": "10px"})

        return f"Showing results for '{tagname}'", year_fig, year_stats, wordcount_fig, wordcount_stats, completion_fig, completion_stats

    except Exception as error:
        return f"Error processing tag '{tagname}': {str(error)}", {}, "", {}, "", {}, ""

# Run app
if __name__ == "__main__":
    app.run(debug = False)
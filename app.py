import dash
from dash import dcc, html, Output, Input
import plotly.express as px
from src.processing import create_master_table, sort_years, sort_word_counts, sort_completion, autocorrect
from src.data_prep import data_prep_process

# Ensure data is ready
data_prep_process()

# Initialize the Dash app
app = dash.Dash(__name__)
# Name app
app.title = "AO3 Tag Data Dive"

# Layout
app.layout = html.Div([
    # Create AO3-themed header
    html.H1("AO3 Tag Data Dashboard",
            style={
                'backgroundColor': 'maroon',
                'color': 'white',
                'fontFamily': 'Arial, sans-serif',
                'textAlign': 'center',
                'padding': '20px',
                'margin': '0'
                }),
    # Create user input area
    html.Div([
        dcc.Input(id="tag-input", 
                  type="text", 
                  placeholder="Enter Tag (Any Character, Fandom, Trope, etc.)", 
                  debounce=True,
                  style={
                      'width': '30%'
                  }),
        # Create "Analyze" button
        html.Button("Analyze", id="analyze-button", n_clicks=0)
    ]),
    # Output message gives user feedback
    html.Div(id="output-message", style={"fontFamily": "Arial, sans-serif"}),
    # Work by Year graph and stats
    html.Div([
        dcc.Graph(id="year-graph"),
        html.Div(id="year-stats", style={"padding": "10px"})
    ]),
    # Work by Wordcount graph and stats
    html.Div([
        dcc.Graph(id="wordcount-graph"),
        html.Div(id="wordcount-stats", style={"padding": "10px"})
    ]),
    # Work by Completion graph and stats
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

def update_dashboard(n_clicks, tagname) -> tuple:
    """
    Updates the dashboard with results based on the given tagname.
    Retrieves the works associated with the specified tagname.
    If the tagname is invalid, offers suggestions for potential matching tags.
    If tag works, generate the year, word count, and completion graphs and statistics.
    
    Parameters:
        n_clicks (int): The number of times the analyze button has been clicked.
                        Even though it isn't used, it causes the function to run 
                        only after the user clicks the button. 
        tagname (str): The tag to search for in the database.

    Returns:
        Tuple:
            - A string message indicating the result of the analysis or an error message.
            - A Plotly figure for the year graph.
            - A Div containing the year statistics.
            - A Plotly figure for the word count graph.
            - A Div containing the word count statistics.
            - A Plotly figure for the completion graph.
            - A Div containing the completion statistics.
    """
    # If tagname has not been inputed, prompt user for tagname and return empty figures
    if not tagname:
        return "Please enter a tag name.", {}, "", {}, "", {}, ""

    try:
        try:
            # Get selected works containing tag
            master_table = create_master_table(tagname)
        # If tag is not found:
        except ValueError as no_tag_found:
            # Find list of potential similar tags
            options = list(autocorrect(tagname))
            if not options:
                # If there are no similar tags, return this error message
                return f"{str(no_tag_found)} No potential matching tags found, sorry!", {}, "", {}, "", {}, ""
            # If there are similar tags, return error message containing possible options
            return f"{str(no_tag_found)} Could you mean one of these options instead? {options}", {}, "", {}, "", {}, ""

        # Year graph
        # Get table of years and num_works
        years_table = sort_years()
        # Create bar chart showing works per year
        year_fig = px.bar(years_table, 
                          x="creation_year", 
                          y="num_works",
                          title=f"Works Containing '{tagname}' Tag by Year", 
                          color_discrete_sequence=['maroon'])
        # Fix x and y axis titles, ensure font remains the consistent for the graph
        year_fig.update_layout(  
            title_font = dict(family="Arial, sans-serif", size = 24, color = "black"),
            font = dict(family = "Arial, sans-serif", size = 14),
            xaxis_title = "Year",
            yaxis_title = "Number of Works",
            xaxis_title_font = dict(family = "Arial, sans-serif", size = 16),
            yaxis_title_font = dict(family = "Arial, sans-serif", size = 16)
        )
        # Get total number of works
        count = sum(years_table['num_works'])
        # Find year with most works
        maximum = years_table[years_table['num_works'] == years_table['num_works'].max()]
        # Find year with least works
        minimum = years_table[years_table['num_works'] == years_table['num_works'].min()]
        # Create relevant statistics for the year chart
        year_stats = html.Div([
            html.P(f"Total Works: {count:,}"),
            html.P(f"Most Popular Year: {maximum['creation_year'].iloc[0]} ({(maximum['num_works'].iloc[0]):,} Works)"),
            html.P(f"Least Popular Year: {minimum['creation_year'].iloc[0]} ({(minimum['num_works'].iloc[0]):,} Works)")
        ], style = {"fontFamily": "Arial, sans-serif", "fontSize": "16px", "padding": "10px"})

        # Word count graph
        # Get table of word count ranges and num_works
        word_count = sort_word_counts()
        # Create bar chart showing works per word count range
        wordcount_fig = px.bar(word_count, 
                        x = "word_bracket", 
                        y = "num_works", 
                        title = f"Works Containing '{tagname}' by Word Count", 
                        color_discrete_sequence = ['maroon']
        )
        # Ensure font remains consistent, fix x and y axis titles
        wordcount_fig.update_layout(  
            title_font = dict(family="Arial, sans-serif", size = 24, color = "black"),
            font = dict(family = "Arial, sans-serif", size = 14),
            xaxis_title = "Word Count",
            yaxis_title = "Number of Works",
            xaxis_title_font = dict(family = "Arial, sans-serif", size = 16),
            yaxis_title_font = dict(family = "Arial, sans-serif", size = 16)
        )
        # Get total word count
        total = int(master_table['word_count'].sum())
        # Get word count of the work with the highest word count
        maximum = master_table[master_table['word_count'] == master_table['word_count'].max()]
        # Get average word count
        average = f"{total/len(master_table):,.1f}"
        # Create word count statistics
        wordcount_stats = html.Div([
            html.P(f"Total Word Count: {total:,} Words"),
            html.P(f"Highest Word Count: {int(maximum['word_count'].iloc[0]):,} Words"),
            html.P(f"Average Word Count per Work: {average} Words")
        ], style = {"fontFamily": "Arial, sans-serif", "fontSize": "16px", "padding": "10px"})

        # Completion graph
        # Get table of completion status and num_works
        completion = sort_completion()
        # Create pie chart of works per completion status
        completion_fig = px.pie(completion,
                        names="complete",  
                        values = "num_works",
                        title = f"Works Containing '{tagname}' by Completion",
                        color = "complete", 
                        color_discrete_map = {'Complete':'maroon',
                                 'Incomplete':'lightgray'}
        )
        # Ensure consistent font
        completion_fig.update_layout(  
            title_font = dict(family="Arial, sans-serif", size = 24, color = "black"),
            font = dict(family = "Arial, sans-serif", size = 14)
        )
        # Get number of completed works
        complete = int(master_table['complete'].sum())
        # Get number of incomplete works
        incomplete = len(master_table) - complete
        # Create statistics for completion status
        completion_stats = html.Div([
            html.P(f"Number of Complete Works: {complete:,} Works"),
            html.P(f"Number of Incomplete Works: {incomplete:,} Works")
        ], style = {"fontFamily": "Arial, sans-serif", "fontSize": "16px", "padding": "10px"})
        # Return the results to display on the dashboard
        return f"Showing results for '{tagname}'", year_fig, year_stats, wordcount_fig, wordcount_stats, completion_fig, completion_stats

    except Exception as error:
        # Handle any errors that may occur during processing
        return f"Error processing tag '{tagname}': {str(error)}", {}, "", {}, "", {}, ""

# Run app
if __name__ == "__main__":
    app.run(debug = False)
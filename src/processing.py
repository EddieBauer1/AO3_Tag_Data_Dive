import sqlite3 
import pandas as pd

def find_tag(tagname: str) -> int:
    """
    Find the tag ID of the given tag name, or raise ValueError if tag not found.
    
    Parameters:
        tagname (str): Name of the tag, as found in the tags table.
    
    Returns:
        tag["id"].values[0] (int): Tag ID associated with the given tag name.
    """
    # Create DataFrame of the given tag's data from tags table
    with sqlite3.connect('data/fanfic.db') as conn:
        tag = pd.read_sql_query(f"""
        SELECT *
        FROM tags
        WHERE name LIKE '{tagname}';
        """, conn)
    # If the DataFrame is empty and there is no matching tag, 
    # raise ValueError stating that tag could not be found
    if tag.empty:
        raise ValueError(f"'{tagname}' tag not found.")
    # Return the tag ID
    return tag["id"].values[0]

def find_works(tagname: str) -> pd.DataFrame:
    """
    Find all work IDs paired with the given tag in the work_tag_pairs table.
    
    Parameters:
        tagname (str): Name of the tag, as found in the tags table.
    
    Returns:
        works (pd.DataFrame): DataFrame containing all work IDs paired with the given tag.
    """
    # Find the tag ID of the given tag
    tag_id = find_tag(tagname)
    # Select all work IDs paired with the tag ID
    with sqlite3.connect('data/fanfic.db') as conn:
        works = pd.read_sql_query(f"""
        SELECT work_id
        FROM work_tag_pairs
        WHERE tag_id = '{tag_id}';
        """, conn)
    return works

def get_work_data(tagname: str) -> pd.DataFrame:
    """
    Find the data of the work IDs paired with the given tag.
    
    Parameters:
        tagname (str): Name of the tag, as found in the tags table.
    
    Returns:
        work_data (pd.DataFrame): DataFrame containing the data for all works 
                                  containing the given tag.
    """
    # Get list of all work IDs paired with the tag ID
    work_list = list(find_works(tagname)["work_id"])
    # Convert work_list into comma-separated string
    work_str = ','.join(str(work) for work in work_list)
    # Select all data from works table for each work ID in work_str
    with sqlite3.connect('data/fanfic.db') as conn:
        work_data = pd.read_sql_query(f"""
        SELECT *
        FROM works
        WHERE work_id IN ({work_str});
        """, conn)
    return work_data

def create_master_table(tagname: str) -> pd.DataFrame:
    """
    Add creation_year column from creation_date,
    and convert DataFrame of works containing given tag into SQL table "selected works".
    
    Parameters:
        tagname (str): Name of the tag, as found in the tags table.
    
    Returns:
        work_no_nan (pd.DataFrame): Final cleaned DataFrame containing the data for all works 
                                    containing the given tag.
    """
    # Get table of works containing the given tag.
    work_data = get_work_data(tagname)
    # Clears out any rows with NaN values (very few rows have NaN word count, etc.)
    work_no_nan = work_data[~work_data.isna().any(axis=1)].copy()
    # Create creation_year column from creation_date
    work_no_nan['creation_year'] = work_no_nan['creation_date'].astype(str).str[:4]
    # Create selected_works table in fanfic.db from work_no_nan 
    # (replacing table for previous search, if necessary)
    with sqlite3.connect('data/fanfic.db') as conn:
        work_no_nan.to_sql("selected_works", conn, if_exists='replace', index=False)
    return work_no_nan

def sort_years() -> pd.DataFrame:
    """
    Sort works in selected_works by year.
    
    Parameters:
        None
    
    Returns:
        years_data (pd.DataFrame): DataFrame containing years and number of works created 
                                   in that year.
    """
    # Create years_data DataFrame, grouping selected_works by creation_year
    with sqlite3.connect('data/fanfic.db') as conn:
        years_data = pd.read_sql_query("""
        SELECT creation_year, count(work_id) as num_works
        FROM selected_works
        GROUP BY creation_year
        """, conn)
    return years_data

def sort_word_counts() -> pd.DataFrame:
    """
    Sort works in selected_works by word count ranges.
    
    Parameters:
        None
    
    Returns:
        word_count_data (pd.DataFrame): DataFrame containing ranges of word counts,
                                        and the number of works that fall within those ranges.
    """
    # Create word_count_data with word_bracket (ranges of word counts) and num_works
    with sqlite3.connect('data/fanfic.db') as conn:
        word_count_data = pd.read_sql_query("""
        SELECT 
            CASE
                WHEN word_count < 1000 THEN '< 1k'
                WHEN word_count BETWEEN 1000 AND 2499 THEN '1k-2.5k'
                WHEN word_count BETWEEN 2500 AND 4999 THEN '2.5k-5k'
                WHEN word_count BETWEEN 5000 AND 9999 THEN '5k-10k'
                WHEN word_count BETWEEN 10000 AND 24999 THEN '10k-25k'
                WHEN word_count BETWEEN 25000 AND 49999 THEN '25k-50k'
                WHEN word_count BETWEEN 50000 AND 74999 THEN '50k-75k'
                WHEN word_count BETWEEN 75000 AND 99999 THEN '75k-100k'
                WHEN word_count BETWEEN 100000 AND 149999 THEN '100k-150k'
                WHEN word_count BETWEEN 150000 AND 199999 THEN '150k-200k'
                WHEN word_count > 199999 THEN '200k+'
            END AS word_bracket,
            COUNT(*) AS num_works
        FROM selected_works
        GROUP BY word_bracket
        """, conn)
    # Word count brackets in increasing order
    order = ['< 1k', '1k-2.5k', '2.5k-5k', '5k-10k', '10k-25k', '25k-50k', '50k-75k',
         '75k-100k', '100k-150k', '150k-200k', '200k+']
    # Use the order of word counts as listed above, instead of alphabetical order
    word_count_data['word_bracket'] = pd.Categorical(word_count_data['word_bracket'], 
                                                     categories=order, 
                                                     ordered=True)
    # Sort word_count_data by word_bracket order
    word_count_data = word_count_data.sort_values('word_bracket')
    return word_count_data

def sort_completion() -> pd.DataFrame:
    """
    Sort works in selected_works by completion.
    
    Parameters:
        None
    
    Returns:
        completion_data (pd.DataFrame): DataFrame containing number of 
                                        complete and incomplete works
    """
    # Get table of number of complete and incomplete works from selected_works
    with sqlite3.connect('data/fanfic.db') as conn:
        completion_data = pd.read_sql_query("""
        SELECT complete, count(work_id) as num_works
        FROM selected_works
        GROUP BY complete
        """, conn)
    # Turn complete/incomplete values into actual "Complete" and "Incomplete" in DataFrame
    completion_data['complete'] = completion_data['complete'].map({1: 'Complete', 
                                                                   0: 'Incomplete'})
    return completion_data

def autocorrect(tagname: str) -> list:
    """
    Find the ten most used tags that contain the given tag name somewhere within their name,
    intended to find tags similar to the one the user inputed.
    
    Parameters:
        tagname (str): Name of the tag that user inputed.
    
    Returns:
        close_tags['name'].tolist() (list): List of ten most used tags containing "tagname"
    """
    # Search tags table for 10 most commonly used tags with "tagname" within
    with sqlite3.connect('data/fanfic.db') as conn:
        close_tags = pd.read_sql_query(f"""
            SELECT name, cached_count
            FROM tags
            WHERE name LIKE '%{tagname}%'
            ORDER BY cached_count DESC
            LIMIT 10;
        """, conn)
    # Return the matching tag names as a list
    return close_tags['name'].tolist()
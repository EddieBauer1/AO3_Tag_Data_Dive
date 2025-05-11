import sqlite3 
import pandas as pd

def find_tag(tagname: str) -> int:
    with sqlite3.connect('data/fanfic.db') as conn:
        tag = pd.read_sql_query(f"""
        SELECT *
        FROM tags
        WHERE name LIKE '{tagname}';
        """, conn)
    if tag.empty:
        raise ValueError(f"'{tagname}' tag not found.")
    return tag["id"].values[0]

def find_works(tagname: str):
    tag_id = find_tag(tagname)
    with sqlite3.connect('data/fanfic.db') as conn:
        works = pd.read_sql_query(f"""
        SELECT work_id
        FROM work_tag_pairs
        WHERE tag_id = '{tag_id}';
        """, conn)
    return works

def get_work_data(tagname: str):
    work_list = list(find_works(tagname)["work_id"])
    work_str = ','.join(str(work) for work in work_list)
    with sqlite3.connect('data/fanfic.db') as conn:
        work_data = pd.read_sql_query(f"""
        SELECT *
        FROM works
        WHERE work_id IN ({work_str});
        """, conn)
    return work_data

def create_master_table(tagname: str):
    work_data = get_work_data(tagname)
    work_no_nan = work_data[~work_data.isna().any(axis=1)].copy()
    work_no_nan['creation_year'] = work_no_nan['creation_date'].astype(str).str[:4]
    with sqlite3.connect('data/fanfic.db') as conn:
        work_no_nan.to_sql("selected_works", conn, if_exists='replace', index=False)
    return work_no_nan

def sort_years():
    with sqlite3.connect('data/fanfic.db') as conn:
        years_data = pd.read_sql_query("""
        SELECT creation_year, count(work_id) as num_works
        FROM selected_works
        GROUP BY creation_year
        """, conn)
    return years_data

def sort_word_counts():
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
    order = ['< 1k', '1k-2.5k', '2.5k-5k', '5k-10k', '10k-25k', '25k-50k', '50k-75k',
         '75k-100k', '100k-150k', '150k-200k', '200k+']
    word_count_data['word_bracket'] = pd.Categorical(word_count_data['word_bracket'], categories=order, ordered=True)
    word_count_data = word_count_data.sort_values('word_bracket')
    return word_count_data

def sort_completion():
    with sqlite3.connect('data/fanfic.db') as conn:
        completion_data = pd.read_sql_query("""
        SELECT complete, count(work_id) as num_works
        FROM selected_works
        GROUP BY complete
        """, conn)
    completion_data['complete'] = completion_data['complete'].map({1: 'Complete', 0: 'Incomplete'})
    return completion_data

def autocorrect(tagname: str) -> list:
    # Fetch matching tag names using SQL LIKE
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
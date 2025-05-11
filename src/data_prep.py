import os
import sqlite3 
import pandas as pd
import requests
import zipfile
from pathlib import Path

def import_data():
    Path("data").mkdir(parents=True, exist_ok=True)
    # Check if files exist first
    tags = Path("data/tags-20210226.csv")
    works = Path("data/works-20210226.csv")
    if tags.is_file() and works.is_file():
        # If so, skip download process
        print('Files Already Exist')
        return True
    else:
        # If files don't exist, start download process 
        # Send the request to the URL to download
        url = "https://media.archiveofourown.org/ao3/stats/2021/02/26/20210226-stats.zip"
        response = requests.get(url)
        with open("data/2021_stats.zip", "wb") as file:
            file.write(response.content)
            
        # Extract files from the zip file into data folder
        with zipfile.ZipFile("data/2021_stats.zip", "r") as zip_ref:
            zip_ref.extractall("data")
        print('Downloading Completed')
        return False

def csv_to_db() -> None:
    # Connect to SQLite database 
    with sqlite3.connect('data/fanfic.db') as conn:
        # Load works CSV data into Pandas DataFrame, using chunks 
        chunks = pd.read_csv('data/works-20210226.csv', chunksize = 50000)
        for chunk in chunks:
            chunk.to_sql("works", conn, if_exists='append', index=False)
        # Load tags CSV data into Pandas Dataframe, using chunks    
        chunks = pd.read_csv('data/tags-20210226.csv', chunksize = 50000)
        for chunk in chunks:
        # Convert DataFrame into SQL table
            chunk.to_sql("tags", conn, if_exists='append', index=False)
    return None

def preprocess() -> None:
    with sqlite3.connect('data/fanfic.db') as conn:
        # Create a cursor object 
        cur = conn.cursor() 
        # Tags table preprocessing
        cur.execute("DELETE FROM tags WHERE cached_count < 5")
        # Works table preprocessing
        cur.execute("""
                CREATE TABLE IF NOT EXISTS new_works(work_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                                    creation_date TEXT, 
                                                    language TEXT, 
                                                    restricted BOOL, 
                                                    complete BOOL, 
                                                    word_count INT, 
                                                    tags TEXT)
                                                    """)
        cur.execute("""
                INSERT INTO new_works (creation_date, language, restricted, complete, word_count, tags)
                SELECT [creation date], language, restricted, complete, word_count, tags FROM works
                """)
        cur.execute("DROP TABLE works")
        cur.execute("ALTER TABLE new_works RENAME TO works")
        conn.commit()
    return None

def split_tags() -> None:
    """Splits the 'tags' column in the 'works' table into individual rows."""
    with sqlite3.connect('data/fanfic.db') as conn:
        cur = conn.cursor()
        #Create new table of work ID and tag ID
        cur.execute("""
        CREATE TABLE IF NOT EXISTS work_tag_pairs (
        work_id INTEGER,
        tag_id INTEGER,
        FOREIGN KEY (work_id) REFERENCES works(work_id),
        FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
        );
        """)

        tag_ids = pd.read_sql_query("SELECT id FROM tags", conn)
        tag_set = set(tag_ids["id"].astype(str))

        # Process the works table in chunks
        chunks = pd.read_sql_query("SELECT work_id, tags FROM works", conn, chunksize=50000)

        for chunk in chunks:
            # Drop rows with missing tags
            chunk = chunk.dropna(subset=["tags"])

            # Split tags into lists, and filter valid tags using vectorized operations
            chunk['tag_list'] = chunk['tags'].str.split('+')  # Split the tags by '+'
            chunk['tag_list'] = chunk['tag_list'].apply(lambda x: [tag.strip() for tag in x if tag.strip() in tag_set])  # Filter valid tags

            # Flatten the list of tags into pairs of (work_id, tag_id)
            pairs = []
            for work_id, tags in zip(chunk['work_id'], chunk['tag_list']):
                for tag_id in tags:
                    pairs.append((work_id, tag_id))

            # Bulk insert pairs for the current chunk
            if pairs:
                cur.executemany("INSERT INTO work_tag_pairs (work_id, tag_id) VALUES (?, ?)", pairs)
        conn.commit()
    return None

def check_if_exists():
    # Check if the CSV files exist
    tags = Path("data/tags-20210226.csv")
    works = Path("data/works-20210226.csv")
    
    # Check if both CSV files exist
    if not (tags.is_file() and works.is_file()):
        return False
    
    # Connect to the SQLite database
    if not os.path.exists('data/fanfic.db'):
        return False
    
    with sqlite3.connect('data/fanfic.db') as conn:
        # Check if the tables exist in the database
        tables_exist = {'works': False, 'tags': False, 'work_tag_pairs': False}

        # Query to get the list of existing tables
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        existing_tables = pd.read_sql_query(query, conn)
        
        # Check each table
        for table in tables_exist:
            if table in existing_tables['name'].values:
                tables_exist[table] = True

        # Print out the status of each table
        if not all(tables_exist.values()):
            return False
    return True
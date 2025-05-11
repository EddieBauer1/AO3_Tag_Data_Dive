import os
import sqlite3 
import pandas as pd
import requests
import zipfile
from pathlib import Path

def import_data() -> None:
    """
    Check if "tags" and "works" CSV files already exist and have been downloaded.
    If not, automatically download and extract data from AO3-published zip file.
    
    Parameters:
        None
    
    Returns:
        None
    """
    #Make /data folder if it doesn't exist already
    Path("data").mkdir(parents=True, exist_ok=True)
    # Check if files exist first
    tags = Path("data/tags-20210226.csv")
    works = Path("data/works-20210226.csv")
    if tags.is_file() and works.is_file():
        # If so, skip download process
        print('Files Already Exist')
    else:
        # If files don't exist, start download process 
        url = "https://media.archiveofourown.org/ao3/stats/2021/02/26/20210226-stats.zip"
        # Send the request to the URL to download
        response = requests.get(url)
        # Download and save zip file
        with open("data/2021_stats.zip", "wb") as file:
            file.write(response.content)
        # Extract files from the zip file into data folder
        with zipfile.ZipFile("data/2021_stats.zip", "r") as zip_ref:
            zip_ref.extractall("data")
        print('Downloading Completed')
    return None

def csv_to_db() -> None:
    """
    Creates fanfic.db SQLite database, then converts both "works" and "tags" CSV files
    into Pandas DataFrames, then into SQL tables within the database.
    
    Parameters:
        None
    
    Returns:
        None
    """
    # Connect to SQLite database 
    with sqlite3.connect('data/fanfic.db') as conn:
        # Load "works" CSV data into Pandas DataFrame, using chunks 
        chunks = pd.read_csv('data/works-20210226.csv', chunksize = 50000)
        for chunk in chunks:
            # Fix creation_date column name before converting
            chunk.rename(columns={'creation date': 'creation_date'}, inplace=True)
            # Convert DataFrame into SQL table
            chunk.to_sql("works", conn, if_exists='append', index=False)
        # Load "tags" CSV data into Pandas Dataframe, using chunks    
        chunks = pd.read_csv('data/tags-20210226.csv', chunksize = 50000)
        for chunk in chunks:
            # Convert DataFrame into SQL table
            chunk.to_sql("tags", conn, if_exists='append', index=False)
    return None

def preprocess() -> None:
    """
    Does necessary preprocessing steps on newly-created works and tags tables.
    Delete all tags with fewer than five associated works, and adds work_id via autoincrement.
    
    Parameters:
        None
    
    Returns:
        None
    """
    with sqlite3.connect('data/fanfic.db') as conn:
        # Create a cursor object 
        cur = conn.cursor() 
        # Tags table preprocessing
        cur.execute("DELETE FROM tags WHERE cached_count < 5")
        # Works table preprocessing
        # Creates new table new_works, which contains autoincrement work_id
        cur.execute("""
                CREATE TABLE IF NOT EXISTS new_works(work_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                                    creation_date TEXT, 
                                                    language TEXT, 
                                                    restricted BOOL, 
                                                    complete BOOL, 
                                                    word_count INT, 
                                                    tags TEXT)
                                                    """)
        # Inserts data from works table into new_works
        cur.execute("""
                INSERT INTO new_works (creation_date, language, restricted, complete, word_count, tags)
                SELECT creation_date, language, restricted, complete, word_count, tags FROM works
                """)
        # Drops old works table
        cur.execute("DROP TABLE works")
        # new_works becomes the new works table, with work_id
        cur.execute("ALTER TABLE new_works RENAME TO works")
        conn.commit()
    return None

def split_tags() -> None:
    """
    Splits the 'tags' column in the 'works' table into individual rows 
    in new work_tag_pairs table.
    
    Parameters:
        None
    
    Returns:
        None
    """
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
        # Select all tag IDs from tags table
        tag_ids = pd.read_sql_query("SELECT id FROM tags", conn)
        # Convert ID column into strings
        tag_set = set(tag_ids["id"].astype(str))
        # Process the works table into Pandas DataFrame in chunks
        chunks = pd.read_sql_query("SELECT work_id, tags FROM works", conn, chunksize=50000)
        for chunk in chunks:
            # Drop rows with missing tags
            chunk = chunk.dropna(subset=["tags"])
             # Split the tags by '+' into lists
            chunk['tag_list'] = chunk['tags'].str.split('+') 
            # Only keep tags that exist in tag_set (valid tags with > 5 works)
            chunk['tag_list'] = chunk['tag_list'].apply(
                lambda x: [tag.strip() for tag in x if tag.strip() in tag_set]
                )
            pairs = []
            # For each work and its list of tags
            for work_id, tags in zip(chunk['work_id'], chunk['tag_list']):
                # For each tag in that list of tags
                for tag_id in tags:
                    # Append a tuple of that work and tag to pairs list
                    pairs.append((work_id, tag_id))
            if pairs:
                # Insert many (work_id, tag_id) pairs into work_tag_pairs table
                cur.executemany("INSERT INTO work_tag_pairs (work_id, tag_id) VALUES (?, ?)", pairs)
        conn.commit()
    return None

def check_if_exists():
    """
    Check if "tags" and "works" CSV files already exist.
    Check if SQLite fanfic.db database already exists.
    Check that works, tags, and work_tag_pairs tables exist in fanfic.db database
    
    Parameters:
        None
    
    Returns:
        boolean: False if any of the above checks fail, 
                 True if all necessary files, databases, and tables exist.
    """
    # Check if both CSV files exist, return False if not
    tags = Path("data/tags-20210226.csv")
    works = Path("data/works-20210226.csv")
    if not (tags.is_file() and works.is_file()):
        return False
    
    # Check if fanfic.db database exists, return False if not
    if not os.path.exists('data/fanfic.db'):
        return False
    
    with sqlite3.connect('data/fanfic.db') as conn:
        # Check if the tables exist in the database
        tables_exist = {'works': False, 'tags': False, 'work_tag_pairs': False}
        # Get the DataFrame of existing tables in fanfic.db
        query = "SELECT name FROM sqlite_master WHERE type='table';"
        existing_tables = pd.read_sql_query(query, conn)
        # Check if each of the three tables in tables_exist exist
        for table in tables_exist:
            if table in existing_tables['name'].values:
                tables_exist[table] = True
        # If any one of the tables is missing, return False
        if not all(tables_exist.values()):
            return False
    # Return True if all checks have passed
    return True

def data_prep_process() -> None:
    """
    Check if all necessary files exist - if not, run the data preparation process.
    
    Parameters:
        None
    
    Returns:
        None
    """
    # If the check fails:
    if not check_if_exists():
        # Import data
        print("Importing Data...")
        import_data()
        # Create fanfic.db database
        print("Creating SQL Database...")
        csv_to_db()
        # Preprocessing steps
        print("Preprocessing...")
        preprocess()
        # Create work_tag_pairs table in fanfic.db
        print("Creating work-tag pairs... (This may take some time, thank you for your patience)")
        split_tags()
    return None
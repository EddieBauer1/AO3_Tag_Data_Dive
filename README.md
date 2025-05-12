# AO3 Data Dive
AO3 Data Dive is a web dashboard for analyzing fanfiction data from Archive of Our Own (AO3). Users can input any AO3 tag - character, relationship, fandom, or trope - and view visual summaries of fanworks involving that tag, using data from AO3's official Selective Data Dump for Fan Statisticians (published February 26, 2021).

## Installation
Enter `git clone https://github.com/EddieBauer1/AO3_Tag_Data_Dive.git` into Powershell when in desired directory to clone the repository.

Once download is completed, enter `cd AO3_Tag_Data_Dive` to enter the project directory.

Install the necessary dependencies with `pip install . --prefer-binary`.

## Starting Up
To run the project, enter:

`python app.py`

If this is the first time running the project, the AO3 data download and preparation process will commence, with messages updating the user of the progress:

- `Importing Data...` indicates the program is downloading the data from the AO3 site, then extracting the data into the `/data` folder. After this step, the user should see:
  - `2021_stats.zip` 
  - `tags-20210226.csv`
  - `works-20210226.csv` 

- These CSVs contain the information for each tag and work on AO3 at the time of the published data dump - February 26th, 2021. `Downloading Completed` indicates that this process is finished.

- `Creating SQL Database...` shows that the `fanfic.db` database is being created in the `/data` folder from the CSV data. The database will contain two tables, `works` and `tags` - one for each downloaded CSV. This will allow for faster processing once completed.

- `Preprocessing...` means the program is deleting any tags with fewer than five associated works (these tags are unnamed in the original AO3 dataset, thus useless for the project), and adding an ID to each work in the "work" table by autoincrementing.

- `Creating work-tag pairs...` signifies that the `work_tag_pairs` table in `fanfic.db` is being filled, in which each tag in each work is created into its own row, allowing for quicker searches according to user input. 

Finally, the user will be given an address on which the dashboard is running. Copy and paste the `http://...` address into a web browser to access the dashboard.

## Usage Tips
To search up a tag used on AO3, enter the desired tag into the search and click the `Analyze` button. The program does have occasional issues with case sensitivity, so make sure to capitalize the first letter of every word, as shown in the example tags below. Searchable tags include:
- Characters (Harry Potter, Rey (Star Wars), etc.)
- Fandoms (Harry Potter - J. K. Rowling, Star Wars - All Media Types, etc.) 
- Relationships (Harry Potter/Ginny Weasley, Padmé Amidala/Anakin Skywalker) 
- Common tropes (Enemies to Lovers, Slow Burn, etc.)
- And more. 

### Searching Partial Tags
If unsure of the exact tag, try entering a part of the tag, and the dashboard will respond with popular tags that contain the entered part.

- For example, Star Wars is a popular fandom, but Star Wars fanworks are separated into a bunch of different tags (Star Wars Sequel Trilogy, Star Wars Original Trilogy, Star Wars Prequel Trilogy, etc.). To find the exact tag, try looking up the incomplete "star wa" which will return:

  - 'star wa' tag not found. Could you mean one of these options instead? ['Star Wars - All Media Types', 'Star Wars Sequel Trilogy', 'Rey (Star Wars)', 'Star Wars Episode VII: The Force Awakens (2015)', 'Star Wars', 'Finn (Star Wars)', 'Star Wars: The Clone Wars (2008) - All Media Types', 'Star Wars Prequel Trilogy', 'Star Wars Original Trilogy', 'Rogue One: A Star Wars Story (2016)']

The user is then given the most popular tags potentially matching what they're looking for, and now knows exactly what to look up.

### Relationship Tags
Relationship tags are formatted as Character1/Character2 on AO3. However, these tags are specific; "Character1/Character2" =/= "Character2/Character1"! To get around this, try using the partial tag method demonstrated above and look up part of a character's name (like "Harry Pott"), which may return popular relationships involving that character, or look up both possible combinations of names.

If all else fails, the user should try looking up the official tag on AO3.

## Results
The user is given three graphs indicating different statistics about the works including the searched tag: 
- A bar graph showing works created by year. 
- A bar graph showing works organized by word count.
- A pie chart showing the percentage of works using that tag that are completed. 

Each graphic also has relevant statistics that may help the user understand the dataset better, such as "Total Works", "Average Word Count per Work", and "Number of Complete Works". Overall, these graphics give the user a simplified view of the often massive amounts of fanworks.

## Project Structure
The project consists of three files: data_prep.py, processing.py, and app.py.
- `data_prep.py` is in the `/src` folder, and contains the functions necessary to download and prepare the AO3 data:
  - `import_data()` automatically downloads and extracts the CSV files from AO3 if they are not already in the `/data` folder.
  - `csv_to_db()` creates the `fanfic.db` database and converts the CSV files into SQL tables.
  - `preprocess()` does necessary preprocessing steps on the `works` and `tags` SQL tables.
  - `split_tags()` creates the `work_tag_pairs` SQL table, splitting the tags column in the `works` table into individual rows.
  - `check_if_exists()` checks that all data necessary for the project exists.
  - `data_prep_process()` runs the data preparation process in order and gives feedback.
- `processing.py` also is in the `/src` folder, and contains the functions used to sort, organize, and filter data from the user input.
  - `find_tag(tagname: str)` returns the tag ID of the given tag name.
  - `find_works(tagname: str)` returns a DataFrame of all work IDs paired with the given tag name in the `work_tag_pairs` SQL table.
  - `get_work_data(tagname: str)` returns a DataFrame of the work data of the work IDs found by `find_works()`.
  - `create_master_table(tagname: str)` converts the DataFrame of works containing given tag into SQL table `selected_works` and returns a cleaned version of the DataFrame.
  - `sort_years()` returns a DataFrame of the works in `selected_works` SQL table sorted by year.
  - `sort_word_counts()` returns a DataFrame of the works in `selected_works` SQL table sorted by preset word count ranges.
  - `sort_completion()` returns a DataFrame of the works in `selected_works` SQL table sorted by completion.
  - `autocorrect(tagname: str)` returns a list of the ten most used tags in the `tags` SQL table that contain `tagname` within their name.
- `app.py` creates and runs the interactive Dash dashboard that users see in the browser.
  - `update_dashboard(n_clicks, tagname)` returns a tuple containing the updated graphs and statistics to be displayed on the dashboard based on the searched tag.




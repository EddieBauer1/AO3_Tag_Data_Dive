# AO3 Data Dive
This project consists of a dashboard that allows the user to input any tag of their choosing on AO3, then returns graphics summarizing statistics of works containing that tag. All data is collected from the AO3-published "Selective data dump for fan statisticians" which was released data of fanworks on the AO3 site.

## Installation
Enter "git clone https://github.com/EddieBauer1/AO3_Tag_Data_Dive.git" into Powershell when in desired directory to download the repository.

Once download is completed, enter "cd AO3_Tag_Data_Dive" to enter the project directory.

## Starting Up
To run the project, enter "python app.py" to run the project. If this is the first time running the project, the AO3 data download process will commence, with messages updating the user of the progress:

"Importing Data..." indicates the program is downloading the data from the AO3 site, then extracting the data into the "data" folder. After this step, the user should see 2021_stats.zip, tags-20210226.csv, and works-20210226.csv. These CSVs contain the information for each tag and work on AO3 at the time of the published data dump - February 26th, 2021. "Downloading Completed" indicates that this process is finished.

"Creating SQL Database..." shows that the fanfic.db database is being created in the "data" folder from the CSV data. The database will contain two tables, "works" and "tags" - one for each downloaded CSV. This will allow for faster processing once completed.

"Preprocessing..." means the program is deleting any tags with fewer than five associated works (these tags are unnamed in the original AO3 dataset, thus useless for the project), and adding an ID to each work in the "work" table by autoincrementing.

"Creating work-tag pairs..." signifies that the work_tag_pairs table in fanfic.db is being filled, in which each tag in each work is created into its own row, allowing for quicker searches according to user input. 

Finally, the user will be given an address on which the dashboard is running. Copy and paste the "http://..." address into a web browser to access the dashboard.

## Usage Tips
To search up a tag used on AO3, enter the desired tag into the search and click the "Analyze" button. Searchable tags include characters, fandoms, relationships, common tropes (Enemies to Lovers, Slow Burn, etc.), and more. If unsure of the exact tag, try entering a part of the tag, and the dashboard will respond with popular tags that contain the entered part.

For example, Star Wars is a popular fandom, but Star Wars fanworks are separated into a bunch of different tags (Star Wars Sequel Trilogy, Star Wars Original Trilogy, Star Wars Prequel Trilogy, etc.). To find the exact tag, try looking up the incomplete "star wa" which will return:

'star wa' tag not found. Could you mean one of these options instead? ['Star Wars - All Media Types', 'Star Wars Sequel Trilogy', 'Rey (Star Wars)', 'Star Wars Episode VII: The Force Awakens (2015)', 'Star Wars', 'Finn (Star Wars)', 'Star Wars: The Clone Wars (2008) - All Media Types', 'Star Wars Prequel Trilogy', 'Star Wars Original Trilogy', 'Rogue One: A Star Wars Story (2016)']

The user is then given the most popular tags potentially matching what they're looking for, and now knows exactly what to look up.

This also works well for relationship tags, which are formatted as Character1/Character2 on AO3. However, these tags are specific; "Character1/Character2" =/= "Character2/Character1"! To get around this, try using the partial tag method demonstrated above and look up part of a character's name (like "Harry Pott"), which may return popular relationships involving that character, or look up both possible combinations of names.

If all else fails, the user should try looking up the official tag on AO3 to find the exact tag, then try that on this app.







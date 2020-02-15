# TrelloPy

# Why
This is a python script to read your Trello Board and write it to Google Sheets or an Excel File.
It is designed to work with Trello boards used for Scrum or Agile. 
This script assumes that the selected board has at least one list for:
 - To do (or Backlog)
 - Doing
 - Done

# How to use

## Setup
First run setup.py (or the jupyter notebook). This will create a configuration.txt file and a credentials.txt file. These files can be changed by hand without the script, or use the same script to change the values.

## Run the script
Run trellopy.py. It loads the configuration file and will look which values are set to True. 

## Options:

Below are the options which can be set to true or false in configuration.txt.


### excelalldata (WIP)
If turned to true, this script will export all trello data to the file set in configuration.txt.

### exceltimeline (WIP)
If turned to true, this script will export a timeline of the last 400 days to the file set in configuration.txt.

### gspreadalldata
If turned to true, this script will export all trello data to the Google Sheet File set in configuration.txt.

### gspreadtimeline
If turned to true, this script will export a timeline of the last 400 days to the Google Sheet File set in configuration.txt.

### cleandonelists
If turned to true, this script will archive all cards in all Done lists if the card is marked as Done for longer than X days (days is set in configuration.txt  
WARNING: this script POSTS to Trello using the API!

### removemembersfromdonecards
If turned to true, this script will delete all members of cards that are done.
WARNING: this script DELETES to Trello using the API!


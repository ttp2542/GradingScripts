import csv
import os

from pathlib import Path
"""
This script is meant to rename all the cloned repositories to be the
students real names (instead of their github usernames). It uses a classlist
gotten from the Github Classroom site

@author Trey Pachucki ttp2542@g.rit.edu
"""
DEFAULT_PATH = 'classroom_roster.csv'

def main():

    # the name of the assignment to get
    assignment_name = input("Please input the assignment name: ")

    # the name of the csv file with the classlist
    classlist = input("Please input the name of the csv file with the classlist: ")
    
    # If nothing is entered, assume the roster is the default path
    if classlist == '':     
        classlist = DEFAULT_PATH

    # gets the cwd for the initial path
    initial_path = Path.cwd()

    # updates the initial path to be the assignment folder
    assignment_path = initial_path / assignment_name

    # creates lists to store the usernames and real names from clasroom_roster.csv
    real_name_list = []
    username_list = []

    # adds the usernames and real names to the lists from the rosters
    with open(classlist) as file:
        filereader = csv.reader(file, delimiter=",", quotechar="\"")
        for line in filereader:
            real_name = line[0].strip("\'")
            real_name_list.append(real_name)

            username = line[1].strip("\"")
            username_list.append(username)

    # updates the name of the repos
    for i in range(len(real_name_list)):
        # gets username and creates the current name of the folder/path
        username = username_list[i]
        foldername = assignment_name + "-" + username
        current_path = assignment_path / foldername

        # the new path name
        new_path = assignment_path / real_name_list[i]

        # sees if the exists and renames if it does.
        if os.path.isdir(current_path):
            current_path.rename(new_path)
        
if __name__ == "__main__":
    main()
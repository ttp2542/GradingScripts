import os
import re

from github import Github
from pathlib import Path
"""
This script changes the commit head of a previously cloned repository.

@author Trey Pachucki ttp2542@g.rit.edu
"""

GITHUB_LINK = 'https://github.com/'
TEMP_FILE_NAME = 'temp.txt'
FIRST_HALF_GIT_REV_LIST = 'git rev-list -n 1 --before="'
SECOND_HALF_GIT_REV_LIST = '" origin/main'


def main():
    # if this script has been run before use the past information
    try:
        file = open(TEMP_FILE_NAME, 'r')
        token = file.readline()
        organization = file.readline()

    # otherwise get the information from the user
    except FileNotFoundError:
        file = open(TEMP_FILE_NAME, 'w')
        token = input("Please input your Github Authentication Token: ")
        organization = input("Please input the organization name: ")

        # write to the file for future ease of use
        file.write(token)
        file.write('\n')
        file.write(organization)

    file.close()

    # logs into github using the token
    gh = Github(token.strip())

    # the name of the assignment to get
    assignment_name = input("Please input the assignment (folder) name: ")

    # the day it's due (before midnight is assumed)
    date_due = input("Please input the date it's due (format = yyyy-mm-dd): ")

    # The time the assignment is due
    time_due = input("Please input the time the "
                     "assignment's due (24 hour time ie 23:59 = 11:59 pm): ")

    # makes the path of the directory that should exist
    initial_path = Path.cwd() / assignment_name

    # ensures that the repos been cloned
    if not os.path.isdir(str(initial_path)):
        print('Please make sure the repositories are cloned or'
              ' that you didn\'t mistype the assignment name')
    else:

        # we are now in the overarching folder for the assignment
        os.chdir(initial_path)
        
        # formatting of the git string
        gitString = FIRST_HALF_GIT_REV_LIST + date_due.strip() + ' ' + time_due + SECOND_HALF_GIT_REV_LIST

        # Iterate over the directories in the folder
        for directory in os.listdir(initial_path):
            next_directory = initial_path / directory
            if os.path.isdir(next_directory):
                
                # go to the cloned repository
                os.chdir(next_directory)

                # get the commit
                process = os.popen(gitString)
                commit = process.read()

                # checkout the commit
                os.system('git checkout ' + commit)
                process.close()


if __name__ == "__main__":  
    main()

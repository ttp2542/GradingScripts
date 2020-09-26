import git
import os
from pygithub3 import Github
from pathlib import Path

"""
This script is meant to get all the repositories before a specific date
for an assignment. It requires an authentication token to be put in, a date,
and the assignment name.

@author Trey Pachucki ttp2542@g.rit.edu
"""
FILENAME = 'temp.txt'
GITHUB_LINK = 'https://github.com/'
FIRST_HALF_GIT_REV_LIST = 'git rev-list -n 1 --before="'
SECOND_HALF_GIT_REV_LIST = '" origin/master'



def main():
    # if this script has been run before use the past information
    try:
        file = open(FILENAME, 'r')
        token = file.readline()
        organization = file.readline()

    # otherwise get the information from the user
    except FileNotFoundError:
        file = open(FILENAME, 'w')
        token = input("Please input your Github Authentication Token: ")
        organization = input("Please input the organization name: ")

        # write to the file for future ease of use
        file.write(token)
        file.write('\n')
        file.write(organization)

    file.close()

    # logs into github using the token
    gh = Github(token.strip())

    #creates the Github link with the organization
    github_link = GITHUB_LINK + organization.strip() + '/'

    # the name of the assignment to get
    assignment_name = input("Please input the assignment name: ")

    # the day it's due (before midnight is assumed)
    date_due = input("Please input the date it's due (format = yyyy-mm-dd): ")

    # The time the assignment is due
    time_due = input("Please input the time the "
                     "assignment's due (24 hour time ie 23:59 = 11:59 pm): ")
    # gets the name of all the student repos ie 'assignment-username'
    student_file_address = input("OPTIONAL : Enter file address of text file containing the usernames of students you are grading (one username per line). To ignore, just hit 'enter' : ")
    if student_file_address == "":
        # Generate repo list like it did prior
        repo_list = get_repos(assignment_name, gh)
    else:
        # Generate repo list with the use of helper file
        repo_list = get_repos_specified_usernames(assignment_name, gh, student_file_address)

    # creates the path for the assignment a string of the path
    initial_path = Path.cwd() / assignment_name

    # makes a folder for the assignment as a whole
    initial_path.mkdir()

    # creates a folder, clones the repository, then checks out to before a date
    # the folder created is within the first folder made above, so all assignments
    # are in one convenient folder
    for repo in repo_list:
        path = initial_path / repo.name
        path.mkdir()
        os.system('git clone ' + github_link + repo.name + ' ' + "\"" + str(path) + "\"")
        os.chdir(str(path))
        gitString = FIRST_HALF_GIT_REV_LIST + date_due.strip() + ' ' + time_due + SECOND_HALF_GIT_REV_LIST
        process = os.popen(gitString)
        commit = process.read()
        os.system('git checkout ' + commit)
        process.close()

    
"""
This function gets the repos for the specific assignment
"""
def get_repos(assignment_name, github):
    repo_list = []
    for repo in github.get_user().get_repos():
        if assignment_name in repo.name:
            repo_list.append(repo)

    return repo_list

"""
Modified to only pull student's repos in the specified text file students.txt 
This function gets the repos for the specific assignment for the students whose usernames are in the text file.

NOTE : student file address leads to the text file containing the usernames of your students. One username per line.
"""
def get_repos_specified_usernames(assignment_name, github, student_file_address):
    students_file = open(student_file_address, "r")
    students = students_file.read().splitlines()
    students_file.close()
    repo_list = []
    for repo in github.get_user().get_repos():
        if assignment_name in repo.name:
            for student in students:
                if student in repo.name:
                    repo_list.append(repo)
    return repo_list

"""
This function makes a folder at a specific path
"""
def make_folder(path):
    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s " % path)


if __name__ == "__main__":
    main()

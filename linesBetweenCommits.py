import git
import os
from pygithub3 import Github
import re
from pathlib import Path

"""
This script checks the average number of lines between each commit for
a specific assignment.

@author Trey Pachucki ttp2542@g.rit.edu
"""
FILENAME = 'temp.txt'
GITHUB_LINK = 'https://github.com/'
GIT_COMMAND = 'git log --oneline --shortstat'
TEMP_FILE_NAME = 'temp.txt'
AVERAGE_LINE_FILE_NAME = 'avgLinesInserted.txt'


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
    assignment_name = input("Please input the assignment name: ")

    # makes the path of the directory that should exist
    initial_path = Path.cwd() / assignment_name

    # ensures that the repos been cloned
    if not os.path.isdir(str(initial_path)):
        print('Please make sure the repositories are cloned or'
              ' that you didn\'t mistype the assignment name')
    else:

        # gets the name of all the student repos ie 'assignment-username'
        repo_list = get_repos(assignment_name, gh)

        # we are now in the overarching folder for the assignment
        os.chdir(initial_path)

        # make a file to store all this shite in
        file = open(AVERAGE_LINE_FILE_NAME, 'w')
        file.write(assignment_name)
        file.write('\n\n')

        # writes the results into a file for convenience sake
        for repo in repo_list:
            # go to the cloned repository
            path = initial_path / repo.name
            os.chdir(path)

            # use git to get the stats (haha git get)
            process = os.popen(GIT_COMMAND)
            process_processing(process, file, repo)
            process.close()

        # closes file when everything is done
        file.close()


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
This function makes a folder at a specific path
"""
def make_folder(path):
    try:
        os.mkdir(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s " % path)


"""
This function does most of the work after the process has been done.
By taking this out, it's easier to see how to redo this in the future.
"""
def process_processing(process, file, repo):
    # get the results from the process
    result = process.read()
    result = result.split('\n')
    list_size = len(result)

    # variables to track relevant information
    average_insert = 0
    total_times_inserted = 0

    # the relevant strings are the first, third, etc...
    # format is something like
    # '20 files committed, insertions(+) 56, deletions(-) 24'
    # for result[i]
    for i in range(1, list_size):   
        if 'file' in result[i] and 'change' in result[i]:
            total_times_inserted += 1

            # cleans up the string and splits it (again) to get insertions
            result[i] = result[i].strip()
            result[i] = result[i].split(', ')

            # checks where insertions should be if files committed
            if len(result[i]) > 1 and 'insertion' in result[i][1]:
                    number_list = re.findall(r'\d+', result[i][1])
                    average_insert += int(number_list[0])

            # checks where insertions should be if no files committed
            elif 'insertion' in result[i][0]:
                number_list = re.findall(r'\d+', result[i][1])
                average_insert += int(number_list[0])

    # this basically checks that there's been any commits
    # thanks Bobby for never committing, let me know about this bug
    if total_times_inserted != 0:
        average_insert = average_insert / total_times_inserted

    # formats the string
    repo_name_split = repo.name.split('-')
    user_name = repo_name_split[len(repo_name_split) - 1]
    insertion_string = user_name + ' Average Insertions: ' + str(average_insert)

    # writes the final result to the file, prints it out, and closes process
    file.write(insertion_string + '\n')
    print(insertion_string)


main()

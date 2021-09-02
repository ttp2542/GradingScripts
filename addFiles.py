import os

from github import Github
from pathlib import Path
"""
This script is meant to be used to copy files from a directory into all the
student's githubs. In order to be used you must specify the directory which
has the files (that's in the same location as the script is being used, using
full paths will result in some less than stellar results), and the path to 
follow in the github repo. Basically, give the program what it asks for.

@author Trey Pachucki ttp2542@g.rit.edu
"""
FILENAME = 'temp.txt'
GITHUB_LINK = 'https://github.com/'

def main():
    # if this script has been run before use the past information
    try:
        file = open('temp.txt', 'r')
        token = file.readline()
        organization = file.readline()

    # otherwise get the information from the user
    except FileNotFoundError:
        file = open('temp.txt', 'w')
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

    # the name of the folder from which files are copied
    start_folder = input("Please input the name of the folder with files: ")

    # the destination folder for the files
    ending_path = input("Please input the path to the folder in github: ")

    # the commit message
    commit_msg = input("Please specify the commit message: ")

    # gets the name of all the student repos ie 'assignment-username'
    repo_list = get_repos(assignment_name, gh)

    # creates the path for the assignment a string of the path
    initial_path = Path.cwd() / assignment_name

    # makes a folder for the assignment as a whole
    initial_path.mkdir()

    # change into the folder to get all the files
    init_folder_path = Path.cwd() / start_folder

    print(repo_list)
    # creates a folder, clones the repository, then checks out to before a date
    # the folder created is within the first folder made above, so all assignments
    # are in one convenient folder
    for repo in repo_list:
        path = initial_path / repo.name
        path.mkdir()

        os.system('git clone ' + github_link + repo.name + ' ' + str(path))
        end_path = ""
        if ending_path != "":
            end_path = path / end_path
            # makes the path in the repository
            end_path.mkdir()
        else:
            end_path = path
           
        

        # processes folder
        process(init_folder_path, end_path)

        # commits and pushes the stuff
        os.chdir(end_path)
        os.system('git commit -m "' + commit_msg + '"')
        os.system('git push')


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
This processes the folders (ie copies the files and adds them via git
"""
def process(item_path, target_directory):
    # if it's a directory go through the items in it and process them
    if os.path.isdir(item_path):
        os.chdir(item_path)
        ls = os.listdir(item_path)
        name_of_directory = str(item_path).split("\\")
        name_of_directory = name_of_directory[len(name_of_directory) - 1]
        new_dir = target_directory / name_of_directory
        new_dir.mkdir()
        for item in ls:
            temp_path = item_path / item
            process(temp_path, new_dir)

    # if not, copy it into the file structure and add it to git
    else:
        # these print statements are technically lava flow, but useful for
        # debugging purposes

        # print("Item_path: " + item_path)
        # print("Target Directory: " + target_directory)

        # copies file and adds them to Git
        os.system("copy " + str(item_path) + " " + str(target_directory))
        item_name = str(item_path).split("\\")
        item_name = item_name[len(item_name) - 1]
        os.chdir(target_directory)
        os.system('git add ' + item_name)


main()

from io import StringIO
from pathlib import Path
import csv
import logging
import os
import shutil
import subprocess
import _thread

from datetime import date, datetime
from github import Github
from github.Organization import Organization
from threading import Thread
from github.Repository import Repository
"""
Script to clone all or some repositories in a Github Organization based on repo prefix and usernames
@author Kamron Cole kjc8084@rit.edu
"""
CONFIG_PATH = 'tmp/config.txt' # Stores token and org name
BASE_GITHUB_LINK = 'https://github.com'


'''
The Thread that clones the repo
'''
class CloneRepoThread(Thread):
    __slots___ = ['__repo', '__assignment_name', '__date_due', '__time_due', '__students', '__student_filename', '__initial_path', '__default_branch']


    def __init__(self, repo, assignment_name, date_due, time_due, students, student_filename, initial_path, default_branch):
        self.__repo = repo
        self.__assignment_name = assignment_name
        self.__date_due = date_due
        self.__time_due = time_due
        self.__students = students
        self.__student_filename = student_filename
        self.__initial_path = initial_path
        self.__default_branch = default_branch
        super().__init__()


    '''
    Clones given repo and renames destination to student real name if class roster is provided.
    '''
    def run(self):
        try:
            clone_repo(self.__repo, self.__assignment_name, self.__date_due, self.__time_due, self.__students, self.__student_filename, self.__initial_path, self.__default_branch)
        except: # Catch exception raised by clone_repo and interrupt main thread
            print(f'ERROR: Sorry, ran into a problem while cloning `{self.__repo.name}`. Check tmp/logs.log.')
            logging.exception('ERROR:')
            _thread.interrupt_main()            


'''
return list of all repos in an organization matching assignment name prefix
'''
def get_repos(assignment_name: str, github_org_client: Organization) -> list:
    return [repo for repo in github_org_client.get_repos() if assignment_name in repo.name]


'''
return list of all repos in an organization matching assignment name prefix and is a student specified in the specified class roster csv
'''
def get_repos_specified_students(assignment_name: str, github_org_client: Organization, students: list) -> list:
    return [repo for repo in github_org_client.get_repos() if assignment_name in repo.name and is_student(repo, students) == True]


'''
Reads class roster csv in the format given by github classroom:
"identifier","github_username","github_id","name"

and returns a dictionary of students mapping github username to real name
'''
def get_students(student_filename: str) -> dict:
    students = {}
    if opener(student_filename):
        with open(student_filename) as f_handle:
            csv_reader = csv.reader(f_handle)
            next(csv_reader)
            for student in csv_reader:
                name = student[0].replace(', ', '-')
                github = student[1]
                if name and github:
                    students[github] = name
    return students


'''
Returns repo name replacing github username sufix with student's real name
'''
def get_new_repo_name(repo: Repository, students: dict, assignment_name: str) -> str:
    for student in students:
        if student in repo.name:
            return f'{assignment_name}-{students[student]}'
    return False


'''
Check if repo belongs to one of the students in specified class roster
'''
def is_student(repo: Repository, students: dict) -> bool:
    for student in students:
        if student in repo.name:
            return True
    return False


'''
File opener for error handling. If file exists return true, else false
'''
def opener(file_name: str) -> bool:
    try:
        with open(file_name) as f_handle:
            return True
    except FileNotFoundError:
        return False


'''
Attempts to remove file if it already exists attempt to remove it, if not exit with an error. If it doesn't exist, create it.
'''
def file_exists_handler(path):
    if Path.exists(path):
        try:
            shutil.rmtree(path)
            Path.mkdir(path)
        except:
            raise FileExistsError()
    else:
        Path.mkdir(path)


'''
Save parameters into config file to be read on future runs
'''
def save_config(token: str, organization: Organization, use_classlist: bool, student_filename: str, default_branch: str):
    with open(CONFIG_PATH, 'w') as config:
        config.write(token)
        config.write('\n')
        config.write(organization)
        config.write('\n')
        config.write(str(use_classlist))
        config.write('\n')
        config.write(student_filename)
        config.write('\n')
        config.write(default_branch)


'''
Reads config containing token, organization, whether to use class list, and path of class list.
Return values as tuple
'''
def read_config_raw() -> tuple:
    token = ''
    organization = ''
    use_classlist = ''
    student_filename = ''
    default_branch = ''
    if opener(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as config:
            token = config.readline().strip()
            organization = config.readline().strip()
            use_classlist = config.readline().strip()
            if use_classlist == 'True':
                use_classlist = True
                student_filename = config.readline().strip()
            elif use_classlist == 'False':
                use_classlist = False
            default_branch = config.readline().strip()
    return (token, organization, use_classlist, student_filename, default_branch)


'''
Checks whether config already exists, if so and use_classlist is False, ask for class roster path
'''
def read_config() -> tuple:
    if opener(CONFIG_PATH): # If config already exists
        token, organization, use_classlist, student_filename, default_branch = read_config_raw() # get variables
        if use_classlist == False:
            print('OPTIONAL: Enter filename of csv file containing username and name of students. To ignore, just hit `enter`')
            student_filename = input('If ignored, repo names will not be changed to match student names: ')
            if student_filename: # if class roster was entered, set in config, check if use_classlist should be updated as well
                use_classlist = input('Use this like every time? (can be changed later in tmp/config.txt) (Y/N): ')
                # Convert raw input boolean
                if 'y' in use_classlist.lower():
                    use_classlist = 'True'
                elif 'n' in use_classlist.lower():
                    use_classlist = 'False'
            else:
                use_classlist = 'False'
            save_config(token, organization, use_classlist, student_filename, default_branch)
    else:
        make_default_config()
        token, organization, use_classlist, student_filename, default_branch = read_config_raw() # Update return variables
    return (token, organization, student_filename, default_branch)


'''
Creates a default config file getting access token, org, class roster, etc
'''
def make_default_config():
    use_classlist = ''
    student_filename = ''
    default_branch = ''
    token = input('Github Authentication Token: ')
    organization = input('Organization Name: ')
    print('OPTIONAL: Enter filename of csv file containing username and name of students. To ignore, just hit `enter`')
    student_filename = input('If ignored, repo names will not be changed to match student names: ')
    if student_filename:
        use_classlist = input('Use this like every time? (can be changed later in tmp/config.txt) (Y/N): ')
        # Convert raw input to boolean
        if 'y' in use_classlist.lower():
            use_classlist = 'True'
        elif 'n' in use_classlist.lower():
            use_classlist = 'False'
    else:
        use_classlist = 'False'
    default_branch = input('Default Branch Name (can be changed later in tmp/config.txt): ')
    save_config(token, organization, use_classlist, student_filename, default_branch)


'''
Clones a repo into the assignment folder.
If a classroom roster is used, replace github names with real names
'''
def clone_repo(repo, assignment_name, date_due, time_due, students, use_students, initial_path, default_branch):
    if use_students: # If student file was input
        path = initial_path / get_new_repo_name(repo, students, assignment_name) # replace repo name when cloning to have student's real name
    else:
        path = initial_path / repo.name
    # Clone repo
    print(f'Cloning {repo.name} into {path}...')
    subprocess.run(f'git clone {repo.clone_url} "{str(path)}"', stderr=subprocess.PIPE) # git clone to output file, Hides output from console
    # Get commit hash at timestamp and reset local repo to timestamp (git rev-list output piped to git checkout)
    rev_list_process = subprocess.Popen(f'git rev-list -n 1 --before="{date_due.strip()} {time_due.strip()}" origin/{default_branch} | git checkout', cwd=path, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with rev_list_process: # Output command responds to log file
        for line in iter(rev_list_process.stdout.readline, b''): # b'\n'-separated lines
            line = str(line)
            if 'fatal' in line.lower() or 'error' in line.lower(): # if git command threw error (usually wrong branch name)
                logging.info('Subprocess: %r', line) # Log error
                raise Exception("ERROR: An error has occured, check tmp/logs.log") # Raise exception to the thread
    exit_code = rev_list_process.wait()

    # if process didn't exit successfully
    if exit_code != 0:
        raise Exception(f'Exit Code: {exit_code}')


'''
Main function
'''
def main():
    # Create log file
    logging.basicConfig(level=logging.INFO, filename='tmp/logs.log')

    # Try catch catches errors and sends them to the log file instead of outputting to console
    try:
        # Read config file, if doesn't exist make one using user input.
        token, organization, student_filename, default_branch = read_config()

        # Create Organization to access repos
        git_org_client = Github(token.strip()).get_organization(organization.strip())

        # Variables used to get proper repos
        assignment_name = input('Assignment Name: ')
        date_due = input('Date Due (format = yyyy-mm-dd, press `enter` for current): ')
        if not date_due:
            current_date = date.today()
            date_due = current_date.strftime("%Y-%m-%d")
            print(f'Using current date: {date_due}')
        time_due = input('Time Due (24hr, press `enter` for current): ')
        if not time_due:
            current_time = datetime.now()
            time_due = current_time.strftime("%H:%M")
            print(f'Using current date: {time_due}')
        print()

        # If student roster is specified, get repos list using proper function
        if student_filename:
            students = get_students(student_filename)
            repos = get_repos_specified_students(assignment_name, git_org_client, students)
        else:
            repos = get_repos(assignment_name, git_org_client)

        # Sets path to same as the script
        initial_path = Path.cwd() / assignment_name

        # Makes parent folder for whole assignment
        file_exists_handler(initial_path)

        threads = []
        # goes through list of repos and clones them into the assignment's parent folder
        for repo in repos:
            # Create thread that clones repo and add to thread list
            thread = CloneRepoThread(repo, assignment_name, date_due, time_due, students, bool(student_filename), initial_path, default_branch)
            thread.setDaemon(True)
            # thread = threading.Thread(target=clone_repo, args=(repo, assignment_name, date_due, time_due, students, bool(student_filename), initial_path, default_branch), daemon=True)
            threads += [thread]

        # Run all clone threads
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        print()
        print(f'Done.')
        print(f'Cloned {len(repos)} repo(s) for assignment `{assignment_name}`')
    except FileExistsError: # Error thrown if parent assignment file already exists
        print()
        print(f'ERROR: File `{path}` already exists, please delete it and run again')
        return
    except KeyboardInterrupt: # When thread fails because subprocess command threw some error/exception
        print()
        print('ERROR: Something happened during the cloning process; your repos are not at the proper timestamp. Delete the assignment folder and run again.')
    except:
        print(f'Cloned {len(next(os.walk(initial_path))[1])}/{len(repos)} repos')
    exit()


if __name__ == '__main__':
    main()

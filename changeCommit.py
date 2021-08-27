import os
import logging
import cloneRepositories

from datetime import date, datetime
from threading import Thread
from pathlib import Path
"""
This script changes the commit head of a previously cloned repository.

@author Trey Pachucki ttp2542@g.rit.edu, Kamron Cole kjc8084@rit.edu
"""
CONFIG_PATH = cloneRepositories.CONFIG_PATH
LOG_FILE_PATH = cloneRepositories.LOG_FILE_PATH
MIN_GIT_VERSION = cloneRepositories.MIN_GIT_VERSION

class Checkout(Thread):
    __slots__ = ['__repo', '__date_due', '__time_due', '__repo_path']

    def __init__(self):
        super().__init__()


def main():
    # Enable color in cmd
    os.system('color')
    # Create log file
    logging.basicConfig(level=logging.INFO, filename=LOG_FILE_PATH)

        # Try catch catches errors and sends them to the log file instead of outputting to console
    try:
        # Check local git version is compatible with script
        check_git_version()
        # Check local PyGithub module version is compatible with script
        check_pygithub_version()
        # Read config file, if doesn't exist make one using user input.
        token, organization, student_filename, output_dir = read_config()

        # Create Organization to access repos
        git_org_client = Github(token.strip(), pool_size = MAX_THREADS).get_organization(organization.strip())

        # Variables used to get proper repos
        assignment_name = input('Assignment Name: ')
        while not assignment_name:
            assignment_name = input('Please input an assignment name: ')
        date_due = input('Date Due (format = yyyy-mm-dd, press `enter` for current): ')
        if not date_due:
            current_date = date.today()
            date_due = current_date.strftime('%Y-%m-%d')
            print(f'Using current date: {date_due}')
        time_due = input('Time Due (24hr, press `enter` for current): ')
        if not time_due:
            current_time = datetime.now()
            time_due = current_time.strftime('%H:%M')
            print(f'Using current date: {time_due}')
        print()

        # Sets path to same as the script
        initial_path = output_dir / assignment_name

        # Makes sure assignments are cloned
        
        num_of_repos = len(next(os.walk(initial_path))[1])
        
        threads = []
        # goes through list of repos and clones them into the assignment's parent folder
        for repo in len():
            # Create thread that clones repo and add to thread list
            thread = RepoHandler(repo, assignment_name, date_due, time_due, students, bool(student_filename), initial_path)
            threads += [thread]

        # Run all clone threads
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        num_of_lines = write_avg_insersions_file(initial_path, assignment_name)
        print()
        print(f'{LIGHT_GREEN}Done.{WHITE}')
        print(f'{LIGHT_GREEN}Cloned {len(next(os.walk(initial_path))[1])}/{len(repos)} repos.{WHITE}')
        print(f'{LIGHT_GREEN}Found average lines per commit for {num_of_lines}/{len(repos)} repos.{WHITE}')
    except FileNotFoundError as e:
        print()
        print(f'Classroom roster `{student_filename}` not found.')
        logging.error(e)
    except FileExistsError as e: # Error thrown if parent assignment file already exists
        print()
        print(f'ERROR: File `{initial_path}` already exists, please delete it and run again')
        logging.error(e)
    except KeyboardInterrupt as e: # When thread fails because subprocess command threw some error/exception
        print()
        print('ERROR: Something happened during the cloning process; your repos are not at the proper timestamp. Delete the assignment folder and run again.')
        logging.error(e)
    except ValueError as e: # When git version is incompatible w/ script
        print()
        print(e)
        logging.error(e)
    except Exception as e:
        print(f'ERROR: Something happened. Check {LOG_FILE_PATH}')
        logging.error(e)
    exit()

    # Variables used to get proper repos
    assignment_name = input('Assignment Name: ')
    while not assignment_name:
        assignment_name = input('Please input an assignment name: ')
    date_due = input('Date Due (format = yyyy-mm-dd, press `enter` for current): ')
    if not date_due:
        current_date = date.today()
        date_due = current_date.strftime('%Y-%m-%d')
        print(f'Using current date: {date_due}')
    time_due = input('Time Due (24hr, press `enter` for current): ')
    if not time_due:
        current_time = datetime.now()
        time_due = current_time.strftime('%H:%M')
        print(f'Using current date: {time_due}')
    print()

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

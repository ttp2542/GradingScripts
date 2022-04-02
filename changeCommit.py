from cloneRepositories import *
"""
This script changes the commit head of a previously cloned repository.

@author Trey Pachucki ttp2542@g.rit.edu, Jin Moon jym2584@g.rit.edu, Kamron Cole kjc8084@rit.edu
"""
from threading import Thread
import _thread

ROLLBACK_COUNT = 0 # keeping track of successful rollback of repos

class RepoHandler(Thread):
    '''
    A Thread that clones a repo, resets it to specific time, and gets average number of lines per commit

    Each thread only clones one repo.
    '''
    __slots___ = ['__folder_name', '__date_due', '__time_due', '__repo_path']


    def __init__(self, folder_name: str, repo_path:str, date_due: str, time_due: str):
        self.__folder_name = folder_name
        self.__repo_path = repo_path
        self.__date_due = date_due 
        self.__time_due = time_due
        super().__init__()


    def run(self):
        '''
        Clones given repo and renames destination to student real name if class roster is provided.
        '''
        try:            

            commit_hash = self.get_commit_hash() # get commit hash at due date
            self.rollback_repo(commit_hash) # rollback repo to commit hash
            
        except: # Catch exception raised and interrupt main thread
            rev_list_process = subprocess.Popen(['git', 'log', '--reverse', '--date-order', '--date=local', '--max-parents=0' '--pretty="format=%ci (%s by %cn)"'], cwd=self.__repo_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            line = None

            for line in iter(rev_list_process.stdout.readline, b'\n'): # b'\n'-separated lines
                line = line.decode().strip() # line is read in bytes. Decode to str
            
            if re.match(r'^error:|^warning:|^fatal:', line):
                print(f'  > {LIGHT_RED}Skipping `{self.__folder_name}`\n\t{line}. {WHITE}') # print error to end user
            else:
                print(f'  > {LIGHT_RED}Skipping `{self.__folder_name}` because the hash is invalid (date is likely too far)\n\tOldest commit: {line.split("Date:   ")[1]}. {WHITE}') # print error to end user
            logging.exception('ERROR:') # log error to log file (logging automatically is passed exception)


    def get_commit_hash(self) -> str:
        '''
        Get commit hash at timestamp and reset local repo to timestamp on the default branch
        '''
        # git rev-parse --abbrev-ref origin/HEAD
        get_default_branch = subprocess.Popen(['git', 'rev-parse', '--abbrev-ref', 'origin/HEAD'], cwd=self.__repo_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        with get_default_branch: # Read rev list output line by line to search for error or commit hash
            for line in iter(get_default_branch.stdout.readline, b''): 
                line = line.decode()
                self.log_errors_given_line(line)
                get_default_branch = line.strip() 

        # run process on system that executes 'git rev-list' command. stdout is redirected so it doesn't output to end user
        rev_list_process = subprocess.Popen(['git', 'rev-list', '-n', '1', f'--before="{self.__date_due} {self.__time_due}"', f'{get_default_branch}'], cwd=self.__repo_path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        with rev_list_process: # Read rev list output line by line to search for error or commit hash
            for line in iter(rev_list_process.stdout.readline, b''): # b'\n'-separated lines
                line = line.decode()
                self.log_errors_given_line(line) # if command returned error raise exception
                return line.strip() # else returns commit hash of repo at timestamp
        

    def rollback_repo(self, commit_hash):
        '''
        Use commit hash and reset local repo to that commit (use git reset instead of git checkout to remove detached head warning)
        '''
        # run process on system that executes 'git reset' command. stdout is redirected so it doesn't output to end user
        # git reset is similar to checkout but doesn't care about detached heads and is more forceful
        checkout_process = subprocess.Popen(['git', 'reset', '--hard', commit_hash], cwd=self.__repo_path, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            print(f'  > Rolling back {self.__folder_name}...') # tell end user what repo is being rolled back
            self.log_errors_given_subprocess(checkout_process)
            global ROLLBACK_COUNT
            ROLLBACK_COUNT += 1
        except Exception as e:
            print(f'  > {LIGHT_RED}Rollback failed for `{self.__folder_name}` (likely due to invalid filename at specified commit).{WHITE}')
            logging.warning(f'Rollback failed for `{self.__folder_name}` (likely due to invalid filename at specified commit).')
    

    def log_errors_given_subprocess(self, subprocess: subprocess):
        '''
        Reads full git command output of a subprocess and raises exception & logs if error is found
        '''
        with subprocess:
            for line in iter(subprocess.stdout.readline, b''): # b'\n'-separated lines
                line = line.decode() # line is read in bytes. Decode to str
                if re.match(r'^error:|^warning:|^fatal:', line): # if git command threw error (usually wrong branch name)
                    logging.info('Subprocess: %r', line) # Log error
                    raise Exception(f'An error has occured with git.') # Raise exception to the thread

    
    def log_errors_given_line(self, line: str):
        '''
        Given 1 line of git command output, check if error.
        If so, log it and raise exception
        '''
        if re.match(r'^error:|^warning:|^fatal:', line): # if git command threw error (usually wrong branch name)
            logging.info('Subprocess: %r', line) # Log error to log file
            raise Exception(f'An error has occured with git.') # Raise exception to the thread


def main():
    # Enable color in cmd
    if os.name == 'nt':
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
        token, organization, student_filename, output_dir, save_repo_stats, add_timestamp = read_config()

        # makes the path of the directory that should exist
        initial_path = output_dir

        # we are now in the overarching folder for the assignment
        os.chdir(initial_path)
        
        # Iterate over the directories in the folder
        folders = dict()
        i = 0

        print(f"Scanned repos from '{initial_path}':")
        for directory in os.listdir(initial_path):
            i += 1
            folders[i] = directory
            print(f'  {i}: {directory}')
        
        print()

        while True:
            get_assignment = input("Which folder do you want to rollback? (enter number or press enter for recent): ")
            if get_assignment:
                try:
                    assignment = folders.get(int(get_assignment))
                    if assignment:
                        break
                except:
                    pass
            else :
                assignment = folders.get(i)
                print("assignment: " + assignment)
                break
        
        initial_path = f'{output_dir}/{assignment}'

        date_due = get_date_due()
        time_due = get_time_due()
        
        print()

        print(f"Output directory: {initial_path}")
        threads = []
        for directory in os.listdir(initial_path):
            if not re.findall("avgLinesInserted", directory):
                path = f'{initial_path}/{directory}'
                thread = RepoHandler(directory, path, date_due, time_due)
                threads.append(thread)

        # Run all clone threads
        for thread in threads:
            thread.start()

        # Make main thread wait for all repos to be cloned, set back to due date/time, and avg lines per commit to be found
        for thread in threads:
            thread.join()

        print()
        print(f'{LIGHT_GREEN}Done.{WHITE}')
        print(f'{LIGHT_GREEN}{ROLLBACK_COUNT}/{len(threads)} repos have been rolled back to {date_due} {time_due}.{WHITE}')


    except FileNotFoundError as e: # If classroom roster file specified in config.txt isn't found.
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
    except NotImplementedError as e:
        print()
        print(e)
        logging.error(e)
    except Exception as e: # If anything else happens
        print(f'ERROR: Something happened. Check {LOG_FILE_PATH}')
        logging.error(e)
    exit()


if __name__ == "__main__":  
    main()

# Grading Script for GCIS

1)  ![Download the script](https://github.com/ttp2542/GradingScripts/archive/refs/heads/master.zip)  
    - Extract it and keep it somewhere easy to access  

2)  Install the requirements by typing `pip install -r requirements.txt`
    - Alternatively, `pip install PyGithub`  or  `py  -m pip install PyGithub`  on powershell  
    - Mac users might have to use  `python3  -m pip install PyGithub`

3)  ![Navigate to the Personal Access Tokens](https://github.com/settings/tokens)
a.  Generate a new token and grant access to these scopes:  
![image](https://user-images.githubusercontent.com/67706639/159988815-1849a06d-d6a6-43d2-8504-666fc714e8a6.png)

b.  **IMPORTANT**  Save  the personal access token  somewhere (preferably  on a notepad)


4) Keep note of these:
	 - ![Find the github organization for your section](https://github.com/settings/organizations)
		 - Copy the org name from the URL -> https://i.imgur.com/NCJM6rm.png

	 - ![Go to github classroom](https://classroom.github.com/classrooms)
		 - Go to the section you're grading (not individual assignments) and click `Students`
		 - Download the classroom_roster.csv and move it somewhere where you will find it
		 - Remove the students (entire row) that you don't want to clone from the csv file

5) Run cloneRepos.bat  from the GradingScripts  
	 - Paste the personal access token  
	 - Type the github organization that you found  (exactly how it is named,  case not sensitive)  
	 - Enter the  directory/full path  (as well as the filename) that  the  classroom_roster.csv is in  
	 - Enter the full  path (ideally) of where you want  the  assignments to be stored


**Now you’re ready to grade!**

## How to use cloneRepos.bat after setup
1) Keep note of the assignment link that you want to clone
2) Follow the instructions regarding the date & time due

**NOTE:** the time is assumed in your local timezone. So an assignment that's due at @ 2:00 PM EST would be 14:00 in 24hr format.

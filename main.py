
from termcolor import colored
import re

from helpers import *

print(colored('Welcome to SelimErrorFinder v0.1', 'blue'))
print(colored('The goal of this script is to find any possible syntax errors in your python script and to fix them if prompted.', 'blue'))
print(colored('Warning: The script is still in alpha stages. Expect to encounter some bugs!', 'yellow'))

while True:
    script_location = input(colored('Enter script location: ', 'magenta'))
    match = re.search(r'(?<=\.)\w+$', script_location)
    extension = match.group() if match else None
        
    if not extension:
        script_location += '.py'
        break
    elif extension != 'py':
        print(colored('Error: file loaded should be a python script. Try again!', 'red'))
    else:
        break

code_lines = loadScript(script_location)
printErrors(code_lines)
print(colored('Warning: Fixing errors automatically is still in beta! You might encounters bugs while using it.', 'yellow'))
while True:
    choice = input(colored('Do you want to automatically fix the errors and save the changes to a new file: ', 'blue'))[0].lower()
    choices = ['y', 'n']
    if choice in choices:
        break
    print(colored('Please answer by (yes) or (no)!', 'blue'))
if choice == 'y':    
    fixErrors(code_lines)
    saveScript(code_lines, 'script-new.py')
print(colored('Thank you for using our program!', 'blue'))
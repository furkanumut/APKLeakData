#!/usr/bin/python
import os
import re
import sys
import json
import argparse
import threading
from src.ApkDecompiler import ApkDecompiler as Decompiler
from src.ColorizedPrint import ColorizedPrint as print_with_color

root_dir=os.getcwd()+"/extractedApk/"
pattern_file="./src/regex.json"
scope_mode=False
project_path=""
apk_path=""

found_patterns=dict()
scope_list=dict()
execute_command_list = dict() #if found pattern and have execute command then execute it

regex_patterns =[]

def is_valid_path(name, project_path):
    print_with_color("I: Checking if the "+ name +" path is valid.", "INFO_WS")
    if (os.path.exists(project_path)==False):
        print_with_color("E: Incorrect "+ name +" path found. Please try again with correct path.", "ERROR")
        print
        exit(1)
    else:
        print_with_color("I: "+ name +" Path Found.", "INFO_WS")

def print_list(lst):
    counter=0
    for item in lst:
        counter=counter+1
        entry=str(counter)+". "+str(item)
        print_with_color(entry, "PLAIN_WS")

def add_pattern(name, value):
    global found_patterns

    name = name.capitalize()
    if name in found_patterns:
        if value in found_patterns[name]:
            return
        found_patterns[name].append(value)
    else:
        found_patterns[name]=[value]

def pattern_search(pattern, name, line):
    try:
        temp=re.findall(pattern,line)
        for element in temp:
            add_pattern(name, element)
            if (scope_mode) and (name in scope_list):
                for scope in scope_list[name].split(","):
                    if scope in element:
                        add_pattern("SCOPE "+name, element)
    except:
        print_with_color("E: Error in pattern: "+pattern, "ERROR")

def pattern_file_to_list(file_name):
    global regex_patterns
    try:
        with open(file_name, mode='r') as file:
            regex_patterns = json.loads(file.read())
    except:
        print_with_color("E: Error json parse in pattern file: "+file_name, "ERROR")
        exit(1)

def pattern_configuration():
    global regex_patterns
    global scope_list
    global scope_mode
    global execute_command_list

    for pattern_name in regex_patterns:
        if isinstance(regex_patterns[pattern_name], dict) :
            if "scope" in regex_patterns[pattern_name].keys():
                scope_mode=True
                scope_list[pattern_name] = regex_patterns[pattern_name]['scope']
            if "command" in regex_patterns[pattern_name].keys():
                execute_command_list[pattern_name] = regex_patterns[pattern_name]['command']
            regex_patterns[pattern_name] = regex_patterns[pattern_name]['regex']

def perform_recon():
    global regex_patterns
    without_file_extensions=['.png', '.webp', '.jpg', '.gif', '.otf', '.ttf']
    filecontent=""

    #skip files with extensions
    skipping_walk = lambda target_directory, excluded_extentions: (
        (root, dirs, [F for F in files if os.path.splitext(F)[1] not in excluded_extentions]) 
        for (root, dirs, files) in os.walk(target_directory)
    )

    #file read and search
    for dir_path, dirs, file_names in skipping_walk(project_path, without_file_extensions):
        for file_name in file_names:
            try:
                fullpath = os.path.join(dir_path, file_name)
                with open(fullpath, mode='r', encoding='utf8') as fileobj:
                    filecontent = fileobj.read()
            except Exception as e:
                if not hidden_error:
                    print_with_color("E: Exception while reading "+fullpath,"ERROR")
                continue

            #threading pattern search for faster results
            threads=[]
            for name, pattern in regex_patterns.items():
                if isinstance(pattern, list):
                    for p in pattern:
                        thread = threading.Thread(target=pattern_search, args=(p, name, filecontent))
                else:
                    thread = threading.Thread(target=pattern_search, args=(pattern, name, filecontent))
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()

def check_result(name, result):
    if (len(result)==0):
        print_with_color("\nNo "+name+" found", "INSECURE")
    else:
        print_with_color("\nList of "+name+"s found in the application", "SECURE")
        print_list(result)
                
def display_results():
    global found_patterns

    for pattern in found_patterns:
            check_result(pattern, found_patterns[pattern])
    if found_patterns=={}:
        print_with_color("No secrets found", "INSECURE")

    print("")

def execute_commands():
    global execute_command_list
    global found_patterns
    print_with_color("I: Executing commands", "INFO_WS")
    for name, command in execute_command_list.items():
        if name not in found_patterns:
            continue
        for found_item in found_patterns[name]:
            if command['replace_item']:
                found_item = found_item.replace(command['replace_item']['old'], command['replace_item']['new'])
            execute = command['execute'].replace("{}", found_item)
            os.system(execute)
    print_with_color("I: Commands executed", "INFO_WS")

def save_results(file_name):
    global found_patterns
    
    for name, result in found_patterns.items():
        if (len(result)==0):
            continue
        with open(file_name, mode='a') as file:
            file.write("List of " + name + "s found in the application" + "\n")
            for item in result:
                file.write(item + "\n")
            file.write("="*50 + "\n\n")
    print_with_color("I: Results saved in "+root_dir+name+".txt", "INFO_WS")
####################################################################################################

print_with_color(""" 

░█████╗░██████╗░██╗░░██╗██╗░░░░░███████╗░█████╗░██╗░░██╗██████╗░░█████╗░████████╗░█████╗░
██╔══██╗██╔══██╗██║░██╔╝██║░░░░░██╔════╝██╔══██╗██║░██╔╝██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
███████║██████╔╝█████═╝░██║░░░░░█████╗░░███████║█████═╝░██║░░██║███████║░░░██║░░░███████║
██╔══██║██╔═══╝░██╔═██╗░██║░░░░░██╔══╝░░██╔══██║██╔═██╗░██║░░██║██╔══██║░░░██║░░░██╔══██║
██║░░██║██║░░░░░██║░╚██╗███████╗███████╗██║░░██║██║░╚██╗██████╔╝██║░░██║░░░██║░░░██║░░██║
╚═╝░░╚═╝╚═╝░░░░░╚═╝░░╚═╝╚══════╝╚══════╝╚═╝░░╚═╝╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░╚═╝

    """, 'OUTPUT')
print_with_color("""                         
                  # Developed By Shiv Sahni - @shiv__sahni
                  # Updated By Furkan Umut Ceylan - @furkanumut
    """, "INSECURE")

parser = argparse.ArgumentParser(description='Passive Enumeration Utility For Android Applications')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-p', '--project', help='Path to the project directory')
group.add_argument('-a', '--apk', help='Set the APK file')
parser.add_argument('-d', '--decompiler', help='If you select apk option, you can specify the decompiler. Default: apktool', default='apktool', choices=['apktool', 'jadx'], required=False)
parser.add_argument('-c', '--custom', help='Custom pattern json file', required=False)
parser.add_argument('-o', '--output', help='Output file path (i.e. ./exampletld.txt)', required=False)
parser.add_argument('-he', '--hidden-error', help='Hidden error for filename read, parse regex', action='store_true', required=False)
args = parser.parse_args()

hidden_error = args.hidden_error

if args.project:
    project_path=args.project
    is_valid_path('Apk Project', project_path)

elif args.apk:
    apk_path=args.apk
    is_valid_path('Apk File', apk_path)

    decompiler = args.decompiler
    apk_name = apk_path.split('/')[-1].rsplit('.', maxsplit=1)[0]
    print_with_color("Apk name; "+apk_name, "OUTPUT")
    project_path=root_dir+apk_name+"_"+decompiler
    if os.path.exists(project_path):
        Decompiler.clean_decompile_path(project_path)

    print_with_color("I: Decompiling the APK file", "INFO_WS")
    decompile = Decompiler(apk_path, decompiler, project_path)
    if decompile.decompile_status != 0:
        print_with_color("E: Decompiling failed, you can change decompiler (jadx or apktool).","ERROR")
        sys.exit(1)
    print_with_color("I: Decompiling completed", "INFO_WS")

if (args.custom):
    is_valid_path('Custom Pattern', project_path)
    custom_pattern_file = args.custom
    pattern_file_to_list(custom_pattern_file)
else:
    is_valid_path("Standart Pattern",pattern_file)
    pattern_file_to_list(pattern_file)

pattern_configuration()
output = args.output

try:
    perform_recon()
    display_results()
    execute_commands()

    if output:
        save_results(output)
except KeyboardInterrupt:
    print_with_color("I: Acknowledging KeyboardInterrupt. Thank you for using APKLeakData", "INFO_WS")
    exit(0)

print_with_color("Thank You For Using APKLeakData","OUTPUT")
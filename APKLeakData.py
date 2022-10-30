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
apk_path=""
project_path=""
scope_mode=False
pattern_file="./src/regex.json"
pattern_list=dict()

scope_list=dict()

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
    global pattern_list

    name = name.capitalize()
    if name in pattern_list:
        if value in pattern_list[name]:
            return
        pattern_list[name].append(value)
    else:
        pattern_list[name]=[value]

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

def pattern_scope_check():
    global scope_list
    global scope_mode
    global regex_patterns

    for pattern_name in regex_patterns:
        if isinstance(regex_patterns[pattern_name], dict) :
            if "scope" in regex_patterns[pattern_name].keys():
                scope_mode=True
                scope_list[pattern_name] = regex_patterns[pattern_name]['scope']
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
    global pattern_list

    for pattern in pattern_list:
            check_result(pattern, pattern_list[pattern])
    if pattern_list=={}:
        print_with_color("No secrets found", "INSECURE")

    print("")

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
pattern_scope_check()

try:
    perform_recon()
    display_results()
except KeyboardInterrupt:
    print_with_color("I: Acknowledging KeyboardInterrupt. Thank you for using APKLeakData", "INFO_WS")
    exit(0)

print_with_color("Thank You For Using APKLeakData","OUTPUT")
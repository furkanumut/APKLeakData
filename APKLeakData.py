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

scope_list=[]
find_functions_list = []

authority_list=[]
in_scope_authority_list=[]
public_ip_list=[]
s3_list=[]
s3_website_list=[]
gmap_keys=[]
custom_pattern_list=dict()

urlRegex='(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+):?\d*)([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?'#regex to extract domain
s3Regex1="https*://(.+?)\.s3\..+?\.amazonaws\.com\/.+?"
s3Regex2="https*://s3\..+?\.amazonaws\.com\/(.+?)\/.+?"
s3Regex3="S3://(.+?)/"
s3Website1="https*://(.+?)\.s3-website\..+?\.amazonaws\.com"
s3Website2="https*://(.+?)\.s3-website-.+?\.amazonaws\.com"
publicIp="https*://(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))(?<!127)(?<!^10)(?<!^0)\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!192\.168)(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!\.255$))"
gMapsAPI="(AIzaSy[\w-]{33})"
custom_pattern_regex =[] #if you set custom pattern file, auto load. example: {'AWS_ACCESS_KEY_ID': 'AKIA[0-9A-Z]{16}', 'AWS_SECRET_ACCESS_KEY': '[0-9a-zA-Z/+]{40}'}

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

def add_custom_pattern(name, value):
    global custom_pattern_list
    if name in custom_pattern_list:
        if value in custom_pattern_list[name]:
            return
        custom_pattern_list[name].append(value)
    else:
        custom_pattern_list[name]=[value]

def findS3Bucket(line):
    temp=re.findall(s3Regex1,line)
    if (len(temp)!=0):
        for element in temp:
            s3_list.append(element)


    temp=re.findall(s3Regex2,line)
    if (len(temp)!=0):
        for element in temp:
            s3_list.append(element)


    temp=re.findall(s3Regex3,line)
    if (len(temp)!=0):
        for element in temp:
            s3_list.append(element)


def findGoogleAPIKeys(line):
    temp=re.findall(gMapsAPI,line)
    if (len(temp)!=0):
        for element in temp:
            gmap_keys.append(element)

def findS3Website(line):
    temp=re.findall(s3Website1,line)
    if (len(temp)!=0):
        for element in temp:
            s3_website_list.append(element)

    temp=re.findall(s3Website2,line)
    if (len(temp)!=0):
        for element in temp:
            s3_website_list.append(element)


def findUrls(line):
    temp=re.findall(urlRegex,line)
    if (len(temp)!=0):
        for element in temp:
            authority_list.append(element[0]+"://"+element[1])
            if(scope_mode):
                for scope in scope_list:
                    if scope in element[1]:
                        in_scope_authority_list.append(element[0]+"://"+element[1])

def find_public_ips(line):
    temp=re.findall(publicIp,line)
    if (len(temp)!=0):
        for element in temp:
            public_ip_list.append(element[0])

def extract_custom_pattern(pattern, name, line):
    try:
        temp=re.findall(pattern,line)
        if (len(temp)!=0):
            for element in temp:
                add_custom_pattern(name, element)
    except:
        print_with_color("E: Error in custom pattern: "+pattern, "ERROR")


def find_custom_pattern(line):
    global find_functions_list
    threads=[]
    for name, pattern in custom_pattern_regex.items():
        if isinstance(pattern, list):
            for p in pattern:
                thread = threading.Thread(target=extract_custom_pattern, args=(p, name, line,))
        else:
            thread = threading.Thread(target=extract_custom_pattern, args=(pattern, name, line,))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

def custom_pattern():
    global find_functions_list, custom_pattern_regex
    with open(custom_pattern_file, mode='r') as file:
        custom_pattern_regex = json.load(file)
    if len(custom_pattern_regex)!=0:
        find_functions_list.append(find_custom_pattern)


def perform_recon():
    global domainList, authority_list, inScopeDomainList, in_scope_authority_list, find_functions_list
    find_functions_list += [findUrls, findS3Bucket, findS3Website, findGoogleAPIKeys, find_public_ips]
    without_file_extensions=['.png', '.webp', '.jpg', '.gif', '.otf', '.ttf']
    filecontent=""

    skipping_walk = lambda target_directory, excluded_extentions: (
        (root, dirs, [F for F in files if os.path.splitext(F)[1] not in excluded_extentions]) 
        for (root, dirs, files) in os.walk(target_directory)
    )

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

            threads = []
            for function in find_functions_list:
                thread = threading.Thread(target=function, args=(filecontent,))
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
    global in_scope_authority_list, authority_list, s3_list, s3_website_list, public_ip_list, gmap_keys, custom_pattern_list
    in_scope_authority_list=list(set(in_scope_authority_list))
    authority_list=list(set(authority_list))
    s3_list=list(set(s3_list))
    s3_website_list=list(set(s3_website_list))
    public_ip_list=list(set(public_ip_list))
    gmap_keys=list(set(gmap_keys))

    check_result('URL', authority_list)
    check_result('Scope in URL', in_scope_authority_list)
    check_result('S3 bucket', s3_list)
    check_result('S3 Website', s3_website_list)
    check_result('IP', public_ip_list)
    check_result('Google Map API', gmap_keys)
    for pattern in custom_pattern_list:
            check_result(pattern, custom_pattern_list[pattern])
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
parser.add_argument('-s', '--scope', help='List of keywords to filter out domains', required=False)
parser.add_argument('-c', '--custom', help='Custom pattern json file', required=False)
parser.add_argument('-he', '--hidden-error', help='Hidden error for filename read, parse regex', action='store_true', required=False)
args = parser.parse_args()

if args.hidden_error:
    hidden_error = True

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

if (args.scope):
    scope_string = args.scope
    scope_list = scope_string.split(",")
    if len(scope_list) > 0:
        scope_mode = True

if (args.custom):
    is_valid_path('Custom Pattern', project_path)
    custom_pattern_file = args.custom
    custom_pattern()

try:
    perform_recon()
    display_results()
except KeyboardInterrupt:
    print_with_color("I: Acknowledging KeyboardInterrupt. Thank you for using APKLeakData", "INFO_WS")
    exit(0)

print_with_color("Thank You For Using APKLeakData","OUTPUT")
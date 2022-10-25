#!/usr/bin/python
import os
import re
import threading
import argparse
import json
from src.ColorizedPrint import ColorizedPrint as myPrint


rootDir=os.path.expanduser("~")+"/.APKLeakData/" #ConfigFolder ~/.SourceCodeAnalyzer/
projectPath=""
apkHash=""
scopeMode=False

scopeList=[]
findFunctionsList = []

authorityList=[]
inScopeAuthorityList=[]
publicIpList=[]
s3List=[]
s3WebsiteList=[]
gmapKeys=[]
vulnerableGmapKeys=[]
customPatternList=dict()

urlRegex='(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+):?\d*)([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?'#regex to extract domain
s3Regex1="https*://(.+?)\.s3\..+?\.amazonaws\.com\/.+?"
s3Regex2="https*://s3\..+?\.amazonaws\.com\/(.+?)\/.+?"
s3Regex3="S3://(.+?)/"
s3Website1="https*://(.+?)\.s3-website\..+?\.amazonaws\.com"
s3Website2="https*://(.+?)\.s3-website-.+?\.amazonaws\.com"
publicIp="https*://(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))(?<!127)(?<!^10)(?<!^0)\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!192\.168)(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!\.255$))"
gMapsAPI="(AIzaSy[\w-]{33})"
customPatternRegex =[] #if you set custom pattern file, auto load. example: {'AWS_ACCESS_KEY_ID': 'AKIA[0-9A-Z]{16}', 'AWS_SECRET_ACCESS_KEY': '[0-9a-zA-Z/+]{40}'}

def isValidPath(name, projectPath):
    myPrint("I: Checking if the "+ name +" path is valid.", "INFO_WS")
    if (os.path.exists(projectPath)==False):
        myPrint("E: Incorrect "+ name +" path found. Please try again with correct path.", "ERROR")
        print
        exit(1)
    else:
        myPrint("I: "+ name +" Path Found.", "INFO_WS")

def printList(lst):
    counter=0
    for item in lst:
        counter=counter+1
        entry=str(counter)+". "+str(item)
        myPrint(entry, "PLAIN_WS")

def addNewCustomPattern(name, value):
    global customPatternList
    if name in customPatternList:
        if value in customPatternList[name]:
            return
        customPatternList[name].append(value)
    else:
        customPatternList[name]=[value]

def findS3Bucket(line):
    temp=re.findall(s3Regex1,line)
    if (len(temp)!=0):
        for element in temp:
            s3List.append(element)


    temp=re.findall(s3Regex2,line)
    if (len(temp)!=0):
        for element in temp:
            s3List.append(element)


    temp=re.findall(s3Regex3,line)
    if (len(temp)!=0):
        for element in temp:
            s3List.append(element)


def findGoogleAPIKeys(line):
    temp=re.findall(gMapsAPI,line)
    if (len(temp)!=0):
        for element in temp:
            gmapKeys.append(element)

def findS3Website(line):
    temp=re.findall(s3Website1,line)
    if (len(temp)!=0):
        for element in temp:
            s3WebsiteList.append(element)

    temp=re.findall(s3Website2,line)
    if (len(temp)!=0):
        for element in temp:
            s3WebsiteList.append(element)


def findUrls(line):
    temp=re.findall(urlRegex,line)
    if (len(temp)!=0):
        for element in temp:
            authorityList.append(element[0]+"://"+element[1])
            if(scopeMode):
                for scope in scopeList:
                    if scope in element[1]:
                        inScopeAuthorityList.append(element[0]+"://"+element[1])

def findPublicIPs(line):
    temp=re.findall(publicIp,line)
    if (len(temp)!=0):
        for element in temp:
            publicIpList.append(element[0])

def extractCustomPattern(pattern, name, line):
    try:
        temp=re.findall(pattern,line)
        if (len(temp)!=0):
            for element in temp:
                addNewCustomPattern(name, element)
    except:
        myPrint("E: Error in custom pattern: "+pattern, "ERROR")


def findCustomPattern(line):
    global findFunctionsList
    threads=[]
    for name, pattern in customPatternRegex.items():
        if isinstance(pattern, list):
            for p in pattern:
                thread = threading.Thread(target=extractCustomPattern, args=(p, name, line,))
        else:
            thread = threading.Thread(target=extractCustomPattern, args=(pattern, name, line,))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()

def customPattern():
    global findFunctionsList, customPatternRegex
    with open(customPatternFile, mode='r') as file:
        customPatternRegex = json.load(file)
    if len(customPatternRegex)!=0:
        findFunctionsList.append(findCustomPattern)


def performRecon():
    global domainList, authorityList, inScopeDomainList, inScopeAuthorityList, findFunctionsList
    findFunctionsList += [findUrls, findS3Bucket, findS3Website, findGoogleAPIKeys, findPublicIPs]
    withoutFileExtensions=['.png', '.webp', '.jpg', '.gif', '.otf', '.ttf']
    filecontent=""

    skippingWalk = lambda targetDirectory, excludedExtentions: (
        (root, dirs, [F for F in files if os.path.splitext(F)[1] not in excludedExtentions]) 
        for (root, dirs, files) in os.walk(targetDirectory)
    )

    for dir_path, dirs, file_names in skippingWalk(projectPath, withoutFileExtensions):
        for file_name in file_names:
            try:
                fullpath = os.path.join(dir_path, file_name)
                with open(fullpath, mode='r', encoding='utf8') as fileobj:
                    filecontent = fileobj.read()
            except Exception as e:
                myPrint("E: Exception while reading "+fullpath,"ERROR")
                continue

            threads = []
            for function in findFunctionsList:
                thread = threading.Thread(target=function, args=(filecontent,))
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()

def checkResult(name, result):
    if (len(result)==0):
        myPrint("\nNo "+name+" found", "INSECURE")
    else:
        myPrint("\nList of "+name+"s found in the application", "SECURE")
        printList(result)

def displayResults():
    global inScopeAuthorityList, authorityList, s3List, s3WebsiteList, publicIpList, gmapKeys, unrestrictedGmapKeys, customPatternList
    inScopeAuthorityList=list(set(inScopeAuthorityList))
    authorityList=list(set(authorityList))
    s3List=list(set(s3List))
    s3WebsiteList=list(set(s3WebsiteList))
    publicIpList=list(set(publicIpList))
    gmapKeys=list(set(gmapKeys))

    checkResult('URL', authorityList)
    checkResult('Scope in URL', inScopeAuthorityList)
    checkResult('S3 bucket', s3List)
    checkResult('S3 Website', s3WebsiteList)
    checkResult('IP', publicIpList)
    checkResult('Google Map API', gmapKeys)
    for pattern in customPatternList:
            checkResult(pattern, customPatternList[pattern])
    print("")

####################################################################################################

myPrint(""" 

░█████╗░██████╗░██╗░░██╗██╗░░░░░███████╗░█████╗░██╗░░██╗██████╗░░█████╗░████████╗░█████╗░
██╔══██╗██╔══██╗██║░██╔╝██║░░░░░██╔════╝██╔══██╗██║░██╔╝██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
███████║██████╔╝█████═╝░██║░░░░░█████╗░░███████║█████═╝░██║░░██║███████║░░░██║░░░███████║
██╔══██║██╔═══╝░██╔═██╗░██║░░░░░██╔══╝░░██╔══██║██╔═██╗░██║░░██║██╔══██║░░░██║░░░██╔══██║
██║░░██║██║░░░░░██║░╚██╗███████╗███████╗██║░░██║██║░╚██╗██████╔╝██║░░██║░░░██║░░░██║░░██║
╚═╝░░╚═╝╚═╝░░░░░╚═╝░░╚═╝╚══════╝╚══════╝╚═╝░░╚═╝╚═╝░░╚═╝╚═════╝░╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░╚═╝

    """, 'OUTPUT')
myPrint("""                         
                  # Developed By Shiv Sahni - @shiv__sahni
                  # Updated By Furkan Umut Ceylan - @furkanumut
    """, "INSECURE")

parser = argparse.ArgumentParser(description='Passive Enumeration Utility For Android Applications')
parser.add_argument('-p', '--project', help='Path to the project directory', required=True)
parser.add_argument('-s', '--scope', help='List of keywords to filter out domains', required=False)
parser.add_argument('-c', '--custom', help='Custom pattern json file', required=False)
parser.add_argument('-he', '--hidden-error', help='Hidden error for filename read, parse regex', action='store_true', required=False)
args = parser.parse_args()

projectPath=args.project
isValidPath('Apk Project', projectPath)

if (args.scope):
    scopeString = args.scope
    scopeList = scopeString.split(",")
    if len(scopeList) > 0:
        scopeMode = True

if (args.custom):
    isValidPath('Custom Pattern', projectPath)
    customPatternFile = args.custom
    customPattern()
    
try:
    performRecon()
    displayResults()
except KeyboardInterrupt:
    myPrint("I: Acknowledging KeyboardInterrupt. Thank you for using APKLeakData", "INFO_WS")
    exit(0)

myPrint("Thank You For Using APKLeakData","OUTPUT")
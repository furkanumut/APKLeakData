# APKLeakData: Passive Enumeration Utility For Android Applications

![https://www.python.org/static/community_logos/python-logo.png](https://www.python.org/static/community_logos/python-logo.png) 


![](image/apkleakdata_info.png)

## Usage
The utility takes APK file as an input, performs reverse engineering and gathers information from the decompiled binary. As of now, the script provides the following information by searching the decompiled code:

* List of domains in the application

* List of S3 buckets referenced in the code

* List of S3 websites referenced in the code

* List of IP addresses referenced in the code

* List of Google Maps API Keys in the code(**NEW**)

![](image/apkleakdata_preview.png)

| Argument   | DESCRIPTION   | EXAMPLE 
|---|---| --- |
| -h  | show help message and args list  | APKLeakData.py -h    |
| -p  | Set project path (apktool decomple output path)  |   pyhon -p APKLeakData.py -p ~/decompile-apk-path  |
| -s  | Filter the set words in the domain  |   pyhon -p APKLeakData.py -p ~/decompile-apk-path -s 'mail,ftp,login'  |
|  -c |  Custom regext pattern file location. File format: Json |  pyhon -p APKLeakData.py -p ~/decompile-apk-path -c custom_search.json   |
| -he | Hidden File reading error(binary file), Regex parse error | pyhon -p APKLeakData.py -p ~/decompile-apk-path -he |

## Custom Pattern File
The file must be in json format. You can use multiple patterns in one value. 

```json
{
    "Pattern Name for list name": "regex parameter",
    "Multiple Pattern Example": [
        'regex',
        'regex2'
        ],
	
    "Google_API_Key": "AIza[0-9A-Za-z\\-_]{35}",
    "Firebase": [
		"[a-z0-9.-]+\\.firebaseio\\.com",
		"[a-z0-9.-]+\\.firebaseapp\\.com"
	],
}
```
If you want a prepared pattern file, you can use the custom_search.json file.

The larger the file, the longer it will take. You can set yourself a json which can be critical information for quick scan.

## New Feature
- It now works with Python 3.
- "argparse" was used in the argument section, so less if-else was used, it was clean code for arg parse.
- Repeated codes were organized for Thread. Function was used for repetitive codes.
- Custom Pattern has been added for the user to search.

## What I plan to do
- Now we can only use the decompile project with APKTOOL. But I want to add it from the APK file and analyze it.
- Save the output to a file.
- Allow the thread limit from the user. In this way, I think it will work faster by increasing the thread limit.
# APKLeakData: Passive Enumeration Utility For Android Applications

![https://www.python.org/static/community_logos/python-logo.png](https://www.python.org/static/community_logos/python-logo.png) 


![](image/apkleakdata_info.png)

## New Feature
- It now works with Python 3.
- "argparse" was used in the argument section, so less if-else was used, it was clean code for arg parse.
- Repeated codes were organized for Thread. Function was used for repetitive codes.
- Custom Pattern has been added for the user to search.
- All regex patterns can be scoped. Read how to make custom pattern file.
- When it finds keys, you can run a command to test them.


## Usage
The utility takes APK file as an input, performs reverse engineering and gathers information from the decompiled binary. As of now, the script provides the following information by searching the decompiled code:

* List of **domains** in the application

* List of **S3 buckets** referenced in the code

* List of **S3 websites** referenced in the code

* List of **IP addresses** referenced in the code

* List of **Google Maps API** Keys in the code

* List of **Custom Patterns** in the code

![](image/apkleakdata_preview.png)

| Argument   | DESCRIPTION   | EXAMPLE 
|---|---| --- |
| -h  | show help message and args list  | APKLeakData.py -h    |
| -p  | Set project path (apktool decomple output path)  |   pyhon APKLeakData.py -p ~/decompile-apk-path  |
| -a | Set apk file | python APKLeakData.py -a apkfile.apk
| -d | If the apk file is selected, you can choose the decompiler. (Apktool or jadx). Default: apktool | python APKLeakData.py -a apkfile.apk -d jadx
|  -c |  Custom regext pattern file location. File format: Json |  pyhon APKLeakData.py -p ~/decompile-apk-path -c custom_search.json   |
| -he | Hidden File reading error(binary file) | pyhon APKLeakData.py -p ~/decompile-apk-path -he |
| -o | Output file path/name | pyhon APKLeakData.py -p ~/decompile-apk-path -o ~/leak-data.txt |

## How to make Custom Pattern File
The file must be in json format. You can use multiple patterns in one value. 

```json
{
    // EXAMPLE
    "Pattern Name for list name": "regex parameter",
    "Pattern with Scope":{
        "scope": "example.com,example2.com,cdn,other.com",
        "regex": "regex parameter"
    },
    "Pattern with Scope and Commands":{
        "scope": "example.com,example2.com,cdn,other.com",
        "regex": "regex parameter",
        "command": {
            "execute": "echo '{}' >> domains.txt",
            "replace_item":{
                "old": "'",
                "new": "\\'"
           }
        }
    },
    ====================================================================
    "Multiple Pattern": [
        "regex",
        "regex2"
    ],
    "Multiple Pattern with Scope and Command":{
        "scope": "example.com,example2.com,cdn,other.com",
        "regex": [
            "regex",
            "regex2"
        ],
       "command": {
            "execute": "echo '{}' >> domains.txt",
            "replace_item":{
                "old": "'",
                "new": "\\'"
           }
        }
    },
    ====================================================================

    // USAGE:
    "Google_API_Key": "AIza[0-9A-Za-z\\-_]{35}",
    "Firebase": [
		"[a-z0-9.-]+\\.firebaseio\\.com",
		"[a-z0-9.-]+\\.firebaseapp\\.com"
	],
    "Url Find": {
        "scope": "domain.tld",
        "regex": [
            "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
            ]
    },
}
```
If you want a prepared pattern file, you can use the custom_search.json file.

The larger the file, the longer it will take. You can set yourself a json which can be critical information for quick scan.

## How to run command to test keys
Testing the data we find from the APK file spends a lot of time. After finding the data, I coded the command operation because it was necessary to test the data.

```
{
    "Url": {
        "regex": ["http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"],
	    "command": {
            "execute": "echo '{}' >> domains.txt",
            "replace_item":{
                "old": "'",
                "new": "\\'"
           }
        }
    }
}
```

| Key  | Description  | Example | Required  |
|---|---|---|---|
| execute  | If you find an api key, which command you want to run. Api Key should be specified as {}.  | you_api_test_script.py --api {}  | Yes | 
| replace_item |  Some api keys and the parameters you are looking for may be a syntax error to run a command. You can use Escape characters using this. |  |  No |
| old  | Specify the character that gives the syntax error.  |  ' |  If use replace_item: yes |
| new | What do you want to change the character that says Old value?  |  \\\\' |  If use replace_item: yes |

I recommend you to browse [Keyhacks](https://github.com/streaak/keyhacks) to create your own api test script.
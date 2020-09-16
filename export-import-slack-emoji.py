import requests
import json
import re
import os
import time
import re
from os import walk

# --------------------------------------
# Set these 4 values then run the script 
# -------------------------------------
sourceSlackOrgCookie = ''
sourceSlackOrgToken = ''
destinationSlackOrgCookie = ''
destinationSlackOrgToken = ''

emojiDownloadFolder = 'slackEmoji'
sourceSlackOrgHeaders = {'cookie': sourceSlackOrgCookie, 'Authorization' : f'Bearer {sourceSlackOrgToken}'}
destinationSlackOrgHeaders = {'cookie': destinationSlackOrgCookie, 'Authorization' : f'Bearer {destinationSlackOrgToken}'}

if not os.path.exists(emojiDownloadFolder):
    os.makedirs(emojiDownloadFolder)

existingEmojiFileNames = []
for (dirpath, dirnames, filenames) in walk(emojiDownloadFolder):
    existingEmojiFileNames.extend(filenames)
    break

def getEmojiNameToUrlDict(headers):
    url = 'https://slack.com/api/emoji.list'
    response = requests.get(url, headers=headers)

    responseJson = json.loads(response.content)
    emojiNameToUrlDict = responseJson["emoji"]

    return emojiNameToUrlDict

# ----------------
# Do the downloading
# ----------------

emojiNameToUrlDict = getEmojiNameToUrlDict(sourceSlackOrgHeaders)

for emojiName in emojiNameToUrlDict:
     
    emojiUrl = emojiNameToUrlDict[emojiName]
    if not emojiUrl.startswith('alias:'):
        
        emojiFileExtension = re.search('\.\w+$', emojiUrl).group()

        emojiFileName = f'{emojiName}{emojiFileExtension}'

        if emojiFileName in existingEmojiFileNames:
            print(f'Emoji {emojiName}{emojiFileExtension} already downloaded, skipping download')
            continue

        response = requests.get(emojiUrl)

        # Write the resposne to a file
        invalidFileNameCharatersRegex = ':|;'
        emojiFileName = f'{emojiDownloadFolder}/{emojiName}{emojiFileExtension}'
        emojiFileName = re.sub(invalidFileNameCharatersRegex, '_', emojiFileName)
        open(emojiFileName, 'wb').write(response.content)

        print(f'Saved {emojiFileName}')

# ----------------
# Do the uploading
# ----------------

# get the existing emoji so we scan skip trying to upload any already existing emoji
destinationEmojiNameToUrlDict = getEmojiNameToUrlDict(destinationSlackOrgHeaders)

url = 'https://slack.com/api/emoji.add'
emojiNum = 0

for emojiFileName in existingEmojiFileNames:

    emojiFileNameWithoutExtension = emojiFileExtension = re.search('([^\.]+)\.', emojiFileName).group(1)

    if emojiFileNameWithoutExtension in destinationEmojiNameToUrlDict:
        print(f'Emoji with a name of {emojiFileNameWithoutExtension} already exits in destination, skipping upload')
        continue

    emojiUploaded = False

    while (not emojiUploaded):

        payload = {
            'mode': 'data',
            'name': emojiFileNameWithoutExtension
        }

        files = [
            ('image', open(f'slackEmoji/{emojiFileName}','rb'))
        ]

        response = requests.request("POST", url, headers=destinationSlackOrgHeaders, data = payload, files = files)

        responseJson = json.loads(response.content)

        if responseJson["ok"]:
            print(f'Uploaded {emojiFileName}')
            emojiUploaded = True
        elif not responseJson["ok"] and responseJson["error"] == "error_name_taken":
            print(f'Emoji with a name of {emojiFileNameWithoutExtension} already exits')
            emojiUploaded = True
        elif not responseJson["ok"] and responseJson["error"] == "ratelimited":
            retryAfter = response.headers['retry-after']
            retryAfterInt = int(retryAfter) + 1
            print(f'Exceeded rate limit, waiting {retryAfterInt} seconds before retrying')
            time.sleep(retryAfterInt)
        else:
            print(f'Unexpected failure! {responseJson["error"]}')
            print(response)
            print(response.headers)
            break

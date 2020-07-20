This is python script that exports emoji from one slack organization and imports then into another via the Slack API. Because the Slack API does not allow you to use a non bot/app user token, you have to get some information from your broswer to the script can emulate broswer Slack API calls.

### NOTE: This script will only work if you have access to see the emoji page for your source slack org and access to add custom emoji in your destination slack org

### Running Instructions

1. Open a broswer window and open your dev tools network tab
1. Set a filter of `/api/emoji.list`
1. Go to https://YOUR-EMOJI-SOURCE-ORG.slack.com/customize/emoji
1. You should see one request in your network tab, click it
1. Copy the `Cookie` request header value into the `sourceSlackOrgCookie` variable value in the script
1. Copy the `Token` form data value into the  `sourceSlackOrgToken` variable value in the script
1. Go to https://YOUR-EMOJI-DESTINATION-ORG.slack.com/customize/emoji
1. You should see one request in your network tab, click it
1. Copy the `Cookie` request header value into the `destinationSlackOrgCookie` variable value in the script
1. Copy the `Token` form data value into the `destinationSlackOrgToken` variable value in the script
1. Run the script :)

The script will not download emoji you have already downloaded and will not try upload emoji you have already uploaded so if you run into a rate limiting error just wait a while and start the script again and you can slowly get them all transfered.

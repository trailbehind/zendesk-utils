Scripts to create subscriptions to zendesk sections or forum topics

To use these scripts:
1. Clone the repo

2. pip install requests

Creating Section Subscriptions:

This script creates a subscription to every existing Help Center Section to the specified user_ids. Users will get notified of new articles created in each section and any comments posted. 

Edit create_section_subscriptions.py

If you don't want the user to get notified of new comments, set "include_comments" to False.


self.user_ids -- takes a list of user ids (this will be a number)
self.zendesk -- The name of the help center. The name can be found in the url of the help center. https://[help_center_name].zendesk.com/ ('gaiagps' - The updated Help Center as of 2018; 'commteamstrong'- support help center)
self.user -- Email address for your Zendesk account + the word /token
self.pwd -- API token for your Zendesk account

Creating Topic Subscriptions:

This script creates a subscription to every existing Community Forum Topic to the specified user_ids. Users will get notified of new articles created in each section and any comments posted. 

Edit create_topic_subscriptions.py

If you don't want the user to get notified of new comments, set "include_comments" to False.


self.user_ids -- takes a list of user ids (this will be a number)
self.zendesk -- The name of the help center. The name can be found in the url of the help center. https://[help_center_name].zendesk.com/
self.user -- Email address for your Zendesk account + the word /token
self.pwd -- API token for your Zendesk account


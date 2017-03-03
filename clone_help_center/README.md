This script searches for all articles, sections and categories in an existing Zendesk Help Center and copies them to a new one

To use this script:
Clone the repo
pip install requests

Usage:

Edit clone.py, replacing these exisiting variables with your account info:

self.origin_brand -- The name of the help center you want to copy from. The name can be found in the url of the help center. https://[help_center_name].zendesk.com/
self.new_brand -- The name of the help center you want to copy to. The name can be found in the url of the help center. https://[help_center_name].zendesk.com/

self.origin_username - Email address for your origin Zendesk account + the word /token
self.origin_token -- API token for your origin Zendesk Account

self.new_username - Email address for your new Zendesk account + the word /token
self.new_token - API token for your new Zendesk Account

(origin and new creditials will be the same if you are copying between brands on the same account)

Notes:
This script only copies the URL for photos. If you delete the photos from the origin help center, they will break in the new one
import json
import requests
#create article labels based on section id

class CreateArticleLabels:

	def __init__(self):
		self.zendesk = ''
		self.sections = 'https://{}.zendesk.com/api/v2/help_center/en-us/sections.json'.format(self.zendesk)
		self.articles_url = 'https://{}.zendesk.com/api/v2/help_center/en-us/articles.json'.format(self.zendesk)
		self.user = '' + '/token'
		self.pwd = ''
		self.headers = {'content-type': 'application/json'}
		self.sections = []

	def get_articles(self):
		articles = []
		articles_list = []
		count = 0
		while self.articles_url:
			response = requests.get(self.articles_url)
			if response.status_code != 200:
				print('FAILED to get get article list with error {}'.format(response.status_code))
				exit()
			data = response.json()
			for article in data['articles']:
				url = "https://help.gaiagps.com/api/v2/help_center/en-us/articles/{}/labels.json".format(article['id'])
				label_data = {"label": {"name": "add_topics"}}
				payload = json.dumps(label_data)
				if article['section_id'] in self.sections:
					print url
					response = requests.post(url, data=payload, headers=self.headers, auth=(self.user, self.pwd))
					if response.status_code != 201:
						print('error {}'.format(response.status_code))
						exit()
					print response
			self.articles_url = data['next_page']


add_labels = CreateArticleLabels()
add_labels.get_articles()

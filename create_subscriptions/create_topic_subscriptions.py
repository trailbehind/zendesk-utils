import json
import requests


class CreateTopicSubscriptions:


	def __init__(self):
		self.user_ids = []
		self.zendesk = ''
		self.topics = 'https://{}.zendesk.com/api/v2/community/topics.json'.format(self.zendesk)
		self.user = '' + '/token'
		self.pwd = ''
		self.headers = {'content-type': 'application/json'}
		

	def get_topics(self):
		topics_list = []
		response = requests.get(self.topics, auth=(self.user, self.pwd))
		if response.status_code != 200:
	  		print('Status:', response.status_code, 'Problem with the request. Exiting.')
	  		exit()
		data = response.json()
		topics = data['topics']
		for topic in topics:
  	  		topic_id = topic['id']
  	  		topics_list.append(topic_id)
  	  	print topics_list
  	  	return self.users(topics_list)


	def users(self, topics_list):
		for number in topics_list:
			topic_id = number
			

			for user in self.user_ids:
				# Package the data in a dictionary matching the expected JSON
				data = {"subscription": {"include_comments": True, "user_id": user}}
				url = 'https://gaiagpshelp.zendesk.com/api/v2/community/topics/{}/subscriptions.json'.format(topic_id)
				# Encode the data to create a JSON payload
				payload = json.dumps(data)

				# Do the HTTP get request
				response = requests.post(url, data=payload, headers=self.headers, auth=(self.user, self.pwd))

				# Check for HTTP codes other than 200
				if response.status_code != 201:
				    print('Status:', response.status_code, 'Problem with the request. Exiting.')
				    exit()


				print('subscription created', topic_id)

topics = CreateTopicSubscriptions()
topics.get_topics()
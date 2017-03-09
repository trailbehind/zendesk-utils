import json
import requests

class CreateSectionSubscriptions:

	def __init__(self):
		self.user_ids = []
		self.zendesk = ''
		self.sections = 'https://{}.zendesk.com/api/v2/help_center/en-us/sections.json'.format(self.zendesk)
		self.user = '' + '/token'
		self.pwd = ''
		self.headers = {'content-type': 'application/json'}
		

	def get_sections(self):
		sections_list = []
		response = requests.get(self.sections, auth=(self.user, self.pwd))
		if response.status_code != 200:
	  		print('Status:', response.status_code, 'Problem with the request. Exiting.')
	  		exit()
		data = response.json()
		sections = data['sections']
		for section in sections:
  	  		section_id = section['id']
  	  		sections_list.append(section_id)
  	  	print sections_list
  	  	return self.users(sections_list)


	def users(self, sections_list):
		for number in sections_list:
			section_id = number

			for user in self.user_ids:
				# Package the data in a dictionary matching the expected JSON
				data = {"subscription": {"source_locale": "en-us", "include_comments": True, "user_id": user}}
				url = 'https://{}.zendesk.com/api/v2/help_center/sections/{}/subscriptions.json'.format(self.zendesk, section_id)
				# Encode the data to create a JSON payload
				payload = json.dumps(data)
				response = requests.post(url, data=payload, headers=self.headers, auth=(self.user, self.pwd))

				# Check for HTTP codes other than 201
				if response.status_code != 201:
				    print('Status:', response.status_code, 'Problem with the request. Exiting.')
				    exit()

				print('subscription created', section_id)

creator = CreateSectionSubscriptions()
creator.get_sections()



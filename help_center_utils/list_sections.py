import json
import requests

class ListSections:

	def __init__(self):
		self.category_id = 
		self.zendesk = ''
		self.sections = 'https://{}.zendesk.com/api/v2/help_center/en-us/categories/{}/sections.json'.format(self.zendesk, self.addtopics_cat_id)
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
  	  	
		
list_sections = ListSections()
list_sections.get_sections()


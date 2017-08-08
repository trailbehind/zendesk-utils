import json
import requests

class CreateNewTicket: 
	def __init__(self):
		self.zendesk = 'gaiagps'
		self.create_ticket_url = 'https://{}.zendesk.com/api/v2/tickets.json'.format(self.zendesk)
		self.user = '' + '/token'
		self.pwd = ''
		self.credentials = (self.user, self.pwd)
		self.headers = {'content-type': 'application/json'}
		self.create_ticket_data = {"ticket":{"subject":"My printer is on fire!", "comment": { "body": "The smoke is very colorful." }}}

	def create_ticket(self):
		response = requests.post(self.create_ticket_url, headers=self.headers, auth=self.credentials, data=json.dumps(self.create_ticket_data))



ticket = CreateNewTicket()
ticket.create_ticket()



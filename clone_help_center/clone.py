#original https://github.com/trailbehind/zendesk-utils/tree/master/uservoice_to_zendesk

import requests, json

class ZendeskToZenDeskImporter:
  '''
      Transfer articles, sections, and categories from an old ZenDesk Help Center to a New one.
  '''

  def __init__(self):
    #setup old zendesk client
    self.origin_brand = 'YourOldBrand'
    self.origin_zendesk = "https://{}.zendesk.com".format(self.origin_brand)
    self.sections = self.origin_zendesk + '/api/v2/help_center/en-us/sections.json'
    self.categories = self.origin_zendesk + '/api/v2/help_center/en-us/categories.json'
    self.origin_username = 'YourEmail' + '/token'
    self.origin_token = 'Origin_API_TOKEN'
    self.origin_credentials = (self.origin_username, self.origin_token) 

    
    #setup new zendesk client
    self.new_brand = 'YourNewBrand'
    self.zendesk_url = "https://{}.zendesk.com".format(self.new_brand)
    self.new_username = 'YourEmail' + '/token'
    self.new_token = 'New_API_Token'
    self.credentials = (self.new_username, self.new_token)

    #other stuff
    self.headers = {'content-type': 'application/json'}
    self.language = 'en-us'
    # keep track of sections we create in zendesk, to minimize the number of API requests
    self.local_sections = {}


  def post_articles(self):

    '''
        fetch articles from origin_brand and post them to new_brand
    ''' 
    url = "https://{}.zendesk.com/api/v2/help_center/en-us/articles.json".format(self.origin_brand)
    articles_list = []
    while url:
      response = requests.get(url, auth=self.origin_credentials)
      if response.status_code != 200:
        print('Status:', response.status_code, 'Problem with the request. Exiting.')
        exit()
      data = response.json()
      for article in data['articles']:
        articles_list.append(article)
      url = data['next_page']

    print "**POSTING ALL ARTICLES, one-by-one since Zendesk help center API won't do bulk"
    for article in articles_list:
      if not article['section_id']:
        print "SKIPPED ARTICLE %s, NO TOPIC" % article['title']
        continue
      if (article['draft'] is not False) :
      	print article['draft']
        print "SKIPPED ARTICLE in %s because it was unpublished" % article['section_id']
        continue

      section_id = None
      if article['section_id'] in self.local_sections:
        section_id = self.local_sections[article['section_id']]
      else:
        section_id = self.get_section_name(article['section_id'])
        if self.get_article_for_title(article['title'], section_id):
          print 'SKIPPED, %s already exists' % article['title']
          continue

      info = {
        'title': article['title'],
        'language': self.language,
        'position': article['position'],
        'body': article['body']
      }

      payload = json.dumps({'article': info})
      url = '{}/api/v2/help_center/sections/{}/articles.json'.format(self.zendesk_url, section_id)
      response = requests.post(url, data=payload, headers=self.headers, auth=self.credentials)
      if response.status_code != 200 and response.status_code != 201:
        print('FAILED to add article with error {}'.format(response.status_code))
        exit()
      else:
        print('ADDED ARTICLE {}'.format(response.json()['article']['title']))
        


  def get_article_for_title(self, title, section_id):
    '''
        returns the article id if their is an article for this title already
        returns None otherwise
    '''
 
    url = '{}/api/v2/help_center/sections/{}/articles.json'.format(self.zendesk_url, section_id)
    response = requests.get(url, headers=self.headers, auth=self.credentials)
    if response.status_code != 200:
      print('FAILED to get article list with error {}'.format(response.status_code))
      exit()
    articles = response.json()['articles']

    for article in articles:
      if article['title'] == title:
        return article['id']
    return None

  def get_section_name(self, section_id):
	response = requests.get(self.sections, auth=self.origin_credentials)
	if response.status_code != 200:
	  print('Status:', response.status_code, 'Problem with the request. Exiting.')
	  exit()
	data = response.json()
	sections_list = data['sections']
	for section in sections_list:
  	  if section['id'] == section_id:
  	  	name = section['name']
  	  	position = section['position']
  	  	category_name = self.get_category_name(section['category_id'])
  	  	category = self.get_or_create_category(category_name)
      	return self.create_or_get_section_id_for_name(name, position, category)

  def get_category_name(self, category_id):
	response = requests.get(self.categories, auth=self.origin_credentials)

	if response.status_code != 200:
	  print('Status:', response.status_code, 'Problem with the request. Exiting.')
	  exit()
	data = response.json()
	categories_list = data['categories']
	for category in categories_list:
		if category['id'] == category_id:
			category_name = category['name']
			return category_name

  def create_or_get_section_id_for_name(self, name, position, category):
    '''
        given a section name, return its id or creates a new section and return its id
    '''

    url = '{}/api/v2/help_center/categories/{}/sections.json'.format(self.zendesk_url, category)
    response = requests.get(url, headers=self.headers, auth=self.credentials)
    if response.status_code != 200:
      print('FAILED to get section list with error {}'.format(response.status_code))
      exit()
    data = response.json()
    sections_list = data['sections']
    for section in sections_list:
      if section['name'] == name:
        return section['id']
    return self.create_section(name, position, category)

  def create_section(self, name, position, category):
    '''
       create a section for a given name and return its id
    '''
    info = {
      'name': name,
      'position': position,
    }

    payload = json.dumps({'section': info})
    url = '{}/api/v2/help_center/categories/{}/sections.json'.format(self.zendesk_url, category)
    response = requests.post(url, data=payload, headers=self.headers, auth=self.credentials)
    if response.status_code != 201:
      print('FAILED to create section {} with error {}'.format(name, response.status_code))
      exit()
    section = response.json()['section']
    print('ADDED SECTION {}'.format(section['name']))
    self.local_sections[section['name']] = section['id']
    return section['id']


  def get_or_create_category(self, name):
    '''
        given a category name, return its id or creates a new category and return its id
    '''

    url = '{}/api/v2/help_center/categories.json'.format(self.zendesk_url)
    response = requests.get(url, headers=self.headers, auth=self.credentials)
    if response.status_code != 200:
      print('FAILED to get category list with error {}'.format(response.status_code))
      exit()
    categories = response.json()['categories']
    for category in categories:
      if category['name'] == name:
        return category['id']
    return self.create_category(name)
 
  def create_category(self, name):
    '''
       create a category for a given name and return its id
    '''

    info = {
      'name': name
    }
    payload = json.dumps({'category': info})
    url = '{}/api/v2/help_center/categories.json'.format(self.zendesk_url)
    response = requests.post(url, data=payload, headers=self.headers, auth=self.credentials)
    if response.status_code != 201:
      print('FAILED to create category {} with error {}'.format(name, response.status_code))
      exit()
    category = response.json()['category']
    print('ADDED CATEGORY {}'.format(category['name']))
    return category['id']


importer = ZendeskToZenDeskImporter()
importer.post_articles()
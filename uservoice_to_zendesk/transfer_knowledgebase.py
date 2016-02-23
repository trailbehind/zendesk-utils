#!/usr/bin/python

import uservoice
import requests, json, sys, re, time
from lxml.html import fromstring, tostring

class UserVoiceToZenDeskImporter:
  '''
      Import a UserVoice Knowledgebase to ZenDesk Help Center.
  '''

  def __init__(self):
    # get UV articles and topics to import
    uservoice_client = uservoice.Client(sys.argv[1], sys.argv[2], sys.argv[3])
    self.uv_user = uservoice_client.login_as_owner().get('/api/v1/users/current')
    self.articles = uservoice_client.get_collection('/api/v1/articles')
    self.topics = uservoice_client.get_collection('/api/v1/topics')
    
    # setup zendesk client
    self.zendesk_url = 'https://%s.zendesk.com' % sys.argv[4]
    self.credentials = sys.argv[5] + '/token', sys.argv[6]
    self.language = 'en-us'
    self.headers = {'Content-Type': 'application/json'}
    self.zendesk_destination_category_id = self.get_or_create_category(sys.argv[7])

    # map new articles to old ones, 
    # so we can rewrite the HTML of the articles in a second pass
    self.uvid_to_zdid = {}

    # keep track of sections we create in zendesk, to minimize the number of API requests
    self.local_sections = {}

  def post_articles(self):
    '''
        post uservoice articles to zendesk
    ''' 

    print "**POSTING ALL ARTICLES, one-by-one since Zendesk help center API won't do bulk"
    for article in self.articles:     
      if not article['topic'] or not article['topic']['name']:
        print "SKIPPED ARTICLE %s, NO TOPIC" % article['title']
        continue
      if not article['published']:
        print "SKIPPED ARTICLE in %s because it was unpublished" % article['topic']['name']
        continue

      section_id = None
      if article['topic']['name'] in self.local_sections:
        section_id = self.local_sections[article['topic']['name']]
      else:
        section_id = self.create_or_get_section_id_for_name(article['topic']['name'])
        if self.get_article_for_title(article['title'], section_id):
          print 'SKIPPED, %s already exists' % article['title']
          continue

      info = {
        'title': article['title'],
        'language': self.language,
        'position': article['position'],
        'body': article['formatted_text']
      }

      payload = json.dumps({'article': info})
      url = '{}/api/v2/help_center/sections/{}/articles.json'.format(self.zendesk_url, section_id)
      response = requests.post(url, data=payload, headers=self.headers, auth=self.credentials)
      if response.status_code != 200 and response.status_code != 201:
        print('FAILED to add article with error {}'.format(response.status_code))
        exit()
      else:
        print('ADDED ARTICLE {}'.format(response.json()['article']['title']))
        self.uvid_to_zdid[article['id']] = response.json()['article']['id']

  def update_zendesk_article_html(self):
    '''
    rewrite the html of zendesk articles 
    to point anchor tags at new zendesk articles, instead of old uservoice articles
    '''
    print "**UPDATING HTML to switch anchor hrefs to zendesk"
    url = '{}/api/v2/help_center/categories/{}/articles.json'.format(self.zendesk_url, self.zendesk_destination_category_id)

    articles = []
    while url:
      response = requests.get(url, headers=self.headers, auth=self.credentials)
      if response.status_code != 200:
        print('FAILED to get get article list with error {}'.format(response.status_code))
        exit()
      data = response.json()
      for article in data['articles']:
        articles.append(article)
      url = data['next_page']
      
    print "UPDATING HTML for {} articles".format(len(articles))
    for article in articles:
      url = "{}/api/v2/help_center/articles/{}.json".format(self.zendesk_url, article['id'])
      response = requests.get(url, headers=self.headers, auth=self.credentials)
      if response.status_code != 200:
        print('FAILED to update HTML for article {} with error {}'.format(article['id'], response.status_code))
        exit()
      html_doc = fromstring(article['body'])
      for anchor_tag in html_doc.cssselect('a'):
        if not anchor_tag.get('href'):
          continue
        number_from_string_regex = re.search('(\d+)', anchor_tag.get('href'))
        if not number_from_string_regex:
          continue
        uv_id = int(number_from_string_regex.group(0))
        if uv_id in self.uvid_to_zdid:
          url = "{}/api/v2/help_center/articles/{}.json".format(self.zendesk_url, self.uvid_to_zdid[uv_id])
          response = requests.get(url, headers=self.headers, auth=self.credentials)
          if response.status_code != 200:
            print('FAILED to get article {} with error {}'.format(self.uvid_to_zdid[uv_id], response.status_code))
            exit()
          new_url = response.json()['article']['html_url']
          try:
          	print('CHANGING {} to {}'.format(anchor_tag.get('href'), new_url))
          except:
          	e = sys.exc_info()[0]
          	print "lxml parsing error {}".format(e)
          anchor_tag.set('href', new_url)
          info = {
            'body': tostring(html_doc)
          }
          payload = json.dumps({'article': info})
          url = "{}/api/v2/help_center/articles/{}.json".format(self.zendesk_url, article['id'])
          response = requests.put(url, data=payload, headers=self.headers, auth=self.credentials)
          if response.status_code != 200:
            print('FAILED to update HTML for article {} with error {}'.format(article['id'], response.status_code))
            exit()
        else:
          print "SKIPPING this href {}".format(anchor_tag.get('href'))

  def delete_all_zendesk_articles(self, category):
    '''
        delete all articles in the category being filled with UV articles
        for our app, we had multiple uservoice knowledge bases, and each gets put in a zendesk category
    '''

    print "**DELETING ALL SECTIONS/ARTICLES in destination category {}".format(category)
    url = '{}/api/v2/help_center/categories/{}/sections.json'.format(self.zendesk_url, category)
    response = requests.get(url, headers=self.headers, auth=self.credentials)
    if response.status_code != 200:
      print('FAILED to delete articles with error {}'.format(response.status_code))
      exit()
    sections = response.json()['sections']
    section_ids=list(section['id'] for section in sections)

    for section_id in section_ids:
      url = "{}/api/v2/help_center/sections/{}.json".format(self.zendesk_url, section_id)
      response = requests.delete(url, headers=self.headers, auth=self.credentials)
      if response.status_code != 204:
        print('FAILED to delete sections for category {} with error {}'.format(category, response.status_code))
        exit()

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

  def create_or_get_section_id_for_name(self, name):
    '''
        given a section name, return its id or creates a new section and return its id
    '''

    url = '{}/api/v2/help_center/categories/{}/sections.json'.format(self.zendesk_url, self.zendesk_destination_category_id)
    response = requests.get(url, headers=self.headers, auth=self.credentials)
    if response.status_code != 200:
      print('FAILED to get section list with error {}'.format(response.status_code))
      exit()
    sections = response.json()['sections']
    for section in sections:
      if section['name'] == name:
        return section['id']
    return self.create_section(name)

  def create_section(self, name):
    '''
       create a section for a given name and return its id
    '''

    info = {
      'name': name
    }
    topic = next((x for x in self.topics if x['name'] == name), None)
    if topic['position']:
    	info['position'] = topic['position']

    payload = json.dumps({'section': info})
    url = '{}/api/v2/help_center/categories/{}/sections.json'.format(self.zendesk_url, self.zendesk_destination_category_id)
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


importer = UserVoiceToZenDeskImporter()
importer.delete_all_zendesk_articles(importer.zendesk_destination_category_id)
importer.post_articles()
importer.update_zendesk_article_html()
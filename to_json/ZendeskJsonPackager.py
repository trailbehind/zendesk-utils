import hmac, time, sys, os, re, csv, math, json, requests
from hashlib import sha1
from project_settings import *

class ZendeskJsonPackager:
  '''
      package zendesk help center articles into JSON
      utility for localization and pdification
  '''  

  def __init__(self):
    print("STARTING: fetching JSON from Zendesk for localization")
    self.zendesk_url = 'https://%s.zendesk.com/api/v2/help_center' % subdomain
    self.zendesk_session = requests.Session()
    self.zendesk_session.auth = (email+'/token', token)
    self.zendesk_session.headers = {'Content-Type': 'application/json'}

    self.package_zendesk_for_gengo_localization()
    

  def package_zendesk_for_gengo_localization(self):
    '''
        generate files based on Help Center articles and metadata
    '''
    self.make_directory("gen")
    self.gen_category_titles_json()
    self.gen_section_titles_json()
    self.gen_articles_json()


  def fetch_all_categories(self):
    '''
        fetch all categories from zendesk and return them as json
    '''
    if hasattr(self, 'categories'):
      return self.categories;
    else:
      print ("ZENDESK API: fetching categories")

    url = '{}/categories.json'.format(self.zendesk_url)
    response = self.zendesk_session.get(url)
    if response.status_code != 200:
      print('FAILED to get category list with error {}'.format(response.status_code))
      exit()
    self.categories = response.json()['categories']
    return self.categories


  def fetch_all_sections(self):
    '''
        fetch all sections from zendesk and return them as json
    '''
    if hasattr(self, 'sections'):
      return self.sections;
    else:
      print ("ZENDESK API: fetching sections")

    url = '{}/sections.json'.format(self.zendesk_url)
    response = self.zendesk_session.get(url)
    if response.status_code != 200:
      print('FAILED to get section list with error {}'.format(response.status_code))
      exit()
    self.sections = response.json()['sections']
    return self.sections


  def fetch_all_articles(self):
    '''
        fetch all articles from zendesk and return them as json
    '''
    if hasattr(self, 'articles'):
      return self.articles;
    else:
      print ("ZENDESK API: fetching articles: {}".format(self.zendesk_url))
   
    url = '{}/articles.json'.format(self.zendesk_url)
    self.articles = []
    self.articles_done_fetching = False;

    # page through all articles, 30 at a time
    while url:
      response = self.zendesk_session.get(url)
      if response.status_code != 200:
        print('FAILED to get article list with error {}'.format(response.status_code))
        exit()
      articles = response.json()['articles']
      for article in articles:
        self.articles.append(article)
      url = response.json()['next_page']
  
    self.articles_done_fetching = True;
    return self.articles;


  def gen_category_titles_json(self):
    '''
        generate a json file with zendesk category titles for build
        package a CSV for translation too
    '''
    categories = self.fetch_all_categories()
    json_dict = {}

    for category in categories:
      localize = False
      if category['id'] in DATA_CONFIG['included_categories']:
        localize = True
      json_dict[category['id']] = {'name':category['name'], 'localize': localize}

    with open('gen/category_names.json', 'w') as outfile:
      json.dump(json_dict, outfile)


  def gen_section_titles_json(self):
    '''
        generate a json file with zendesk section titles to be translated
    '''
    sections = self.fetch_all_sections()
    included_sections = self.included_sections()
    json_dict = {}
    
    # only include sections from whitelisted categories
    with open('gen/category_names.json', 'r') as category_file:
      category_dict = json.load(category_file)

    for section in sections:
      category_name = category_dict[str(section['category_id'])]['name']
      json_dict[section['id']] = {'localize':self.should_localize_section(section), 
                                  'name':section['name'], 
                                  'category_id':section['category_id'], 
                                  'category':category_name
                                 }

    with open('gen/section_names.json', 'w') as outfile:
      json.dump(json_dict, outfile)


  def should_localize_section(self, section):
    # only include sections from whitelisted categories
    with open('gen/category_names.json', 'r') as category_file:
      category_dict = json.load(category_file)

    included_sections = self.included_sections()
    localize = True
    if not section['id'] in included_sections:
      localize = False
    if not str(section['category_id']) in category_dict or not category_dict[str(section['category_id'])]['localize']:
      localize = False
    if section['name'] in DATA_CONFIG['unlocalized_words']:
      localize = False
    return localize


  def included_sections(self):
    '''
     include whitelisted sections,
     and sections that have an article to be translated
    '''
    included_sections = DATA_CONFIG['included_sections']
    for section_id in self.gen_missing_sections_for_articles():
      if not section_id in included_sections:
        included_sections.append(section_id)
    return included_sections


  def gen_missing_sections_for_articles(self):
    '''
       generate sections for whitelisted articles
    '''
    if hasattr(self, 'missing_section_ids'):
      return self.missing_section_ids;

    self.missing_section_ids = []
    articles = self.fetch_all_articles();
    for article in articles:
      section_id = str(article['section_id'])
      if article['id'] in DATA_CONFIG['blacklist_articles']:
        continue
      if article['id'] in DATA_CONFIG['whitelist_articles']:
        if not article['section_id'] in self.missing_section_ids:
          self.missing_section_ids.append(article['section_id'])
    return self.missing_section_ids;


  def gen_articles_json(self):
    '''
        generate a json list of articles, specifying whether to localize each one,
        and which category and section its in
    '''
    # create a dict to dump to file
    json_dict = {}
    # use these genned files to mark up files for translation
    with open('gen/category_names.json', 'r') as category_file:
      category_dict = json.load(category_file)
    with open('gen/section_names.json', 'r') as category_file:
      section_dict = json.load(category_file)

    for article in self.fetch_all_articles():
      section_id = str(article['section_id'])
      category_id = str(section_dict[section_id]['category_id'])
      if article['id'] in DATA_CONFIG['blacklist_articles']:
        continue
      if article['id'] in DATA_CONFIG['whitelist_articles']:
        True
      elif not section_dict[section_id]['localize']:
        continue
      elif not category_dict[category_id]['localize']:
        continue
      json_dict[article['id']] = {'title': article['title'], 
                                  'category': category_dict[category_id]['name'], 
                                  'category_id': category_id, 
                                  'section': section_dict[section_id]['name'], 
                                  'section_id': article['section_id'], 
                                  'section': section_dict[section_id]['name'], 
                                  'should_localize': True, 
                                  'html_url': article['html_url'],    
                                  'url': article['url']    }

    with open('gen/article_info.json', 'w') as outfile:
      json.dump(json_dict, outfile)


  def make_directory(self, new_dir):
    '''
       make a directory or complain it already exists
    '''
    try:
      os.mkdir(new_dir);
    except:
      print("WARNING: cant make directory '{}', already exists (probably OK)".format(new_dir))
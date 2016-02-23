import hmac, time, sys, os, re, csv, math, json, requests
from bs4 import BeautifulSoup
from hashlib import sha1
from project_settings import *
from ZendeskJsonPackager import ZendeskJsonPackager 


class ZenDeskLocalizer:
  '''
      package zendesk help center article for Gengo translation
      post translations to gengo and deploy results to zendesk
        1) all category and section names get translated
        2) only articles that are in both DATA_CONFIG.included_categories and DATA_CONFIG.included_sections get translated
        3) DATA_CONFIG.whitelist_articles get translated, even ignoring section/category restrictions in #2
        4) DATA_CONFIG.blacklist_articles never get translated
  '''  

  def __init__(self):
    self.zendesk_url = 'https://%s.zendesk.com/api/v2/help_center' % subdomain
    self.zendesk_session = requests.Session()
    self.zendesk_session.auth = (email+'/token', token)
    self.zendesk_session.headers = {'Content-Type': 'application/json'}
    
    self.gengo_headers = {"Accept": "application/json"}
    self.gengo_api_url = GENGO_API_URL
    
    self.word_count = 0 # count words to translate, to estimate cost


  def package_zendesk_for_gengo_localization(self):
    '''
        generate files based on Help Center articles and metadata,
        to post to gengo for translation
    '''
    self.json_packager = ZendeskJsonPackager()
    self.json_packager.make_directory("handoff")
    self.json_packager.package_zendesk_for_gengo_localization()
    
    self.json_packager.make_directory(TRANSLATION_RESPONSE_DIR)
    self.package_category_titles_csv()
    self.package_section_titles_csv()
    self.package_articles()

  def package_category_titles_csv(self):
    '''
        generate a cav file with zendesk category titles for translation
    '''
    categories = self.json_packager.fetch_all_categories()
    csv_file = open('handoff/category_names.csv','w')
    wr = csv.writer(csv_file, dialect='excel')
    url = "http://" + subdomain + ".zendesk.com/hc/en-us"
    translator_instructions = "[[[" + "NOTE FOR TRANSLATOR: These are category titles shown here: " + url + " ]]]"
    wr.writerow([translator_instructions])
    wr.writerow([])
    wr.writerow([self.escape_for_gengo('category name'),self.escape_for_gengo('explanation for translator'),self.escape_for_gengo('id')])

    # add explanation for translators
    with open('data/category_name_explanations.json', 'r') as category_file:
      category_explanations = json.load(category_file)

    # write each category to a CSV row, and escape untranslatable text for gengo
    for category in categories:
      localize = False
      if category['id'] in DATA_CONFIG['included_categories']:
        localize = True
      explanation = ""
      if str(category['id']) in category_explanations:
        explanation = self.escape_for_gengo(category_explanations[str(category['id'])]['translator_explanation'])
      category_id = self.escape_for_gengo(str(category['id']))
      if category['name'] in DATA_CONFIG['unlocalized_words']:
        wr.writerow([self.escape_for_gengo(category['name']),explanation, category_id])
      else:
        wr.writerow([category['name'],explanation, category_id])
        self.word_count += len(category['name'].split(" "))


  def package_section_titles_csv(self):
    '''
        generate a json file with zendesk section titles to be translated
    '''

    sections = self.json_packager.fetch_all_sections()

    # explanation for the translator to merge
    with open('data/section_name_explanations.json', 'r') as section_file:
      section_explanations = json.load(section_file)

    url = "http://" + subdomain + ".zendesk.com/hc/en-us/categories/" + str(sections[0]['category_id'])
    translator_instructions = "[[[" + "NOTE FOR TRANSLATOR: These are section titles like what is shown here: " + url + " ]]]"

    csv_file = open('handoff/section_names.csv','w')
    wr = csv.writer(csv_file, dialect='excel')
    wr.writerow([translator_instructions])
    wr.writerow([])
    wr.writerow([self.escape_for_gengo('section name'),self.escape_for_gengo('explanation for translator'),self.escape_for_gengo('id')])

    for section in sections:
      if self.json_packager.should_localize_section(section):
        wr.writerow([section['name'],
                     self.escape_for_gengo(section_explanations[str(section['id'])]['translator_explanation']),
                     self.escape_for_gengo(str(section['id']))])
        self.word_count += len(section['name'].split(" "))


  def delocalize_zendesk_hrefs(self):
    '''
        make sure all hrefs point at relative links, without localization in url
    '''
    self.json_packager = ZendeskJsonPackager()
    articles = self.json_packager.fetch_all_articles()
    for article in articles:
      url = 'https://{}.zendesk.com/api/v2/help_center/articles/{}/translations.json'.format(subdomain, article['id'])
      response = self.zendesk_session.get(url)
      for local_article in response.json()['translations']:
        clean_body = self.delocalize_hrefs(local_article['body'])
        if clean_body != BeautifulSoup(local_article['body'], "html.parser").prettify():
          data = {'translation': {'title': local_article['title'],
                                  'locale': local_article['locale'], 
                                  'body': clean_body
                                  }
                 }
          url = '{}/articles/{}/translations/{}.json'.format(self.zendesk_url, article['id'], local_article['locale'])
          response = self.zendesk_session.put(url, data=json.dumps(data))
          if response.status_code != 200:
            print('Status:', response.status_code, 'Problem with the post request. Exiting.')
            exit()
          print "updated {} {}".format(article['id'], local_article['locale'])          


  def delocalize_hrefs(self, html):
    '''
        https://myhelp.zendesk.com/hc/en-us/articles/216159817
        changes to
        /hc/articles/216159817
    '''
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all('a'):
      if not 'href' in tag.attrs:
        continue
      href = tag['href']
      if not 'hc/en-us/articles/' in href:
        continue
      base_url = 'https://%s.zendesk.com/' % subdomain
      href = href.replace(base_url, '/')
      href = href.replace('hc/en-us/articles/', 'hc/articles/')
      href = re.sub("(.*?)([0-9]{9}).*", self.trim_url, href)
      print "DELOCALIZED URL TO: " + href
      tag['href'] = href
    return soup.prettify()


  def trim_url(self, match):
    return match.group(1) + match.group(2)


  def package_articles(self):
    '''
        write a bunch of html files to a directory to feed to gengo API,
        and escape all the non-translatable tokens (html tags, "Company Name", etc) with [[[]]]
    '''
    with open('gen/section_names.json', 'r') as section_file:
      section_dict = json.load(section_file)
    with open('gen/article_info.json', 'r') as article_file:
      article_dict = json.load(article_file)

    article_count = 0
    origin_locale = 'en-us'
    for article_id in article_dict:
      url = 'https://{}.zendesk.com/api/v2/help_center/articles/{}/translations/{}.json'.format(subdomain, article_id, origin_locale)
      article = article_dict[article_id]
      response = self.zendesk_session.get(url)
      data = response.json()
      tree = BeautifulSoup('<html></html>', "html.parser")
      body = BeautifulSoup(data['translation']['body'], "html.parser")

      title = tree.new_tag('p')
      title.string = "[[[ NOTE TO TRANSLATOR - VIEW THIS PAGE AT:\n   " + data['translation']['html_url'] + '   ]]]'
      tree.html.append(title)

      title = tree.new_tag('h1')
      title.string = data['translation']['title']
      tree.html.append(title)

      tree.html.append(body)
      filename = '{}.html'.format(article_id)

      gengo_html = re.sub("<[^>]*>", self.escape_re_for_gengo, tree.prettify())
      gengo_html = re.sub("\d+\.", self.escape_re_for_gengo, gengo_html)
      for noun in DATA_CONFIG['proper_nouns']:
        gengo_html = re.sub(noun, self.escape_for_gengo(noun), gengo_html)
      
      word_delta = 0
      dont_count_substrings = ["]]]","[[[", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
      for noun in DATA_CONFIG['proper_nouns']:
        dont_count_substrings.append(noun)

      dont_count_matches = ["[", "*", "\n"]
      for word in re.split("[ ,]+", gengo_html):
        if not any(token in word for token in dont_count_substrings):
          if not word in dont_count_matches:
            word_delta += 1
      self.word_count += word_delta
      article_count += 1

      with open(os.path.join("handoff", filename), mode='w', encoding='utf-8') as f:
        f.write(gengo_html)
      print('{}\t\t{}/{} words\t\t{}\t\t"{}"'.format(article_count, word_delta, self.word_count, filename, data['translation']['title']))


  def get_language_pairs(self):
    '''
        you can inspect this response to see codes gengo uses for languages,
        the main pipeline doesn't use this method
    '''
    URL = "{}service/language_pairs".format(self.gengo_api_url)
    data = self.gengo_params()
    self.set_api_sig(data)
    get_language_pair = requests.get(URL, headers=self.gengo_headers, params=data)
    language_pair_json = self.handle_response(get_language_pair)
    print(language_pair_json)


  def post_jobs_to_gengo(self):
    '''
        post articles in /handoff to gengo
    '''
    URL = "{}jobs".format(self.gengo_api_url)
    data = self.gengo_params()
    self.set_api_sig(data)

    jobs = {}     
    article_count = 0
    source_dir = 'handoff/'

    for fn in os.listdir(source_dir):
      with open (source_dir+fn, 'r') as file_handle:
        article_count += 1
        slug = 'Translation {}'.format(article_count)
        src=file_handle.read()
        for locale in DATA_CONFIG['locales_to_translate']:
          job = {
            'slug': slug,
            'body_src': src,
            'lc_src': 'en',
            'lc_tgt': locale,
            'tier': 'standard',
            'auto_approve': 1
          }
          jobs[slug+locale] = job

    data["data"] = json.dumps({'jobs': jobs}, separators=(',', ':'))
    post_job = requests.post(URL, data=data, headers=self.gengo_headers)

    gengo_json = self.handle_response(post_job)
    with open(os.path.join("gen/", "gengo_order_status.json"), mode='w', encoding='utf-8') as f:
      f.write(json.dumps(gengo_json['response']))
  

  def retrieve_jobs_from_gengo(self):
    '''
        retrieve job status and and completed jobs,
        and write ranslated text to disk for later posting to zendesk
    '''
    filepath = 'gen/' + "gengo_order_status.json"
    with open (filepath, 'r') as file_handle:
       order_info = json.load(file_handle)
       print('retrieving order # {}'.format(order_info['order_id']))
    order_url = "{}order/{}".format(self.gengo_api_url, order_info['order_id'])
    data = self.gengo_params()
    self.set_api_sig(data)
    get_order = requests.get(order_url, params=data, headers=self.gengo_headers)
    gengo_json = self.handle_response(get_order)
    order_info = gengo_json['response']['order']
    with open('gen/article_info.json', 'r') as article_file:
      article_dict = json.load(article_file)
 
    for job in order_info['jobs_approved']:
      job_url = "{}job/{}".format(self.gengo_api_url, job)
      data = self.gengo_params()
      self.set_api_sig(data)
      get_order = requests.get(job_url, params=data, headers=self.gengo_headers)
      gengo_json = self.handle_response(get_order)['response']['job']
      try:
        os.mkdir( "{}{}".format(TRANSLATION_RESPONSE_DIR,gengo_json['lc_tgt']));
      except:
        print("gen already exists")

      if '[[[category name]]]' in gengo_json['body_src']:
        with open(os.path.join(TRANSLATION_RESPONSE_DIR, '{}/categories.csv'.format(gengo_json['lc_tgt'])), mode='w', encoding='utf-8') as f:
          csv_source = gengo_json['body_tgt'].replace('[[[','').replace(']]]','')
          f.write(csv_source)
      elif '[[[section name]]]' in  gengo_json['body_src']:
        with open(os.path.join(TRANSLATION_RESPONSE_DIR, '{}/sections.csv'.format(gengo_json['lc_tgt'])), mode='w', encoding='utf-8') as f:
          csv_source = gengo_json['body_tgt'].replace('[[[','').replace(']]]','')
          f.write(csv_source)
      else: 
        html_source = gengo_json['body_tgt'].replace('[[[','').replace(']]]','')
        tree = BeautifulSoup(html_source, "html.parser")

        # strip the translator advice
        first_p = tree.p.string.strip()
        tree.p.decompose()  
        article_id = re.findall("[0-9]{9}$", first_p)[0]

        with open(os.path.join(TRANSLATION_RESPONSE_DIR, '{}/{}.html'.format(gengo_json['lc_tgt'],article_id)), mode='w', encoding='utf-8') as f:
          f.write(tree.prettify())


  def update_zendesk_from_gengo_info(self):
    '''
        post files in gen/gengo_translations to zendesk help center
    '''
    for subdir, dirs, files in os.walk(TRANSLATION_RESPONSE_DIR):
      for locale in dirs:   
        locale_path = subdir + locale
        for fn in os.listdir(locale_path):
          filepath = locale_path + '/' + fn
          article_id, suffix = fn.split('.')
          if suffix == 'html':
            # its an article
            print('Reading {}/{} ...'.format(locale, fn))
            payload = self.create_zendesk_payload(locale, filepath)
            url = '{}/articles/{}/translations.json'.format(self.zendesk_url, article_id)
            response = self.zendesk_session.post(url, data=payload)
            if response.status_code == 400:
              print("translation exists, updating instead")
              url = '{}/articles/{}/translations/{}.json'.format(self.zendesk_url, article_id, locale)
              response = self.zendesk_session.put(url, data=payload)
              if response.status_code != 200:
                print('Status:', response.status_code, 'Problem with the post request. Exiting.')
                exit()
            elif response.status_code != 201:
              print('Status:', response.status_code, 'Problem with the post request. Exiting.')
              exit()
            else:
              print('Translation created successfully.')
          elif suffix == 'csv':
            datatype = article_id
            print('Posting {} {} {}'.format(filepath, datatype, locale))
            self.post_csv_to_zendesk(filepath, datatype, locale)


  def create_zendesk_payload(self, locale, file):
    '''
        strip metadata we added to the file for the pipeline,
        and package in a json dict for posting to zendesk
    '''
    with open(file, mode='r', encoding='utf-8') as f:
        html_source = f.read()
    tree = BeautifulSoup(html_source, "html.parser")
    title = tree.h1.string.strip()
    tree.h1.decompose()  # strip title we added for locaization
    data = {'translation': {'title': title, 'locale': locale, 'body': str(tree)}}
    return json.dumps(data)


  def post_csv_to_zendesk(self, filepath, datatype, locale):
    '''
        post translated category or section names to zendesk
    '''
    with open(filepath, encoding='utf-8', newline='') as f:
      etitle_reader = csv.reader(f, dialect='excel')
      row_count = 0
      for row in etitle_reader:
        row_count += 1
        if len(row) == 0 or row_count == 1:
          continue
        # row[0] = name, row[len(row)-1] = id
        url = '{}/{}/{}/translations.json'.format(self.zendesk_url, datatype, row[len(row)-1])
        data = {'translation': {'locale': locale, 'title': row[0]}}
        payload = json.dumps(data)
        response = self.zendesk_session.post(url, data=payload)
        print(url)
        print("Translation for locale '{}' created for section/category {}.".format(locale, row[len(row)-1]))


  def set_api_sig(self, data):
    '''
       use your private_key to create an hmac
    '''
    data["api_sig"] = hmac.new(
        str.encode(data["api_sig"]),
        str.encode(data["ts"]),
        sha1
    ).hexdigest()


  def gengo_params(self): 
    '''
       attach keys and timestamp to all gengo requests
    '''
    return {
        "api_key": GENGO_PUBLIC_KEY,
        "api_sig": GENGO_PRIVATE_KEY,
        "ts": str(int(time.time())) 
    }


  def handle_response(self, gengo_response):  
    '''
        returns json for a gengo request, or throws an error
    '''
    res_json = json.loads(gengo_response.text)
    if not res_json["opstat"] == "ok":
        msg = "API error occured.\nerror msg: {0}".format(
            res_json["err"]
        )
        raise AssertionError(msg)
    else:
        return res_json


  def escape_for_gengo(self, string):
    '''
       wrap some strings in brackets so gengo won't bill us and translators will ignore
    '''
    return "[[[{}]]]".format(string)


  def escape_re_for_gengo(self, match):
    '''
       use a regex to wrap some strings in brackets so gengo won't bill us and translators will ignore
    '''
    return "[[[{}]]]".format(match.group(0))


  def escape_re_for_gengo_with_space(self, match):
    '''
       use a regex to wrap some strings in brackets so gengo won't bill us and translators will ignore
       add a trailing space
    '''
    return "[[[{}]]] ".format(match.group(0))


zdl = ZenDeskLocalizer()
if sys.argv[1] == 'package':
  zdl.package_zendesk_for_gengo_localization()
elif sys.argv[1] == 'post':
  zdl.post_jobs_to_gengo()
elif sys.argv[1] == 'retrieve':
  zdl.retrieve_jobs_from_gengo()
elif sys.argv[1] == 'update':
  zdl.update_zendesk_from_gengo_info()
elif sys.argv[1] == 'delocalize_zendesk_hrefs':
  zdl.delocalize_zendesk_hrefs()
else:
  print("parameters are: package, post, retrieve, update")
# zendesk
subdomain = 'your_zendesk_domain'                
email = 'you@example.com'                       
token = ''                 

# gengo
GENGO_PUBLIC_KEY = ''
GENGO_PRIVATE_KEY = ''
GENGO_API_URL = 'http://api.gengo.com/v2/translate/'
TRANSLATION_RESPONSE_DIR = "gen/gengo_translations/"
    
GENGO_DEBUG = False
if GENGO_DEBUG:
  GENGO_PUBLIC_KEY = ''
  GENGO_PRIVATE_KEY = ''
  GENGO_API_URL = 'http://sandbox.gengo.com/v2/translate/'

DATA_CONFIG = {
  proper_nouns: [],
	included_categories: [],
	included_sections: [],
	whitelist_articles: [],
	blacklist_articles: [],
	locales_to_translate: []
  #locales_to_translate: ['zh-cn', 'zh-tw', 'nl', 'fr-fr', 'fr-CA', 'de', 'it', 'pt', 'pt-BR', 'ru', 'es-419', 'es-ES', 'sv', 'tr' ]  
}
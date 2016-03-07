'''
    zendesk config
'''
subdomain = 'your_zendesk_domain'                
email = 'you@example.com'                       
token = ''                 

'''
    gengo config
'''
GENGO_PUBLIC_KEY = ''
GENGO_PRIVATE_KEY = ''
GENGO_API_URL = 'http://api.gengo.com/v2/translate/'
TRANSLATION_RESPONSE_DIR = "gen/gengo_translations/"
    
GENGO_DEBUG = False
if GENGO_DEBUG:
  GENGO_PUBLIC_KEY = ''
  GENGO_PRIVATE_KEY = ''
  GENGO_API_URL = 'http://sandbox.gengo.com/v2/translate/'

S3_BUCKET_FOR_MANUAL = ''
S3_ACCESS_KEY_FOR_MANUAL = ''
S3_SECRET_KEY_FOR_MANUAL = ''

'''
   settings for look and feel of cover
   point these at your images to customize the PDF cover pages
'''
# 8.5 x 11 image
BACKGROUND_IMAGE_PATH = './data/images/background.png'

# n X 11 image
BANNER_IMAGE_PATH = './data/images/logo-banner.jpg'

# small square image (~72px)
ICON_IMAGE_PATH = './data/images/app-icon.png'

'''
    the object the code refers to a lot
    configure this for your project
'''

DATA_CONFIG = {
  category_blacklist_for_pdfs: [],
  proper_nouns: [],
	included_categories: [],
	included_sections: [],
	whitelist_articles: [],
	blacklist_articles: [],
	locales_to_translate: []
  #locales_to_translate: ['zh-cn', 'zh-tw', 'nl', 'fr-fr', 'fr-CA', 'de', 'it', 'pt', 'pt-BR', 'ru', 'es-419', 'es-ES', 'sv', 'tr' ]  
}
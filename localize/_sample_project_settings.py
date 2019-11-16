'''
    zendesk config
'''
ZENDESK_SUBDOMAIN = 'your_zendesk_domain'
ZENDESK_EMAIL = 'you@example.com'
ZENDESK_TOKEN = ''

URL_LIST_CATEGORIES = None

'''
    gengo config
'''
GENGO_PUBLIC_KEY = ''
GENGO_PRIVATE_KEY = ''
GENGO_API_URL = 'http://api.gengo.com/v2/translate/'
TRANSLATION_RESPONSE_DIR = "gen/gengo_translations/"

'''
    gengo sandbox config
'''
GENGO_DEBUG = False
if GENGO_DEBUG:
  GENGO_PUBLIC_KEY = ''
  GENGO_PRIVATE_KEY = ''
  GENGO_API_URL = 'http://sandbox.gengo.com/v2/translate/'

'''
    select articles/words/sections/categories to translate
'''
DATA_CONFIG = dict(
  unlocalized_words = [],            # REQUIRED
  locales_to_translate = [],         # REQUIRED
  category_blacklist_for_pdfs = [],  # config if batch localizing
  included_categories = [],          # config if batch localizing
  included_sections = [],            # config if batch localizing
  whitelist_articles = [],           # config if batch localizing
  blacklist_articles = [],           # config if batch localizing
)
# EXAMPLE locales_to_translate: ['zh-cn', 'zh-tw', 'nl', 'fr-fr', 'fr-CA', 'de', 'it', 'pt', 'pt-BR', 'ru', 'es-419', 'es-ES', 'sv', 'tr' ]


'''
   NOT NEEDED FOR LOCALIZATION
   settings for look and feel of cover
   point these at your images to customize the PDF cover pages
'''
S3_BUCKET_FOR_MANUAL = ''
S3_ACCESS_KEY_FOR_MANUAL = ''
S3_SECRET_KEY_FOR_MANUAL = ''

# 8.5 x 11 image
BACKGROUND_IMAGE_PATH = '/data/images/background.png'

# n X 11 image
BANNER_IMAGE_PATH = '/data/images/logo-banner.jpg'

# small square image (~72px)
ICON_IMAGE_PATH = '/data/images/app-icon.png'

SLACK_NOTIFICATION_URL = None
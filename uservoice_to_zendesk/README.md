# Overview

This script migrates a UserVoice KnowledgeBase, housing it as a category in a ZenDesk Help Center.

### href Migration

It migrates the intra-knowledgebase hrefs in the articles as you'd expect.

### img Migration

It doesn't touch the img src links, leaving those on UserVoice and elsewhere.

# Setup

    pip install uservoice
    pip install requests

# Usage

    python transferknowledgebase.py {uv_subdomain} {uv_api_key} {uv_api_secret} {zd_subdomain} {zd_email} {zd_api_token} {zd_destination_category_name}

# Updating the Script

Read up on the zendesk rest API and python examples to learn to edit the script.

```
sample dict to move from UserVoice

{
'formatted_text': '<img src="https://foobar.uservoice.com/assets/91625817/SwipeUp.jpg"> 
'title': 'eh', 
'position': 2, 
'topic': {'id': 32361, 'name': 'Manaacks'},
'updated_by': {'name': 'Ain', 'title': 'Adventurport', 'url': 'http://foobar.uservoice.com/users/-ain', 'created_at': '2015/08/31 16:25:21 +0000', 'updated_at': '2016/01/06 12:44:17 +0000', 'id': 99331452, 'avatar_url': 'https://secure.gravatar.com/avatar/6da6d5ce7bd589a68c119.png', 'karma_score': 0, 'email': 'ain@foobar.com'}, 'title': 'Troubleshooting', 'url': 'http://foobar.uservoice.com/knowledgebase/articles/171267-troubleshooting', 'text': "Troubleshooting\n\n  If foobar can't locate a GPS signal, follow these instructions to make sure location services are turned on.not work if you are in a car or if you are near metal or\n    magnetic things.\n  \n\n  &nbsp;", 'created_at': '2013/02/26 01:05:14 +0000', 'question': 'Troubleshooting', 'updated_at': '2015/11/30 06:33:33 +0000', 'answer_html': '<h1>Troubleshooting<br></h1>\n\n  <br>If foobar can\'t locate a GPS signal, <a href="http://help.foobar.com/knowledgebase/articles/171276-gisn-t-lo">follow these instructions</a> to make sure location services are turned on.<br>\n\n\n\n\n\n\n\n<p class="p1"><span class="s1">If location services are turned on, force close the app completely by double tapping the Home button and then swiping up the  GPS window.</span></p><br><span><img src="https://foobar.uservoice.com/assets/91625817/SwipeUp.jpg"></span><br>\n\n            <br>If shutting down the app doesn\'t work, try restarting your\n    phone.<br><br><br>Please note:\n\n  <ul>\n    <li>The compass will not work if you are in a car or if you are near metal or\n    magnetic things.</li>\n  </ul>\n\n  <p>&nbsp;</p><div></div>', 'topic': {'id': 28921, 'name': 'Troubleshooting'}, 
'uses': 7, 
'published': True, 
'instant_answers': 4, 
'path': '/knowledgebase/articles/171267-troubleshooting', 
'id': 171267
}


sample dict to create on ZenDesk

{
body:  '<img src="https://foobar.zendesk.com/hc/en-us/article_attachments/204747168/add_sources_1.jpg">
name:  'Adding and Managing Map Sources', 
title: 'Adding and Managing Map Sources', 
url:   'https://foobar.zendesk.com/api/v2/help_center/en-us/articles/216117167-Adding-and-Managing-Map-Sources.json', u'vote_sum': 0, u'created_at': u'2016-01-06T16:32:38Z', u'source_locale': u'en-us', u'comments_disabled': True, u'html_url': u'https://foobar.zendesk.com/hc/en-us/articles/2161d7r67-Adding-and-Managing-Map-Sources',
u'updated_at': u'2016-01-06T18:39:59Z', 
u'section_id': 203d37127, 
u'label_names': [], 
u'locale': u'en-us',
u'vote_count': 0, 
u'draft': False, 
u'promoted': False, 
u'position': 0, 
u'author_id': 392d70d078, 
u'outdated': False, 
u'id': 216dd167
}
```
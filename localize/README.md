# Localizing Zendesk Help Center

## Install Requirements

    brew install python3
    pip install -r requirements.txt    
    export PYTHONPATH=$PYTHONPATH:../localize:../to_json

## Config Gengo and Zendesk

    cp _sample_project_settings.py project_settings.py

## Config for One Article at a Time

To do one article at a time, you should configure these settings:

 * GENGO_PUBLIC_KEY 
 * GENGO_PRIVATE_KEY
 * ZENDESK_EMAIL
 * ZENDESK_SUBDOMAIN
 * ZENDESK_TOKEN
 * DATA_CONFIG = { unlocalized_words: [], 'locales_to_translate': [] }

## Config for Batch Localizing Articles/Sections/Categories

If you want to do more than one article at a time, set up the rest of DATA_CONFIG in project_settings.py.

## Usage

Retrieve one article from ZenDesk, and package to send to Gengo:

    python3 ZenDeskLocalizer.py package-article ZENDESK_ID    

Retrieve a batch of articles based on project_settings.py files from ZenDesk, and package to send to Gengo:

    python3 ZenDeskLocalizer.py package    

Post to Gengo:

    python3 ZenDeskLocalizer.py post    

Check your dashboard on Gengo for the order to complete (can take days), then retrieve the files:

    python3 ZenDeskLocalizer.py retrieve    

Post the translations to  ZenDesk:

    python3 ZenDeskLocalizer.py update    

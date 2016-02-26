# Localizing Zendesk Help Center

## Config

    cp _sample_project_settings.py project_settings.py

Update project_settings.py with your:

 * zendesk creddentials
 * gengo credentials
 * locales, articles, sections, and categories to localize 

## Install Requirements

    pip install -r requirements.txt    
    export PYTHONPATH=$PYTHONPATH:../localize:../to_json

## Usage

Retrieve files from ZenDesk, and package to send to Gengo:

    python ZenDeskLocalizer.py package    

Post to Gengo:

    python ZenDeskLocalizer.py post    

Check your dashboard on Gengo for the order to complete (can take days), then retrieve the files:

    python ZenDeskLocalizer.py retrieve    

Post the translations to  ZenDesk:

    python ZenDeskLocalizer.py update    


## Future  Work

  * schedule multiple jobs at once
  * localize the screenshots too
  * config/constants for handoff and gen directories

# Install wkhtmltopdf

Because the pip install didn't work for me, install a static binary from http://wkhtmltopdf.org/

Install other Python requirements

    pip install -r requirements.txt
    export PYTHONPATH=$PYTHONPATH:/PATH_TO_REPO/zendesk_utils/localize:/PATH_TO_REPO/zendesk_utils/to_json

# Config

If you didn't already do this using this localize script, you need to clone and update the config file.

    cp ../localize/_sample_project_settings.py ../localize/project_settings.py

# Generate PDFs

    python ZendeskPDFMaker.py create  
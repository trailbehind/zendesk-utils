# Install wkhtmltopdf

Because the pip install didn't work for me, install a static binary from http://wkhtmltopdf.org/

Install other Python requirements

    pip install -r requirements.txt
    export PYTHONPATH=$PYTHONPATH:..

# Config

If you didn't already do this using this localize script, you need to clone and update the config file.

    cp ../localize/_sample_project_settings.py ../localize/project_settings.py

# Install Chinese Fonts (if on Ubuntu Linux, Mac has these by default)

Thanks for help from [this blog post](http://cnedelcu.blogspot.com/2015/04/wkhtmltopdf-chinese-character-support.html).

    apt-get install fonts-wqy-microhei ttf-wqy-microhei fonts-wqy-zenhei ttf-wqy-zenhei 

Note: package names might be different if you aren't under Ubuntu (try apt-cache search ... to search for packages)
Then, run this command to update the font cache:

    fc-cache -f -v

# Generate and Post PDFs

    python ZendeskPDFMaker.py create  
    python ZendeskPDFMaker.py post 

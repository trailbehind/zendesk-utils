#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import datetime
import json
import os
import sys
import time
from subprocess import check_output
from urllib.parse import urljoin

import boto3
import localize.project_settings as settings
import pdfkit
import requests
from bs4 import BeautifulSoup
from to_json.ZendeskJsonPackager import ZendeskJsonPackager

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
ZENDESK_UTIL_DIR = os.path.abspath(os.path.join(FILE_DIR, ".."))


class ZendeskPDFMaker:

    """
      package zendesk help center articles into a PDF
  """

    def create_pdfs(self):
        """
        generate PDF files based on Help Center articles and metadata
    """

        # make PDFs for each category except blacklisted categories
        self.blacklist_categories = settings.DATA_CONFIG["category_blacklist_for_pdfs"]

        # set these to 1 or 2 for testing
        self.max_section_count = sys.maxsize
        self.max_article_count = sys.maxsize

        self.json_packager = ZendeskJsonPackager()
        self.json_packager.make_directory("gen")
        self.json_packager.make_directory("gen/pdf")
        self.json_packager.package_zendesk_for_gengo_localization()
        self.create_pdf_files()

    def create_pdf_files(self):
        """
        create PDFs from help center locales
    """
        with open("gen/category_names.json", "r") as category_file:
            category_dict = json.load(category_file)

        for category_id in category_dict:
            category_name = category_dict[category_id]["name"]
            if category_name in self.blacklist_categories:
                print("Skipping PDF for category: " + category_name)
                continue
            print("MAKING PDF FOR CATEGORY: " + category_name)
            url = "{}/categories/{}/translations.json".format(
                self.json_packager.zendesk_url, category_id
            )
            print(url)
            response = self.json_packager.zendesk_session.get(url)
            if response.status_code != 200:
                print(
                    "FAILED to get category localization info with error {}".format(
                        response.status_code
                    )
                )
                exit()
            category_info = response.json()["translations"]
            for locale_info in category_info:
                # zendesk has odd tastes in adding fr and fr-fr
                if locale_info["locale"] == "fr-fr":
                    continue
                self.create_manual(category_id, category_name, locale_info["locale"])

    def create_manual(self, category_id, category_name, locale):
        """
        create a PDF for a given category and locale of a Zendesk Help Center
    """
        article_list = self.json_packager.fetch_all_articles()
        sections = self.json_packager.fetch_all_sections()
        pdf_story = (
            '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'
        )
        pdf_story += "<style>body { font-size: 1.7em }</style>\n"
        section_count = 0
        for section in sections:
            if str(section["category_id"]) == category_id:
                article_count = 0
                for article in article_list:
                    if article["section_id"] == section["id"]:
                        translation = self.translation_for_article(
                            article["id"], locale
                        )
                        if not translation or not translation["body"]:
                            continue
                        pdf_story = self.append_article_to_pdf_html(
                            article_count,
                            pdf_story,
                            translation["title"],
                            translation["body"],
                            self.localized_name_for_section(section, locale),
                        )
                        article_count += 1
                        # only gets used for short, test runs
                        if article_count == self.max_article_count:
                            break
                # only gets used for short, test runs
                section_count += 1
                if section_count == self.max_section_count:
                    break

        with codecs.open(
            os.path.join(FILE_DIR, "data/local_manual_titles.json"),
            "r",
            encoding="utf-8",
        ) as local_manual_titles:
            local_title_dict = json.load(local_manual_titles)

        with open(
            os.path.join(FILE_DIR, "data/localized_toc_titles.json"),
            "r",
            encoding="utf-8",
        ) as local_toc_titles:
            local_toc_dict = json.load(local_toc_titles)

        with open(
            os.path.join(FILE_DIR, "data/pdf_story.html"), "w", encoding="utf-8"
        ) as html_story_doc:
            html_story_doc.write(pdf_story)

        pdfkit.from_string(
            pdf_story,
            os.path.join(ZENDESK_UTIL_DIR, "gen/pdf/{}-{}.pdf").format(
                category_name, locale
            ),
            toc=self.table_of_contents_dict(local_toc_dict[locale]),
            cover=self.path_for_created_cover(local_title_dict[locale]),
            options=self.wkhtmltopdf_options(),
        )

    def translation_for_article(self, article_id, locale):
        """
       fetch and return the translation dict for an article from Zendesk
    """
        url = (
            self.json_packager.zendesk_url
            + "/articles/{}/translations/{}.json".format(article_id, locale)
        )
        response = self.json_packager.zendesk_session.get(url)
        try:
            return response.json()["translation"]
        except KeyError:
            # not localized
            return None

    def append_article_to_pdf_html(
        self,
        article_count,
        pdf_story,
        localized_title,
        localized_body,
        localized_section_name,
    ):
        """
        add a header and article and return the updated html for the pdf
    """
        soup = self.clean_soup_for_printing(
            BeautifulSoup(localized_body, "html.parser")
        )
        if article_count == 0:
            pdf_story += (
                '<h1 style="page-break-before:always;font-size:1em">'
                + localized_section_name
                + "</h1>"
            )
        else:
            pdf_story += (
                '<strong style="display:block;page-break-before:always">'
                + localized_section_name
                + "</strong>"
            )
        pdf_story += "<h2>" + localized_title + "</h2>"
        pdf_story += soup.prettify()
        return pdf_story

    def localized_name_for_section(self, section, locale):
        url = "{}/sections/{}/translations.json".format(
            self.json_packager.zendesk_url, section["id"]
        )
        response = self.json_packager.zendesk_session.get(url)
        if response.status_code != 200:
            print(
                "FAILED to get section localization info with error {}".format(
                    response.status_code
                )
            )
            exit()
        sections = response.json()["translations"]
        localized_section_name = section["name"]
        for section_info in sections:
            if section_info["locale"] == locale:
                localized_section_name = section_info["title"]
        return localized_section_name

    def clean_soup_for_printing(self, soup):

        # makes wkhtmltopdf faster to render
        [s.extract() for s in soup(["iframe", "script"])]
        for tag in soup():
            for attribute in ["class", "id", "alt", "style", "target"]:
                del tag[attribute]

        # this might make it faster too
        for match in soup.find_all(["span", "font"]):
            match.unwrap()

        # make img src urls absolute so images render
        # make hrefs absolute so clicking works
        return self.make_urls_absolute(soup, self.json_packager.zendesk_url)

    def make_urls_absolute(self, soup, url):
        """
        pdfkit needs absolute urls
    """
        for tag in soup.find_all("a"):
            if isinstance(tag, list):
                for sub_tag in tag:
                    if "href" in tag and tag["href"].startswith("/"):
                        tag["href"] = urljoin(url, tag["href"])
            else:
                if "href" in tag and tag["href"].startswith("/"):
                    tag["href"] = urljoin(url, tag["href"])
        for tag in soup.find_all("img"):
            tag["src"] = urljoin(url, tag["src"])
        return soup

    def path_for_created_cover(self, localized_title):
        """
        generate an html file for a cover for the PDF, and return the path
    """
        cover_html_path = "gen/cover.html"
        cover_html = (
            '<h1 style="font-size:4em;z-index:1;margin-top:50%;margin-left:20px;color:white;position:absolute"> '
            + localized_title
            + "</h1>"
        )
        date = "{:%b %d, %Y}".format(datetime.date.today())

        bg_image_path = os.path.join(ZENDESK_UTIL_DIR, settings.BACKGROUND_IMAGE_PATH)
        banner_image_path = os.path.join(ZENDESK_UTIL_DIR, settings.BANNER_IMAGE_PATH)
        icon_image_path = os.path.join(ZENDESK_UTIL_DIR, settings.ICON_IMAGE_PATH)

        cover_html += (
            "\n"
            + '<h1 style="z-index:1;color:lightgray;position:absolute;bottom:18px;right:112px">'
            + date
            + "</h1>"
        )
        cover_html += (
            "\n"
            + '<img style="position:absolute; height:100%" src="{}" />'.format(
                bg_image_path
            )
        )
        cover_html += "\n" + '<img style="position:absolute" src="{}" />'.format(
            banner_image_path
        )
        cover_html += (
            "\n"
            + '<img style="position:absolute; bottom:20px; right:20px; width:72px" src="{}" />'.format(
                icon_image_path
            )
        )

        with open(cover_html_path, "w") as outfile:
            outfile.write(cover_html)
        return cover_html_path

    def table_of_contents_dict(self, toc_title):
        """
        generate an xsl file for a ToC for the PDF, and return the path wrapped in a dict for wkhtmltopdf
    """
        toc_xsl_path = os.path.join(ZENDESK_UTIL_DIR, "gen/toc.xsl")

        with open(toc_xsl_path, "wb") as outfile:
            toc_xsl = check_output(["wkhtmltopdf", "--dump-default-toc-xsl"])
            soup = BeautifulSoup(toc_xsl, "html.parser")
            for tag in soup.find_all("h1"):
                tag.string = toc_title
            soup.find_all("style")[0].append("ul { font-size: 1.7em }\n")
            outfile.write(soup.prettify().encode("utf-8"))
        return {"xsl-style-sheet": toc_xsl_path}

    def wkhtmltopdf_options(self):
        """
        some options to style the generated PDF
    """
        return {
            "page-offset": "-1",
            "margin-top": "0.75in",
            "margin-right": "0.75in",
            "margin-bottom": "0.75in",
            "margin-left": "0.75in",
            "footer-right": "[page]",
        }

    def percent_cb(self, complete, total):
        sys.stdout.write("{}/{}\n".format(complete, total))
        sys.stdout.flush()

    def post_pdfs_to_s3(self):
        s3_client = boto3.client("s3")

        bucket_name = settings.S3_BUCKET_FOR_MANUAL
        bucket_dir = settings.S3_DIRECTORY_FOR_MANUAL
        source_dir = os.path.join(ZENDESK_UTIL_DIR, "gen/pdf/")
        print("posting pdfs from %s" % source_dir)
        section_dict = {}
        for fn in os.listdir(source_dir):
            print(source_dir + fn)

            chunks = fn.split("-")
            category = chunks[0]

            filename = chunks[0] + "/" + chunks[1] + "-" + chunks[2]
            print(filename)
            print(bucket_name)
            if category not in section_dict:
                section_dict[category] = ""
            section_dict[
                category
            ] += '<tr><td style="padding-right:10px;padding-bottom:5px"><a href=http://{}/{}/{}/{}>{}</a></td><td>http://{}/{}/{}/{}</td></tr>'.format(
                bucket_name,
                bucket_dir,
                category,
                filename,
                filename,
                bucket_name,
                bucket_dir,
                category,
                filename,
            )
            filename = bucket_dir + "/" + filename
            filepath = source_dir + fn
            print(filepath)
            s3_client.upload_file(
                filepath,
                bucket_name,
                filename,
                ExtraArgs={"ContentType": "application/pdf"},
            )

            print("POSTING PDF to S3: " + filename)

        # self.post_inventory_html(section_dict, bucket_name)

    def post_inventory_html(self, section_dict, bucket_name):
        manual_urls = "<h1>{}</h1>".format("Manual PDFs")

        for category in section_dict:
            if (
                settings.URL_LIST_CATEGORIES is None
                or category in settings.URL_LIST_CATEGORIES
            ):
                manual_urls += "<h2>{}</h2>".format(category)
                manual_urls += "<table>"
                manual_urls += section_dict[category]
                manual_urls += "</table>"
        date = time.strftime("%l:%M%p %Z on %b %d, %Y")
        manual_urls += '<h3 style="color:gray"><em>Last Updated: {}</em></h3>'.format(
            date
        )

        with open(os.path.join(ZENDESK_UTIL_DIR, "gen/url_list.html"), "w") as url_file:
            url_file.write(manual_urls)
        with open(os.path.join(ZENDESK_UTIL_DIR, "gen/url_list.html"), "r") as url_file:
            filename = settings.S3_DIRECTORY_FOR_MANUAL + "/url_list.html"
        #   s3_client.upload_file(url_file, bucket_name, filename)

        print("POSTED inventory html to S3 at: " + bucket_name + filename)

    def ping_slack(self):
        payload = "Manual generation finished, see: http://{}/{}/url_list.html".format(
            settings.S3_BUCKET_FOR_MANUAL, settings.S3_DIRECTORY_FOR_MANUAL
        )
        requests.post(settings.SLACK_NOTIFICATION_URL, data=payload)


def print_usage():
    print("\nparameters are: create, post, ping_slack, run\n")


zdpm = ZendeskPDFMaker()
if len(sys.argv) < 2:
    print_usage()
    sys.exit(2)

if sys.argv[1] == "create":
    zdpm.create_pdfs()
elif sys.argv[1] == "post":
    zdpm.post_pdfs_to_s3()
elif sys.argv[1] == "ping_slack":
    zdpm.ping_slack()
elif sys.argv[1] == "run":
    zdpm.create_pdfs()
    zdpm.post_pdfs_to_s3()
    if settings.SLACK_NOTIFICATION_URL:
        zdpm.ping_slack()
else:
    print_usage()

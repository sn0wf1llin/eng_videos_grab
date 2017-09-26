__author__ = 'MA573RWARR10R'
# -*- coding: utf-8 -*-

import requests
import re
import os
from bs4 import BeautifulSoup
import urllib.request

username = "valerina99@mail.ru"
password = "4646"
base_url = "http://cabinet.gettrenings.ru/"
login_url = base_url
user_cabinet = "http://cabinet.gettrenings.ru"
login_data = {'login': username, 'passw': password}


class SiteGrabber:
    def __init__(self, user=None, passw=None):
        self.is_auth = False
        self.session = requests.Session()
        if user is not None and passw is not None:
            self.set_user(user, passw)
        else:
            self.username = user
            self.password = passw

    def set_user(self, user, passw):
        self.username = user
        self.password = passw

        if self.login():
            self.is_auth = True

    def login(self, post_url=login_url, post_data=login_data):
        if not self.is_auth:
            response = self.session.post(post_url, post_data)
            self.is_auth = True
        else:
            response = self.session.get(base_url)

        if response.status_code == 200:
            return True

        return False

    def get_page(self, page_url):
        try:
            return self.session.get(page_url).content
        except Exception as e:
            print("Error %s" % e)
            if self.login():
                return self.session.get(page_url).content

    """
        there is special for current site grabber realization
        in the bottom

        more universal is in the top
    """

    def reanimate_cookies_on_page(self, page):
        context = self.get_page(page)
        soup = BeautifulSoup(context, "html.parser")

        return soup

    def _get_open_unit_urls(self, page_soup):
        unit_urls = set()
        for unit_o in page_soup.find('div', {'class': "pagenav"}).find_all('div', {'class': "unit_open"}):
            unit_urls.add(unit_o.find('a')['href'])
        try:
            unit_work_uno = page_soup.find('div', {'class': "pagenav"}).find('div', {'class': "unit_work"})

        except Exception as e:
            print("Not added! \nCookies dead! \nMake them alive again!\n%s" % e)
            soup = self.reanimate_cookies_on_page(user_cabinet)
            unit_work_uno = soup.find('div', {'class': "pagenav"}).find('div', {'class': "unit_work"})

        unit_urls.add(unit_work_uno.find('a')['href'])

        return unit_urls

    @staticmethod
    def _save_parsed_lessons_info(mdata_list, filename="saved_lessons_info.txt"):
        with open(filename, "w") as f:
            for unit in mdata_list:
                for lesson_info in unit:
                    for i in lesson_info:
                        f.write(i)
                        f.write("\n")
                    f.write("___________________\n")
        print("saved successfully!")

    @staticmethod
    def _save_link_as_parsed(link):
        with open('parsed_lesson_urls.txt', 'a') as f:
            f.write(link)

    @staticmethod
    def _get_parsed_lesson_videos(filename='parsed_lesson_urls.txt'):
        parsed = []
        try:
            with open(filename, 'r') as f:
                for href_ in f.readlines():
                    parsed.append(href_)
        except FileNotFoundError:
            return []

        return parsed

    def _get_lessons_urls(self, unit_url):
        recently_parsed = self._get_parsed_lesson_videos(unit_url)

        page = self.get_page(base_url + unit_url)

        unit_soup = BeautifulSoup(page, "html.parser")

        unit_data = []

        if unit_soup.find('div', {'class': "pagenav"}) is None:
            unit_soup = self.reanimate_cookies_on_page(user_cabinet)

        for lesson in unit_soup.find_all('div', {'id': "less_cont_left"}):
            if lesson.find('a') is not None:
                lesson_video_link = lesson.find('a')['href']

                if lesson_video_link not in recently_parsed:
                    lesson_name = lesson.find('a').text
                    new_lln = [lesson_video_link, lesson_name]

                    video_open_page = self.get_page(base_url + lesson_video_link)
                    video_page_soup = BeautifulSoup(video_open_page, "html.parser")

                    if video_page_soup.find('video', {'id': "video"}) is None:
                        "cookies dead again\n"
                        video_page_soup = self.reanimate_cookies_on_page(base_url + lesson_video_link)

                    try:
                        video_href = video_page_soup.find('source')['src']
                    except TypeError:
                        video_href = "not a video"

                    new_lln.append(video_href)
                    print('success')

                    self._save_link_as_parsed(lesson_video_link)
                    print("saved as parsed %s" % lesson_video_link)

                    unit_data.append(new_lln)

                else:
                    pass
            else:
                pass

        return unit_data

    def _get_unit_data(self, context):
        soup = BeautifulSoup(context, "html.parser")

        if soup.find('div', {'class': "pagenav"}) is None:
            soup = self.reanimate_cookies_on_page(user_cabinet)

        unit_urls = self._get_open_unit_urls(soup)

        """
            save parsed hrefs to a file, to avoid parsing them again
        """

        """
            write open unit urls to a file
        """
        with open('open_unit_urls.txt', 'w') as f:
            for href in unit_urls:
                f.write(href)
                f.write("\n")

        all_data = []
        while True:
            hr = unit_urls.pop()
            unitdata = self._get_lessons_urls(hr)
            all_data.append(unitdata)

            if len(unit_urls) == 0:
                break
                # except Exception as e:
                #     print("\t\t\tadded again %s" % hr)
                #     unit_urls.add(hr)

        self._save_parsed_lessons_info(all_data)


def get_unit_lesson(non_formatted_line):
    unum = non_formatted_line.split("&")[1].split("=")[1]
    lnum = clean_text(non_formatted_line.split("&")[2].split("=")[1])
    return unum, "lesson" + str(lnum)


def clean_text(text):
    return re.sub('[^A-Za-z0-9]+', '', text)


def download_video_by_link(link, lesson_name, store_path):
    vname = store_path + "/" + lesson_name + ".mp4"

    try:
        urllib.request.urlretrieve(link, vname)
        return True
    except Exception:
        pass


def main():
    # sgrab = SiteGrabber(username, password)
    #
    # main_cabinet_page = sgrab.get_page(user_cabinet).decode('utf-8')
    #
    # sgrab._get_unit_data(main_cabinet_page)
    #
    # exit()

    with open("saved_lessons_info.txt", 'r') as f:
        for line in f.readlines():
            if "&" in line:
                unit_number, lesson_name = get_unit_lesson(line)
                store_path = "units/unit_" + str(unit_number)

                if not os.path.exists(store_path):
                    os.makedirs(store_path , 755)

            if "»" in line:
                lesson_name += "_" + line

            if "upload" in line:
                link = line
                if download_video_by_link(link, lesson_name, store_path):
                    print('uploaded %s' % lesson_name)

if __name__ == "__main__":
    main()

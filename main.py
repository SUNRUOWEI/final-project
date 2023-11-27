import urllib.parse
import json

import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib as plt
import os

headers = {
    'authority': 'm.media-amazon.com',
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'referer': 'https://m.imdb.com/',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'script',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
}


def extract_movie_info_text(movie_info_div):
    title = movie_info_div.find('h3', class_='ipc-title__text')
    detail_url = movie_info_div.find('a', class_='ipc-title-link-wrapper')
    year = movie_info_div.find('span', class_='cli-title-metadata-item')
    duration = year.next_sibling
    rate = movie_info_div.findNext('span', class_='ipc-rating-star')
    span = title.text.find(' ')
    print(span)
    rank = title.text[0: span - 1]
    title = title.text[span:].strip()
    return rank, title, detail_url.get('href'), year.text, duration.text, rate.text


def get_movie_details(detail_url):
    response = requests.get(detail_url, headers=headers, verify=False)
    if response.status_code != 200:
        print(detail_url, 'request failed, response status code is', response.status_code)
    soup = BeautifulSoup(response.text, 'html.parser')
    response.close()

    describe = soup.find('span', class_='sc-466bb6c-1 dWufeH').text
    detail_in_banner = soup.find('ul',
                                 class_='ipc-metadata-list ipc-metadata-list--dividers-all title-pc-list ipc-metadata-list--baseAlt')
    li_list = detail_in_banner.find_all('li', class_='ipc-metadata-list__item')
    directors = li_list[0].find_all('a',
                                    class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
    writers = li_list[1].find_all('a',
                                  class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
    stars = li_list[2].find_all('a',
                                class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
    directors = [director.text for director in directors]
    writers = [writer.text for writer in writers]
    stars = [star.text for star in stars]

    detail_in_section = soup.find(attrs={'data-testid': 'Details'})
    countries = detail_in_section.find(attrs={'data-testid': 'title-details-origin'})
    countries = countries.find('li', class_='ipc-inline-list__item')

    language = detail_in_section.find(attrs={'data-testid': 'title-details-languages'})
    language = language.find('li', class_='ipc-inline-list__item')
    countries = [country.text for country in countries]
    language = [l.text for l in language]

    directors = ','.join(directors)
    writers = ','.join(writers)
    stars = ','.join(stars)
    countries = ','.join(countries)
    language = ','.join(language)

    return countries, language, directors, writers, stars


def scrape_top250():
    url = "https://m.imdb.com/chart/top/?ref_=nv_mv_250"
    movie_list = []

    response = requests.get(url, headers=headers, verify=False)
    if response.status_code != 200:
        print(url, 'request failed, response status code is', response.status_code)
    soup = BeautifulSoup(response.text, 'html.parser')
    response.close()

    for movie_info_div in soup.find_all('div', class_='ipc-metadata-list-summary-item__c'):
        print('=================')
        rank, title, detail_url, year, duration, rate = extract_movie_info_text(movie_info_div)
        detail_url = urllib.parse.urljoin(url, detail_url)
        print(rank, title, detail_url, year, duration, rate)
        movie_detail = {
            'rank': rank,
            'title': title,
            'detail_url': detail_url,
            'year': year,
            'duration': duration,
            'rate': rate
        }

        print(movie_detail)
        print('=================')
        movie_list.append(movie_detail)

    return movie_list


def save_json_file(movie_list, file_name):
    with open(file_name, 'w') as file_object:
        json.dump(movie_list, file_object, indent=4)


def main():
    file_name = './movie.json'
    if not os.path.exists(file_name):
        movie_list = scrape_top250()
        save_json_file(movie_list, file_name)

    folder_path = "./movie_details"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        # build 250 empty JSON files
        for i in range(0, 250):
            detail_name = f"count{i}.json"
            file_path = os.path.join(folder_path, detail_name)
            # build one empty JSON file
            data = {}
            with open(file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
    with open(file_name, 'r') as movie_list_file:
        movie_list_data = json.load(movie_list_file)
        for i in range(0, len(movie_list_data)):
            with open('./movie_details/count' + str(i) + '.json', 'w') as file_object:
                countries, language, directors, writers, stars = get_movie_details(
                    movie_list_data[i]['detail_url'])
                print(i, " ====" , countries, language, directors, writers, stars)
                movie_detail = {
                    'rank': movie_list_data[i]['rank'],
                    'title': movie_list_data[i]['title'],
                    'detail_url': movie_list_data[i]['detail_url'],
                    'year': movie_list_data[i]['year'],
                    'duration': movie_list_data[i]['duration'],
                    'rate': movie_list_data[i]['rate'],
                    'country': countries,
                    'language': language,
                    'director': directors,
                    'writer': writers,
                    'star': stars
                }
                json.dump(movie_detail, file_object, indent=4)



if __name__ == '__main__':
    main()

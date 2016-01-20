#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import json
import pageanalytics
from datetime import datetime, timedelta

inputcsv = 'D:\\projects\\AppPicker\\app strength\\articleversion_apps_daily_downloads.csv'
outputcsv = 'D:\\projects\\AppPicker\\app strength\\art_versn_apps_w_pageviews.csv'

class ArticleTypeException(Exception):
    def __init__(self, customMessage = 'Unknown article type was specified'):
        self.customMessage = customMessage
    def __str__(self):
        return repr(self.customMessage)

class articleUrls():

    def __init__(self, article_type:int, article_id:int, slug:str):
        if article_type in (0, '0'):
            self.value = 'http://www.apppicker.com/news/{}/{}'.format(article_id, slug)
        elif article_type in (1, '1'):
            self.value = 'http://www.apppicker.com/reviews/{}/{}'.format(article_id, slug)
        elif article_type in (2, '2'):
            self.value = 'http://www.apppicker.com/applists/{}/{}'.format(article_id, slug)
        elif article_type in (3, '3'):
            self.value = 'http://www.apppicker.com/interviews/{}/{}'.format(article_id, slug)
        elif article_type in (4, '4'):
            self.value = 'http://www.apppicker.com/developernews/{}/{}'.format(article_id, slug)
        elif article_type in (5, '5'):
            self.value = 'http://www.apppicker.com/appsale/{}/{}'.format(article_id, slug)
        elif article_type in (6, '6'):
            self.value = 'http://www.apppicker.com/appmanscorner/{}/{}'.format(article_id, slug)
        else:
            raise ArticleTypeException('Unknown article type was specified: ' + str(article_type))

    def __str__(self):
        return self.value
    def __eq__(self, y):
        return self.value==y.value
   
def mysql_datetime_str_to_object(dt_string:str):
    return datetime.strptime(dt_string, '%d/%m/%Y %H:%M')

def roundtonearestdate(dt:datetime):
    newdt = datetime.date(dt + timedelta(hours=12))
    return newdt

def preprocess():
    # open output file
    broker = pageanalytics.Broker()

    with open(outputcsv, 'w', newline='', encoding='utf-8') as outfileh:
        writer = csv.writer(outfileh, delimiter=',', quotechar='"', escapechar='~', doublequote=False, quoting=csv.QUOTE_NONNUMERIC)

        # write out headings
        writer.writerow(['app_id', 'article_id', 'article_type', 'days', 'version', 'published_at', 'super_version', 'super_published_at',
                         'download_date', 'app_title', 'downloads', 'daily_downloads', 'page_views', 'page_url'])

        # open input file
        with open(inputcsv, newline='\n', encoding='utf-8') as inputfileh:
            reader = csv.DictReader(inputfileh, fieldnames=('app_id', 'article_id', 'article_type', 'slug', 'days', 'version',
                                                            'published_at', 'super_version', 'super_published_at', 'download_date',
                                                            'app_title', 'downloads', 'daily_downloads'),
                                    delimiter=',', quotechar='"')
            i = 1
            next(reader) # skip header row
            for row in reader:
                if i % 10 == 0: print('Record: {}'.format(i))

                article_id = row['article_id']
                article_type = row['article_type']
                slug = row['slug']
                article_url = articleUrls(article_type, article_id, slug)
                published_at = row['published_at']
                super_published_at = row['super_published_at']
#                print('published_at: {}, super_published_at: {}'.format(published_at,super_published_at))

                # get Google Analytics page views data for this period of publication
                # first round datetime strings to nearest whole dates
                dt1 = mysql_datetime_str_to_object(published_at)
                start_date = (roundtonearestdate(dt1)).strftime('%Y-%m-%d')
                dt2 = mysql_datetime_str_to_object(super_published_at)
                end_date = (roundtonearestdate(dt2)).strftime('%Y-%m-%d')
#                print('start_date: {}, end_date: {}'.format(start_date, end_date))
#                print('pagePath: {}'.format(str(article_url).replace('http://www.apppicker.com','')))
                # now get pageviews
                garesults = broker.get_results(pagePath=str(article_url).replace('http://www.apppicker.com',''), start_date=start_date, end_date=end_date)
                pageviews = broker.extract_pageviews(garesults)
#                print('pageviews: {}\n'.format(pageviews))
#                print('{}'.format(json.dumps(row)))

                writer.writerow([row['app_id'], article_id, article_type, row['days'], row['version'], published_at, row['super_version'],
                                super_published_at, row['download_date'], row['app_title'],  row['downloads'], row['daily_downloads'], pageviews, article_url])
                i += 1
                if i==20:break
        inputfileh.close()
    outfileh.close()
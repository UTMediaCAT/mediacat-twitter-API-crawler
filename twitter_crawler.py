# twitter_crawler.py
#   Author: Shengsong Xu
#   Date: March 20th, 2022
#   Description: Crawl tweets for the given twitter handles using twitter API v2
#   Parameters: -s: indicate to seprate output.csv to several output_i.csv files
#               -st: crawl tweets start from this start_time
#               -en: crawl tweets start from this end_time
#               -n: write to output every n twitter_handles
#   Preperation: To set your enviornment variables in your terminal run the following line:
#                export 'BEARER_TOKEN'='<your_bearer_token>'
#   Usage: "python3 twitter_crawler.py"
#          "python3 twitter_crawler.py -s"
#          "python3 twitter_crawler.py -s -st 2010-01-01 -en 2022-01-02"
#          "python3 twitter_crawler.py -s -st 2010-01-01 -en 2022-01-02 -n 3"


import pandas as pd
import datetime
import csv
import sys
import requests
import os
import json
import re
import argparse
from searchtweets import ResultStream, gen_request_parameters, load_credentials, collect_results

# The maximum number of tweets we get per request (500 is the max)
MAX_TWEETS_PER_CALL = 500
# The maximum number of tweet that we will request per user ( We can get 10 million total tweets a month)
MAX_TWEETS_PER_USER = 1000
# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = os.environ.get("BEARER_TOKEN")
ROW_PER_FILE = 10000
OUTPUT_FOLDER = 'Output'


def parse_csv(file):
    """
    parse the input csv file and get a list of twitter handles and tag_list
    :param df: a csv file
    :rtype: two lists
    """
    # try to read csv file
    try:
        df = pd.read_csv(file)
    except(Exception):
        print("Input file is not csv or doesn't exist such csv")
        exit(1)

    name_list = df["Twitter Handle"].tolist()
    # parse name_list by remove '@'
    twitter_handles = []
    try:
        for eve in name_list:
            if not pd.isna(eve):
                txtname = eve.split('@')[1].strip()
                twitter_handles.append(txtname)
    except(Exception):
        pass

    tags_list = []
    # parse tags
    df = df.astype("string")
    df.fillna('', inplace=True)
    tags = df.filter(like='Tag', axis=1)
    tags = tags.values.tolist()
    for li in tags:
        tags_list.append('|'.join(li))
    return twitter_handles, tags_list

## functions for getting user data for each twitter handle ##


def create_url_retweet(id):
    # Specify the usernames that you want to lookup below
    # You can enter up to 100 comma-separated values.
    expansions = "expansions=author_id"
    users = "user.fields=name"
    # User fields are adjustable, options include:
    # created_at, description, entities, id, location, name,
    # pinned_tweet_id, profile_image_url, protected,
    # public_metrics, url, username, verified, and withheld
    url = "https://api.twitter.com/2/tweets/{}?{}&{}".format(
        id, expansions, users)
    return url


def create_url(usernames_list):
    # Specify the usernames that you want to lookup below
    # You can enter up to 100 comma-separated values.
    usernames = "usernames={}".format(usernames_list)
    user_fields = "user.fields=public_metrics"
    # User fields are adjustable, options include:
    # created_at, description, entities, id, location, name,
    # pinned_tweet_id, profile_image_url, protected,
    # public_metrics, url, username, verified, and withheld
    url = "https://api.twitter.com/2/users/by?{}&{}".format(
        usernames, user_fields)
    return url


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserLookupPython"
    return r


def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oauth,)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()

## functions for getting user data for each twitter handle ##

## functions for creating output after the crawl ##


def create_csv_title(index, sub_num):
    row = (
        'id',
        'twitter_handle',
        'author_id',
        'created_at',
        'text',
        'referenced_tweets',
        'public_metrics',
        'entities',
        'referenced_entities',
        'conversation_id',
        'lang',
        'in_reply_to_user_id',
        'possibly_sensitive',
        'withheld',
        # 'geo',
        'tags',
        'tweet_url',
        'citation_urls'
    )
    file_name = OUTPUT_FOLDER + '/' + str(sub_num) + '_output.csv' if index == - \
        1 else OUTPUT_FOLDER + '/' + str(sub_num) + '_output_' + str(index) + '.csv'
    with open(file_name, 'a') as new_file:
        csv_writer = csv.writer(new_file)
        csv_writer.writerow(row)

    new_file.close()


def create_output_row(data, tags, twitter_handle, index, sub_num):
    try:
        referenced_tweets = data['referenced_tweets']
    except(Exception):
        referenced_tweets = []
    try:
        withheld = data['withheld']
    except(Exception):
        withheld = {}
    try:
        geo = data['geo']
    except(Exception):
        geo = {}
    try:
        in_reply_to_user_id = data['in_reply_to_user_id']
    except(Exception):
        in_reply_to_user_id = ''
    try:
        entities = data['entities']
    except(Exception):
        entities = ''
    try:
        url_jsons = data['entities']['urls']
    except(Exception):
        url_jsons = []
    try:
        retweet_jsons = data['retweet_entities']['urls']
    except(Exception):
        retweet_jsons = []

    citation_urls = []
    for url_json in url_jsons:
        citation_urls.append(url_json['expanded_url'])
    for retweet_json in retweet_jsons:
        if not retweet_json in citation_urls:
            citation_urls.append(retweet_json['expanded_url'])
    if 'referenced_urls' in data.keys():
        for referenced_url in data['referenced_urls']:
            citation_urls.append(referenced_url)

    tweet_url = "https://twitter.com/" + \
        twitter_handle + "/status/" + data['id']

    row = (
        data['id'],
        twitter_handle,
        data['author_id'],
        data['created_at'],
        data['text'],
        referenced_tweets,
        data['public_metrics'],
        entities,
        data['referenced_urls'] if 'referenced_urls' in data.keys() else [],
        data['conversation_id'],
        data['lang'],
        in_reply_to_user_id,
        data['possibly_sensitive'],
        withheld,
        # geo,
        tags,
        tweet_url,
        citation_urls
    )

    file_name = OUTPUT_FOLDER + '/' + str(sub_num) + '_output.csv' if index == - \
        1 else OUTPUT_FOLDER + '/' + str(sub_num) + '_output_' + str(index) + '.csv'
    with open(file_name, 'a') as new_file:
        csv_writer = csv.writer(new_file)
        csv_writer.writerow(row)

    new_file.close()


def create_seperate_output(tweets, tags_list, sub_num):
    row_count = 0
    csv_index = 0
    index = 0

    ### initialize output_0.csv ###
    create_csv_title(csv_index, sub_num)
    for twitter_handle in tweets.keys():
        for i in range(0, len(tweets[twitter_handle]['data'])):
            if (row_count == ROW_PER_FILE):
                csv_index = csv_index + 1
                row_count = 0
                create_csv_title(csv_index, sub_num)
            create_output_row(tweets[twitter_handle]
                              ['data'][i], tags_list[index], twitter_handle, csv_index, sub_num)
            row_count = row_count + 1
        index = index + 1


def create_output(tweets, tags_list, sub_num):
    ### initialize output.csv ###
    create_csv_title(-1, sub_num)

    # traverse each data
    index = 0
    for twitter_handle in tweets.keys():
        for i in range(0, len(tweets[twitter_handle]['data'])):
            create_output_row(tweets[twitter_handle]
                              ['data'][i], tags_list[index], twitter_handle, -1, sub_num)
        index = index + 1

## functions for creating output after the crawl ##


def append_referenced_tweets(tweets_handle):
    # clean up referenced tweets
    referenced_tweets = []
    for expansion in tweets_handle['expansions']:
        if 'tweets' in expansion.keys():
            for referenced_tweet in expansion['tweets']:
                referenced_tweets.append({
                    'id': referenced_tweet['id'],
                    'text': referenced_tweet['text'],
                    'url': 'https://twitter.com/' + referenced_tweet['author']['username'] + '/status/' + referenced_tweet['id'] if 'author' in referenced_tweet.keys() else 'https://twitter.com/' + 'unkown' + '/status/' + referenced_tweet['id'],
                    'entities': referenced_tweet['entities'] if 'entities' in referenced_tweet.keys() else {}
                })
    print('referenced_tweets:', len(referenced_tweets))

    # update referenced tweets to tweets_handle
    i = 0
    for tweet in tweets_handle['data']:
        if (len(referenced_tweets) <= 0):
            break
        if ('referenced_tweets' in tweet.keys()):
            tweet['referenced_urls'] = []
            for index in range(0, len(tweet['referenced_tweets'])):
                if (tweet['referenced_tweets'][index]['id'] == referenced_tweets[0]['id']):
                    if tweet['referenced_tweets'][index]['type'] == 'retweeted':
                        regex = r'(.*[RT] @.*[:]).*'
                        matches = re.search(
                            regex, tweet['text'], re.IGNORECASE)
                        if matches:
                            tweet['text'] = matches[1] + \
                                referenced_tweets[0]['text']
                    tweet['retweet_entities'] = referenced_tweets[0]['entities']
                    tweet['referenced_urls'].append(
                        referenced_tweets[0]['url'])
                    referenced_tweets.pop(0)
                    i = i + 1

    print('first', i)

    for referenced_tweet in referenced_tweets:
        for tweet in tweets_handle['data']:
            if ('referenced_tweets' in tweet.keys()):
                if ('referenced_urls' in tweet.keys()):
                    if (len(tweet['referenced_urls']) == len(tweet['referenced_tweets'])):
                        continue
                else:
                    tweet['referenced_urls'] = []

                for tweet_type in tweet['referenced_tweets']:
                    if (tweet_type['id'] == referenced_tweet['id']):
                        if tweet_type['type'] == 'retweeted':
                            regex = r'(.*[RT] @.*[:]).*'
                            matches = re.search(
                                regex, tweet['text'], re.IGNORECASE)
                            if matches:
                                tweet['text'] = matches[1] + \
                                    referenced_tweet['text']
                        tweet['retweet_entities'] = referenced_tweet['entities']
                        tweet['referenced_urls'].append(
                            referenced_tweet['url'])
                        i = i + 1
    print('sec', i)
    return tweets_handle


def twitter_crawler(twitter_handles, tags_list, sep_output, start_time, end_time, sub_num):
    """
    function that generate requests to twitter API v2

    """
    # get number of tweets for each twitter handle to set up max_tweets
    handle_list = ''
    for twitter_handle in twitter_handles:
        twitter_handle = twitter_handle.strip()
        handle_list = handle_list + twitter_handle + ','
    user_request_url = create_url(handle_list[:len(handle_list)-1])
    user_jsons = connect_to_endpoint(user_request_url)
    print(user_jsons)
    if (len(user_jsons['data']) != len(twitter_handles)):
        print('contain error twitter handle')
        return

    ### load credentials for tweet_search###
    full_archive_seach_args = load_credentials(filename="./twitter_keys.yaml",
                                               yaml_key="search_tweets_fullarchive_dev",
                                               env_overwrite=False)

    ### define request inputs ###
    tweet_fields = 'id,author_id,created_at,text,public_metrics,referenced_tweets,entities,conversation_id,lang,in_reply_to_user_id,possibly_sensitive,withheld'
    expansions = 'referenced_tweets.id,referenced_tweets.id.author_id'
    tweets = {}

    ### start crawling ###
    i = 0
    for twitter_handle in twitter_handles:
        # prepare query
        print(i, 'procesing', twitter_handle)
        print(user_jsons['data'][i]['public_metrics']['tweet_count'])

        query = gen_request_parameters("from:"+twitter_handle,
                                       granularity=None,
                                       start_time=start_time,
                                       end_time=end_time,
                                       tweet_fields=tweet_fields,
                                       expansions=expansions,
                                       results_per_call=MAX_TWEETS_PER_CALL)
        # make calls to twitter api
        # results_pages = collect_results(
        #     query, MAX_TWEETS_PER_USER, result_stream_args=full_archive_seach_args)
        results_pages = collect_results(
            query, max_tweets=user_jsons['data'][i]['public_metrics']['tweet_count'], result_stream_args=full_archive_seach_args)
        # # see twitter_api_demo for how results_pages looks like
        '''
            for result in results_pages:
                for data in result['data']
                    list.append(data)
            That is what the below do
        '''
        tweets[twitter_handle] = {
            "data": [data for result in results_pages for data in result['data']],
            "expansions": [result['includes'] for result in results_pages]
        }
        print(twitter_handle, 'has', len(
            tweets[twitter_handle]['data']), 'tweets')

        i = i + 1

        tweets[twitter_handle] = append_referenced_tweets(
            tweets[twitter_handle])

    ### create output ###
    if (sep_output):
        create_seperate_output(tweets, tags_list, sub_num)
    else:
        create_output(tweets, tags_list, sub_num)


def valid_datetime(date_text):
    """
    check if the input start_date and end_date is a valid datetime
    """
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        print("Incorrect data format, should be YYYY-MM-DD")
        return False


if __name__ == "__main__":
    ## Parsing arguments ##

    parser = argparse.ArgumentParser(description='Crawler parameters.')
    parser.add_argument('-s', action='store_true')
    parser.add_argument('-st', default='2006-03-21', type=str)
    parser.add_argument('-n', type=int)
    today = datetime.date.today()
    end_time = today.strftime("%Y-%m-%d")
    parser.add_argument('-en', default=end_time, type=str)
    args = parser.parse_args()
    if (args.s):
        print('will create seperate output.csv')
    if (args.st):
        if not valid_datetime(args.st):
            sys.exit(0)
        print('start time: ' + args.st)
    if (args.en):
        if not valid_datetime(args.en):
            sys.exit(0)
        print('end time: ' + args.en)

    twitter_handles, tags_list = parse_csv('kpp_copy.csv')
    if (args.n):
        num_per_crawl = args.n
    else:
        num_per_crawl = len(twitter_handles)
    ## Parsing arguments ##

    # parse input file
    twitter_handles, tags_list = parse_csv('kpp_copy.csv')
    # print(twitter_handles)
    # start crawling
    twitter_handles_chunks = [twitter_handles[x:x+num_per_crawl]
                              for x in range(0, len(twitter_handles), num_per_crawl)]
    sub_num = 0
    for sub_twitter_handles in twitter_handles_chunks:
        twitter_crawler(sub_twitter_handles, tags_list,
                        args.s, args.st, args.en, sub_num)
        sub_num += 1

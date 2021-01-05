#!/usr/bin/env python
# coding: utf-8

# In[1]:


import tweepy
import pandas as pd
# == OAuth Authentication ==
#
# This mode of authentication is the new preferred way
# of authenticating with Twitter.

# The consumer keys can be found on your application's Details
# page located at https://dev.twitter.com/apps (under "OAuth settings")


api_key = 'Your api_key'
api_secret_key = 'Your api_secret_key'

#
# The access tokens can be found on your applications's Details
# page located at https://dev.twitter.com/apps (located under "Your access token")  # nopep8
access_token = 'Your access_token'
access_token_secret = 'Your access_token_secret'

auth = tweepy.OAuthHandler(api_key, api_secret_key)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)


# get all methods for tweepy api
def get_methods():
    methods = [method for method in dir(tweepy.api) if callable(getattr(tweepy.api, method))]  # nopep8
    return methods


# get API limit
def get_api_limit():
    return api.rate_limit_status()


# get method limit
def get_api_method_limit(api_limit, method_name):
        resources = api_limit['resources']  # noqa
        try:
            user = resources['users'][method_name]
            return user['remaining']
        except KeyError as e:  # noqa
            pass
        try:
            status = resources['statuses'][method_name]
            return status['remaining']
        except KeyError as e:  # noqa
            pass
        try:
            application = resources['application'][method_name]
            return application['remaining']
        except KeyError as e:  # noqa
            pass

        return None


# User Object
# get user object
def get_user(twitter_handle):
    # attributes = [attr for attr in dir(user) if not callable(getattr(user, method))]  # nopep8
    # print attributes
    user = api.get_user(twitter_handle)
    # methods = [method for method in dir(user) if callable(getattr(user, method))]  # nopep8
    return user


# get twitter account creation time
def get_user_created_at(user):
    return user.created_at.strftime('%a %Y-%m-%d %H:%M:%S')


# default profile
def is_user_default_profile(user):
    if not user.default_profile:
        return False
    return True


# default profile img
def is_user_default_profile_img(user):
    if not user.default_profile_image:
        return False
    return True


# get description
def get_user_description(user):
    return user.description


# get fav count
def get_user_fav_cnt(user):
    return user.favourites_count


# get followers list
def get_user_followers(user):
    return user.followers()


# get friends
def get_user_friends(user):
    return user.friends()


# get follower ids
def get_user_follower_ids(user):
    return user.followers_ids()


# get no of followers
def get_user_followers_count(user):
    return user.followers_count


def get_user_friends_count(user):
    return user.friends_count


# get name
def get_user_name(user):
    return user.name


# get location
def get_user_location(user):
    return user.location


# get screen name
def get_user_screen_name(user):
    return user.screen_name


# get utc offset
def get_user_utc_offset(user):
    return user.utc_offset


# get time zone
def get_user_time_zone(user):
    return user.time_zone


# get geo enabled
def get_user_geo_enabled(user):
    return user.geo_enabled


# get user id
def get_user_id_string(user):
    return user.id_str


# get user language
def get_user_language(user):
    return user.lang


# get user protected
def get_user_protected(user):
    return user.protected


# get user statuses or tweets count
def get_user_statuses_count(user):
    return user.statuses_count


# get user url
def get_user_url(user):
    return user.url


# is user verified
def is_user_verified(user):
    return user.verified


# get profile bg img url
def get_user_prof_bg_img_url(user):
    return user.profile_background_image_url


# get profile banner url (this attribute might not appear on some accounts,
# and an exception will be thrown)
def get_user_prof_banner_url(user):
    return user.profile_banner_url


# is user using prof bg img
def is_user_prof_bg_img(user):
    return user.profile_use_background_image


# Tweet Object
# get timeline: user tweets
def get_timeline(twitter_handle):
    statuses = api.user_timeline(screen_name=twitter_handle)
    return statuses


# get author, which is an object of user
def get_status_author(status):
    return status.author.screen_name


# get author id string
def get_status_author_id_string(status):
    return status.author.id_str


# get tweet created timestamp
def get_status_created_at(status):
    return status.created_at.strftime('%a %Y-%m-%d %H:%M:%S')


# get tweet favourite count
def get_status_favorite_count(status):
    return status.favorite_count


# get tweet coordinates
def get_status_coordinates(status):
    return status.coordinates


# get tweet id
def get_status_id_string(status):
    return status.id_str


# get tweet language
def get_status_language(status):
    return status.lang


# get retweet count
def get_status_retweet_count(status):
    return status.retweet_count


# get tweet source
def get_status_source(status):
    return status.source


# get tweet source url
def get_status_source_url(status):
    return status.source_url


# get tweet text
def get_status_text(status):
    return status.text


# get geo info
def get_status_geo(status):
    return status.geo


def get_status_id(status):
    return status.id


def get_status_entities(status):
    return status.entities


# check if there is a unidirectional or bi-directional link betweet two twitter users  # nopep8
def check_link(src_name, tgt_name):
    source, target = api.show_friendship(source_screen_name=src_name, target_screen_name=tgt_name)  # nopep8
    if source.followed_by:
        print("%s followed by %s" % (source.screen_name, target.screen_name))
    if source.following:
        print("%s following %s" % (source.screen_name, target.screen_name))
    if target.followed_by:
        print("%s followed by %s" % (target.screen_name, source.screen_name))
    if target.following:
        print("%s following %s" % (target.screen_name, source.screen_name))


# get user profile
def get_user_profile(twitter_handle):
    user = get_user(twitter_handle)
    profile = {}
    profile["created_at"] = str(get_user_created_at(user))
    profile["followers_count"] = get_user_followers_count(user)
    profile["followees_count"] = get_user_friends_count(user)
    if is_user_default_profile(user):
        profile["default_profile"] = True
    else:
        profile["default_profile"] = False
    if is_user_default_profile_img(user):
        profile["default_profile_img"] = True
    else:
        profile["default_profile_img"] = False
    profile["description"] = get_user_description(user).encode('utf-8')
    profile["name"] = get_user_name(user).encode('utf-8')
    profile["location"] = get_user_location(user).encode('utf-8')
    profile["screen_name"] = get_user_screen_name(user).encode('utf-8')
    profile["fave_count"] = get_user_fav_cnt(user)
    profile["time_zone"] = get_user_time_zone(user)
    profile["utc_offset"] = str(get_user_utc_offset(user))
    profile["user_id"] = get_user_id_string(user)
    profile["acc_protected"] = get_user_protected(user)
    profile["status_count"] = get_user_statuses_count(user)
    return profile


# print user profile
def print_user_profile(profile):
    print("twitter handle=%s" % profile["screen_name"])
    print("account created at=%s" % profile["created_at"])
    print("followers count=%d" % profile["followers_count"])
    print("followees count=%d" % profile["followees_count"])
    print("default profile=%d" % profile["default_profile"])
    print("default profile img=%d" % profile["default_profile_img"])
    print("description: %s" % profile["description"])
    print("name: %s" % profile["name"])
    print("location: %s" % profile["location"])
    print("screen name: %s" % profile["screen_name"])
    print("fav count: %d" % profile["fave_count"])
    print("time zone: %s" % profile["time_zone"])
    print("UTC offset: %s" % profile["utc_offset"])
    print("user id=%s" % profile["user_id"])
    print("acc is protected=%d" % profile["acc_protected"])
    print("status count=%d" % profile["status_count"])


# get user tweets
def get_user_tweets(twitter_handle):
    statuses = get_timeline(twitter_handle)
    tweet = {"source": [],
             "text": [],
             "created_at": [],
             "author": [],
             "coordinate": [],
             "geo": [],
             "lang": [],
             "fav_cnt": [],
             "rt_cnt": [],
             "id": [],
             "link": [],
             "entities": None,
             "hashtags": [],
             "mentions": [],
             "urls": []
             }
    for status in statuses:
        tweet["source"].append(get_status_source(status))
        tweet["text"].append(get_status_text(status))
        tweet["created_at"].append(str(get_status_created_at(status)))
        tweet["author"].append(str(get_status_author(status)))
        tweet["coordinate"].append(get_status_coordinates(status))
        tweet["geo"].append(get_status_geo(status))
        tweet["lang"].append((get_status_language(status)))
        tweet["fav_cnt"].append(get_status_favorite_count(status))
        tweet["rt_cnt"].append(get_status_retweet_count(status))
        tweet["id"].append(get_status_id(status))
        tweet["link"].append("https://twitter.com/" + str(get_status_author(status)) + "/status/" + str(get_status_id(status)))  # nopep8
        tweet["entities"] = get_status_entities(status)
        tweet["hashtags"].append(tweet["entities"]['hashtags'])
        tweet["mentions"].append(tweet["entities"]['user_mentions'])
        tweet["urls"].append(tweet["entities"]['urls'])

    return tweet


def get_list(file):
    """
    crawling each twitter user's tweets and generate csv output.
    :param df: a csv file
    :rtype: a list
    """
    try:
        # try to read csv file
        df = pd.read_csv(file)
        name_list = df["Source"].tolist()
        return name_list
    except(Exception):
        print("Input file is not csv or doesn't exist such csv")
        exit(1)


# In[5]:


def write_user_tweets(tweet, twitter_handle):
    retweet = pd.DataFrame({'id': tweet["id"],
                            "link": tweet["link"],
                            "name": tweet["author"],
                            "date": tweet["created_at"],
                            "hashtags": tweet["hashtags"],
                            "mentions": tweet["mentions"],
                            "urls": tweet["urls"],
                            "tweet": tweet["text"],
                            "source": tweet["source"],
                            "coord": tweet["coordinate"],
                            "place": tweet["geo"],
                            "lang": tweet["lang"],
                            "fav_cnt": tweet["fav_cnt"],
                            "rt_cnt": tweet["rt_cnt"]})
    retweet.to_csv('csv/' + twitter_handle + ".csv", index=False, encoding='utf-8-sig')  # nopep8


def twitter_crawler(file):
    """
    get twitter user from csv and return a list ie["@aaa","@bbb","@ccc"]
    :param df: a csv file
    :rtype: a list of error twitter handle
    """

    # create a subprocess and error list
    error_list = []
    # get the twitter list
    list_name = get_list(file)
    for eve in list_name:
        try:
            txtname = eve.split('@')[1]
            print(txtname)
            tweets = get_user_tweets(txtname)
            write_user_tweets(tweets, txtname)
        except(Exception):
            error_list.append(txtname)
            pass

    print(error_list)
    return(error_list)


if __name__ == "__main__":
    twitter_crawler("twitter.csv")

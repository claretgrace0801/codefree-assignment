from flask import Flask, request
import subprocess
import json

app = Flask(__name__)

max_results = 20


@app.route('/index', methods=["GET"])
def index():
    """
    Index method, to test if the API is running
    """
    return {"message": "API is live"}


@app.route('/get_data', methods=["POST"])
def get_data():
    """
    Returns the tweets in json format

    Parameters:
    -----------
    url: string
        The url of the twitter profile

    Returns:
    --------
    dict
        A json object containing a list of tweets 
    """
    data = request.get_json()
    user = get_user(data['url'])

    output = subprocess.check_output(
        f"snscrape --jsonl --max-results {max_results} twitter-profile '{user}'", shell=True).decode('utf-8')

    tweets = []
    for line in str(output).splitlines():
        tweets.append(json.loads(line))

    parsed_tweets = [{"text": tweet['rawContent'], "media": tweet['media'],
                      "tags": tweet['hashtags'], "mentioned": parse_users(tweet['mentionedUsers'])} for tweet in tweets]

    return {"tweets": parsed_tweets}


def get_user(url):
    """A helper method to get the username from a twitter url"""
    split_url = url.split('/')
    return split_url[-1] if split_url[-1] else split_url[-2]


def parse_users(users):
    """A helper method to parse the mentioned users correctly"""
    return [{"username": user['username'], "url": user['url']} for user in users] if users else None


if __name__ == '__main__':
    app.run(port=5000)

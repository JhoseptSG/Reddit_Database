import requests 
import sys
# Getting the data from reddit using the API

word = input("Enter the subreddit you want to get the data from: ")

with open("CLIENT_ID.txt") as f:
    CLIENT_ID = f.read().strip()

with open("SECRET_KEY.txt") as f:
    SECRET_KEY = f.read().strip()

with open("password_reddit.txt") as f:
    pwred = f.read().strip()

auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_KEY)
data = {'grant_type' : "password", 'username' : 'Goico192', 'password' : pwred}

headers = {"User-Agent" : "MyAPI/0.0.1"} 

res = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=headers)

TOKEN = res.json()['access_token'] 

headers = {**headers, **{"Authorization" : f"bearer {TOKEN}"}}

res = requests.get(f"https://oauth.reddit.com/r/{word}/hot", headers=headers) 

# Connecting to mongo database

from pymongo import MongoClient

with open("Mongo_url.txt") as f:
    MONGODB_URI = f.read().strip() 


client = MongoClient(MONGODB_URI)

# create a new database if not exist

reddit_database = client['reddit_database']

if word in reddit_database.list_collection_names():
    print("The collection was already created.")
    sys.exit()

collection = reddit_database[word]

# Inserting the data into the database
data = []

for post in res.json()["data"]["children"]:
    temp = {
    "subreddit": post["data"]["subreddit"],
    "title": post["data"]["title"],
    "upvote_ratio": post["data"]["upvote_ratio"],
    "ups": post["data"]["ups"],
    "downs": post["data"]["downs"],
    "score": post["data"]["score"],
    "num_comments": post["data"]["num_comments"],
    "created": post["data"]["created"]
    }

    if post["data"].get("selftext", "").strip():  # Check if selftext exists and is not empty after stripping whitespace
        temp["selftext"] = post["data"]["selftext"]


    data.append(temp)

result = collection.insert_many(data)

document_ids = result.inserted_ids

print("Ids of inserted documents:\n" + "\n ObjectID: ".join(str(doc_id) for doc_id in document_ids))

print("number of documents inserted: " + str(len(document_ids)))

print("The collection was created successfully.")


client.close()
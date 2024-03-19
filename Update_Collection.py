from pymongo import MongoClient
import sys
import requests 
# Getting the data from reddit using the API

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

# Connecting to mongo database
word = input("Enter the subreddit you want to get the data from: ")

with open("Mongo_url.txt") as f:
    MONGODB_URI = f.read().strip() 

client = MongoClient(MONGODB_URI) 

reddit_database = client['reddit_database']

if word not in reddit_database.list_collection_names():
    print("The collection doesn't exist. Please create it first.")
    sys.exit()

collection = reddit_database[word]

Documents_to_update = collection.find({},{ "_id": 1, "id_reddit": 1})

# updating the attributes of the documents
for element in Documents_to_update:
    id_reddit = element["id_reddit"]
    id = element["_id"]
    res = requests.get(f"https://oauth.reddit.com/api/info?id={id_reddit}", headers=headers)
    post_info = res.json()["data"]["children"][0]["data"]
    new_ups = post_info["ups"]
    new_downs = post_info["downs"]
    new_score = post_info["score"]
    new_upvoratio = post_info["upvote_ratio"]
    new_comments = post_info["num_comments"]
    collection.update_one({"_id": id}, {"$set": {"ups": new_ups, "downs": new_downs, "score": new_score, "upvote_ratio": new_upvoratio, "num_comments": new_comments}})

#adding new documents to the collection

print("The collection was updated successfully.")


##
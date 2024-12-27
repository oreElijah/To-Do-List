import os
import pymongo

client = pymongo.MongoClient(os.environ.get("MONGODB_URL"))


db = client['mydatabase']

dbs = db['Users']
task_db = db["Tasks"]

# data = {
# "Date": datetime.now().strftime("%d/%m/%Y, %H:%M"),
# "Task": "task"
#     }

# task_db.insert_one(data)
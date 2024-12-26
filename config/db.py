import pymongo
from datetime import datetime

client = pymongo.MongoClient("mongodb://localhost:27017")


db = client['mydatabase']

dbs = db['Users']
task_db = db["Tasks"]

# data = {
# "Date": datetime.now().strftime("%d/%m/%Y, %H:%M"),
# "Task": "task"
#     }

# task_db.insert_one(data)
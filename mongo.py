import pymongo

server = pymongo.MongoClient()
__dbname__ = 'tdx'
__setname__ = 'company_info'
global db,set
db = server.get_database(__dbname__)
set = db.get_collection(__setname__)

def insert(list):
    set.insert(list)

def find(str):
    pass


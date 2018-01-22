from pymongo import MongoClient

class Database():
    def __init__(self):
        self.mongo = MongoClient('mongodb://localhost:27017/WS')
        self._id = self.mongo.WS.CampZ.find().limit(1).sort([('_id', -1)])[0]['_id']

    def completed(self):
        return 'Completed' in self.mongo.WS.CampZ.find({'_id': self._id})[0]

    def add(self, key, failed=None, started=None, finished=None, score=None):
        obj = dict()
        if failed != None:
            obj['failed'] = failed
        if started:
            obj['started'] = started
        if finished:
            obj['finished'] = finished
        if score:
            obj['score'] = score
        self.mongo.WS.CampZ.update_one({'_id': self._id}, {'$set':{key:obj}})

    def append(self, key, started_by=None, started=None, message=None, time=None):
        obj = dict()
        if started_by:
            obj['started_by'] = started_by
        if started:
            obj['started'] = started
        if message:
            obj['message'] = message
        if time:
            obj['time'] = time
        self.mongo.WS.CampZ.update_one({'_id': self._id}, {'$push':{key:obj}})

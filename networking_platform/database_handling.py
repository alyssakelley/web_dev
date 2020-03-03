import utility

#logs in to the database url with credentials
#Returns a mongodb database object
def getDatabase(url, username, password):
    pass

#Gets the collection object from the database object
#Where colName is the name of the collection
#Returns a collection object
def getCollection(database, colName):
    pass

#Returns a single bson document that matches the query string
def getDocument(collection, query):
    pass

#Returns an object with variables that are equivalent to the bson document returned
def getDocumentToObj(collection, query, objType):
    return utility.bsonToObj(getDocument(collection, query), objType)

#Add a document to the collection
#Returns the same as the insert_one command
def insertDocument(collection, bsonObj):
    pass

#Add a document to the collection from an obj that is converted to a bson object
#Returns the same as the insert_one command
def insertDocumentFromObj(collection, obj):
    return insertDocument(collection, utility.objToBson(obj))

def getResumeCount(resume_type, username, userdb):

    resumes = userdb.user_resumes.find_one({"username":username})
    cnt = 0
    if resumes != None:
        if resume_type == "uploads":
            cnt = len(resumes["resume_uploads"])
        elif resume_type == "creations":
            cnt = len(resumes["resume_creations"])

    return cnt

def getCoverLetterCount(cl_type, username, userdb):

    resumes = userdb.user_cover_letters.find_one({"username":username})
    cnt = 0
    if resumes != None:
        if cl_type == "uploads":
            cnt = len(resumes["cover_letter_uploads"])
        elif cl_type == "creations":
            cnt = len(resumes["cover_letter_creations"])

    return cnt

def deleteResume(resume_type, resume_key, username, userdb):

    if resume_type == "uploads":
        array_name = "resume_uploads"
        match_key = "key"
    elif resume_type == "creations":
        array_name = "resume_creations"
        match_key = "title"

    return userdb.user_resumes.update_one({"username":username}, {"$pull" : {array_name : {match_key : resume_key}}})

def deleteCoverLetter(resume_type, resume_key, username, userdb):

    if resume_type == "uploads":
        array_name = "cover_letter_uploads"
        match_key = "key"
    elif resume_type == "creations":
        array_name = "cover_letter_creations"
        match_key = "title"

    return userdb.user_cover_letters.update_one({"username":username}, {"$pull" : {array_name : {match_key : resume_key}}})
import bson

#This takes a bson object and converts all of its key/value pairs
#to a python object of type "objType"
#Pass the class name only to "objType" and it will return an instance of that object
#If any key in "bsonObj" does not an equivilently named variable in the "objType"
#class, then it will throw an exception
def bsonToObj(bsonObj, objType):
    bsonDict = bson.BSON.decode(bsonObj)
    objToReturn = objType()
    for item in list(bsonDict.keys()):
        if hasattr(objType, item):
            setattr(objToReturn, item, bsonDict[item]) #sets the variabl in the object with name "item" to the bson value
        else:
            raise Exception(objType.__name__ +
                            " class does not have an attribute with the name of '" +
                            item +
                            "' that is present in the passed bson object")
    return objToReturn

#Need to test this
def objToBson(obj):
    return bson.BSON.encode(obj.__dict__)

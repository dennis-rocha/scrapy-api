#Use this Script for insert data to mongo for app.py
#The best strategy for not duplicating keys is to use mongo's '_id' column
#For didactic purposes and also for ease, we will create a random 'key'
from pymongo import MongoClient
cliente = MongoClient("mongodb://localhost:27017/")
db = cliente.myFirstmongoDB

conexao = db.testeUser
autho = db.authorization

#AUTHORIZATHION HERE
user={
    'user':{
        'nome':'Jurere',
        'cpf':'12345678901'
    },
    'authorization':{
        'insert':True,
        'delete':False,
        'update':False,
        'read':False
    },
    'key':'26ac37bj'
}
autho.insert_one(user)

user={
    'user':{
        'nome':'Joaquina',
        'cpf':'12345678901'
    },
    'authorization':{
        'insert':True,
        'delete':True,
        'update':True,
        'read':True
    },
    'key':'abc9873a'
}
autho.insert_one(user)

user={
    'user':{
        'nome':'Daniela',
        'cpf':'12345678901'
    },
    'authorization':{
        'insert':True,
        'delete':False,
        'update':False,
        'read':True
    },
    'key':'88ab00ac'
}
autho.insert_one(user)

user={
    'user':{
        'nome':'Canasvieiras',
        'cpf':'12345678901'
    },
    'authorization':{
        'insert':False,
        'delete':False,
        'update':False,
        'read':True
    },
    'key':'90ab30ac'
}
autho.insert_one(user)
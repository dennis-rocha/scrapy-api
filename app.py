from itertools import count
from sys import meta_path
from types import MethodDescriptorType
from flask import Flask, request
import flask
from bs4 import BeautifulSoup
from pymongo import message
from pymongo.message import insert, update
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from datetime import date,datetime
import json
from pymongo import MongoClient
from werkzeug.datastructures import Authorization
#Ocultar Webdriver
_options = webdriver.ChromeOptions()
_options.add_argument("--headless")
_webdriver = ChromeDriverManager().install() 
#conexao mongo
cliente = MongoClient("mongodb://localhost:27017/")
db = cliente.myFirstmongoDB
conexao = db.testeUser
autho = db.authorization
today = date.today()
#(conexao.find_one())
#conexao.insert({"nome":"joaquim","idade": 21})

app = Flask("Bot")

def ageCalc(data):
    try:
        born = data['data_nasc']
    except:
        born = data['personal_information']['data_nasc']

    _date = datetime.strptime(born, '%Y-%m-%d').date()

    return  today.year - _date.year -((today.month, today.day) < (_date.month, _date.day))

def openDriver(uf=None):
    url="https://www.4devs.com.br/gerador_de_pessoas"
    page=webdriver.Chrome(_webdriver, options=_options )

    #page = webdriver.Chrome("./chromedriver", chrome_options=options)
    page.get(url)

    #if uf:
    #    page.find_element_by_xpath('//*[@id="cep_estado"]').send_keys(uf)

    page.find_element_by_xpath("/html/body/main/div/div[2]/div/div[4]/div[1]/div[3]/label/input").click()
    
    sleep(2)
    page_source = page.page_source
    html=BeautifulSoup(page_source, "html.parser")

    data=json.loads(html.find('textarea').text)

    #FILTRANDO OS DADOS
    a=data['cpf']
    data['cpf']=f'{a[:3]}{a[4:7]}{a[8:11]}{a[12:]}'

    day,month,year=data['data_nasc'].split('/')
    data['data_nasc']=f"{year}-{month}-{day}"

    data['idade'] = ageCalc(data)


    list_filter=["pai","senha","signo","peso", "altura","tipo_sanguineo","cor"]
    [data.pop(key,None) for key in list_filter]

    list_filter_personal_information = ["nome","idade","cpf","rg","data_nasc","sexo","mae"]
    data["personal_information"]={key:data.pop(key,None) for key in list_filter_personal_information}

    list_filter_contacts = ["email","celular","telefone_fixo"]
    data["contacts"]={key:data.pop(key,None) for key in list_filter_contacts}
        
    list_filter_address = ["cep","endereco","numero","bairro","cidade","estado"]
    data["address"]={key:data.pop(key,None) for key in list_filter_address}
    
    page.quit()

    return data


def generateResponses (status, message, name_content=False,content=False):
    response = {}
    response["status"] = status
    response["message"]= message

    if name_content and content:
        response[name_content] = content

    return response


def insertData(data):
    conexao.insert_one(data)

def findInput(cpf):
    
    conexao.find_one_and_update({'personal_information.cpf':cpf},{"$set":{'personal_information.idade':ageCalc(conexao.find_one({"personal_information.cpf":cpf}))}})
    data = conexao.find_one({"personal_information.cpf":cpf})    

    data["id"]=str(data["_id"])
    del data["_id"]

    return data


def updateUser(body,cpf):
    user=findInput(str(cpf))
    del user["id"]

    conexao.find_one_and_update({'personal_information.cpf':cpf},{"$set":{'personal_information.idade':ageCalc(user)}})

    for i in body:
        for key in user:
            for j in user[key]:
                if i == j:  
                    to_data={"$set":{key+'.'+i:body[i]}}
                    conexao.find_one_and_update(
                        {
                            'personal_information.cpf':cpf
                        },
                        to_data
                    )

    return findInput(str(cpf))

def read_authorizathion(header=None,methods=None):
    #Methods -> 'insert' 'delete' 'update' 'read'
    data = autho.find_one({'key':header})

    if not data:
        message="User Not Authorized"
        status=404
    
    else:
        if data['authorization'][methods]:
            message="Authorized"
            status=200
    
        else:
            message="Only authorized people"
            status=401
    
    return status,message


#FAMOSO OLÁ MUNDO
@app.route("/olamundo", methods=["GET"])
def olamundo ():
    header = request.headers.get('Authorization')
    
    if '88a00cb' == header:
        return {"Message":"Consegui"}
    else:

        resp = flask.Response("Foo bar baz")
        resp.headers['Acces-Control-Allow-Origin'] = '*'

        return {"Mensagem":"VOCE NAO TEM AUTORIZAÇÃO"}


#INSERINDO DADOS NO BANCO DE DADOS
@app.route("/input/users", methods=["GET"])
def inputBots():
    header=request.headers.get("Authorization")
    status,message=read_authorizathion(header,'insert')
    
    if status == 200:
        data=openDriver()  
        insertData(data.copy())
        return generateResponses(200, "Usuario cadastrado com sucesso", "user", data)
    
    else:
        return generateResponses(status,message,'Authorization',header)

@app.route("/status/input/especifica/<cpf>", methods=["GET"])
def find_one_input(cpf):
    header=request.headers.get("Authorization")
    status,message=read_authorizathion(header,'read')
    
    if status == 200:
        data=findInput(str(cpf))
        return generateResponses(200,"Usuario encontrado com sucesso", "user", data)
    
    else:
        return generateResponses(status,message,'Authorization',header)


@app.route("/update/input/<cpf>", methods=["POST"])
def update_user(cpf):
    body = request.get_json()
    header=request.headers.get("Authorization")
    status,message=read_authorizathion(header,'update')
    
    if status == 200:
        data=updateUser(body,cpf)
        return generateResponses(200,"Usuario Atualizado com sucesso", "user", data)
    
    else:
        return generateResponses(status,message,'Authorization',header)

@app.route("/del/one_user/<cpf>", methods=["GET"])
def del_user(cpf):
    header=request.headers.get("Authorization")
    status,message=read_authorizathion(header,'delete')
    
    if status == 200:
        data=conexao.find_one_and_delete({"personal_information.cpf":cpf})
        del data["_id"]
        return generateResponses(200,"Usuario Deletado com sucesso", "user", data)

    else:
        return generateResponses(status,message,'Authorization',header)


app.run()
"""
if __name__ == '__main__':
    pass
    
    TESTAR OS DADOS QUE É CAPTURADO PELO BOT
    data_main = openDriver()
    cpf = 61559414910
    teste=findInput(str(cpf))
    """

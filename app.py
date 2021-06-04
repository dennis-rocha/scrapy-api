from itertools import count
from sys import meta_path
from types import MethodDescriptorType
from flask import Flask, request
import flask
from bs4 import BeautifulSoup
from pymongo.message import update
from selenium import webdriver
from time import sleep
import json
from pymongo import MongoClient
from werkzeug.datastructures import Authorization
#Ocultar Webdriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")
#conexao mongo
cliente = MongoClient("mongodb://localhost:27017/")
db = cliente.myFirstmongoDB
conexao = db.testeUser
#print(conexao.find_one())
#conexao.insert({"nome":"joaquim","idade": 21})

app = Flask("Bot")

def openDriver(uf=None):

    url="https://www.4devs.com.br/gerador_de_pessoas"

    page = webdriver.Chrome("./chromedriver", chrome_options=options)
    page.get(url)

    #if uf:
    #    page.find_element_by_xpath('//*[@id="cep_estado"]').send_keys(uf)

    page.find_element_by_xpath("/html/body/main/div/div[2]/div/div[4]/div[1]/div[3]/label/input").click()
    
    sleep(2)
    page_source = page.page_source
    html=BeautifulSoup(page_source, "html.parser")

    data=json.loads(html.find('textarea').text)

    #FILTRANDO OS DADOS
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


"""
    sleep(1)
    page.find_element_by_xpath("/html/body/main/div/div[2]/div/div[4]/div[1]/div[3]/label/input").click()
    sleep(1)
    page.find_element_by_xpath("/html/body/main/div/div[2]/div/div[4]/div[1]/div[7]/div/textarea")
    #page.find_element_by_xpath('//*[@id="cep_estado"]').send_keys("SC")






caso nao funcione a conexao com o mongo:
    sudo mongod --dbpath /var/lib/mongodb/ --journal
    mongo <- para abrir
"""



def generateResponses (status, message, name_content=False,content=False):
    response = {}
    print(content)
    response["status"] = status
    response["message"]= message

    if name_content and content:
        response[name_content] = content

    print("-"*50,'\n',response)
    print("-"*50,'\n'*5)
    return response





def insertData(data):
    conexao.insert_one(data)

def findInput(cpf):
    if len(cpf) == 11:
        new_cpf=f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"

        cpf=new_cpf
    
    data=conexao.find_one({"personal_information.cpf":cpf})

    data["id"]=str(data["_id"])
    del data["_id"]

    

    return data



def updateUser(body,cpf):
    user=findInput(str(cpf))
    
    id_client=str(user["id"])
    del user["id"]
    for i in body:
        
        for key in user:
            for j in user[key]:
                if i == j:
                    #conexao.find_one_and_update(dict(key.j),to_data)
                    print("ok")
                    to_data={"$set":{key+'.'+i:body[i]}}
                    
                    conexao.find_one_and_update(
                        {
                            'personal_information.cpf':cpf
                        },
                        to_data
                    )


    return findInput(str(cpf))


#FAMOSO OLÁ MUNDO
@app.route("/olamundo", methods=["GET"])
def olamundo ():
    header = request.headers.get('Authorization')
    if '88a00cb' == header:
        return {"Message":"Consegui"}
    else:

        resp = flask.Response("Foo bar baz")
        resp.headers['Acces-Control-Allow-Origin'] = '*'

        return resp


#INSERINDO DADOS NO BANCO DE DADOS
@app.route("/input/users", methods=["GET"])
def inputBots():

    data=openDriver()

    #Função para salvar dados no mongo    
    insertData(data.copy())


    return generateResponses (200, "Usuario cadastrado com sucesso", "User", data)
    

@app.route("/status/input/especifica/<cpf>", methods=["GET"])
def find_one_input(cpf):

    data=findInput(str(cpf))

    

    return generateResponses(200,"Usuario encontrado com sucesso", "User", data)


@app.route("/update/input/<cpf>", methods=["POST"])
def update_user(cpf):
    body = request.get_json()
    
    data=updateUser(body,cpf)

    return generateResponses(200,"Usuario Atualizado com sucesso", "User", data)

@app.route("/del/one_user/<cpf>", methods=["GET"])
def del_user(cpf):
    data=conexao.find_one_and_delete({"personal_information.cpf":cpf})
    del data["_id"]
    return generateResponses(200,"Usuario Deletado com sucesso", "User", data)




app.run()
"""
if __name__ == '__main__':
    #TESTAR OS DADOS QUE É CAPTURADO PELO BOT
#    data_main = openDriver()
    cpf = 61559414910
    teste=findInput(str(cpf))
"""
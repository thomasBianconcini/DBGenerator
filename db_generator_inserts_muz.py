from flask import Flask, jsonify
import sqlite3
import pandas as pd
import os 
import subprocess
import csv

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.llms import LlamaCpp
from langchain.prompts import PromptTemplate

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import requests
import json

app = Flask(__name__)


def import_database():
   
   conn = sqlite3.connect('fakeDB.db')
   c = conn.cursor()
   schemaUrl= input("Inserisci path file \n")

   with open(schemaUrl,"r") as file:
       sqlite_file=file.read()
       commands= sqlite_file.split(";")
       for command in commands:
           command=command + ";" 
           if "sqlite_sequence" not in command:
            c.execute(command)
            conn.commit()
    

   
def create_database_mock():

    conn = sqlite3.connect('fakeDB.db')
    c = conn.cursor()

    nt = str(input("quante tabelle vuoi generare?\n"))
    natt = str(input("quanti attributi per ogni tabella?\n"))
    ntup = str(input("Quante tuple vuoi generare per ogni tabella?\n"))

    # Callbacks support token-wise streaming
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

    # Make sure the model path is correct for your system!
    llm = LlamaCpp(
        model_path="/home/muz/llama.cpp/models/dolphin2.1-openorca-7b.Q4_K_M.gguf",
        temperature=0.75,
        max_tokens=2000,
        top_p=1,
        callback_manager=callback_manager,
        verbose=True,  # Verbose is required to pass to the callback manager
        grammar_path = "list.gbnf"
    )


    prompt= "Generate a list of table names related to a table users. the first table must be users and the others must be related to users. The length of the list must be " + nt + "."
    print(prompt)
    output = llm(prompt)

    # Processing the output to extract only table names
    table_names = output.replace("[","").replace("]","").replace("\"","").strip().split(",")


    clean_att = []
    print("Starting attribute generation...")
    for name in table_names:
        prompt_att = "Generate a list of attribute names related to the table "+ name+". The length of the list must be "+natt + "."
        output_att=llm(prompt_att)
        clean_att.append(output_att.replace("[","").replace("]","").replace("\"","").strip().split(","))
        print(name)

    print("\n Generated Table Names:\n")
    for name in table_names:
        print(name)


    print("\n Generated  attributes: \n")
    for t in clean_att:
        for name in t:
            print(name)


    #------------------------------------------------------# SCRIPT SELENIUM#------------------------------------------------------#

    #MODIFICHE PER RENDERE SELENIUM UNDETECTABLE
    firefox_capabilities = DesiredCapabilities.FIREFOX
    firefox_capabilities['marionette'] = False
    profile=webdriver.FirefoxProfile()
    profile.set_preference("dom.webdriver.enabled", False)
    profile.set_preference("useAutomationExtension", False)
    profile.update_preferences()

    #INIZIO SCRIPT SELENIUM
    options = Options()
    options.add_argument("--headless")
    #driver = webdriver.Firefox(firefox_profile=profile, options=options)
    driver = webdriver.Firefox(firefox_profile=profile)
    MOCKAROO_LINK = "https://www.mockaroo.com/"
    driver.get(MOCKAROO_LINK)

    driver.find_element(By.XPATH,f"//span[contains(., 'Generate fields using AI...')]").click()

    temp_att_list = sum(clean_att, [])

    attribute_list = []

    for idx, el in enumerate(temp_att_list):
        attribute_list.append(f"{table_names[idx//int(natt)]}_{el}")                ##ho dovuto aggiungere "tablename"_ prima del nome dell'attributo perchè senno con attributi che si chiamavano uguale esplodeva
        print(el)                                                                                  


    input_bar=driver.find_element(By.XPATH,f"//input[contains(@placeholder, 'Examples')]")
    input_bar.send_keys(str(attribute_list))
    input_bar2=driver.find_element(By.NAME, "count")
    input_bar2.clear()
    input_bar2.send_keys(str(len(attribute_list)))
    driver.find_element(By.XPATH,f"//span[contains(., 'Replace Existing Fields')]").click()
    sleep(15)
    divs=driver.find_elements(By.XPATH,f"//div/div[contains(@class, 'schema-column')]/div/button/span/div")
    types_list=[]
    #print("\n\n\n",attribute_list,"\n\n\n")

    for div in divs:
        types_list.append(div.text)

    #print("\n\n",types_list, "\n\n")

    driver.quit()#CHIUDE BROWSER--- 

    my_key="c1a2daf0"
    url = f"""https://api.mockaroo.com/api/generate.sql?key={my_key}&fields=["""

    inserts = []

    i=0
    j=0
    for el in clean_att:#per ogni table
        for l in el:#per ogni attributo
            if types_list[i]=="Custom List":
                types_list[i]="Row Number"
            url=url+ "{"+f'"name": "{l}","type": "{types_list[i]}"'+"}"
            if j!=len(el)-1:
                url=url+","
            i=i+1
            j=j+1
        j=0
        url=url+"]&count=4"#NUMERO DI ROW--------------------------------------
        payload = {}
        headers = {}
        print("URL: ",url)
        response = requests.request("POST", url, headers=headers, data=payload)
        url=f"""https://api.mockaroo.com/api/generate.sql?key={my_key}&fields=["""
        inserts.append(response.text)

    print(type(inserts))

    ins3=[]
    for ins in inserts:
        ins2=ins.split(";\n")
        ins3.append(ins2)
  
    for ins in ins3:
        #print("TYPE INS: ",type(ins))
        for i in ins:
            if i == '':
                ins.remove(i)
            #print("\nTYPE i: ",type(i),"\t,ins: ",i)
    j=0
    st = []
 

    for index,name in enumerate(table_names):
        id = False     
        table_to_create= f"CREATE TABLE IF NOT EXISTS {name} (\n"
        for attribute in clean_att[index]:
            if "id" in attribute:
                id = True
        if not id:
            table_to_create+= "  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"

        for i,attribute in enumerate(clean_att[index]):
            if id:
                if i ==0:
                    table_to_create = table_to_create +  "\n     "+attribute+" VARCHAR(500)"
                else:
                    table_to_create = table_to_create +  ",\n     "+attribute+" VARCHAR(500)"
            else:
                table_to_create = table_to_create +  ",\n     "+attribute+" VARCHAR(500)"
        id = False
        table_to_create = table_to_create + "\n);"
        print(table_to_create)
        c.execute(table_to_create)
    conn.commit()

    wf_inserts = []
    print("FOR INS: \n\n")
    for i,t in enumerate(table_names):
        wf_inserts=[]
        for ins in ins3[i]:
            indice_values = ins.find('values')
            valori_dopo_values = ins[indice_values + len('values'):].strip()
            print("\n valori dopo values: ", valori_dopo_values)
            ins = 'insert into ' + str(t) +' VALUES ' + valori_dopo_values
            print("\n------\n")
            print(ins)
            wf_inserts.append(ins)
            print("\n------\n")
            #c.execute(ins)
        print("WELL FORMATTED INSERTS: ", wf_inserts)
        for wfins in wf_inserts:
            print("wfins: ", wfins)
            #c.execute(wfins)
        for wfins in wf_inserts:
            c.execute(wfins)


    conn.commit()

    conn.close()

    # Return the table as an HTML response
    
if __name__ == '__main__':
    DB_esitente = input("Hai un DB? S o N \n")
    if DB_esitente == "N":
       print("creating DB")
       create_database_mock()
    else:
        import_database()
        print("importing DB")
    #comando = "docker cp test:/app/people.db /home/thomas/Desktop/progettoCyber/people.db"
    #output = subprocess.run(comando, shell=True)
  
    #app.run(debug=True, host='0.0.0.0')


    

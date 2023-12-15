import sqlite3
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.llms import LlamaCpp

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options

from time import sleep
import requests
import random
import re

#from langchain.prompts import PromptTemplate
#from langchain.chains import LLMChain
#from flask import Flask, jsonify
#import pandas as pd
#import os 
#import csv
#from selenium.webdriver.common.action_chains import ActionChains


path_to_models="../llama.cpp/models/"   # modelli inseriti dentro a ..../llama.cpp/models/
api_mockaroo_key="c1a2daf0"             # es. /home/user/Cyber/llama.cpp/models/

def mockaroo_values_generation(table_names, clean_att, imp, ntup, natt=0):

    conn = sqlite3.connect('fakeDB.db')
    c = conn.cursor()

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
    if imp==False:
        for idx, el in enumerate(temp_att_list):
            attribute_list.append(f"{table_names[idx//int(natt)]}_{el}")                ##ho dovuto aggiungere "tablename"_ prima del nome dell'attributo perchè senno con attributi che si chiamavano uguale esplodeva
            print(el)
    else:
        for idx, el in enumerate(clean_att):
            for l in el:
                attribute_list.append(f"{table_names[idx]}_{l}") 
                print(el)

    input_bar=driver.find_element(By.XPATH,f"//input[contains(@placeholder, 'Examples')]")
    input_bar.send_keys(str(attribute_list))
    input_bar2=driver.find_element(By.NAME, "count")
    input_bar2.clear()
    input_bar2.send_keys(str(len(attribute_list)))
    driver.find_element(By.XPATH,f"//span[contains(., 'Replace Existing Fields')]").click()
    sleep(16)
    divs=driver.find_elements(By.XPATH,f"//div/div[contains(@class, 'schema-column')]/div/button/span/div")
    types_list=[]

    for div in divs:
        types_list.append(div.text)

    driver.quit()#CHIUDE BROWSER--- 

    url = f"""https://api.mockaroo.com/api/generate.sql?key={api_mockaroo_key}&fields=["""

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
        url=url+f"]&count={ntup}"#NUMERO DI ROW--------------------------------------
        payload = {}
        headers = {}
        #print("URL: ",url)
        response = requests.request("POST", url, headers=headers, data=payload)
        url=f"""https://api.mockaroo.com/api/generate.sql?key={api_mockaroo_key}&fields=["""
        inserts.append(response.text)

    #print(type(inserts))

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
        attributes_table=clean_att[i]
        filtered_att=[]
        #for att in attributes_table:
            #if not("ID" in att or "id" in att):
                #filtered_att.append(att)
        
        str_att=",".join(attributes_table)
        wf_inserts=[]
        for ins in ins3[i]:
            indice_values = ins.find('values')
            valori_dopo_values = ins[indice_values + len('values'):].strip()
            #print("\n valori dopo values: ", valori_dopo_values)
            ins= "INSERT INTO "+ str(t)+"( "+str_att+" ) VALUES " + valori_dopo_values
            #ins = 'insert into ' + str(t) +' VALUES ' + valori_dopo_values
            #print("\n------\n")
            #print(ins)
            wf_inserts.append(ins)
            #print("\n------\n")
            #c.execute(ins)
        #print("WELL FORMATTED INSERTS: ", wf_inserts)
        for wfins in wf_inserts:
            print("\n---------\nwfins: ", wfins)
            #c.execute(wfins)
        for wfins in wf_inserts:
            c.execute(wfins)


    conn.commit()

    conn.close()

#------------------------------------------------------------------------------------------------

def import_database():
    conn = sqlite3.connect('fakeDB.db')
    c = conn.cursor()
    schemaUrl= input("Inserisci path file \n")

    list_commands=[]

    with open(schemaUrl,"r") as file:
        sqlite_file=file.read()
        commands= sqlite_file.split(";")
        for command in commands:
            if command!="" and command!="\n":
                command=command + ";"
                if "sqlite_sequence" not in command:
                    #print("COMMAND:",command)
                    list_commands.append(command)

    table_names=[]
    clean_att=[]

    for command in list_commands:
        pattern_a = r"([a-z_]+) \w+\(?\d*\)?"
        pattern_t=r'\bCREATE TABLE (\w+)'
        column_names = re.findall(pattern_a, command)
        clean_att.append(column_names)
        #print("ATTRIBUTI estratto con re: ",column_names)
        column_names = re.findall(pattern_t, command)
        table_names.append(column_names[0])
        #print("TABLENAME estratto con re: ",column_names)

    #print(table_names)
    #print(clean_att)

    ntup = str(input("Quante tuple vuoi generare per ogni tabella?\n"))

    mockaroo_values_generation(table_names, clean_att, True, ntup)

    """
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
    """

#------------------------------------------------------------------------------------------------

def create_database_mock():

    nt = str(input("quante tabelle vuoi generare?\n"))
    natt = str(input("quanti attributi per ogni tabella?\n"))
    ntup = str(input("Quante tuple vuoi generare per ogni tabella?\n"))

    # Callbacks support token-wise streaming
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

    # Make sure the model path is correct for your system!
    llm = LlamaCpp(
        model_path=f"{path_to_models}dolphin2.1-openorca-7b.Q4_K_M.gguf",
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

    mockaroo_values_generation(table_names, clean_att, False, ntup, natt)
 
#------------------------------------------------------------------------------------------------

def create_database_full_lama():

    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    llm2 = LlamaCpp(
        model_path=f"{path_to_models}llama-2-7b-chat.Q4_K_M.gguf",
        temperature=0.75,
        max_tokens=2000,
        top_p=1,
        callback_manager=callback_manager,
        verbose=True,  # Verbose is required to pass to the callback manager
        grammar_path = "list.gbnf"
    )
    llm = LlamaCpp(
        model_path=f"{path_to_models}dolphin2.1-openorca-7b.Q4_K_M.gguf",
        temperature=0.75,
        max_tokens=2000,
        top_p=1,
        callback_manager=callback_manager,
        verbose=True, 
        grammar_path = "list.gbnf"
    )

    nt = str(input("quante tabelle vuoi generare?\n"))
    natt = str(input("quanti attributi per ogni tabella?\n"))
    ntup=str(input("quante tuple vuoi generare?\n"))
    conn = sqlite3.connect('fakeDB.db')
    c = conn.cursor()
    prompt= "Generate a list of table names related to a table users. the first table must be users and the others must be related to users. The length of the list must be " + nt + "."
    print("\n"+prompt+"\n")
    output = llm(prompt)

    # Processing the output to extract only table names
    table_names = output.replace("[","").replace("]","").replace("\"","").replace(" ","").strip().split(",")

    clean_att = []
    print("Starting attribute generation...")
    
    for name in table_names:
        prompt_att = "Generate a list of attribute names related to the table "+ name+". The length of the list must be "+natt + "."
        output_att=llm(prompt_att)
        clean_att.append(output_att.replace("[","").replace("]","").replace("\"","").replace(" ","").strip().split(","))
        print(name)

    print("\n Generated Table Names:\n")
    for name in table_names:
        print(name)


    print("\n Generated  attributes: \n")
    for t in clean_att:
        for name in t:
            print(name)
    print("\n")

    values =[]
    st_rows=[]
    atts= ""

    for index,name in enumerate(table_names):   #cicla ogni table
        attributes= clean_att[index]
        rk=False #reference key
        create_t="CREATE TABLE IF NOT EXISTS "
        table_to_crete= name+ " (\n"  + "     id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT" #HARDCODATO
        n_att=0
        attributes= list(set(attributes)) #elimina duplicati
        for attribute in attributes:
            
            if "user" in name:
                if "id" not in attribute:
                    n_att= n_att+1
                    table_to_crete = table_to_crete +  ",\n     "+attribute+" VARCHAR(50)"
            else:
                if "id" in attribute or "ID" in attribute:
                    table_to_crete = table_to_crete +  ",\n     userID INT" 
                    rk=True
                else:
                    n_att= n_att+1
                    table_to_crete = table_to_crete +  ",\n     "+attribute+" VARCHAR(50)"
        if rk==True:
            table_to_crete = table_to_crete +",\n     FOREIGN KEY (userID) REFERENCES users(id)"
        table_to_crete = table_to_crete + "\n);"
        create_t= create_t+table_to_crete
        print(create_t+"\n")
        c.execute(create_t)
        p_att= "["

        #CICLO IN NUMERO DI TUPLE
        for i in range(int(ntup)):
            for attribute in attributes:
                        if "id" not in attribute and "ID" not in attribute:  
                            p_att=p_att+" "+ attribute+str(i+1)+"," #genero la string per il prompt
        p_att=p_att+"]"

        filtered_att=[]
        #rimuovo gli id
        for attribute in attributes:
            if not("id" in attribute or "ID" in attribute):
                filtered_att.append(attribute)
        print("\nATTRIBUTES")
        print(filtered_att)
        print("\n")
       
        prompt_att = "You have a table of a database: "+ str(table_to_crete) + "  create a list with random real examples. The output must be: "+p_att
        print("\n"+prompt_att+"\n")
        output_att=llm2(prompt_att)
        elements =  output_att.replace("[","").replace("]","").replace("\"","").strip().split(",")
        
        print("\nDati:\n")
        count=0
        #genera stringa di attributes
        str_att= ",".join(filtered_att)
        if rk==True:
            str_att= str_att+", userID"
        #genera lista di liste per tupla
        list_tuple= [elements[i:i+n_att] for i in range(0,len(elements),n_att)]
        insert_data= "INSERT INTO "+ name+"( "+str_att+" ) VALUES\n"
        #ciclo le tuple 
        listt_bypass= list_tuple[:int(ntup)] #bypass per svarioni llama
        print(listt_bypass)
        for inx,tupla in enumerate(listt_bypass):
            print(tupla)
            countt=0
            #ciclo gli attributi di una tupla
            for attribute in tupla:
                if name=="user" or rk==False: # se sono user o non ho la RK
                    if countt==0:
                        insert_data= insert_data+" ('"+ attribute+"', '" #se sono un attributo in mezzo
                    elif countt == n_att-1 and inx == int(ntup)-1:
                        insert_data= insert_data+ attribute+"' )\n;\n" #se sono l'ultimo
                    elif countt != n_att-1:
                        insert_data= insert_data+ attribute+"', '"
                    else:
                        insert_data= insert_data+ attribute+"' ),\n" #se sono l'ultimo attribute ma non l'ultima tupla
                    countt=countt+1
                else:
                    if countt==0:
                        insert_data= insert_data+" ('"+ attribute+"', '" #se sono un attributo in mezzo
                    elif countt == n_att-1 and inx == int(ntup)-1:
                        insert_data= insert_data+ attribute #se sono l'ultimo
                        if rk== True:
                            insert_data= insert_data +"', '"+ str(random.randint(1,int(ntup))) #ultimo con rk

                        insert_data= insert_data+ "' )\n;\n" #se sono l'ultimo
                    elif countt != n_att-1:
                        insert_data= insert_data+ attribute+"', '"
                    else:
                        if rk== True:
                            insert_data= insert_data +"', '"+ str(random.randint(1,int(ntup)))
                        insert_data= insert_data+ attribute+"' ),\n" #se sono l'ultimo attribute ma non l'ultima tupla
                    countt=countt+1
                       
        print("\n\n\n"+insert_data)
        c.execute(insert_data)
    conn.commit()
    conn.close()

#------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    DB_esitente = input("Hai un DB? Y o N \n")
    while DB_esitente != "N" and DB_esitente != "Y" and DB_esitente != "n" and DB_esitente != "y":
       DB_esitente = input("\nInput errato! Riprova...\nHai un DB? Y o N \n")

    if DB_esitente == "N" or DB_esitente == "n":
        choose = input("Vuoi un Database creato con solo LLAMA (LLAMA) oppure con l'appoggio di Mockaroo(MOCK)?\n")
        while choose != "LLAMA" and choose != "llama" and choose != "MOCK" and choose != "mock":
            choose = input("Input errato! Vuoi un Database creato con solo LLAMA (LLAMA) oppure con l'appoggio di Mockaroo(MOCK)?\n")
        
        print("creating DB")#CASO NUOVO DATABASE
        if choose=="MOCK" or choose=="mock":
            create_database_mock() #CASO MOCKAROO
        elif choose=="LLAMA" or choose=="llama":
            create_database_full_lama() #CASO FULL LLAMA
    elif DB_esitente == "Y" or DB_esitente == "y":
        import_database() #CASO IMPORT DATABASE
        print("importing DB")


    #comando = "docker cp test:/app/people.db /home/thomas/Desktop/progettoCyber/people.db"
    #output = subprocess.run(comando, shell=True)
    #app.run(debug=True, host='0.0.0.0')

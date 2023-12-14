#from flask import Flask, jsonify
import sqlite3
import random
from faker import Faker
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.llms import LlamaCpp
from langchain.prompts import PromptTemplate


callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
llm2 = LlamaCpp(
    model_path="/home/thomas/Desktop/llama.cpp/models/llama-2-7b-chat.Q4_K_M.gguf",
    temperature=0.75,
    max_tokens=2000,
    top_p=1,
    callback_manager=callback_manager,
    verbose=True,  # Verbose is required to pass to the callback manager
    grammar_path = "list.gbnf"
)
llm = LlamaCpp(
    model_path="/home/thomas/Desktop/llama.cpp/models/dolphin2.1-openorca-7b.Q4_K_M.gguf",
    temperature=0.75,
    max_tokens=2000,
    top_p=1,
    callback_manager=callback_manager,
    verbose=True, 
    grammar_path = "list.gbnf"
)
#app = Flask(__name__)
fake = Faker()

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
    

   
def create_database():
    nt = str(input("quante tabelle vuoi generare?\n"))
    natt = str(input("quanti attributi per ogni tabella?\n"))
    ntup=str(input("quante tuple vuoi generare?\n"))
    conn = sqlite3.connect('fakeDB.db')
    c = conn.cursor()
    prompt= "Generate a list of table names related to a table users. the first table must be users and the others must be related to users. The length of the list must be " + nt + "."
    print(prompt)
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

    values =[]
    st_rows=[]
    atts= ""

    for index,name in enumerate(table_names):   #cicla ogni table
        attributes= clean_att[index]
        rk=False #reference key
        create_t="CREATE TABLE IF NOT EXISTS "
        table_to_crete= name+ " (\n"  + "     id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT" #HARDCODATO
        n_att=0
        
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
        print(create_t)
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
        print("ATTRIBUTES")
        print(filtered_att)

        #inutile
        length_list_att= str(int(ntup)*int(n_att))
        print(length_list_att)

        prompt_att = "You have a table of a database: "+ str(table_to_crete) + "  create a list with random real examples. The output must be: "+p_att
        print(prompt_att)
        output_att=llm2(prompt_att)
        elements =  output_att.replace("[","").replace("]","").replace("\"","").replace(" ","").strip().split(",")
        
        print("Dati:\n")
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
                            insert_data= insert_data +"', '"+ random.randint(1,int(ntup)) #ultimo con rk

                        insert_data= insert_data+ "' )\n;\n" #se sono l'ultimo
                    elif countt != n_att-1:
                        insert_data= insert_data+ attribute+"', '"
                    else:
                        insert_data= insert_data+ attribute+"' ),\n" #se sono l'ultimo attribute ma non l'ultima tupla
                    countt=countt+1
                    
                      

                
        print(insert_data)
        c.execute(insert_data)
    conn.commit()
    conn.close()


    # Return the table as an HTML response
    
if __name__ == '__main__':
    DB_esitente = input("Hai un DB? Y o N \n")
    if DB_esitente == "N":
       print("creating DB")
       create_database()
    else:
        import_database()
        print("importing DB")
    #comando = "docker cp test:/app/people.db /home/thomas/Desktop/progettoCyber/people.db"
    #output = subprocess.run(comando, shell=True)
  
    #app.run(debug=True, host='0.0.0.0')


    

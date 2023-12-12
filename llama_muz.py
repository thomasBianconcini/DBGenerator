from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.llms import LlamaCpp
from langchain.prompts import PromptTemplate

nt = str(input("quante tabelle vuoi generare?\n"))
natt = str(input("quanti attributi per ogni tabella?\n"))



#prompt_t = PromptTemplate(template=template, input_variables=["question","nt","natt"])

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


#prompt = """
 #           Given an input question, generate a list of strings of names related to that question. Write the List between <list></list>.
#            
#            Below are three example Questions and the corresponding outputs. 
#            <example>
#            Question: Give me a list of 3 names related to Users to use as table names in a db.
#            output: <list>name1,name2,name3</list>
#            </example>
#            <example>
#            Question: Give me a list of 4 names related to Users to use as table names in a db.
#            output: <list>name1,name2,name3, name4</list>
#           </example>
#           <example>
#            Question:Generate a list of 5 of random names related to Users to use in a db
#            output: <list>name1,name2,name3, name4, name5</list>
#            </example>
#                        
#            Please provide the SQL query for this question: 
#            Question:Create a list of {nt} random  names to use as table names in a db.
#            List:
#"""

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

values =[]
st_rows=[]
atts= ""

print("Generating values to populate the db...\n")
for index,name in enumerate(table_names):

    #prompt = "Generate a list of 8 random user IDs"



    prompt = "###CONTEXT: I am creating a database. An ID is an integer number. a Date is a date of the calendar. I have the table " + name + "( \n ID INT PRIMARY KEY AUTOINCREMENT "
    for j,att in enumerate(clean_att[index]):
        atts = atts + " " + att
        prompt = prompt + ",\n" + att + " VARCHAR(50)"
    for i in range(0,2):
        prompt = prompt + " ###QUESTION: Generate a list of values to insert in the table. The length of the list must be " +natt +"."
        print("PROMPT COMPOSTO DINAMICAMENTE: " + prompt)
        prompt_val = "Generate a list of values of data to use to populate a row of the table " + name + ". The table has these attributes: "+ atts + " . The length of the list must be " +natt +"."
        output_val = llm(prompt)
        st_rows.append(output_val.replace("[","").replace("]","").replace("\"","").strip().split(","))
    values.append(st_rows)
    st_rows=[]

    

            
    #values.append()

         
   # values.append(st_rows)
   # st_rows=[]

for tr in values:
    for v in tr:
        print(v)
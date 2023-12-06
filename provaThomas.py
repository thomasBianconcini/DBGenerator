from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.llms import LlamaCpp
from langchain.prompts import PromptTemplate
import sqlite3
from faker import Faker

nt = input("quante tabelle vuoi generare?\n")
natt = input("quanti attributi per ogni tabella?\n")
fake = Faker()
template = """Question: {question}

Answer: tables= random1,random2,ranodm3....]"""

template2 = """Question: {question}

Answer: table1= random1,random2,random3... ,
table2= random1,random2,random3...
table3= random1,random2,random3...
table4= random1,random2,random3...
...]"""


prompt_t = PromptTemplate(template=template, input_variables=["question"])
prompt_t2 = PromptTemplate(template=template2, input_variables=["question"])
# Callbacks support token-wise streaming
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# Make sure the model path is correct for your system!
llm = LlamaCpp(
    model_path="/home/thomas/Desktop/llama.cpp/models/llama-2-7b-chat.Q8_0.gguf",
    temperature=0.75,
    max_tokens=2000,
    top_p=1,
    callback_manager=callback_manager,
    verbose=True,  # Verbose is required to pass to the callback manager
)

#prompt = "   Generate me one last list of 4 rows of data to populate each table. The output must be a unique list of strings made only of names."
#llm(prompt)

#prompt_t = "I am creating a fake db about Users. Generate a list of "+ str(nt) +" random names of SQL tables. "

#prompt_at = "Generate one more list of " + str(natt) + " attribute names for each table name you generated in the previouse prompt. "

#prompt_d = "Generate a list of strings of data to insert into the tables you just created. I need 2 rows for each table created. "

prompt_t = f"Generate {nt} names of SQL tables related to a table user (example user.id, first_name, surname, date of birth, city) in a comma-separated format and insert them in the list tables. Do not create duplicates, create {nt} table not more the first must be users. Do not add world just give me a string like that tables= users,profile,...."

#prompt_at = f"Please provide a list of {natt} attribute names for each table, in a comma-separated format."

#prompt_d = "Generate a comma-separated list of data strings to insert into the tables. I need 2 rows for each table."


res = llm(prompt_t)

prompt_t2 = f" Generate {natt} names of SQL attributes for each table in {res}, first attribute of each table must be the id of the table and the second must be user_id  , do not add world just give me a string for each table  like that : Users= user_id,user_name, ... , profile= profile_id, user_id , ... \n "

res2=llm(prompt_t2)
print("\n\n\n\n\n\n\n\n\n\n\n\n"+str(res)+"\n"+str(res2))

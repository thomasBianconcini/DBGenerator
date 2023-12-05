from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import LLMChain
from langchain.llms import LlamaCpp
from langchain.prompts import PromptTemplate

nt = input("quante tabelle vuoi generare?\n")
natt = input("quanti attributi per ogni tabella?\n")

template = """Question: {question}

Answer: Please list the names in a comma-separated format: name1, name2, name3. Output must be only values with nothing more."""

prompt = PromptTemplate(template=template, input_variables=["question"])

# Callbacks support token-wise streaming
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# Make sure the model path is correct for your system!
llm = LlamaCpp(
    model_path="/home/muz/llama.cpp/models/openorca-platypus2-13b.gguf.q4_0.bin",
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

prompt_t = f"Generate {nt} names of SQL tables about Users in a comma-separated format."

#prompt_at = f"Please provide a list of {natt} attribute names for each table, in a comma-separated format."

#prompt_d = "Generate a comma-separated list of data strings to insert into the tables. I need 2 rows for each table."


res = llm(prompt_t)


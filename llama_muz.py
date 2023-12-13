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

nt = str(input("quante tabelle vuoi generare?\n"))
natt = str(input("quanti attributi per ogni tabella?\n"))


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
#el=driver.find_element(By.XPATH,f"//span[contains(., 'Generate fields using AI...')]").click().perform()
#ActionChains(driver).move_to_element(element).click().perform()
#driver.execute_script("arguments[0].click();", el)

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

print("\n\n",types_list, "\n\n")

#driver.quit()#CHIUDE BROWSER--- 

my_key="c1a2daf0"
url = f"""https://api.mockaroo.com/api/generate.json?key={my_key}&fields=["""

i=0
print("\n\nlunghezze liste: \n",len(attribute_list)," (att) - ",  len(types_list), "\n\n")
for idx,el in enumerate(attribute_list):
    url=url+ "{"+f'"name": "{el}","type": "{types_list[i]}"'+"}"                  
    if i!=len(attribute_list)-1:
        url=url+","
    i=i+1
url=url+"]&count="+str(len(attribute_list))
print("\n\n")

payload = {}
headers = {}
response = requests.request("POST", url, headers=headers, data=payload)
dati = json.loads(response.text)
print(dati)


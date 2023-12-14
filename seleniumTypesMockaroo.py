from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import requests
import json
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


clean_att=[["user", "email", "password"],["price", "discount", "likes"]]# LISTA DI LISTE CON ATTRIBUTI(clean_att)---------------------------------
attribute_list = sum(clean_att, [])

input_bar=driver.find_element(By.XPATH,f"//input[contains(@placeholder, 'Examples')]")
input_bar.send_keys(str(attribute_list))
input_bar2=driver.find_element(By.NAME, "count")
input_bar2.clear()
input_bar2.send_keys(str(len(attribute_list)))
driver.find_element(By.XPATH,f"//span[contains(., 'Replace Existing Fields')]").click()
sleep(6)
divs=driver.find_elements(By.XPATH,f"//div/div[contains(@class, 'schema-column')]/div/button/span/div")
types_list=[]
#print("\n\n\n",attribute_list,"\n\n\n")

for div in divs:
    types_list.append(div.text)
#print(types_list)

driver.quit()#CHIUDE BROWSER---

my_key="c1a2daf0"
url = f"""https://api.mockaroo.com/api/generate.sql?key={my_key}&fields=["""

inserts=[]

#{"name": "Packages","type": "Words"},{"name": "Date","type": "Number"}]&count=4
i=0
j=0
for el in clean_att:#per ogni table
    for l in el:#per ogni attributo
        #print("l: ",l,"\ti:",i,"\ttypelist[i]: ",types_list[i])
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

table_names="users"
print(type(inserts))

ins3=[]
for ins in inserts:
    ins2=ins.split(";\n")
    ins3.append(ins2)
#for j in ins3:
#    print(j)
#    print("\n------\n")

inserts_single = sum(ins3, [])

while '' in inserts_single:
    inserts_single.remove('')

for j in inserts_single:
    print(j)
    print("\n------\n")

#url=url+"]&count="+str(len(attribute_list))#NUMERO DI ROW

"""
name_table="users"

coppie_per_sottolista = 3
sottoliste = [
    {k: v for idx, (k, v) in enumerate(d.items()) if idx // coppie_per_sottolista == sublist_idx}
    for d in dati
    for sublist_idx in range(len(d) // coppie_per_sottolista)
]
"""

"""
j=0
k=0
insert_string=f"INSERT INTO {name_table} VALUES "
for el in dati:# per ogni oggetto
    insert_string+="("
    for val in el.values():# per ogni singolo 
        insert_string=insert_string+f'"{val}"'
        if k!=len(el.values())-1:
            insert_string+=", "
        k=k+1
    k=0
    insert_string+=")"
    if j!=len(dati)-1:
        insert_string+=", "
    else:
        insert_string+=";"
    j=j+1

print("\n\nINSERTTT: ",insert_string,"\n\n")
"""

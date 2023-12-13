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
#el=driver.find_element(By.XPATH,f"//span[contains(., 'Generate fields using AI...')]").click().perform()
#ActionChains(driver).move_to_element(element).click().perform()
#driver.execute_script("arguments[0].click();", el)

clean_att=[["user", "email", "password", "customerID", "order"],["price", "discount", "likes", "posts", "numID"]]# LISTA DI LISET CON ATTRIBUTI(clean_att)---------------------------------

attribute_list = sum(clean_att, [])


input_bar=driver.find_element(By.XPATH,f"//input[contains(@placeholder, 'Examples')]")
input_bar.send_keys(str(attribute_list))
input_bar2=driver.find_element(By.NAME, "count")
input_bar2.clear()
input_bar2.send_keys(str(len(attribute_list)))
driver.find_element(By.XPATH,f"//span[contains(., 'Replace Existing Fields')]").click()
sleep(8)
divs=driver.find_elements(By.XPATH,f"//div/div[contains(@class, 'schema-column')]/div/button/span/div")
types_list=[]
#print("\n\n\n",attribute_list,"\n\n\n")

for div in divs:
    types_list.append(div.text)
#print(types_list)

driver.quit()#CHIUDE BROWSER--- 

my_key="c1a2daf0"
url = f"""https://api.mockaroo.com/api/generate.json?key={my_key}&fields=["""

i=0
for el in attribute_list:
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












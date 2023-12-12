from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep
#------------------------------------------------------# SCRIPT SELENIUM#------------------------------------------------------#

#MODIFICHE PER RENDERE SELENIUM UNDETECTABLE
firefox_capabilities = DesiredCapabilities.FIREFOX
firefox_capabilities['marionette'] = False
profile=webdriver.FirefoxProfile()
profile.set_preference("dom.webdriver.enabled", False)
profile.set_preference("useAutomationExtension", False)
profile.update_preferences()

#INIZIO SCRIPT SELENIUM
driver = webdriver.Firefox(firefox_profile=profile)
MOCKAROO_LINK = "https://www.mockaroo.com/"
driver.get(MOCKAROO_LINK)

driver.find_element(By.XPATH,f"//span[contains(., 'Generate fields using AI...')]").click()

input_bar=driver.find_element(By.XPATH,f"//input[contains(@placeholder, 'Examples')]")
input_bar.send_keys('"User", "mail", "password"') #HARDCODATO----------------------------------------------------DA INSERIRE GLI ATTRIBUTI OTTENUTI NEL FORMATO DI ESEMPIO

input_bar2=driver.find_element(By.NAME, "count")
input_bar2.clear()
input_bar2.send_keys('5')#HARDCODATO-----------------------------------------------------------DA INSERIRE IL NUMERO DI ATTRIBUTI SI VOGLIONO (IL NUMERO DI ATTRIBUTI SCRITTI SOPRA)

driver.find_element(By.XPATH,f"//span[contains(., 'Replace Existing Fields')]").click()
sleep(8)

divs=driver.find_elements(By.XPATH,f"//div/div[contains(@class, 'schema-column')]/div/button/span/div")
types=[] #xpath_expression = "//button[contains(@class, 'MuiButtonBase-root') and contains(., 'Generate Fields Using AI')]"

for div in divs:
    types.append(div.text)
print(types)

sleep(200)
driver.quit()
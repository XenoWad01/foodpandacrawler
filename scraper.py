# General / system imports
import os
from dotenv import load_dotenv
import time

# Our imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
import csv

# Load .env 
load_dotenv()


# Config 
CHROME_DRIVER_PATH = os.getenv('ChromeDriverPath', 'nothing here haha xD')
driver = webdriver.Chrome(CHROME_DRIVER_PATH)
wait = WebDriverWait(driver, 10)
actions = ActionChains(driver)


# Function for writing data for one vendor to a csv file 
#  output pe CSV file, fiecare rand sa contina:
# - name
# - address.house_number
# - address.road
# - address.city
# - address.country (numele complet al tarii)
# - address.postcode
# - coords.lat
# - coords.lng (coordonatele nu sunt necesare, poti sa lasi gol gen pui virgule fara text intre ele)
# - description (daca este, daca nu, lasi gol)
# - tags (fiecare tag sa fie separat de o virgula)
def write_vendor_to_file(file, vendor_data):
    header = ['name', 'address.house_number', 'address.road', 'address.city'
          , 'address.country', 'address.postcode', 'coords.lat', 'coords.lng', 'description', 'tags']

    with open('countries.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerows(vendor_data)


# Helper function that checks if element exists (and returns it if it does) by xpath
def check_exists_and_get(xpath):
    try:
        element = wait.until(
            expected_conditions.element_to_be_clickable((By.XPATH, xpath)))
    except Exception:
        return False
    return element


# Helper function that c̶l̶o̶s̶e̶s̶ literally F͟U͟C͟K͟S͟  modals into oblivion if any pop up
def fuck_modal(xpath):
    print(f' -> modal fucking closed, 🔥cunt🔥')
    modal = check_exists_and_get(xpath)
    if modal:
        driver.find_element(By.XPATH, xpath).click()
    else:
        print(' +  gay ass modal will not pop up so we don\'t wait for it, cunt')


# Helper function that extracts vendor info
def extract_vendor_info():
    name_xpath = """/html/body/div[5]/div[2]/div/div[2]/div[1]/div[1]/div/h1""" # As is 
    tags_xpath = """/html/body/div[5]/div[2]/div/div[2]/div[1]/div[1]/ul""" # Needs to be parsed except foodpanda
    adress_string_xpath = """//*[@id="about-panel"]/div[1]/div[2]/p""" # Needs to be split for adress - the country
    maps_image_xpath = """//*[@id="about-panel"]/div[2]/img""" # lat / lng is in img src
    #TODO extract info from these xpaths and return it in a structured vendor_data object
    return None
#  Function for scraping a vendor
def scrape_vendor(vendor):
    # here we can set the xpath of the damn pesky ass modal we want to delete from existance
    xpath_of_modal_to_close = "/html/body/div[1]/div[2]/div/div[2]/div/button"

    print('----------------- ATTEMPTING TO 🔥🔥STEAL🔥🔥 VENDOR DATA -----------------')

    # we get the link of the vendor
    wait.until(expected_conditions.visibility_of_all_elements_located)
    vendor_link = vendor.find_element(By.XPATH, 'a').get_attribute("href")
    print(f' +  got vendor link = {vendor_link}')

    # we now navigate to the page from the link
    driver.get(vendor_link)
    print(f' ->  navigating to {vendor_link}')

    # Fuck modals, just fuck em and fuck foodpanda too. I swear to god this took hours off my life for no logical reason. 
    fuck_modal(xpath_of_modal_to_close)

    # we need to find the info button to click
    info_button = driver.find_element(By.XPATH, '//*[@id="reactRoot"]/main/div/div/section[1]/div[2]/div[1]/div/button[2]')
    print(f' +  found info button')

    # we will now click ze buttOn
    info_button.click()
    print(f' -> clicked info button')
    extracted_info = extract_vendor_info()
    write_vendor_to_file(extracted_info)
    # driver.back() UNDO
    time.sleep(2) ## DELETE after testing that everything works for 1 vendor

# Scraping app
city_to_find = input('Enter city to scrape for\n').lower()
driver.get(f'https://www.foodpanda.ro/city/{city_to_find}')
vendor_list = driver.find_element(By.CLASS_NAME, "vendor-list").find_elements(By.XPATH, 'li')

# Notes:
#   For i in range is needed instead of for in here
#   because the vendor_list elements will be 'stale' on the second pass.
#   When we navigate to a different page and come back we loose the references
#   to the list elements as they technically do not exist anymore
#   so we need to get the list on each iteration.

# We loop through vendors and scrape the fuck out of each of them
# for i in range(len(vendor_list)): UNDO
    # vendors = driver.find_element(By.CLASS_NAME, "vendor-list").find_elements(By.XPATH, 'li') UNDO
    # scrape_vendor(vendors[i]) UNDO
scrape_vendor(vendor_list[1])


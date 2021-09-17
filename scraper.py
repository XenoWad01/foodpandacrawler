# General / system imports
import os
from typing import Match
from dotenv import load_dotenv
import time

# Our imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from postal.parser import parse_address as postal_parse
from postal.expand import expand_address

import csv

# Load .env 
load_dotenv()


# Config 
CHROME_DRIVER_PATH = os.getenv('ChromeDriverPath', 'nothing here haha xD')
driver = webdriver.Chrome(CHROME_DRIVER_PATH)
wait = WebDriverWait(driver, 10)


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

    with open(file, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerow(vendor_data)


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


# Helper function that parses the address into the required format
def parse_address(address_string):
    parsed_address = [None] * 5
    print(address_string)
    result = postal_parse(address_string)

    for field in result:
        key = field[1]
        value = field[0]
        if key == 'house_number':
            parsed_address[0] = value if not parsed_address[0] else parsed_address[0]
        elif key == 'road':
            parsed_address[1] = value if not parsed_address[1] else parsed_address[1]
        elif key == 'city':
            parsed_address[2] = value if not parsed_address[2] else parsed_address[2]
        elif key == 'country':
            parsed_address[3] = value if not parsed_address[3] else parsed_address[3]
        elif key == 'postcode':
            parsed_address[4] = value if not parsed_address[4] else parsed_address[4]
    print(parsed_address)
    return parsed_address


# Helper function that parses coords into required format 
def parse_image(image_element):
    src = image_element.get_attribute('src')
    src = src.split('/')
    result = [src[len(src) - 2], src[len(src) - 1]]
    print(result)

    return result



# Helper function that parses tags into required format
def parse_tags(tag_element):
    tags = []
    tags_li = tag_element.find_elements(By.XPATH, 'li')
    for li in tags_li:
        tag = li.find_element(By.XPATH, 'span').text
        if tag != '$' and tag != 'foodpanda delivery':
            tags.append(tag)
    print(tags)

    return tags


# Helper function that parses extracted data into the required format
def parse_vendor_data(name_h, tags_li, address_p, maps_image):
    print(' -> parsing vendor data')
    name = name_h.text
    address_string = address_p.text
    parsed_address = parse_address(address_string)
    parsed_tags = parse_tags(tags_li)
    parsed_coords = parse_image(maps_image)

    return [name, *parsed_address, *parsed_coords,'', *parsed_tags]


# Helper function that extracts vendor info
def extract_vendor_info():
    print(' +  attempting to extract data')
    # XPATHS
    name_xpath = """/html/body/div[3]/div[2]/div/div[2]/div[1]/div[1]/div/h1""" # As is 
    tags_xpath = """/html/body/div[3]/div[2]/div/div[2]/div[1]/div[1]/ul"""
    adress_string_xpath = """//*[@id="about-panel"]/div[1]/div[2]/p""" # Needs to be split for adress - the country
    maps_image_xpath = """//*[@id="about-panel"]/div[2]/img""" # lat / lng is in img src


    # Notes:
    #       We need to wait for these elements to be visible to access the .text property 
    #   but there are alternatives where the element doesen't need to be visible.
    #   As an optimization try using .get_attribute('textContent') so we dont need to wait
    #   for the component to be visible maybe( if it makes a difference )

    # extract data out of elements
    name = wait.until(expected_conditions.visibility_of_element_located((By.XPATH, name_xpath)))
    tags_li = wait.until(expected_conditions.visibility_of_element_located((By.XPATH, tags_xpath)))
    adress_string = wait.until(expected_conditions.visibility_of_element_located((By.XPATH, adress_string_xpath)))
    maps_image = wait.until(expected_conditions.visibility_of_element_located((By.XPATH, maps_image_xpath)))

    # parse data into required format and return it
    return parse_vendor_data(name, tags_li, adress_string, maps_image)


#  Function for scraping a vendor
def scrape_vendor(vendor):
    # here we can set the xpath of the damn pesky ass modal we want to delete from existance
    xpath_of_modal_to_close = "/html/body/div[1]/div[2]/div/div[2]/div/button"

    print('----------------- ATTEMPTING TO 🔥🔥STEAL🔥🔥 VENDOR DATA -----------------')

    # we get the link of the vendor
    wait.until(expected_conditions.visibility_of_all_elements_located)
    vendor_link = vendor.find_element(By.XPATH, 'a').get_attribute("href")
    print(f' +  found vendor link = {vendor_link}')

    # we now navigate to the page from the link
    driver.get(vendor_link)
    print(f' ->  navigating to {vendor_link}')

    # Fuck modals, just fuck em and fuck foodpanda too. I swear to god this took hours off my life for no logical reason. 
    fuck_modal(xpath_of_modal_to_close)

    # we need to find the info button to click
    info_button = driver.find_element(By.XPATH, '//*[@id="reactRoot"]/main/div/div/section[1]/div[2]/div[1]/div/button[2]')
    print(' +  found info button')

    # we will now click ze buttOn
    info_button.click()
    print(' -> clicked info button')

    # we extract the data out of the elements and parse it into one object
    extracted_info = extract_vendor_info()
    print(' -> extracted data')
    print(extracted_info)

    # we write our vendor data to the file
    write_vendor_to_file('output.csv', extracted_info)
    # print(' -> writing vendor_data to file')
    time.sleep(2)

    # we can then go back to the City page so we can start over again
    driver.back()


# Scraping app
city_to_find = input('Enter city to scrape for\n').lower()
driver.get(f'https://www.foodpanda.ro/city/{city_to_find}')
vendor_list = driver.find_element(By.CLASS_NAME, "vendor-list").find_elements(By.XPATH, 'li')
#
# Notes:
#   For i in range is needed instead of for in here
#   because the vendor_list elements will be 'stale' on the second pass.
#   When we navigate to a different page and come back we loose the references
#   to the list elements as they technically do not exist anymore
#   so we need to get the list on each iteration.

# We loop through vendors and scrape the fuck out of each of them
for i in range(len(vendor_list)):
    vendors = driver.find_element(By.CLASS_NAME, "vendor-list").find_elements(By.XPATH, 'li')
    scrape_vendor(vendors[i])
# scrape_vendor(vendor_list[1])


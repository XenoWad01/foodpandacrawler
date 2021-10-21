# General / system imports
from capcha_passer.bypass_recapcha import solve_captcha
import os
from dotenv import load_dotenv
import time
import dotenv

# Our importorts
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from postal.parser import parse_address as postal_parse
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent

import csv

# Load .env 
load_dotenv()


# Config 
user_agent_provider = UserAgent()
CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', 'CHROME_DRIVER_PATH missing')
driver_options = Options()
driver_options.add_argument("start-maximized")
driver_options.add_argument('--disable-notifications')
driver_options.add_argument("--mute-audio")
driver_options.add_experimental_option("excludeSwitches", ["enable-automation"])
driver_options.add_experimental_option('useAutomationExtension', False)
driver_options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=driver_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

wait = WebDriverWait(driver, 1)
captcha_wait = WebDriverWait(driver, 1)
long_wait = WebDriverWait(driver, 5)
scrapped_results = []
failed_scrapping_results = []
output_file = os.getenv('OUTPUT_FILE_NAME_PREFIX', 'OUTPUT_FILE_NAME_PREFIX missing') + time.strftime("%Y%m%d-%H%M%S")


# Function for writing data for one vendor to a csv file 
def write_vendor_to_file(file, vendor_data):
    header = ['name', 'address.house_number', 'address.road', 'address.city'
          , 'address.country', 'address.postcode', 'coords.lat', 'coords.lng', 'description', 'tags']

    with open(file, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the header
        writer.writerow(header)

        # write multiple rows
        writer.writerow(vendor_data)


# Helper function that writes failed results to a file
def write_failed_to_file(failed_data):
    pass


# Helper function that checks if element exists (and returns it if it does) by xpath
def check_exists_and_get(xpath):
    try:
        element = long_wait.until(
            expected_conditions.element_to_be_clickable((By.XPATH, xpath)))
    except Exception:
        return False
    return element


# Helper function that waits for given element of xpath recursively
def wait_for_element(xpath):
        return wait.until(expected_conditions.visibility_of_element_located((By.XPATH, xpath)))

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
    print(' +  attempting to parse address')
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
    print(' +  attempting to parse image')
    src = image_element.get_attribute('src')
    src = src.split('/')
    result = [src[len(src) - 2], src[len(src) - 1]]
    print(result)

    return result



# Helper function that parses tags into required format
def parse_tags(tag_element):
    print(' +  attempting to parse image')
    tags = []
    tags_li = tag_element.find_elements(By.XPATH, 'li')
    for li in tags_li:
        tag = li.find_element(By.XPATH, 'span').text
        if tag != '$' and tag != 'foodpanda delivery':
            tags.append(tag)
    print(tags)

    return tags

# Helper function that passes extracted data into the required format
def parse_description(description_p):
    print(' +  attempting to parse description')
    # description_p will be none if there is none 
    return None


# Helper function that parses extracted data into the required format
def parse_vendor_data(name_h, tags_li, address_p, maps_image, description_p):
    print(' -> parsing vendor data')
    name = name_h.text
    address_string = address_p.text
    parsed_address = parse_address(address_string)
    parsed_tags = parse_tags(tags_li)
    parsed_coords = parse_image(maps_image)
    parsed_description = parse_description(description_p) if description_p else ''
    return [name, *parsed_address, *parsed_coords,parsed_description , *parsed_tags]


# Helper function that determines if the pesky description element which is very rare is present
def has_optional_description():
    restaurant_info_xpath = """/html/body/div[5]/div[2]/div/div[2]/div[2]/div[1]/div[3]/h2"""
    restaurant_info_xpath2 = """/html/body/div[5]/div[2]/div/div[2]/div[2]/div[1]/div[4]/h2"""
    try:
        if wait.until(expected_conditions.visibility_of_element_located((By.XPATH, restaurant_info_xpath))).text == wait.until(expected_conditions.visibility_of_element_located((By.XPATH, restaurant_info_xpath))).text == 'Restaurant information':
            return True
        return False
    except TimeoutException:
        return False


# Helper function that extracts vendor info
def extract_vendor_info():
    print(' +  attempting to extract data')
    # XPATHS
    name_xpath = """/html/body/div[3]/div[2]/div/div[2]/div[1]/div[1]/div/h1""" # As is
    tags_xpath = """/html/body/div[3]/div[2]/div/div[2]/div[1]/div[1]/ul"""
    adress_string_xpath = """//*[@id="about-panel"]/div[1]/div[2]/p"""
    maps_image_xpath = """//*[@id="about-panel"]/div[2]/img"""
    description = None
    if has_optional_description():
      description = """/html/body/div[5]/div[2]/div/div[2]/div[2]/div[1]/div[3]/p"""

    # Notes:
    #       We need to wait for these elements to be visible to access the .text property 
    #   but there are alternatives where the element doesen't need to be visible.
    #   As an optimization try using .get_attribute('textContent') so we dont need to wait
    #   for the component to be visible maybe( if it makes a difference )

    # we try extract data out of elements
    print(' +  waiting for elemnts to load ...')
    try:
        name = wait_for_element(name_xpath)
        tags_li = wait_for_element(tags_xpath)
        adress_string = wait_for_element(adress_string_xpath)
        maps_image = wait_for_element(maps_image_xpath)
    except TimeoutException:
        print(' +  some elements did not correctly load')
        return None

    # parse data into required format and return it
    return parse_vendor_data(name, tags_li, adress_string, maps_image, description)

# Helper function that waits for and solves captcha if any is present
def solve_captcha_if_any():
    try:
        print(' +  detecting capcha ...')
        is_captcha_present = captcha_wait.until(expected_conditions.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[name^='a-']")))
    except Exception:
        is_captcha_present = False
    if is_captcha_present:
        print(' +  capcha detected')
        print(' -> solving capcha')
        solve_captcha(driver)
    else:
        print(' +  no capcha found')


#  Function for scraping a vendor
def scrape_vendor(vendor):
    # We set the user agent to random one on each request so we don't get are you a robot capcah
    driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": f"{user_agent_provider.random}"}})

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
    solve_captcha_if_any()
    fuck_modal(xpath_of_modal_to_close)
    # we need to find the info button to click
    try:
        info_button = wait_for_element('//*[@id="reactRoot"]/main/div/div/section[1]/div[2]/div[1]/div/button[2]')
    except TimeoutException:
        info_button = None
        print(' -> special exception detected on vendor page, we will ignore this one')

    # if the button is present we click it and go on extracting the vendor info
    if info_button:
        print(' +  found info button')
        info_button.click()
        print(' -> clicked info button')

        # we extract the data out of the elements and parse it into one object
        extracted_info = extract_vendor_info()

        if extracted_info:
            print(' -> successfully extracted vendor info')
            # we add our extracted_info to scrapped_results
            scrapped_results.append(extracted_info)
        else:
            print(' -> something went wrong with extracting vendor info, 🔥ignoring this one🔥 ')
            # we add the url to the failed_scrapping_results array so we knnow which vendors failed
            failed_scrapping_results.append(
                (driver.current_url, 'could not extract vendor_data')
            )
    else:
        print(' +  we could not find the info button, 🔥ignoring this one🔥')
        # we add the url to the failed_scrapping_results array so we knnow which vendors failed
        failed_scrapping_results.append(
            (driver.current_url, 'info_button not found')
        )
    # time.sleep(1000)
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

# we can now write our results to our output file
write_vendor_to_file(output_file, scrapped_results)
write_failed_to_file(failed_scrapping_results)

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

import os
import time,requests
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


def audioToText(driver, mp3Path):
    driver.execute_script('''window.open("","_blank");''')
    driver.switch_to.window(driver.window_handles[1])

    driver.get(googleIBMLink)

    # Upload file 
    time.sleep(1)
    root = driver.find_element_by_id('root').find_elements_by_class_name('dropzone _container _container_large')
    btn = driver.find_element(By.XPATH, '//*[@id="root"]/div/input')
    btn.send_keys(mp3Path)

    # Audio to text is processing
    time.sleep(audioToTextDelay)

    text = driver.find_element(By.XPATH, '//*[@id="root"]/div/div[6]/div/div/div').find_elements_by_tag_name('span')
    result = " ".join( [ each.text for each in text ] )

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return result


def saveFile(content, filename):
    with open(filename, "wb") as handle:
        for data in content.iter_content():
            handle.write(data)



delayTime = 2
audioToTextDelay = 10
filename = 'test.mp3'
googleIBMLink = 'https://speech-to-text-demo.ng.bluemix.net/'

def solve_captcha(driver):
    long_wait = WebDriverWait(driver, 5)
    checkbox = driver.find_element(By.CSS_SELECTOR, """span[role='checkbox']""")
    checkbox.click()
    print(driver.execute_script("return window.frameElement.name"))
    driver.execute_script("return window.frameElement.name")
    print(f'Frame Name : !!{driver.frame.name}')
    audioBtn = long_wait.until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR,"""button[title="Get an audio challenge"]""")))
    print(f'Found audio button!!!')
    audioBtn.click()
    driver.implicitly_wait(1000)
    allIframesLen = driver.find_elements_by_tag_name('iframe')
    audioBtnFound = False
    audioBtnIndex = -1

    for index in range(len(allIframesLen)):
        driver.switch_to.default_content()
        iframe = driver.find_elements_by_tag_name('iframe')[index]
        driver.switch_to.frame(iframe)
        driver.implicitly_wait(delayTime)
        try:
            audioBtn = driver.find_element_by_id('recaptcha-audio-button') or driver.find_element_by_id('recaptcha-anchor')
            audioBtn.click()
            audioBtnFound = True
            audioBtnIndex = index
            break
        except Exception as e:
            pass

    if audioBtnFound:
        try:
            while True:
                href = driver.find_element_by_id('audio-source').get_attribute('src')
                response = requests.get(href, stream=True)
                saveFile(response,filename)
                response = audioToText(driver, os.getcwd() + '/' + filename)
                print(response)

                driver.switch_to.default_content()
                iframe = driver.find_elements_by_tag_name('iframe')[audioBtnIndex]
                driver.switch_to.frame(iframe)

                inputbtn = driver.find_element_by_id('audio-response')
                inputbtn.send_keys(response)
                inputbtn.send_keys(Keys.ENTER)

                time.sleep(2)
                errorMsg = driver.find_elements_by_class_name('rc-audiochallenge-error-message')[0]

                if errorMsg.text == "" or errorMsg.value_of_css_property('display') == 'none':
                    print("Success")
                    break

        except Exception as e:
            print(e)
            print('Caught. Need to change proxy now')
    else:
        print('Button not found. This should not happen.')

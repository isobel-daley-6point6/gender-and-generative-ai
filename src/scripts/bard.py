# Python code taken from AutomateBard.com

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import logging
from datetime import datetime

class QueryBard():
    
    def __init__(self, cookie_value, web_driver, options):
        
        self.__cookie_value=cookie_value
        self.__web_driver=web_driver
        self.__cookie_name = "__Secure-1PSID"
        self.__options = options
        
    def search_bard(self, web_driver, search_string):
        
        search_bar = web_driver.find_element("id", "mat-input-0")
        search_bar.clear()

        # Enter Search String
        search_bar.send_keys(search_string)

        # Submit Search
        search_bar.send_keys(Keys.ENTER)

        # Allow time for Bard to respond
        time.sleep(15.0)

        # Grab response and return
        
        response = web_driver.find_element(By.CLASS_NAME, "model-response-text").text
        
        if response.startswith("I'm Bard, your creative and helpful collaborator. I have limitations and won't always get it right"):
            
            # Sleep for 30 seconds
            time.sleep(240.0)
            
            # Clear search
            search_bar.clear()

            # Enter Search String
            search_bar.send_keys(search_string)

            # Submit Search
            search_bar.send_keys(Keys.ENTER)
            
            # Allow time for Bard to respond
            time.sleep(15.0)
            
            response = web_driver.find_element(By.CLASS_NAME, "model-response-text").text
        
        return response
    
    def connect_bard(self, search_string):
        
        driver = None
        # Create log file
        logging.basicConfig(filename=f'logs/{datetime.now().strftime("%Y%m%d%H%M%S")}_bard.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s')
        
        try:
            driver = webdriver.Chrome(options=self.__options)
            driver.implicitly_wait(1.0)
            
            # Connect to dummy site
            driver.get("https://bard.google.com/u/1/")

            # Add cookie
            driver.add_cookie({
                "name": self.__cookie_name,
                "value": self.__cookie_value
            })
            driver.get("https://bard.google.com/u/1/")

            response = self.search_bard(driver, search_string)

            return response

        except TimeoutException as e:
            retry_time = 10
            time.sleep(retry_time)
            return e
        
        except NoSuchElementException as e:
            retry_time=10
            time.sleep(retry_time)
            return e
        
        except WebDriverException as e:
            retry_time=10
            time.sleep(retry_time)
            return e

        finally:
            if driver is not None:
                driver.close()
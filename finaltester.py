import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

TWITTER_USERNAME = 'guy1021671'
TWITTER_PASSWORD = 'BackCakeDeal48'

# Twitter (X) handle to scrape
TWITTER_HANDLE = '4chan_AI_Terror'
PATH_TO_WEBDRIVER = '/Users/parthgaba/Downloads/chromedriver-mac-x64/chromedriver'

BASE_DOWNLOAD_PATH = 'twitter_data'
IMAGES_DOWNLOAD_PATH = os.path.join(BASE_DOWNLOAD_PATH, 'images')

# Create directories if they do not exist
os.makedirs(IMAGES_DOWNLOAD_PATH, exist_ok=True)

def configure_driver():
    options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": BASE_DOWNLOAD_PATH,
        "download.prompt_for_download": False,
        "directory_upgrade": True,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome()
    return driver

def login_to_twitter(driver):
    driver.get('https://twitter.com/login')
    time.sleep(10)
    
    # Enter username
    username_field = driver.find_element(By.XPATH, '//input[@name="text"]')
    username_field.send_keys(TWITTER_USERNAME)
    driver.find_element(By.XPATH, '//span[text()="Next"]').click()
    time.sleep(5)
    
    # Enter password
    password_field = driver.find_element(By.XPATH, '//input[@name="password"]')
    password_field.send_keys(TWITTER_PASSWORD)
    driver.find_element(By.XPATH, '//span[text()="Log in"]').click()
    time.sleep(10)

def scroll_down(driver):
    driver.execute_script("window.scrollBy(0, 1000);")
    time.sleep(3)

def download_image(img_url, save_path):
    retries = 3
    for i in range(retries):
        try:
            img_data = requests.get(img_url).content
            with open(save_path, 'wb') as handler:
                handler.write(img_data)
            break
        except requests.exceptions.ConnectionError as e:
            if i < retries - 1:
                time.sleep(2)
            else:
                print(f"Failed to download {img_url} after {retries} retries")

def log_progress(image_count):
    with open("progress.log", "w") as log_file:
        log_file.write(str(image_count))

def read_progress():
    if os.path.exists("progress.log"):
        with open("progress.log", "r") as log_file:
            return int(log_file.read())
    return 0

def is_video_thumbnail(img):
    parent_div = img.find_parent('div')
    if parent_div and parent_div.find('svg'):
        return True
    return False

def is_profile_picture(img):
    parent_div = img.find_parent('a')
    if parent_div and 'href' in parent_div.attrs and '/photo' in parent_div['href']:
        return True
    if 'class' in img.attrs:
        for class_name in img['class']:
            if 'avatar' in class_name or 'profile' in class_name:
                return True
    return False

if __name__ == '__main__':
    driver = configure_driver()
    
    try:
        login_to_twitter(driver)
        
        # Navigate to the user's Media tab
        driver.get(f'https://twitter.com/{TWITTER_HANDLE}/media')
        time.sleep(5)
        
        downloaded_images = set()
        scroll_attempts = 0
        total_images_downloaded = read_progress()
        
        while scroll_attempts < 1000 and total_images_downloaded < 7000:  # Adjust as needed
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            images = soup.find_all('img', {'src': True})
            for img in images:
                print("found ",img['src'])
                img_url = img['src']
                if img_url not in downloaded_images:
                    save_path = os.path.join(IMAGES_DOWNLOAD_PATH, f'image_{total_images_downloaded}.jpg')
                    print("saving image to : ",save_path)
                    download_image(img_url, save_path)
                    downloaded_images.add(img_url)
                    total_images_downloaded += 1
                    print("down loaded :",total_images_downloaded)
                    if total_images_downloaded >= 3:
                        break
                '''if img_url not in downloaded_images and not is_video_thumbnail(img) and not is_profile_picture(img):
                    save_path = os.path.join(IMAGES_DOWNLOAD_PATH, f'image_{total_images_downloaded}.jpg')
                    download_image(img_url, save_path)
                    downloaded_images.add(img_url)
                    total_images_downloaded += 1
                    log_progress(total_images_downloaded)
                    if total_images_downloaded >= 7000:
                        break
                '''
            scroll_down(driver)
            scroll_attempts += 1

    finally:
        driver.quit()

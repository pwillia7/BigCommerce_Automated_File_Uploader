import os
import sys
import json
import time
import base64
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import argparse

# Load configuration from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

username = config['username']
password = config['password']
store_hash = config['store_hash']
start_product_id = config['start_product_id']
end_product_id = config['end_product_id']
driver_path = config['driver_path']

# Argument parsing
parser = argparse.ArgumentParser(description='Upload files to BigCommerce products.')
parser.add_argument('folder_path', type=str, help='Path to the folder containing product subfolders')
parser.add_argument('identifier_type', type=str, choices=['id', 'sku', 'name'], help='Type of identifier (id, sku, name) used for subfolder names')
args = parser.parse_args()

folder_path = os.path.abspath(args.folder_path)
identifier_type = args.identifier_type

# Store URL
store_url = f'https://store-{store_hash}.mybigcommerce.com/manage/products/edit/'

# Initialize the Chrome driver
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

def wait_for_angular(driver):
    driver.execute_script("""
    return new Promise((resolve, reject) => {
        if (window.getAllAngularTestabilities) {
            window.getAllAngularTestabilities().forEach((testability) => {
                testability.whenStable(resolve);
            });
        } else {
            resolve();
        }
    });
    """)

def click_element(driver, by, value):
    element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((by, value)))
    driver.execute_script("arguments[0].click();", element)

def get_files_for_product(folder_path, identifier):
    product_folder = os.path.join(folder_path, identifier)
    if os.path.isdir(product_folder):
        return [os.path.join(product_folder, f) for f in os.listdir(product_folder) if os.path.isfile(os.path.join(product_folder, f))]
    else:
        return []

def upload_file(driver, file_path):
    with open(file_path, 'rb') as file:
        file_data = file.read()
    
    file_name = os.path.basename(file_path)
    file_data_base64 = base64.b64encode(file_data).decode('utf-8')
    script = """
    var target = document.getElementById('productInput-upload_file_from_computer');
    var file_data_base64 = arguments[0];
    var file_name = arguments[1];
    
    var byteCharacters = atob(file_data_base64);
    var byteNumbers = new Array(byteCharacters.length);
    for (var i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    var byteArray = new Uint8Array(byteNumbers);
    var file = new File([byteArray], file_name);
    
    var dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    
    var dragoverEvent = new DragEvent('dragover', {
        dataTransfer: dataTransfer
    });
    target.dispatchEvent(dragoverEvent);

    var dropEvent = new DragEvent('drop', {
        dataTransfer: dataTransfer
    });
    target.dispatchEvent(dropEvent);
    """
    driver.execute_script(script, file_data_base64, file_name)

try:
    # Navigate to the login page
    driver.get(f'https://store-{store_hash}.mybigcommerce.com/manage')
    
    # Wait for the page to load
    time.sleep(5)
    
    # Enter login credentials
    driver.find_element(By.ID, 'user_email').send_keys(username)
    driver.find_element(By.ID, 'user_password').send_keys(password)
    driver.find_element(By.NAME, 'commit').click()
    
    # Wait for user to complete 2FA
    input("Complete the 2FA process and press Enter to continue...")

    for product_id in range(start_product_id, end_product_id + 1):
        try:
            # Navigate to the product page
            driver.get(f'{store_url}{product_id}')

            # Wait for the page to load
            time.sleep(2)

            # Switch to the iframe containing the necessary elements
            iframe = driver.find_element(By.ID, 'content-iframe')
            driver.switch_to.frame(iframe)

            # Get the identifier based on user input
            if identifier_type == 'id':
                identifier = str(product_id)
            elif identifier_type == 'sku':
                identifier = driver.find_element(By.ID, 'productInput-sku').get_attribute('value')
            elif identifier_type == 'name':
                identifier = driver.find_element(By.ID, 'productInput-name').get_attribute('value')

            # Get files to upload
            files_to_upload = get_files_for_product(folder_path, identifier)
            if not files_to_upload:
                print(f"No files found for product with {identifier_type}: {identifier}")
                continue

            for file_path in files_to_upload:
                # Click the Files sidebar element to ensure the upload button is rendered
                click_element(driver, By.XPATH, "//div[contains(text(), 'Files')]")
                time.sleep(2)  # Wait for the upload button to be rendered

                # Open the upload file modal
                click_element(driver, By.XPATH, "//div[@class='addEditFiles-buttons']/button[@id='addEditImages-add-button']")
                print(f'Product ID {product_id}: Upload modal opened.')
                time.sleep(2)

                # Upload the file using the dynamically created file input
                upload_file(driver, os.path.abspath(file_path))
                print(f'Uploaded file: {os.path.abspath(file_path)}')
                
                # Click the save button within the modal
                click_element(driver, By.XPATH, "/html/body/section/div/div[2]/form/div[5]/button[2]")
                print(f'File saved: {os.path.abspath(file_path)}')
                
                # Wait for the modal to close
                time.sleep(2)

            # Click the final save button
            click_element(driver, By.XPATH, '//*[@id="add-edit-contents"]/form/div[11]/div/div/button[1]')
            print(f'Product ID {product_id}: All files uploaded and final save completed.')

            # Wait a few seconds before moving to the next product
            time.sleep(5)
        
        except Exception as e:
            print(f'Error handling Product ID {product_id}: {e}')
        
        finally:
            # Switch back to the default content
            driver.switch_to.default_content()

finally:
    driver.quit()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from flask import Flask, jsonify
from dotenv import load_dotenv
import requests as r
import os

load_dotenv()
app = Flask(__name__)

@app.route('/vars', methods=['GET'])
def vars():
  print(os.getenv('URL_LOGIN'))
  print(os.getenv('URL_DATA'))
  print(os.getenv('USERNAME'))
  print(os.getenv('PASSWORD'))
  print(os.getenv('EXTRA_HEADER'))

  return jsonify(os.getenv('URL_DATA'))

@app.route('/get-text', methods=['GET'])
def get_text():

  # Driver's options
  chrome_options = Options()
  chrome_options.add_argument("--headless=new")
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument("--disable-extensions")
  chrome_options.add_argument("--disable-dev-shm-usage")

  # Init web driver
  service = Service('./chromedriver-win64/chromedriver.exe')
  driver = webdriver.Chrome(service=service, options=chrome_options)

  driver.get(os.getenv('URL_LOGIN'))

  input1 = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '[formcontrolname="username"]'))
  )
  input2 = WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '[formcontrolname="password"]'))
  )

  # Complete inputs
  input1.send_keys(os.getenv('EMAIL'))
  input2.send_keys(os.getenv('PASSWORD'))

  WebDriverWait(driver, 5).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, '[type="submit"]'))
  ).click()

  WebDriverWait(driver, 5).until(lambda d: len(d.get_cookies()) > 0)

  all_cookies = driver.get_cookies()
  driver.quit()

  # Get cookie in a string to put in headers
  cookies_str = ''
  for cookie in all_cookies:
    cookies_str = cookies_str + cookie['name'] + '='+ cookie['value'] + ';'

  # Request to get payments
  s = r.Session()
  s.headers.update({ 'Cookie': cookies_str })
  s.headers.update({ 'Usuario-Extra': os.getenv('EXTRA_HEADER') })
  res1 = s.get(os.getenv('URL_DATA'))

  payments = res1.text

  return jsonify(payments)

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000)
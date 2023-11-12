import time

from datetime import datetime, timedelta
import pytz

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By

def pretty_print_time_to_midnight():
    paris_tz = pytz.timezone('Europe/Paris')
    now = datetime.now(paris_tz)

    tomorrow = now.date() + timedelta(days=1)
    midnight = paris_tz.localize(datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0))

    remaining_time = midnight - now

    hours, remainder = divmod(remaining_time.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    print(f"Remaining time: {hours}h {minutes}min {seconds}s")

def extract_guess(soup):
    word = soup.find('td', {'class': 'word'})
    if not word:
        return None

    word = word.get_text(strip=True)

    numbers = soup.find_all('td', {'class': 'number'})
    try:
        temperature = float(numbers[-2].get_text(strip=True))
        pourcent = int(numbers[-1].get_text(strip=True))
    except ValueError:
        return None

    emoji = soup.find('td', {'class': 'emoji'}).get_text(strip=True)

    return (word, temperature, emoji, pourcent)

def extract_guesses(soup):
    table = soup.find('table', {'id': 'cemantix-guessable'})

    top_guess_soup = table.thead.find('tr', {'class': 'guesses'})

    guesses = [extract_guess(top_guess_soup)]
    for row in table.tbody.find_all('tr'):
        guesses.append(extract_guess(row))

    guesses = sorted(set(filter(bool, guesses)), key=lambda x: x[-1], reverse=True)
    return guesses



# create a new instance of the Firefox driver
driver = webdriver.Firefox()

dt = 0.1
driver.get("https://cemantix.certitudes.org/")

time.sleep(dt)
driver.find_element(By.ID, 'dialog-close').click()

time.sleep(dt)
driver.find_element(By.ID, "cloud-button").click()

time.sleep(dt)
driver.find_element(By.ID, "start").click()

time.sleep(dt)
token = driver.find_element(By.ID, "code").get_attribute("value")

time.sleep(dt)
driver.find_element(By.ID, 'dialog-close').click()

print(token)
pretty_print_time_to_midnight()

prev_state = driver.find_element_by_id('cemantix-guessable').get_attribute('outerHTML')
while True:
    time.sleep(5)
    cur_state = driver.find_element_by_id('cemantix-guessable').get_attribute('outerHTML')
    if cur_state != prev_state:
        soup = BeautifulSoup(cur_state, 'html.parser')
        guesses = extract_guesses(soup)
        print('-----------')
        for guess in guesses:
            print(guess)
        if guesses[0][-1] == 1000:
            print("Word found, killing session...")
            break
        prev_state = cur_state

driver.close()

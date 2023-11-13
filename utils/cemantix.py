import time
from datetime import datetime, timedelta
from threading import Thread

import pytz

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By

class CemantixSession(Thread):
    delay = 0.1

    def __init__(self):
        super().__init__()
        self.driver = None
        self.token = None
        self.guesses = None

        self.create_session()

    def __del__(self):
        if self.driver is not None:
            self.driver.close()
            self.driver = None

    def create_session(self):
        self.driver = driver = webdriver.Firefox()

        driver.get("https://cemantix.certitudes.org/")

        time.sleep(self.delay)
        driver.find_element(By.ID, 'dialog-close').click()

        time.sleep(self.delay)
        driver.find_element(By.ID, "cloud-button").click()

        time.sleep(self.delay)
        driver.find_element(By.ID, "start").click()

        time.sleep(self.delay)
        self.token = driver.find_element(By.ID, "code").get_attribute("value")

        time.sleep(self.delay)
        driver.find_element(By.ID, 'dialog-close').click()

        return self

    def run(self):
        self._pretty_print_time_to_midnight()

        prev_state = self.driver.find_element_by_id('cemantix-guessable').get_attribute('outerHTML')

        while True:
            time.sleep(10)
            cur_state = self.driver.find_element_by_id('cemantix-guessable').get_attribute('outerHTML')
            if cur_state != prev_state:
                soup = BeautifulSoup(cur_state, 'html.parser')
                guesses = self._extract_guesses(soup)
                self.guesses = guesses
                print('-----------')
                for guess in guesses:
                    print(guess)
                if guesses[0][-1] == 1000:
                    print("Word found, killing session...")
                    break
                prev_state = cur_state

        self.driver.close()
        self.driver = None

    def _pretty_print_time_to_midnight(self):
        paris_tz = pytz.timezone('Europe/Paris')
        now = datetime.now(paris_tz)

        tomorrow = now.date() + timedelta(days=1)
        midnight = paris_tz.localize(datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0))

        remaining_time = midnight - now

        hours, remainder = divmod(remaining_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        print(f"Remaining time: {hours}h {minutes}min {seconds}s")

    def _extract_guess(self, soup):
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

    def _extract_guesses(self, soup):
        table = soup.find('table', {'id': 'cemantix-guessable'})

        top_guess_soup = table.thead.find('tr', {'class': 'guesses'})

        guesses = [self._extract_guess(top_guess_soup)]
        for row in table.tbody.find_all('tr'):
            guesses.append(self._extract_guess(row))

        guesses = sorted(set(filter(bool, guesses)), key=lambda x: x[-1], reverse=True)
        return guesses

if __name__ == '__main__':
    session = CemantixSession()
    session.run()

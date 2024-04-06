import time
from datetime import datetime, timedelta
from threading import Thread, Lock

import pytz

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import WebDriverException, NoSuchElementException

class CemantixSession(Thread):
    timezone = pytz.timezone('Europe/Paris')
    game_name = 'cemantix'
    game_url = "https://cemantix.certitudes.org/"
    delay = 0.2

    def __init__(self):
        super().__init__()

        self.driver = None
        self.token = None
        self.guesses = None

        self.lock = Lock()

        self.game_end_time = self.determine_game_end_time()

        self.create_session()

    def __del__(self):
        self.close()

    @property
    def has_guesses(self):
        return self.guesses and self.guesses[0]

    @property
    def best_guess(self):
        return self.guesses[0] if self.has_guesses else None

    @property
    def solution_found(self):
        return self.has_guesses and self.best_guess[-1] == 1000

    @property
    def time_is_over(self):
        return self.remaining_time().total_seconds() <= 0

    @property
    def game_is_over(self):
        return self.solution_found or self.time_is_over

    @classmethod
    def now(cls):
        return datetime.now(cls.timezone)

    @classmethod
    def determine_game_end_time(cls):
        tomorrow = cls.now().date() + timedelta(days=1)
        midnight = cls.timezone.localize(datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0, 0))
        return midnight

    def remaining_time(self):
        return self.game_end_time - self.now()

    def remaining_time_str(self):
        remaining_time = self.remaining_time()
        hours, remainder = divmod(remaining_time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}min {seconds}s"

    def create_session(self):
        service = Service(executable_path='/usr/local/bin/geckodriver', log_output='/home/freebox/ljk-slack-bot/geckodriver.log')
         
        options = webdriver.FirefoxOptions()
        options.add_argument('-headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')

        self.driver = driver = webdriver.Firefox(options=options, service=service)

        driver.get(self.game_url)

        time.sleep(self.delay)
        try:
            if btn := driver.find_element(By.CSS_SELECTOR, ".fc-button.fc-cta-do-not-consent.fc-secondary-button"):
                btn.click()
        except NoSuchElementException:
            pass

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

        self.running = True

        return self

    def close(self):
        with self.lock:
            self.running = False
            if self.driver is not None:
                self.driver.close()
                self.driver = None
        return self

    def run(self):
        prev_state = self.driver.find_element_by_id(f'{self.game_name}-guessable').get_attribute('outerHTML')

        while not self.game_is_over:
            # make the thread sleep 10s
            for i in range(100):
                time.sleep(0.1)
                if not self.running:
                    return

            self.lock.acquire()
            if self.driver is None:
                return

            # click on reveal solution if solution was found
            try:
                if btn := self.driver.find_element(By.ID, f'{self.game_name}-reveal'):
                    btn.click()
                    time.sleep(self.delay)
                if btn := self.driver.find_element(By.ID, f'{self.game_name}-guess-btn'):
                    btn.click()
                    time.sleep(self.delay)
            except WebDriverException:
                pass

            # show all close words is solution was found
            try:
                if btn := self.driver.find_element(By.ID, f'{self.game_name}-see'):
                    btn.click()
                    time.sleep(self.delay)
            except WebDriverException:
                pass

            # extract current guesses
            cur_state = self.driver.find_element_by_id(f'{self.game_name}-guessable').get_attribute('outerHTML')
            if cur_state != prev_state:
                soup = BeautifulSoup(cur_state, 'html.parser')
                guesses = self._extract_guesses(soup, self.game_name)
                self.guesses = guesses
                prev_state = cur_state

            self.lock.release()

        return self.close()

    @classmethod
    def _extract_guess(cls, soup):
        word = soup.find('td', {'class': 'word'})
        if not word:
            return None

        word = word.get_text(strip=True)

        numbers = soup.find_all('td', {'class': 'number'})
        try:
            temperature = float(numbers[-2].get_text(strip=True))
            percent = int(numbers[-1].get_text(strip=True))
        except ValueError:
            return None

        emoji = soup.find('td', {'class': 'emoji'}).get_text(strip=True)

        return (word, temperature, emoji, percent)

    @classmethod
    def _extract_guesses(cls, soup, game_name):
        table = soup.find('table', {'id': f'{game_name}-guessable'})

        top_guess_soup = table.thead.find('tr', {'class': 'guesses'})

        guesses = [cls._extract_guess(top_guess_soup)]
        for row in table.tbody.find_all('tr'):
            guesses.append(cls._extract_guess(row))

        guesses = sorted(set(filter(bool, guesses)), key=lambda x: x[-1], reverse=True)
        return guesses


class CemantleSession(CemantixSession):
    timezone = pytz.timezone('America/Los_Angeles')
    game_name = 'cemantle'
    game_url = "https://cemantle.certitudes.org/"


if __name__ == '__main__':
    session = CemantixSession()
    session.start()

    session = CemantleSession()
    session.start()

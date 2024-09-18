import tkinter as tk
from tkinter import ttk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import sys
import os
import datetime
from tkcalendar import DateEntry
import threading


class SeleniumTkinterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Selenium Tkinter App")

        self.label_username = ttk.Label(root, text="Username:")
        self.label_password = ttk.Label(root, text="Password:")
        self.label_start_time = ttk.Label(root, text="Start Time:")
        self.label_end_time = ttk.Label(root, text="End Time:")
        self.label_chosen_date = ttk.Label(root, text="Chosen Date:")

        self.entry_username = ttk.Entry(root)
        self.entry_username.insert(0, "TRAFCONMJ3")
        self.entry_password = ttk.Entry(root, show="*")

        self.chosen_date_var = tk.StringVar()
        self.chosen_date_var.set(datetime.date.today())
        self.chosen_date_entry = DateEntry(root, textvariable=self.chosen_date_var, date_pattern="yyyy-mm-dd")

        self.start_time_var = tk.StringVar()
        self.start_time_var.set("00:00")
        self.start_time_dropdown = ttk.Combobox(root, textvariable=self.start_time_var, values=self.get_hour_ranges())

        self.end_time_var = tk.StringVar()
        self.end_time_var.set("00:00")
        self.end_time_dropdown = ttk.Combobox(root, textvariable=self.end_time_var, values=self.get_hour_ranges())

        self.button_login = ttk.Button(root, text="Login", command=self.start_selenium_thread)

        self.label_username.grid(row=0, column=0, pady=5, sticky=tk.E)
        self.entry_username.grid(row=0, column=1, pady=5)
        self.label_password.grid(row=1, column=0, pady=5, sticky=tk.E)
        self.entry_password.grid(row=1, column=1, pady=5)
        self.label_chosen_date.grid(row=2, column=0, pady=5, sticky=tk.E)
        self.chosen_date_entry.grid(row=2, column=1, pady=5)
        self.label_start_time.grid(row=3, column=0, pady=5, sticky=tk.E)
        self.start_time_dropdown.grid(row=3, column=1, pady=5)
        self.label_end_time.grid(row=4, column=0, pady=5, sticky=tk.E)
        self.end_time_dropdown.grid(row=4, column=1, pady=5)
        self.button_login.grid(row=5, column=1, pady=10)

    def get_hour_ranges(self):
        return [f"{hour:02d}:00-{hour:02d}:59" for hour in range(24)]

    def start_selenium_thread(self):
        selenium_thread = threading.Thread(target=self.perform_login)
        selenium_thread.start()

    def perform_login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        start_time = self.start_time_var.get()
        end_time = self.end_time_var.get()
        chosen_date = self.chosen_date_var.get()

        start_hour = int(start_time.split(":")[0])
        end_hour = int(end_time.split(":")[0])

        self.run_selenium(username, password, start_hour, end_hour, chosen_date)

    def run_selenium(self, username, password, start_hour, end_hour, chosen_date):

        chosen_date = datetime.datetime.strptime(chosen_date, '%Y-%m-%d').date()
        current_date = chosen_date
        next_day_date = current_date + datetime.timedelta(days=1)

        next_day = next_day_date.isoweekday()
        next_day_str = str(next_day)
        day_of_week = str(current_date.isoweekday())

        first_day_of_month = current_date.replace(day=1)
        first_day_of_week = first_day_of_month.isoweekday()

        week_number = (current_date.day + first_day_of_week - 2) // 7 + 1
        week_number_str = str(week_number)

        next_week = (next_day_date.day + first_day_of_week - 2) // 7 + 1
        next_week_str = str(next_week)

        if next_day_date.month == current_date.month and next_week > week_number:
            next_week += 1

        if getattr(sys, 'frozen', False):
            # If running in a bundled executable
            script_dir = sys._MEIPASS
        else:
            # If running in a script
            script_dir = os.path.dirname(os.path.abspath(__file__))
        webdriver_path = os.path.join(script_dir, 'chromedriver.exe')
        driver_path = webdriver_path
        url = 'https://ebrama.baltichub.com/login'

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-gpu')

        # Use Service object instead of executable_path
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        try:
            driver.get(url)

            username_input = driver.find_element(By.ID, "UserName")
            username_input.send_keys(username)

            password_input = driver.find_element(By.ID, "Password")
            password_input.send_keys(password)

            login_button = driver.find_element(By.ID, "loginBtn")
            login_button.click()

            # Wait for the side menu to load
            xpath_element = '//*[@id="side-menu"]/li[6]/a'
            new_page_element = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, xpath_element))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", new_page_element)

            try:
                new_page_element.click()  # Try normal click
            except:
                driver.execute_script("arguments[0].click();", new_page_element)  # Use JavaScript click if normal click is intercepted

            # Wait for the submenu to be clickable
            submenu_xpath = '/html/body/div[5]/nav/div/ul/li[6]/ul/li[2]/a'
            submenu_element = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, submenu_xpath))
            )

            # Again, try to click or use JavaScript to click if intercepted
            try:
                submenu_element.click()
            except:
                driver.execute_script("arguments[0].click();", submenu_element)

            xpath_element = '//*[@id="Grid"]/div/div/div/div[1]/table/tbody/tr/td[7]/div[1]/div[1]/a'
            new_page_element = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, xpath_element))
            )
            new_page_element.click()

            while True:
                try:
                    test = '//*[@id="av-slots"]/div[1]/span/button'
                    test_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, test))
                    )
                except Exception as e:
                    print("not loaded")
                try:
                    # Click on the next day in the slot selector
                    xpath_element = '//*[@id="slotSelector"]/div/ul/li[1]/div/div[1]/table/tbody/tr[' + next_week_str + ']/td[' + next_day_str + ']'
                    new_page_element = WebDriverWait(driver, 60).until(
                        EC.presence_of_element_located((By.XPATH, xpath_element))
                    )
                    new_page_element.click()
                except Exception as e:
                    print("dzien nastepny")
                try:
                    test = '//*[@id="av-slots"]/div[1]/span/button'
                    test_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, test))
                    )
                except Exception as e:
                    print("not loaded")
                try:
                    # Click on the current day in the slot selector
                    xpath_element = '//*[@id="slotSelector"]/div/ul/li[1]/div/div[1]/table/tbody/tr[' + week_number_str + ']/td[' + day_of_week + ']'
                    new_page_element = WebDriverWait(driver, 60).until(
                        EC.presence_of_element_located((By.XPATH, xpath_element))
                    )
                    new_page_element.click()
                except Exception as e:
                    print("dzien nastepny")
                for i in range(start_hour + 1, end_hour + 2):
                    element = '//*[@id="av-slots"]/div[' + str(i) + ']/span/button'
                    try:
                        page_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, element))
                        )

                        # Check if the button is both displayed and enabled
                        if page_element.is_displayed() and page_element.is_enabled():
                            # Button is enabled, perform the click action
                            page_element.click()
                            page_element.send_keys(Keys.ENTER)
                            # page_element.send_keys(Keys.ENTER)
                            print(f"Index {i} is clickable")
                        else:
                            print(f"Element at index {i} is not clickable (not displayed or not enabled)")

                    except Exception as e:
                        print(f"Exception occurred: {e}")
        finally:
            driver.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = SeleniumTkinterApp(root)
    root.mainloop()

import time
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import stealth_sync
import csv


def build_url(name, city, prop):
    url_name = name.replace(" ", "%20")
    url_city = city.replace(" ", "%20") + ",%20" + prop
    search_url = "https://www.truepeoplesearch.com/results?name=" + url_name + "&citystatezip=" + url_city
    return search_url

def get_info(search_url):
    print("Go to Search Url")
    page.goto(search_url)
    print("Arrive Search Url")

    try:
        print("Find Detail Button")
        detail_button = page.wait_for_selector('a[aria-label="View All Details"]')
        print("Placed Detail Button")

        print("Click Detail Button")
        detail_button.click()
        print("Clicked Detail Button")

        print("Find Phone elements")
        phone_elements = page.query_selector_all('span[itemprop="telephone"]')
        print("Placed Phone elements")
        phone_numbers = []
        if len(phone_elements):
            for element in phone_elements:
                phone_number = page.evaluate('(element) => element.textContent', element)
                phone_numbers.append(phone_number)
        else:
            print("There are no phone numbers")
        print("phone numbers", phone_numbers)

        print("Find Email elements")
        email_elements = page.query_selector_all('.col > div:last-child:has-text("@")')
        emails = []
        for element in email_elements:
            text = page.evaluate('(element) => element.textContent', element).strip()
            if text != "support@truepeoplesearch.com" and emails.count(text) == 0:
                emails.append(text)
        if len(emails) == 0:
            print("There are no emails")
        print("emails", emails)

        return(phone_numbers, emails)
    
    except Exception as e:
        print(e)

def read_csv(file):
    with open(file, 'r') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]
    return data

def write_csv(file, data):
    with open(file, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

if __name__ == "__main__": 
    file = "temp50.csv"
    input_data = read_csv(file)
    output_data = []
    
    browser = sync_playwright().start().firefox.launch(headless=True, slow_mo=120)
    context = browser.new_context(
        proxy={
            "server": f"205.161.78.131:6383",
            "username": "BEUXY836",
            "password": "DHIQY137",
        }
    )

    page = context.new_page()
    page.set_default_timeout(5000)
    page.set_default_navigation_timeout(5000)
    stealth_sync(page)

    start = time.time()
    for item in input_data:
        name = item["Full Name"]
        city = item["Property City"]
        prop = item["Property State"]

        print(name)
        start_time = time.time()

        try:
            url = build_url(name, city, prop)
            phone_numbers, emails = get_info(url)
            i = 1
            while len(phone_numbers):
                phone = phone_numbers.pop(0)
                if i < 7:
                    item["Phone "+str(i)] = phone
                    i += 1
            j = 1
            while len(emails):
                email = emails.pop(0)
                if j < 3:
                    item["Email "+str(j)] = email
                    j += 1
        except Exception as e:
            print(e)
            with open("error.txt", "a") as errorfile:
                errorfile.write(name+"\n")
        output_data.append(item)
        end_time = time.time()

        elapsed_time = end_time - start_time

        print(f"Elapsed time: {elapsed_time} seconds\n\n")

    write_csv("output.csv", output_data)

    end = time.time()
    gap = end - start
    print(f"Total time: {gap} seconds\n\n")

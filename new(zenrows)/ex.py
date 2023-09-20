from bs4 import BeautifulSoup
import re


with open("html.txt", "r", encoding="UTF-8") as file:
    html = file.read()



age_regex = re.compile(r'Age \d+ \([A-Za-z]{3} \d+\)')

detail_soup = BeautifulSoup(html, 'html.parser')

owner = detail_soup.select_one('h1.oh1')
print(owner.text)
  
age_span_1 = detail_soup.find('span', string=age_regex)    
print(age_span_1.text.strip())

phone_numbers_1 = []
phone_divs = detail_soup.select('div.row div.col-12')
for phone_div in phone_divs:
    try:
        phone_span = phone_div.select_one('a[data-link-to-more="phone"] span[itemprop="telephone"]')
        phone = phone_span.text.strip()

        phone_type_span = phone_div.select_one('span.smaller')
        phone_type = phone_type_span.text.strip()

        phone_info = f"{phone} - {phone_type}"
        if phone_info not in phone_numbers_1:
            phone_numbers_1.append(phone_info)
    except:
        pass
print(phone_numbers_1)

emails_1 = []
email_divs = detail_soup.select('.col > div:last-child')
for email_div in email_divs:
    text = email_div.text.strip()
    if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
        if text != "support@truepeoplesearch.com" and text not in emails_1:
            emails_1.append(text)

print(emails_1)
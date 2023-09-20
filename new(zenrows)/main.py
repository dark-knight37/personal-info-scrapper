import time
import re
import openpyxl
from zenrows import ZenRowsClient
from bs4 import BeautifulSoup

zenrows_key = ""

def read_xlsx(file):
    wb = openpyxl.load_workbook(file)
    worksheet = wb.active
    keys = []
    data = []
    for row in worksheet.iter_rows():
        if len(keys):
            line = {}
            i = 0
            for cell in row:
                line[keys[i]] = cell.value
                i += 1
            data.append(line)
        else:
            for cell in row:
                keys.append(cell.value)
    return data

def check_entity(name):
    if "Corp" in name or "LLC" in name or "LP" in name:
        return 1
    else:
        return 0

def build_url(data, entity_type, owner_num):
    if entity_type:
        address = data["Mailing Address"]
        citystatezip = data["Mailing City St  Zip"]
        search_url = "https://www.truepeoplesearch.com/resultaddress?streetaddress=" + address.replace(" ", "%20") + "&citystatezip=" + citystatezip.replace(" ", "%20")
    else:
        if owner_num == 1:
            name = data["Owner name 01"]
        if owner_num == 2:
            name = data["Owner name 02"]
        citystatezip = data["Mailing City St  Zip"]
        search_url = "https://www.truepeoplesearch.com/resultaddress?name=" + name.replace(" ", "%20") + "&citystatezip=" + citystatezip.replace(" ", "%20")

    return search_url


def scrap(data, client, params):
    age_regex = re.compile(r'Age \d+ \([A-Za-z]{3} \d+\)')

    first_name = data["Owner name 01"]
    entity_type = check_entity(first_name)

    search_url = build_url(data, entity_type, 1)

    print("\n\n")
    print(first_name)
    print(search_url)

    response = client.get(search_url, params=params)

    soup = BeautifulSoup(response.text, 'html.parser')
    a_tag = soup.find('a', {'class': 'btn btn-success btn-lg detail-link shadow-form'})

    try:
        detail_url = "https://www.truepeoplesearch.com" + a_tag['href']

        print(detail_url)

        detail_response = client.get(detail_url, params=params)

        with open("html.txt", "w", encoding="UTF-8") as output:
            output.write(detail_response.text)

        detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
        
        owner = detail_soup.select_one('h1.oh1')
        if entity_type:
            data["Entity Owner's Name (Only if ENTITY)"] = owner
        
        age_span_1 = detail_soup.find('span', string=age_regex)    
        data["Age1"] = age_span_1.text.strip()
        
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
        i = 1
        while len(phone_numbers_1):
            phone = phone_numbers_1.pop(0)
            if i < 7:
                data["Phone1-"+str(i)] = phone
                i += 1

        emails_1 = []
        email_divs = detail_soup.select('.col > div:last-child')
        for email_div in email_divs:
            text = email_div.text.strip()
            if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
                if text != "support@truepeoplesearch.com" and text not in emails_1:
                    emails_1.append(text)

        j = 1
        while len(emails_1):
            email = emails_1.pop(0)
            if j < 3:
                data["Email1-"+str(j)] = email
                j += 1
    except:
        print("Cannot Fine Detail Link")
        with open("error.txt", "a", encoding="UTF-8") as error:
            error.write(first_name)


    second_name = data["Owner name 02"]
    if second_name:
        entity_type = check_entity(second_name)
        
        search_url = build_url(data, entity_type, 2)

        print("\n\n")
        print(second_name)
        print(search_url)

        response = client.get(search_url, params=params)
        soup = BeautifulSoup(response.text, 'html.parser')

        a_tag = soup.find('a', {'class': 'btn btn-success btn-lg detail-link shadow-form'})

        try:
            detail_url = "https://www.truepeoplesearch.com" + a_tag['href']

            print(detail_url)

            detail_response = client.get(detail_url, params=params)

            detail_soup = BeautifulSoup(detail_response.text, 'html.parser')
        
            age_span_2 = detail_soup.find('span', string=age_regex)    
            data["Age2"] = age_span_2.text.strip()

            phone_numbers_2 = []
            phone_divs = detail_soup.select('div.row div.col-12')
            for phone_div in phone_divs:
                try:
                    phone_span = phone_div.select_one('a[data-link-to-more="phone"] span[itemprop="telephone"]')
                    phone = phone_span.text.strip()

                    phone_type_span = phone_div.select_one('span.smaller')
                    phone_type = phone_type_span.text.strip()

                    phone_info = f"{phone} - {phone_type}"
                    if phone_info not in phone_numbers_2:
                        phone_numbers_2.append(phone_info)
                except:
                    pass
            i = 1
            while len(phone_numbers_2):
                phone = phone_numbers_2.pop(0)
                if i < 7:
                    data["Phone2-"+str(i)] = phone
                    i += 1

            emails_2 = []
            email_divs = detail_soup.select('.col > div:last-child')
            for email_div in email_divs:
                text = email_div.text.strip()
                if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
                    if text != "support@truepeoplesearch.com" and text not in emails_2:
                        emails_2.append(text)

            j = 1
            while len(emails_2):
                email = emails_2.pop(0)
                if j < 3:
                    data["Email2-"+str(j)] = email
                    j += 1
        except:
            print("Cannot Fine Detail Link")
            with open("error.txt", "a", encoding="UTF-8") as error:
                error.write(second_name)        

    return data

if __name__ == "__main__":
    client = ZenRowsClient(zenrows_key)
    params = {"js_render":"true","antibot":"false","premium_proxy":"true"}

    input_file = 'Upwork Test LLCs.xlsx'
    input_data = read_xlsx(input_file)
    
    output_data = []

    input_temp = input_data[8:9]

    for item in input_temp:
        print(item)
        start_time = time.time()
        data = scrap(item, client, params)
        print(data)
        end_time = time.time()
        print(end_time - start_time)
    # output_data.append(item)



    # print(response.text)
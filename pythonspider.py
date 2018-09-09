import random,time,pymongo
from urllib.parse import quote, urlencode
from pyquery import PyQuery
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

browser = webdriver.Chrome()
wait = WebDriverWait(browser,10)
KEYWORD = 'python爬虫'
link_list = []

MONGO_DB = 'lagou'
MONGO_COLLECTION = 'jobInfo'
client = pymongo.MongoClient(host='localhost')
db = client[MONGO_DB]

def get_one_page(link):
    browser.get(link)
    return browser.page_source


def parse_one_page(html):
    doc = PyQuery(html)
    company = doc('.job-name .company').text()
    job_name = doc('.job-name .name').text()
    job_request = doc('.job_request').text().replace('\n','').split('/')
    job_bt = doc('.job_bt').text()
    yield {
        'company':company,
        'job_name':job_name,
        'salary':job_request[0],
        'location':job_request[1].strip(),
        'experience':job_request[2].strip(),
        'job_desc':job_bt
    }


def save_to_mongo(item):
    try:
        if db[MONGO_COLLECTION].insert_one(item):
            print('Successful')
    except:
        print('Failed')



def main():
    city = {'city':'北京'}
    url = 'https://www.lagou.com/jobs/list_' + quote(KEYWORD) + '?' + urlencode(city)
    browser.get(url)
    while True:
        a_list = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'.position_link')))
        for a in a_list:
            link = a.get_attribute('href')
            link_list.append(link)
        next_page = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.pager_next ')))
        try:
            next_page_disabled = browser.find_element_by_class_name('pager_next_disabled')
            if next_page_disabled:
                break
        except NoSuchElementException:
            print('下一页')
        next_page.click()
        time.sleep(random.randint(2, 5))
    for link in link_list:
        time.sleep(random.randint(2,20))
        html = get_one_page(link)
        for item in parse_one_page(html):
            save_to_mongo(item)


main()

import math
import unicodedata
import unidecode
import requests
from bs4 import BeautifulSoup as bs
import time
import simplejson
import json
from lxml import etree
import boto3
from configparser import ConfigParser

parser = ConfigParser()
parser.read('config')
bucket = parser.get('AWS', 'bucket')


salaries = []
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
url = 'https://www.glassdoor.com.br/Sal%C3%A1rios/s%C3%A3o-paulo-engenheiro-de-dados-sal%C3%A1rio-SRCH_IL.0,9_IM1009_KO10,29_IP{}.htm?clickSource=searchBtn'


def send_data_to_S3(file):
    s3 = boto3.resource('s3')    
    s3.Object(bucket, 'salaries.json').put(Body=json.dumps(file))



def call_page(i):
    ret = requests.get(url.format(i), headers=headers)
    return bs(ret.content, "lxml")    

def conv_salary(salary):
    return salary.replace('R$ ', '').replace('.','').replace(' mil','000')

def get_total_pages():
    soup = call_page(0)
    dom = etree.HTML(str(soup))
    data_per_page = int((dom.xpath('/html/body/div[4]/div/div/div/div[11]/div/div/div[2]/div[4]/div[1]/div[3]/div/div[2]')[0].text.split()[3]))
    total = int((dom.xpath('/html/body/div[4]/div/div/div/div[11]/div/div/div[2]/div[4]/div[1]/div[3]/div/div[2]')[0].text.split()[-1].replace('.','')))/data_per_page
    total = math.ceil(total)
    return total
    
total_pages = get_total_pages() + 1

for i in range(1,total_pages):
    print(f"Getting page {i} from {total_pages - 1}")
    time.sleep(0.1)

    soup = call_page(i)

    selector = 'div > h3 ~ div'
    list = soup.select(selector)

    company = ''

    for item in list:
        if str(item.find("span")).find("hora") > 0:
            hour = True
        else:
            hour = False

        a = (item.find("a"))
        if a:
            company = (a['href']).split("/")[2]
            pos = company.find("-Engenheiro")
            company = unidecode.unidecode(company[:pos])

            data = {'company': company, 'salary': salary, 'page':i}
            salaries.append(data)

        res = item.find("h3")

        if res:         
            if len(res) == 7:
                salary_high = unicodedata.normalize("NFKD", res.contents[6])
            else:
                salary_high = '0'   


            salary = unicodedata.normalize("NFKD", res.contents[0])


            if str(salary).find("R$") >= 0:    
                salary = conv_salary(salary)            
                salary_high = conv_salary(salary_high)


                if int(salary_high) > 0:
                    salary = ( int(salary) + int(salary_high) ) / 2

                if hour:
                    salary = int(salary) * 168
                else:
                    salary = int(salary)
                
                

send_data_to_S3(salaries)                
f = open('result.json', 'wt', encoding='utf-8')
simplejson.dump(salaries, f)
f.close()



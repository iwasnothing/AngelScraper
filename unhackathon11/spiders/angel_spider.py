import scrapy
import requests
from urllib.parse import urlencode
from fake_useragent import UserAgent
import re
import json
from bs4 import BeautifulSoup

class QuotesSpider(scrapy.Spider):
    name = "angel"
    #search_url = 'https://angel.co/company_filters/search_data'
    search_url = 'https://angel.co/company_filters/search_data'
    start_page = 1
    sort = 'signal'
    location = 'San Francisco'
    market = 'Social Media'
    stage = 'Series C'


    def start_requests(self):
        search_url = self.search_url
        start_page = self.start_page
        sort = self.sort
        location = self.location
        market = self.market
        stage = self.stage
        is_first_page = int(start_page == 1)
        query = {}
        query['sort'] = sort
        query['page'] = start_page
        if location is not None:
            query['filter_data[keywords]:'] = location
        if market is not None:
            query['filter_data[markets][]'] = market
        if stage is not None:
            query['filter_data[stage]'] = stage
        #search_response = requests.get(search_url, data=query, headers={'User-Agent': UserAgent().chrome})
        search_response = requests.get(search_url)
        resp = search_response.json()
        hexdigest = resp['hexdigest']
        total = resp['total']
        ids = [int(x) for x in resp['ids']]
        sort= resp['sort']
        is_new = resp['new']
        num_page = resp['page']
        #print("------I get ressult-----")
        #print(total)
        #print(ids[0])
        #print(ids)

        params = {'ids[]':ids, 'total':total, 'page':num_page, 'sort':sort, 'new': is_new, 'hexdigest':hexdigest}
        url = requests.Request('GET','https://angel.co/companies/startups', params=params).prepare().url
        yield scrapy.Request(url=url, callback=self.parse_list)

    def parse_list(self,response):
        #r = requests.get('https://angel.co/companies/startups', params=params)
        #print(r.content)
        soap = BeautifulSoup(json.loads(response.body)['html'], 'html')
        startup_names = soap.find_all('div', {'class':'name'})
        for i, name in enumerate(startup_names):
            id = name.find('a')['data-id']
            link = name.find('a')['href']
            name = name.find('a').text
            print(id)
            print(name)
            print(link)
            yield {
                'id': id,
                'link': link,
                'name': name,
            }
            yield scrapy.Request(url=link, callback=self.parse)


        #url = requests.Request('GET','https://angel.co/companies/startups', params=params).prepare().url
        #print(r)
        #print("------end ressult-----")
        #yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        company = response.css('.s-vgBottom0_5::text').extract_first()
        founder = response.css('.profile-link::text').extract_first()
        pf = response.css('.profile-link::attr(href)').extract_first()
        yield {
            'company': company,
            'founder': founder,
            'user profile': pf,
        }
        #print(response.text)
        #jjjprint(response.text)
        #lst = re.split('<>',response.text.replace('\\u003e','>').replace('\\u003c','<'))
        #print(lst)

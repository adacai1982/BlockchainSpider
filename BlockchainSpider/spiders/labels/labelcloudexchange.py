import logging
import re
from urllib.parse import urlsplit, urljoin, urlencode

import scrapy
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from BlockchainSpider import settings
from BlockchainSpider.items import LabelAddressItem, LabelTransactionItem, LabelReportItem


class LabelsCloudSpiderExchange(scrapy.Spider):
    exchangeList = ['Bitfinex', 'Bitstamp' , 'Bittrex', 'Binance', 'Coinbase', 'Coinone', 'CoinMetro', 'Coinhako', 
    'Coinsquare', 'Crypto-com', 'Deribit', 'Gate-io', 'Gemini', 'Hotbit', 'Huobi', 'Korbit', 'Kraken', 'KuCoin', 
    'OKX', 'Poloniex', 'Paribu', 'Tornado-Cash', 'Upbit','Exchange', 'MaskEX']
    name = 'labels.labelcloud.exchange'
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'BlockchainSpider.middlewares.SeleniumMiddleware': 900,
            **getattr(settings, 'DOWNLOADER_MIDDLEWARES', dict())
        },
        'ITEM_PIPELINES': {
            'BlockchainSpider.pipelines.LabelsPipeline': 299,
            **getattr(settings, 'ITEM_PIPELINES', dict())
        }
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.driver_options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(options=self.driver_options)

        self.site = kwargs.get('site', 'etherscan')
        self.site2net = {
            'etherscan': 'eth',
            'bscscan': 'bsc',
            'polygonscan': 'polygon',
            'snowtrace': 'avax', 
            'optimisticscan': 'optimistic',
            'arbiscan': 'arbitrum',
            'ftmscan':'fantom'
        }
        self._allow_site = {
            'etherscan': 'https://etherscan.io',
            'bscscan': 'https://bscscan.com',
            'polygonscan': 'https://polygonscan.com',
            'snowtrace': 'https://snowtrace.io',
            'optimisticscan': 'https://optimistic.etherscan.io',
            'arbiscan': 'https://arbiscan.io',
            'ftmscan': 'https://ftmscan.com/'
        }
        assert self.site in self._allow_site.keys()

        self.url_site = self._allow_site[self.site]
        self.url_label_cloud = self.url_site + '/labelcloud'
        self.page_size = int(kwargs.get('size', 100))

        self.out_dir = kwargs.get('out', './data')
        self.label_names = kwargs.get('labels', None)
        if self.label_names is not None:
            self.label_names = self.label_names.split(',')
        self.label_categories = kwargs.get('categories', 'accounts')
        self.label_categories = self.label_categories.split(',')

    def start_requests(self):
        # open selenium to login in
        
        print (self.url_site + '/login')
        self.driver.get(self.url_site + '/login')
        WebDriverWait(
            driver=self.driver,
            timeout=300,
        ).until(lambda d: d.current_url.find('myaccount') > 0)

        # generate request for label cloud
        yield scrapy.Request(
            url=self.url_label_cloud,
            method='GET',
            cookies=self.driver.get_cookies(),
            callback=self.parse_label_cloud,
        )

    def parse_label_cloud(self, response, **kwargs): 
        for a in self.exchangeList:
              
            request = scrapy.Request(
                url=self.url_site + '/accounts/label/' + a + '?subcatid=1&size=1000&start=0&col=1&order=asc',
                method='GET',
                cookies=response.request.cookies,
                callback=self.parse_labels,
                cb_kwargs=dict(label=a, category='Account')
            )

            if self.label_names is None:
                yield request
            else:
                for label_name in self.label_names:
                    if href.find(label_name) >= 0:
                        yield request
 


    def parse_labels(self, response, **kwargs):
        self.log(
            message='Extracting items from ' + response.url,
            level=logging.INFO
        )
        label = kwargs.get('label')


        info_headers = list()
        for header in response.xpath('//thead/tr/th').extract():
            header = re.sub('<.*?>', '', header)
            header = re.sub(r'\s*', '', header)
            info_headers.append(header)

        for row in response.xpath('//tbody/tr'):
            info = dict(url=response.url)
            for i, td in enumerate(row.xpath('./td').extract()):
                info[info_headers[i]] = re.sub('<.*?>', '', td)
            addresses = list()
            transactions = list()
            if kwargs.get('category') == 'accounts' or kwargs.get('category') == 'tokens':
                addresses.append({**LabelAddressItem(
                    net=self.site2net[self.site],
                    address=info.get('Address', info.get('ContractAddress')),
                )})
            if kwargs.get('category') == 'transactions':
                transactions.append({**LabelTransactionItem(
                    net=self.site2net[self.site],
                    transaction_hash=info.get('TxnHash'),
                )})
            yield LabelReportItem(
                labels=[label],
                urls=list(),
                addresses=addresses,
                transactions=transactions,
                description=info,
                reporter=self.site,
            )

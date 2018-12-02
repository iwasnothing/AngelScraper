#!/bin/sh
rm -f angel.json
python gen_proxy.py 
scrapy crawl angel -o angel.json

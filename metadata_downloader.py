#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 13:48:41 2019

@author: kelly
"""

import requests
import os
archive_it_user = ""
archive_it_pw = ""
env_file = "credentials.env"
env_vars = {}
crawl_nums_file = "crawl_nums.txt"
from colorama import Fore

# file download function
def download_metadata_file(url, crawl_num):
    r = requests.get(url, auth=(archive_it_user, archive_it_pw))
    # Write downloaded file
    try:
        filename = r.headers.get('content-disposition').split("filename=")[1] \
                            .split("\"")[1].replace(":", "_")
        print('\nDownloading ' + filename + "...")
        with open(os.getcwd() + '/' + filename, 'wb') as f:  
            f.write(r.content)
    except:
        print(Fore.RED + "\nIMPORTANT: Metadata file not found at url: " + url)
        print(Fore.RESET)

 # Get username and password from credentials.env file
with open(env_file) as f:
    for line in f:
        if line.startswith('#'):
            continue
        key, value = line.strip().split('=', 1)
        env_vars[key] = value

archive_it_user = env_vars['ARCHIVE-IT-USER']
archive_it_pw = env_vars['ARCHIVE-IT-PWD']

crawl_nums = []
with open(crawl_nums_file) as f:
    for line in f:
        crawl_nums.append(int(line))
        

dir_name = "crawl_metadata_" + input("collection number: ")

try:       
    os.mkdir(dir_name)
except:
    pass

os.chdir(dir_name)
 
for crawl_num in crawl_nums:       
    # Download seed, host, and mimetype lists
    seed_list_url = ('https://partner.archive-it.org/api/reports/seed/' 
                     + str(crawl_num) + '?format=csv&limit=1000000')
    host_list_url = ('https://partner.archive-it.org/api/reports/host/' 
                     + str(crawl_num) + '?format=csv&limit=1000000')
    mimetype_list_url = ('https://partner.archive-it.org/api/reports/mimetype/' 
                         + str(crawl_num) + '?format=csv&limit=1000000')
       
    download_metadata_file(seed_list_url, crawl_num)
    download_metadata_file(host_list_url, crawl_num)
    download_metadata_file(mimetype_list_url, crawl_num)
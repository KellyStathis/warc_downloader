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
env_file = "archiveit.env"
env_vars = {}

# file download function
def download_metadata_file(url, crawl_num):
    r = requests.get(url, auth=(archive_it_user, archive_it_pw))
    # Write downloaded file
    filename = r.headers.get('content-disposition').split("filename=")[1] \
                        .split("\"")[1].replace(":", "_")
    print('\nDownloading ' + filename + "...")
    with open(os.getcwd() + '/' + filename, 'wb') as f:  
        f.write(r.content)

 # Get username and password from archiveit.env file
with open(env_file) as f:
    for line in f:
        if line.startswith('#'):
            continue
        key, value = line.strip().split('=', 1)
        # os.environ[key] = value  # Load to local environ
        #env_vars.append({'name': key, 'value': value}) # Save to a list
        env_vars[key] = value

archive_it_user = env_vars['ARCHIVE-IT-USER']
archive_it_pw = env_vars['ARCHIVE-IT-PWD']
        
crawl_nums = [88693, 153407, 153606]
 
for crawl_num in crawl_nums:       
    # Download seed, host, and mimetype lists
    seed_list_url = ('https://partner.archive-it.org/api/reports/seed/' 
                     + str(crawl_num) + '?format=csv&offset=0&limit=1')
    host_list_url = ('https://partner.archive-it.org/api/reports/host/' 
                     + str(crawl_num) + '?format=csv&offset=0&limit=3')
    mimetype_list_url = ('https://partner.archive-it.org/api/reports/mimetype/' 
                         + str(crawl_num) + '?format=csv&offset=0&limit=3')
       
    download_metadata_file(seed_list_url, crawl_num)
    download_metadata_file(host_list_url, crawl_num)
    download_metadata_file(mimetype_list_url, crawl_num)
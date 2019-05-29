#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 23 15:42:08 2019

@author: kelly
"""

import requests
import hashlib
import os

# global variables
warcs = []
num_warcs = 0
download_all_files = 'n'
crawl_time_after = 0
crawl_time_before = 0
collnum = -1

# prompt functions
def collnum_prompt():
    while True:
        try:
            collnum = int(input('Enter collection number: '))
            if collnum > 0:
                return collnum
                break
        except:
            pass
        
def crawl_time_before_prompt():
    while True:
        try:
            crawl_time_before = str(input('Enter an end date (YYYY-MM-DD): '))
            if is_date(crawl_time_before):
                return crawl_time_before
                break
        except:
            pass
        
def crawl_time_after_prompt():
    while True:
        try:
            crawl_time_after = str(input('Enter a start date (YYYY-MM-DD): '))
            if is_date(crawl_time_after):
                return crawl_time_after
                break
        except:
            pass

def download_all_files_prompt():
    while True:
        try:
            download_all_files = str(input('Download all files? Enter y or n: '))
            if download_all_files.lower() == 'y':
                num_warcs == len(warcs)
                return download_all_files
                break
            elif download_all_files == 'n':
                return download_all_files
                break
        except:
            pass
    
# byte conversion functions
def size_string(byte_size):
    megabyte_size = megabyte(byte_size)
    if megabyte_size > 1000:
        return str(gigabyte(byte_size)) + "GB"
    else:
        return str(megabyte_size) + "MB"
    
def megabyte(byte_size):
    return byte_size / 1000000

def gigabyte(byte_size):
     return byte_size / 1000000000

# date check function
def is_date(crawl_time):
    ymd = crawl_time.split("-")
    if len(ymd) != 3:
        return False
    try:
        year = int(ymd[0])
        month = int(ymd[1])
        day = int(ymd[2])
    except:
        return False
    if year < 2000:
        return False
    if month < 0 or month > 12:
        return False
    if day < 0 or day > 31:
        return False
    if month == 2 and day > 29:
        return False
    if month in [4, 6, 9, 11] and day > 30:
        return False
    return True
    
# request prompt functions
def request(request_string):
    global warcs, num_warcs
    warcs = []
    num_warcs = 0
    total_size = 0
    
    print("\nRequest string: " + request_string)
    r = requests.get(request_string, auth=('kelly.stathis', 'DIwarc19$'))
    r_json = r.json()
    files = r_json['files']
    
    # Build the list of warcs
    for file in files:
        warcs.append({'file': file['locations'][0], 'md5': file['checksums']['md5'], 'size': file['size'], 'crawl': file['crawl']})
        total_size += file['size']
    
    num_warcs = len(warcs)
    print("\nQuery returned " + str(num_warcs) + " WARC files, totalling " + size_string(total_size))
    
def request_dates(request_string):    
    global crawl_time_after, crawl_time_before
 
    crawl_time_after = crawl_time_after_prompt()
    crawl_time_before = crawl_time_before_prompt()
    request_string += "&crawl-time-after=" + str(crawl_time_after) + "&crawl-time-before=" + str(crawl_time_before)
    
    request(request_string)

# main function    
def main():
    global num_warcs
    
    # Prompt for collection number
    collnum = collnum_prompt()
    
    # Initial request
    request_string = 'https://warcs.archive-it.org/wasapi/v1/webdata?collection=' + str(collnum)
    request(request_string)
    
    # If 0 files, do nothing
    if num_warcs == 0:
        print("\nNo WARC files in collection " + str(collnum) + "; exiting.")
    # If files found continue
    else:
        # Must narrow by date if 100 or more files; indicates incomplete API result.
        while num_warcs == 100:
            print(("\nIMPORTANT: Must use date ranges to narrow to < 100 files."))
            request_dates(request_string)
            if num_warcs == 0:
                print("\nDate range too narrow; try again.")
                num_warcs = 100      
        # Give option to narrow by date anyway        
        while True:
            try:
                narrow_by_date = str(input('Would you like to narrow further by date? Enter y or n: '))
                if narrow_by_date.lower() == 'y':
                     request_dates(request_string)
                     while num_warcs == 0:
                         print("\nDate range too narrow; try again.")
                         request_dates(request_string)
                     break
                elif narrow_by_date == 'n':
                    break
            except:
                pass
        
        # Prompt user to download files        
        download_all_files = download_all_files_prompt()
            
        if download_all_files == 'y':  
            for warc in warcs:
                url = warc['file']
                size = size_string(int(warc['size']))
                cwd = os.getcwd()
        
                # Get file name
                filename=url.split("https://warcs.archive-it.org/webdatafile/")[1]
                
                
                # Download file
                print('\nDownloading ' + filename + ' (' + size + '...')
                r = requests.get(url, auth=('kelly.stathis', 'DIwarc19$'))
                            
                # Write downloaded file    
                with open(cwd + '/' + filename, 'wb') as f:  
                    f.write(r.content)
                
                # Open, close, read file and calculate MD5 on its contents 
                with open(filename, 'rb') as file_to_check:
                    # read contents of the file
                    data = file_to_check.read()    
                    # pipe contents of the file through
                    md5_returned = hashlib.md5(data).hexdigest()
                    if md5_returned == warc['md5']:
                        print("md5 match: " + md5_returned)
                    else:
                        print("IMPORTANT: md5 fail: " + md5_returned + " should be " + warc['md5'])
                        
                # Download crawl metadata
                if type(warc['crawl']) == int:
                    crawl_num = warc['crawl']
                   
                    # Download seed list
                    # TODO: Ensure this doesn't download the seed list multiple times for crawls with multiple WARCs
                    seed_list_url = 'https://partner.archive-it.org/api/reports/seed/' + str(crawl_num) + '?format=csv&offset=0&limit=1'
                    r = requests.get(seed_list_url, auth=('kelly.stathis', 'DIwarc19$'))
                    # Write downloaded file
                    seed_list_filename = r.headers.get('content-disposition').split("filename=")[1].split("\"")[1].replace(":", "_")
                    print('\nDownloading ' + seed_list_filename + "...")
                    with open(cwd + '/' + seed_list_filename, 'wb') as f:  
                        f.write(r.content)
        

if __name__== "__main__":
     main()
        
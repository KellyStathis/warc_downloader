#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 23 15:42:08 2019

@author: kelly
"""

import requests
import hashlib
import os
import datetime
from colorama import Fore

# Global variables
warcs = []
num_warcs = 0
download_files = 'n'
crawl_time_after = 0
crawl_time_before = 0
collection_num = -1
collection_cwd = ""
env_file = "credentials.env"
env_vars = {}
archive_it_user = ""
archive_it_pw = ""

def collection_num_prompt():
    """Prompt the user for the collection number."""
    while True:
        try:
            collection_num = int(input('Enter collection number: '))
            if collection_num > 0:
                return collection_num
                break
        except:
            pass
        
def crawl_time_before_prompt():
    """Prompt the user for end date in YYYY-MM-DD format  and returns response if valid.
    
    'Before' means that WARCs before this date are returned by WASAPI.
    Note that the  end date is not inclusive.
    For example, to get all files from 2019, use start date 2019-01-01 and end date 2020-01-01.
    """
    while True:
        try:
            crawl_time_before = str(input('Enter an end date (YYYY-MM-DD): '))
            if is_date(crawl_time_before):
                return crawl_time_before
                break
        except:
            pass
        
def crawl_time_after_prompt():
    """Prompt the user for start date in YYYY-MM-DD format and returns response if valid.
    
    'After' means that WARCs after this date are returned by WASAPI.
    """
    while True:
        try:
            crawl_time_after = str(input('Enter a start date (YYYY-MM-DD): '))
            if is_date(crawl_time_after):
                return crawl_time_after
                break
        except:
            pass

def download_files_prompt():
    """Prompts the user to download files and returns result (y or n)."""
    while True:
        try:
            download_files = str(input('Download files? Enter y or n: ')).lower()
            if download_files == 'y' or download_files == 'n':
                return download_files
                break
        except:
            pass
    
def size_string(byte_size):
    """Returns a string indicating file size in MB or GB."""
    megabyte_size = megabyte(byte_size)
    if megabyte_size > 1000:
        return "{0:.3f}".format(gigabyte(byte_size)) + " GB"
    else:
        return "{0:.3f}".format(megabyte_size) + " MB"
    
def megabyte(byte_size):
    """Returns bytes converted to megabytes."""
    return byte_size / 1000000

def gigabyte(byte_size):
    """Returns bytes converted to gigabytes."""
    return byte_size / 1000000000

def is_date(crawl_time):
    """Returns true if string is in YYYY-MM-DD format and a valid date; false otherwise."""
    ymd = crawl_time.split("-")
    if len(ymd) != 3:
        return False
    try:
        year = int(ymd[0])
        month = int(ymd[1])
        day = int(ymd[2])
        datetime.date(year, month, day)
        return True
    except:
        return False
    
def request(request_string):
    """Makes request to WASAPI to get information about WARC files.
    
    Using request_string, sends GET request to WASAPI and saves:
        - WARC file locations 
        - md5 checksums
        - file sizes
    
    Updates global variables:
        - warcs: list of above information
        - num_warcs: the number of WARC files 
        
    Prints the number of WARC files and the total size returned by query.
    """
    global warcs, num_warcs
    warcs = []
    num_warcs = 0
    total_size = 0
    
    # Make WASAPI request
    print("\nRequest string: " + request_string)
    r = requests.get(request_string, auth=(archive_it_user, archive_it_pw))
    r_json = r.json()
    files = r_json['files']
    
    # Build the list of WARCs
    for file in files:
        warcs.append({'file': file['locations'][0], 
                      'md5': file['checksums']['md5'], 'size': file['size'], 
                      'crawl': file['crawl']})
        total_size += file['size']
    
    # Save the number of WARC files
    num_warcs = len(warcs)
    
    # Print results of request
    print("\nQuery returned " + str(num_warcs) + " WARC files, totalling "
          + size_string(total_size))
    
def request_with_dates(request_string):
    """Makes request to WASAPI limited by a date range.
    
    Prompts the user for start and end dates (crawl_time_after and crawl_time_before).
    Constructs updated request_string using dates.
    Calls request(request_string).
    """
    global crawl_time_after, crawl_time_before
 
    crawl_time_after = crawl_time_after_prompt()
    crawl_time_before = crawl_time_before_prompt()
    request_string += ("&crawl-time-after=" + str(crawl_time_after) 
                    + "&crawl-time-before=" + str(crawl_time_before))
    
    request(request_string)
    
def download_metadata_file(url):
    """Download the metadata file at url."""
    r = requests.get(url, auth=(archive_it_user, archive_it_pw))
    # Write downloaded metadata file
    try:
        filename = r.headers.get('content-disposition').split("filename=")[1] \
                        .split("\"")[1].replace(":", "_")
        print('\nDownloading ' + filename + "...")
        with open(os.getcwd() + '/' + filename, 'wb') as f:  
            f.write(r.content)
    except:
        print(Fore.RED + "\nIMPORTANT: Metadata file not found at url: " + url)
        print(Fore.RESET)
        
def write_warc(filename, r):
    """Write the WARC file (filename) from r.content."""
    with open(os.getcwd() + '/' + filename, 'wb') as f:  
         f.write(r.content) # TO TEST WITHOUT DOWNLOADING: COMMENT OUT
         #print("write_warc not writing for test") # TO TEST WITHOUT DOWNLOADING: UNCOMMENT
 
def main():
    global num_warcs
    global collection_cwd
    global archive_it_user
    global archive_it_pw
    crawl_nums = [] # List of downloaded crawl IDs
    
    # Parse username and password from credentials.env file
    with open(env_file) as f:
        for line in f:
            if line.startswith('#'):
                continue
            key, value = line.strip().split('=', 1)
            env_vars[key] = value
    
    # Set username and password to local variables
    archive_it_user = env_vars['ARCHIVE-IT-USER']
    archive_it_pw = env_vars['ARCHIVE-IT-PWD']
    
    # Prompt for collection number
    collection_num = collection_num_prompt()
    
    # Initial request to WASAPI
    request_string = 'https://warcs.archive-it.org/wasapi/v1/webdata?collection=' + str(collection_num)
    request(request_string)
    
    # If WASAPI request returns 0 files, do nothing
    if num_warcs == 0:
        print("\nNo WARC files in collection " + str(collection_num) + "; exiting.")  
    # If WASAPI request finds files, continue
    else:
        # If there are exactly 100 files, must narrow by date until < 100;
        # exactly 100 files indicates incomplete results, because limit is 100.
        while num_warcs == 100:
            print((Fore.RED + "\nIMPORTANT: Must use date ranges to narrow to < 100 files."))
            print(Fore.RESET)
            request_with_dates(request_string)
            if num_warcs == 0:
                print("\nDate range too narrow; try again.")
                num_warcs = 100
        # Even if there are < 100 files, give option to narrow results by date        
        while True:
            try:
                narrow_by_date = str(input('Would you like to narrow further by date? Enter y or n: ')).lower()
                if narrow_by_date == 'y':
                     request_with_dates(request_string)
                     while num_warcs == 0:
                         print("\nDate range too narrow; try again.")
                         request_with_dates(request_string)
                elif narrow_by_date == 'n':
                    break
            except:
                pass
        
        # After user declines to narrow further by date, prompt to download files        
        download_files = download_files_prompt()
        
        # Download files if user responds with 'y'
        if download_files == 'y':
            # Create collection folder, e.g. ARCHIVEIT-1234, if it doesn't exist yet
            collection_folder = "ARCHIVEIT-" + str(collection_num)
            try:
                os.mkdir(collection_folder)
            except:
                pass
            
            os.chdir(collection_folder) # Change directory to collection folder
            collection_cwd = os.getcwd() # Save the path of the collection folder
            
            # For each WARC file listed by WASAPI response
            for warc in warcs:
                url = warc['file']
                size = size_string(int(warc['size']))
                crawl_num = warc['crawl']
                
                os.chdir(collection_cwd) # Change directory (back) to the collection folder
        
                # Get filename of WARC file
                filename=url.split("https://warcs.archive-it.org/webdatafile/")[1]
                
                # Download WARC file
                print('\nDownloading ' + filename + ' (' + size + ')...')
                r = requests.get(url, auth=(archive_it_user, archive_it_pw)) # TO TEST WITHOUT DOWNLOADING: COMMENT OUT
                #r = "" # TO TEST WITHOUT DOWNLOADING: UNCOMMENT
                            
                # Make package directory for crawl and write downloaded WARC file
                # Note that if crawl_num is not an int, this means the crawl ID is missing;
                # without crawl_num, files will download to the collection folder
                if type(crawl_num) == int:
                    crawl_folder = "ARCHIVEIT_COLLECTION-" + str(collection_num) + "_JOB-" + str(crawl_num)
                    # Create package folder for crawl, e.g. ARCHIVEIT_COLLECTION-1234_JOB-4567
                    try:
                        os.mkdir(crawl_folder)
                    except:
                        pass
                    os.chdir(crawl_folder)
                    # Make ARCHIVEIT_COLLECTION-1234_JOB-4567/objects (WARCs go here)
                    try:
                        os.mkdir("objects")
                    except:
                        pass
                    # Make ARCHIVEIT_COLLECTION-1234_JOB-4567/metadata/submissionDocumentation (metadata goes here)
                    try:
                        os.mkdir("metadata")
                        os.chdir("metadata")
                        os.mkdir("submissionDocumentation")
                        os.chdir('..')
                    except:
                        pass
                    # Change directory to objects sub-folder
                    os.chdir("objects")
                
                # Write the downloaded WARC file
                write_warc(filename, r)
                
                # Open and read WARC file and compute MD5 on its contents
                with open(filename, 'rb') as file_to_check:
                    data = file_to_check.read()# read contents of the file   
                    md5_returned = hashlib.md5(data).hexdigest() # pipe contents of the file through
                    # Compare computed MD5 with checksum from WASAPI
                    if md5_returned == warc['md5']:
                        print("md5 match: " + md5_returned)
                    else:
                        print(Fore.RED + "IMPORTANT: md5 fail: " + md5_returned 
                              + " should be " + warc['md5'])
                        print(Fore.RESET)
                   
                # Download crawl metadata files to metadata/submissionDocumentation
                if type(crawl_num) == int and crawl_num not in crawl_nums:
                    # Change directory to metadata/submissionDocumentation folder
                    os.chdir("..")
                    os.chdir("metadata/submissionDocumentation")
                   
                    # URLs for metadata file downloads
                    seed_list_url = ('https://partner.archive-it.org/api/reports/seed/' 
                                     + str(crawl_num) + '?format=csv&limit=1000000')
                    host_list_url = ('https://partner.archive-it.org/api/reports/host/' 
                                     + str(crawl_num) + '?format=csv&limit=1000000')
                    mimetype_list_url = ('https://partner.archive-it.org/api/reports/mimetype/' 
                                         + str(crawl_num) + '?format=csv&limit=1000000')
                   
                    # Download seed, host, and mimetype lists as csv files
                    download_metadata_file(seed_list_url)
                    download_metadata_file(host_list_url)
                    download_metadata_file(mimetype_list_url)
                    
                    # After metadata has downloaded, add crawl ID to list of downloaded crawls
                    crawl_nums.append(crawl_num)
        

if __name__== "__main__":
     main()
        
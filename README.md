# warc_downloader
This project is a Python script that Archive-It partners can use to download their WARC files and associated metadata. 

## Overview
This script uses Archive-It's [Web Archiving Systems API (WASAPI)](https://warcs.archive-it.org/wasapi/v1/webdata) and [Partner API](https://partner.archive-it.org/api/) to download WARC files and associated metadata. The code was developed as part of a Professional Experience project at the UBC iSchool for use by UBC Library Digital Initiatives, with the goal of digitally preserving WARC files captured using Archive-It.

Because the files will be preserved in Archivematica, the script organizes downloads in the following Submission Information Package (SIP) structure:

* ARCHIVEIT_COLLECTION-\<collection number\>_JOB-\<crawl ID\>
  * metadata
    * submissionDocumentation
    * \<host-list csv\>: list of host names and summary data from [hosts report](https://support.archive-it.org/hc/en-us/articles/208333883-Read-your-crawl-s-hosts-report)
    * \<mimetype-list csv\>: list of mimetypes and summary data from [file types report](https://support.archive-it.org/hc/en-us/articles/208333873-Read-your-crawl-s-file-types-report-)
    * \<seed-list csv\>: list of seed URLs and summary data from [seed report](https://support.archive-it.org/hc/en-us/articles/208333893-Read-your-crawl-s-seeds-report)
    * objects
      * \<WARC file(s)\>
      
Each package contains one crawl's WARC files and administrative metadata. At present, descriptive metadata is not downloaded by this script.

## Prerequisites
1. [Python 3](https://www.python.org/downloads/)
2. [pipenv](https://docs.pipenv.org/en/latest/)

## Dependencies
* [requests](https://2.python-requests.org/en/master/)
* [colorama](https://pypi.org/project/colorama/)

## Project Files
| Filename          | Description |
|--------------------|-------------|
| warc_downloader.py | Main script |
| Pipfile            | Pipfile containing dependencies |
| credentials.env    | Example file – edit with your Archive-It credentials |

## Setup
1. Clone or download this repository
2. Run `pipenv install` within the project folder
3. Edit credentials.env, replacing sampleUsername and samplePassword with your Archive-It credentials

## Execution
1. Run `pipenv run python warc_downloader.py`
2. Follow the prompts provided:


| Prompt | Notes |
| --- | --- |
|  `Enter collection number:` | Enter the collection number from which to download WARC files. | 
|  `Would you like to narrow further by date? Enter y or n:` |  `y` to provide a date range for which WARC files to download, `n` to proceed with current results. <br>If a collection has > 100 files, the initial query will only return 100 files, and you will be required to narrow the results by date. | 
|  `Enter a start date (YYYY-MM-DD):`  | Enter the earliest date for which to retrieve WARC files. | 
|  `Enter an end date (YYYY-MM-DD):` | Enter the latest date for which to retrieve WARC files.<br>Note that the end date is not inclusive. For example, to get all files from 2019, use start date 2019-01-01 and end date 2020-01-01. | 
|  `Download files? Enter y or n:` | `y` to download files, `n` to exit. | 

3. As the files download, scan for any output in red text. The script will indicate if there is any file corruption (md5 checksum did not match) or missing metadata files.

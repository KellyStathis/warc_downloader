# warc_downloader
This project is a Python script that Archive-It partners can use to download their WARC files and associated metadata. 

## Overview
This script uses Archive-It's [Web Archiving Systems API (WASAPI)](https://warcs.archive-it.org/wasapi/v1/webdata) and [Partner API](https://partner.archive-it.org/api/) to download WARC files and associated metadata.

The code was developed as part of a Professional Experience project at the UBC iSchool for use by UBC Library Digital Initiatives, with the goal of digitally preserving downloaded WARC files in Archivematica. For this reason, the downlaods are organized in the following package structure:

* ARCHIVEIT_COLLECTION-<collection number>_JOB-<crawl ID>
  * metadata
    * submissionDocumentation
      * *host-list csv*
      * *mimetype-list csv*
      * *seed-list csv*
    * objects
      * *WARC file(s)*

## Prequisites
1. [Python 3](https://www.python.org/downloads/)
2. [pipenv](https://docs.pipenv.org/en/latest/)

## Description of files
[brief description of each file]

## Setup
1. Clone or download this repoistory
2. Run `pipenv install` wthin the project folder
3. Edit credentials.env, replacing sampleUsername and samplePassword with your Archive-It credentials

## Execution
1. Run `pipenv run python warc_downloader.py`
2. [explain prompts here]


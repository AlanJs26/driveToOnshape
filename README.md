# driveToOnshape

A script for transferring files from Google Drive to Onshape using Selenium.

## How to use

First, you must be logged in to your Onshape and Google Drive accounts on Google Chrome. Then, you must change the fields `drive_root_link` and `onshape_root_link` in `config.json,` specifying the roots of the transfer. Once you have done that, run `runner.py`.


> Keep in mind that, being a web scraper script, any changes to the website will break this program. I have placed this script here so that anyone who has the same problem as I had when transferring deeply nested sets of folders from Google Drive to Onshape can have a starting point.

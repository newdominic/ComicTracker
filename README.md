# ComicTracker.py #

## Introduction ##

Keep track of the comics episodes on www.8comic.com.

For educational purposes only.

## Dependencies ##

**Python-Requests**

[http://docs.python-requests.org/en/master/user/install](http://docs.python-requests.org/en/master/user/install/)

## Usage ##

	python ComicTracker.py

- 'Add': Input the comic id on www.8comic.com (e.g. http://www.comicbus.com/html/103.html, 103 is the comic id).
- 'Delete': Delete the selected comic item in the list.
- '^': Move up the selected comic item.
- 'v': Move Down the selected comic item.
- 'Current EP': Reader's current progress.
- 'Open in browser': Open the comic main page in default browser. Can also be done by double-clicking the items in the list.
- 'Keep up automatically': If selected, the 'Current EP' will synchroize with 'Latest EP' automatically.
- 'Update Frequency': The frequency of automatically update in hours.
- 'Save': Save the settings and the comic data into 'comic.db'.
- 'Update': Update the comic data manually.
- 'Quit': Save and quit.
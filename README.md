# Music Metadata Enhancer
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-310/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
## Requirements
```shell
pip3 install -r /path/to/requirements.txt
```
## API Access
* Request new token at https://www.discogs.com/settings/developers
* Set token as environment variable
```shell
 $ export DISCOGSTOKEN=$DISCOGS_API_TOKEN
```
* Note: replace $DISCOGS_API_TOKEN with token obtained in previous step
## Write file paths of song files *.flac to a *.txt file
Example of text file:
```shell
$ cat /foo/songs.txt
/foo/song1.flac
/foo/song2.flac
/bar/song3.flac
```
Specifying `/foo/songs.txt` will evaluate the 3 flac files specified in the text file
## Adding Genre to metadata
This is a beta and only adds Genre which is noted as style on Discogs
## Running command line tool
```shell
$ $PATH_TO_PROJECT/music-metadata/music_metadata_enrichment.py -f $PATH_TO_LIST_OF_SONG_FILE_PATHS_TXT_FILE
```
The -f flag specifies the list of songs file path

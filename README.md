# snatcher

Idk why i wrote this thing :D

It snatches comics from [existentialcomics](https://existentialcomics.com/) and [xkcd](https://xkcd.com/)


## Quick start
`python3` for linux and maybe `python` for windows


- With virtualenv (NOT REQUIRED)
```
$ python3 -m virtualenv venv
$ source venv/bin/activate
```

- Install dependencies
```
$ pip install -r requirements.txt
```





## Usage
```
$ python3 main.py
usage: main.py [-h] {comic} ...

positional arguments:
  {comic}     snatch wut

optional arguments:
  -h, --help  show this help message and exit
```

## Usage for `comic`
```
$ python3 main.py comic
usage: main.py comic [-h] [--save-as SAVE_AS] [--save-in SAVE_IN] [--download-from DOWNLOAD_FROM] [--pdf] {xkcd,ext}

positional arguments:
  {xkcd,ext}

optional arguments:
  -h, --help            show this help message and exit
  --save-as SAVE_AS     save comic as
  --save-in SAVE_IN     save comic in which folder?
  --download-from DOWNLOAD_FROM
                        download from this page
  --pdf                 create pdf
```


## In action
Fetches random comic from [existentialcomics](https://existentialcomics.com/) and saves it as a pdf
```
$ python3 main.py comic ext --pdf
```

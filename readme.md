# TripleJ Downloader

## What is this?

TripleJ (Well, ABC, technically) makes it impossible to download their recordings, and they usually expire after a few days. I like listening back to old TripleJ Mixup recordings so I built this tool to scrape the chunks from Akamai and assemble them into an m4a (Thats the format they're stored in, not my choice)

## How do I install this?

You can use my hosted version here at https://abc.adamparsons.id.au

Alternatively, you can install it by...

  * Install ffmpeg
  * Install Python3, I have not tested Python2 and I doubt it will work. 
  * Download this repo
  * Install the dependencies in the Pipfile (Pipenv install, if you have it)
  * ./manage.py runserver
  * open http://localhost:8000 in your browser

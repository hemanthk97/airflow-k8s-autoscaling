import sys

import time

from bs4 import BeautifulSoup

soup = BeautifulSoup('<b class="boldest">Extremely bold</b>')
tag = soup.b
time.sleep(25)
print(tag.name)

soup = BeautifulSoup('<div class="boldest">Extremely bold</div>')
tag = soup.div
time.sleep(25)
print(tag.name)

soup = BeautifulSoup('<span class="boldest">Extremely bold</span>')
tag = soup.span
print(tag.name)
time.sleep(25)
print(tag['class'])

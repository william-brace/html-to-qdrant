import wget 
from links import linksCO, linksNY

# Download the HTML files
for link in linksCO:
    wget.download(link, 'websites')

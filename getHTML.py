import wget 
from links import linksCO, linksNY, linksMA

# Download the HTML files
for link in linksMA:
    wget.download(link, 'websites')

# wget.download('https://paidleave.wa.gov/get-ready-to-apply/', 'websites')



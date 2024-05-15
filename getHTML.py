import wget 
from links import linksCO, linksNY, linksMA, linksCA, linksWA, linksRI, linksDC, linksCT
import wget
import os
import hashlib

for file_number, link in enumerate(linksRI):
    
    filename = f'pfl{str(file_number)}.html'
    output_path = os.path.join("websites", filename)
    wget.download(link, out=output_path)

# wget.download('https://paidleave.wa.gov/get-ready-to-apply/', 'websites')



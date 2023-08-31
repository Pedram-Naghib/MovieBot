import requests
from bs4 import BeautifulSoup
import html.parser


read = requests.get("https://mubi.com/en/tr/films/annette/awards")
soup = BeautifulSoup(read.content, "html.parser")
# returns an iterable containing all the HTML for all the listings displayed on that page
awards = soup.find_all("div", class_="css-wffprx e1at15620")

for award in awards:
    # extract title
    title = award.find("a", class_="css-15hqn5v e1at15624").text
    # extract price (located in 2 span tag)
    year = award.find("div", class_="css-16kkjs e1at15626").text.split(' ')[0]
    # display result
    print(f"Title: {title}\nYear: {year}")
    print("_"*40)
    # if you want only the first result uncomment next line:
    # break
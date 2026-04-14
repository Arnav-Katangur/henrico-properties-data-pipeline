import requests

url = "https://realestate.henrico.gov/"
response = requests.get(url)

print(response.text)
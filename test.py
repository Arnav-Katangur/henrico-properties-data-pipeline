"""Small scraper experiment for Henrico real estate search."""
import requests
from bs4 import BeautifulSoup
import json
import urllib
import re
import json

with open("entry_info.local.json", "r", encoding="utf-8") as file:
    entry_info = json.load(file)


url = "https://realestate.henrico.gov/"
session = requests.Session()

page = session.get(url)

soup = BeautifulSoup(page.text, "html.parser")

form = soup.find("form", id="wwvFlowForm")
submit_url = urllib.parse.urljoin(page.url, form["action"])

hidden_items = form.find_all(type="hidden")
hidden_values = {}

wanted_ids = {
    "pSalt",
    "pPageItemsProtected",
    "pPageItemsRowVersion",
    "pPageFormRegionChecksums",
}

for item in hidden_items:
    if item.get("name"):
        hidden_values[item.get("name")] = item.get("value", "")
    elif item.get("id") in wanted_ids:
        hidden_values[item.get("id")] = item.get("value", "")

p_json = {
    "salt": hidden_values["pSalt"],
    "pageItems": {
        "itemsToSubmit": [
            {"n": "P1_PARCEL_ID", "v": ""},
            {"n": "P1_VISION_PID", "v": ""},
            {"n": "P1_STR_NUM", "v": entry_info['P1_STR_NUM']},
            {"n": "P1_STR_PREFIX", "v": ""},
            {"n": "P1_ADDRESS", "v": entry_info['P1_ADDRESS']},
            {"n": "P1_STR_UNIT", "v": ""},
            {"n": "P1_USE_CODE", "v": ""},
            {"n": "P1_LEGAL_DESC", "v": ""},
            {"n": "P1_SEL_SORT", "v": "slh_own_name"},
        ],
        "protected": hidden_values["pPageItemsProtected"],
        "rowVersion": hidden_values["pPageItemsRowVersion"],
        "formRegionChecksums": [],
    },
}

payload = {
    "p_json": json.dumps(p_json, separators=(",",":")),
    "p_flow_id": hidden_values["p_flow_id"],
    "p_flow_step_id": hidden_values["p_flow_step_id"],
    "p_instance": hidden_values["p_instance"],
    "p_page_submission_id": hidden_values["p_page_submission_id"],
    "p_request": "SEARCH",
    "p_reload_on_submit": hidden_values["p_reload_on_submit"]
}

result = session.post(submit_url, data=payload)

print(result.status_code)
print(result.url)
result_soup = BeautifulSoup(result.text.lower(), "html.parser")
print(result_soup.prettify())
print(result_soup.find_all("a"))
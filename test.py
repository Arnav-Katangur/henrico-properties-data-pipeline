"""Small scraper experiment for Henrico real estate search."""
import requests
from bs4 import BeautifulSoup
import json
import urllib
import re
import json
from playwright.sync_api import sync_playwright

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

#print(result.status_code)
#print(result.url)
result_soup = BeautifulSoup(result.text, "html.parser")
#print(result_soup.prettify())

#finds table with final link
table = result_soup.find("table", class_="t15standardalternatingrowcolors")
first_td = table.find("td")
link = first_td.find("a")

#goes to full page
href = link.get("href")
detail_url = urllib.parse.urljoin(result.url, href)
detail_page = session.get(detail_url)
full_data_soup = BeautifulSoup(detail_page.text, "html.parser")
#print(full_data_soup.prettify())

fields = {
    "parcel_id": full_data_soup.find(id="P5_PARCEL_ID"),
    "pid": full_data_soup.find(id="P5_PID"),
    "state_code": full_data_soup.find(id="P5_STATE_CODE"),
    "use_code": full_data_soup.find(id="P5_USE_CODE"),
    "tax_type": full_data_soup.find(id="P5_TAX_TYPE_DESC"),
    "subdivision": full_data_soup.find(id="P5_SUBDIVISION"),
    "assessment_price": full_data_soup.find(id="report_R71237002985465692"),
    "owner": full_data_soup.find(id="P5_OWNER_CUR"),
    "school_information": full_data_soup.find(id="report_R272557515384942239"),
    "sq_feet": full_data_soup.find(id="P5_RES_SQ_FT_FIN_LIV"),
    "year_built": full_data_soup.find(id="P5_RES_YEAR_BUILT"),
    "residential_style": full_data_soup.find(id="P5_RES_STYLE"),
    "air_conditioner": full_data_soup.find(id="P5_RES_AIR_COND"),
    "bedroom_count": full_data_soup.find(id="P5_RES_BEDROOMS"),
    "full_bathrooms": full_data_soup.find(id="P5_RES_FULL_BATH"),
    "half_bathrooms": full_data_soup.find(id="P5_RES_HALF_BATH"),
    "fireplace": full_data_soup.find(id="P5_RES_FIREPLACE"),
    "no. of stories": full_data_soup.find(id="P5_RES_NUM_STORIES"),
    "Transfer Info": full_data_soup.find(id="R71235786808465691"),
    "Basement": full_data_soup.find(id="P5_RES_BASEMENT"),
    "Finished Basement": full_data_soup.find(id="P5_RES_FIN_BASEMENT"),
    "Floodplain": full_data_soup.find(id="P5_FLOODPLAIN"),
    "Finished Attic": full_data_soup.find(id="P5_RES_FINISHED_ATTIC"),
    "Neighborhood": full_data_soup.find(id="P5_NEIGHBORHOOD"),
    "Exterior Walls": full_data_soup.find(id="P5_RES_EXT_WALLS"),
    "Roof": full_data_soup.find(id="P5_RES_ROOF"),
    "Chimneys": full_data_soup.find(id="P5_NUM_CHIMNEYS"),
    "Total Rooms": full_data_soup.find(id="P5_RES_TOTAL_ROOMS"),
    "Sketch Details": full_data_soup.find(id="R71258888584566206"),
    "Foundation Type": full_data_soup.find(id="P5_RES_BSMT_TYPE"),
    "Basement/Garage": full_data_soup.find(id="P5_RES_BASEMENT_GAR"),
    
}

for field in fields:
    print(f"{field}: {fields[field].get_text().strip()}")

plats_url = urllib.parse.urljoin(detail_page.url, "f?p=510101:52::::RP::")
plats_page = session.get(plats_url)

plat_links = [
    a["href"]
    for a in BeautifulSoup(plats_page.text, "html.parser").select('a[href*="/plats/"][href$=".pdf"]')
]

for i in plat_links:
    print(i)

image_table = full_data_soup.find(id="R71233805899465688")
image_sources = []

if image_table:
    for img in image_table.find_all("img", src=True):
        src = img["src"].replace("\\", "/")
        if src.startswith("/vision_web/photos/"):
            image_sources.append(urllib.parse.urljoin(detail_page.url, src))

for image_source in image_sources:
    if "sketch" in image_source:
        print("Sketch:",  image_source)
    else:
        print("Photo of House:", image_source)

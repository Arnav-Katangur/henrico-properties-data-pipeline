from playwright.sync_api import sync_playwright

def log_request(request):
    print("\nREQUEST")
    print("method:", request.method)
    print("url:", request.url)


def log_response(response):
    print("\nRESPONSE")
    print("status:", response.status)
    print("url:", response.url)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.on("request", log_request)
    page.on("response", log_response)

    page.goto("https://realestate.henrico.gov/")

    browser.close()
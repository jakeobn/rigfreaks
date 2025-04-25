import trafilatura

def get_website_text_content(url):
    # Send a request to the website
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        text = trafilatura.extract(downloaded)
        return text
    return None

urls = [
    "https://www.chillblast.com",
    "https://www.pcspecialist.co.uk"
]

for url in urls:
    print(f"\n=== Analyzing {url} ===\n")
    content = get_website_text_content(url)
    if content:
        print(f"Content length: {len(content)} characters")
        print(f"Preview: {content[:500]}...")
    else:
        print(f"Failed to retrieve content from {url}")
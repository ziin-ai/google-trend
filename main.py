from fastapi import FastAPI, Query
import requests
import xml.etree.ElementTree as ET
from fastapi.responses import JSONResponse

app = FastAPI()

BASE_URL = "https://trends.google.com/trending/rss"

def fetch_trends(geo: str):
    try:
        rss_url = f"{BASE_URL}?geo={geo}"
        response = requests.get(
            rss_url,
            headers={"User-Agent": "Mozilla/5.0"},
            verify=False  
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return {"error": str(e)}

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError as e:
        return {"error": f"XML Parse Error: {str(e)}"}

    trends = []
    namespaces = {'ns0': 'https://trends.google.com/trending/rss'}
    for item in root.findall(".//item"):
        first_news_item = item.find("ns0:news_item", namespaces=namespaces)

        if first_news_item is not None:
            news_item_title = first_news_item.findtext("ns0:news_item_title", namespaces=namespaces)
            news_item_url = first_news_item.findtext("ns0:news_item_url", namespaces=namespaces)
        else:
            news_item_title = None
            news_item_url = None

        trends.append({
            "title": item.find("title").text if item.find("title") is not None else None,
            "pubDate": item.find("pubDate").text if item.find("pubDate") is not None else None,
            "picture": item.find("ns0:picture", namespaces=namespaces).text if item.find("ns0:picture", namespaces=namespaces) is not None else None,
            "news_item_title": news_item_title,
            "news_item_url": news_item_url,
        })

    return trends

@app.get("/trends")
def get_trends(geo: str = Query("US", description="COUNTRY CODE (ex: US, KR, JP)")):
    data = fetch_trends(geo.upper())
    if isinstance(data, dict) and "error" in data:
        return JSONResponse(content=data, status_code=500)
    return {"geo": geo.upper(), "trends": data}


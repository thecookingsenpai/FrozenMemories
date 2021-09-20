import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
from GoogleNews import GoogleNews
from newspaper import Article
from sanitize_filename import sanitize
import io
import wget

def initialize():
    driver = ""
    try:
        options = Options()
        options.binary_location = thisPath + "\\chrome\\App\\Chrome-bin\\chrome.exe"
        options.add_argument("--log-level=3")
        options.headless = True
        options.add_experimental_option("prefs", {
            "download.default_directory": "/path/to/download/dir",
            "download.prompt_for_download": False,
        })
        options.add_argument(f'user-agent={myUserAgent}')
        driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior',
                  'params': {'behavior': 'allow', 'downloadPath': "/path/to/download/dir"}}
        command_result = driver.execute("send_command", params)
    except Exception as e:
        print("[x] Something went wrong with initialization.")
        print(e)
        exit(-1)
    print("[*] Headless chrome started.")
    return driver

def get_google_news(driver, keyword, watchList):
    for attempt in range(3):
        try:
            googlenews = GoogleNews(period='1d', region="US")
            googlenews.search(keyword)
            result = googlenews.result()
            newsRank = rank_news(result, keyword, watchList)
            return result, newsRank
        except:
            pass
    print("[x] Failed to fetch news.")
    exit(-1)

def rank_news(result, keyword, watchList):
    count = 0
    newsRanking = []
    for news in result:
        newsLink = news.get("link")
        newsRelevance = 0
        print(news.get("title"))
        words = keyword.split(" ")
        for word in words:
            if word in news.get("title").lower():
                newsRelevance += 1
            if len(watchList) > 0:
                for highlight in watchList:
                    if highlight in news.get("title").lower():
                        newsRelevance +=1
        print("Relevance: " + str(newsRelevance))
        newsRanking.append({"title": news.get("title"), "relevance": newsRelevance, "position": count})
        count += 1
    newsRanking = sorted(newsRanking, key=lambda k: k['relevance'], reverse=True)
    return newsRanking



thisPath = os.getcwd()
print(thisPath)
CHROMEDRIVER_PATH = thisPath + "\\chromedriver.exe"
myUserAgent = "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36"
# Initialization
print("[..] Starting headless chrome using " + str(myUserAgent) + "...")
driver = initialize()
print("[..] Getting some news...")
watchList = ["terrorism", "memorial", "2001", "osama", "bin laden"]
newsList, newsRank = get_google_news(driver, "11 september", watchList)
counter = 0
for news in newsList:
    if newsRank[counter].get("relevance") > 0:
        newsLink = news.get("link")
        print("[..] Getting:")
        print(newsLink)
        print("[..] Sanitizing filename...")
        unsanitizedFilename = news.get("title").replace(" ", "_") + ".html"
        sanitizedFilename = sanitize(unsanitizedFilename)
        print("[*] Flename is: " + sanitizedFilename)
        print("[..] Saving...")
        os.system("wkhtmltox\\bin\\wkhtmltopdf.exe '" + newsLink + "' saved\\" + sanitizedFilename + ".pdf")
        os.system("pdfsizeopt.exe saved\\" + sanitizedFilename + ".pdf saved\\" + sanitizedFilename + "_optimized.pdf")
        os.remove("saved\\" + sanitizedFilename + ".pdf")
        #with io.open("saved/" + sanitizedFilename, 'w', encoding="utf-8") as f:
        #    f.write(driver.page_source)
        print("[*] Done. Article saved.")
        print("============GIBE ANOTHER?===========")
    counter += 1
print("NOPE, WE FINISHED!")
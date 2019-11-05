import datetime
import requests
import os
import time
from bs4 import BeautifulSoup
from urllib.parse import quote


request_url = "https://portalsso.kaist.ac.kr/ssoProcess.ps"
returnUrl = "portal.kaist.ac.kr/user/ssoLoginProcess.face?timestamp=1572808652841"

portal_id = os.getenv('PORTAL_ID')
portal_password = os.getenv('PORTAL_PASSWORD')


def scrape(portal_id, portal_password):
    payload = {
        "userId": portal_id, 
        "password": portal_password,
        "langKnd": "en"
    }

    with requests.Session() as session:
        login_page = session.get("https://portal.kaist.ac.kr/portal/")
        if login_page.url.startswith("https://portalsso.kaist.ac.kr/"):
            ret = quote(returnUrl.replace("1=1", ""))
            time = int(datetime.datetime.now().timestamp()*1000)
            login_attempt = session.post(request_url + "?returnUrl=" +\
                ret + "&timestamp=" + str(time), data = payload)
            
            if not login_attempt.url.startswith("https://portal.kaist.ac.kr/portal"):
                return "Could not login"

            session.get("https://portal.kaist.ac.kr/lang/changeLang.face?langKnd=en")
            today_notice = session.get(("https://portal.kaist.ac.kr/board/list.brd?boardId="
                "today_notice&lang_knd=en&userAgent=Netscape&isMobile=false&"))

            soup = BeautifulSoup(today_notice.text, "html.parser")
            try:
                table = soup.find('table', attrs={'class': 'req_tbl_01'}).find('tbody')
                notices = []
                for row in table.find_all('tr'):
                    anchor = row.find('a')
                    href = anchor.attrs['href']
                    title = anchor.text
                    notices.append((href, title.strip()))
                return notices

            except (RuntimeError, TypeError, ValueError, AttributeError):
                return "Table of today notices couldn't be fetched"
        else:
            return "Unexpected behavior"
                
def try_scrape(portal_id, portal_password):
    notices = scrape(portal_id, portal_password)
    if isinstance(notices, str):
        return False
    return notices[0]

def schedule(portal_id, portal_password, last_href):
    while True:
        notices = scrape(portal_id, portal_password)
        if isinstance(notices, str):
            break
        for notice in notices:
            if notice[0] == last_href:
                break
            # Else send the notice to the user
        
        # Sleep 10 minutes
        time.sleep(600)
    return "Scheduler broke :("

print(scrape(portal_id, portal_password))

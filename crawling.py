import requests
from datetime import datetime, timedelta
import pytz
import re
import html
import api_url


queries = [
    "상수도",
    "하수도",
    "상수관",
    "하수관",
    "씽크홀",
    "싱크홀",
    # "지반침하",
    # "지반 침하",
    # "땅꺼짐",
    # "지하시설물",
    # "지하 시설물",
    # "물기술",
    # "물산업",
]
queries_2 = [
    # "상수도",
    # "하수도",
    # "상수관",
    # "하수관",
    # "씽크홀",
    # "싱크홀",
    "지반침하",
    "지반 침하",
    "땅꺼짐",
    "지하시설물",
    "지하 시설물",
    "물기술",
    "물산업",
]
max_batch_size = 10


def search_naver_news(keyword, client_id, client_secret):
    url = config.NAVER_API_URL
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}

    params = {
        "query": keyword,
        "display": 100,  # 검색 결과 출력 건수 (최대 100)
        "start": 1,  # 검색 시작 위치 (페이징 처리용, 1부터 시작)
        "sort": "sim",  # 정렬 옵션: sim(유사도순), date(날짜순)
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    # print(data)

    articles = []
    if "items" in data:
        for item in data["items"]:
            title = item["title"]
            # 태그 제거
            title = re.sub("<.*?>", "", title)
            title = html.unescape(title)

            description = item["description"]
            description = re.sub("<.*?>", "", description)
            description = html.unescape(description)

            if keyword in title:
                pub_date = item["pubDate"]
                if is_recent(pub_date):
                    pub_datetime = datetime.strptime(
                        pub_date, "%a, %d %b %Y %H:%M:%S %z"
                    )
                    kst = pytz.timezone("Asia/Seoul")
                    pub_datetime = pub_datetime.astimezone(kst)
                    day_of_week = ["월", "화", "수", "목", "금", "토", "일"]
                    pub_date_formatted = pub_datetime.strftime(
                        "%Y-%m-%d ({}) %H:%M"
                    ).format(day_of_week[pub_datetime.weekday()])

                    link = item["link"]
                    if (
                        # "com"
                        # in link
                        (
                            ("naver.com" in link and ("상수도" in title))
                            or ("상수도" not in title)
                        )
                        and (
                            ("naver.com" in link and ("하수도" in title))
                            or ("하수도" not in title)
                        )
                        # and "웹툰" not in title
                        # and "시신" not in title
                        and "태평양" not in title
                    ):
                        articles.append(
                            {
                                "title": title,
                                "link": link,
                                "description": description,
                                "date": pub_date_formatted,
                            }
                        )

    return articles


def is_recent(pub_date):
    pub_datetime = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
    now = datetime.now(pytz.timezone("Asia/Seoul"))
    time_diff = now - pub_datetime

    return time_diff <= timedelta(hours=24)


# Slack 메시지 전송 함수
def send_slack_message(message):
    data = {"text": message}
    response = requests.post(config.SLACK_WEBHOOK_NAVER_URL, json=data)
    if response.status_code == 200:
        print("Slack message sent successfully")
    else:
        print("Slack message sending failed")


# 검색 및 슬랙 메시지 전송
messages = []
seen_titles = set()  # Set to keep track of unique titles


def crawling():
    # global messages
    global messages

    for query in queries:
        # print(query)
        articles = search_naver_news(query, config.CLIENT_ID, config.CLIENT_SECRET)
        if not articles:
            message = f"-------------------------------------------------------------------\n*검색어 : {query}*\n검색결과가 없습니다\n"
            messages.append(message)

        # 최신 순으로 정렬
        articles = sorted(articles, key=lambda x: x["date"], reverse=True)

        for idx, article in enumerate(articles):
            title = article["title"]
            if title in seen_titles:
                continue  # Skip duplicate article
            seen_titles.add(title)  # Add title to the set

            if idx == 0:
                message = f"-------------------------------------------------------------------\n*검색어 : {query}*\n제목: {article['title']}\n내용: {article['description']}\n링크: {article['link']}\n날짜: {article['date']}\n\n"
            else:
                message = f"-------------------------------------------------------------------\n제목: {article['title']}\n내용: {article['description']}\n링크: {article['link']}\n날짜: {article['date']}\n\n"
            messages.append(message)

    if messages:
        send_slack_message("\n".join(messages))
        print(messages)
        messages = []

    for query in queries_2:
        articles = search_naver_news(query, config.CLIENT_ID, config.CLIENT_SECRET)
        if not articles:
            message = f"-------------------------------------------------------------------\n*검색어 : {query}*\n검색결과가 없습니다\n"
            messages.append(message)

        # 최신 순으로 정렬
        articles = sorted(articles, key=lambda x: x["date"], reverse=True)

        for idx, article in enumerate(articles):
            title = article["title"]
            if title in seen_titles:
                continue  # Skip duplicate article
            seen_titles.add(title)  # Add title to the set

            if idx == 0:
                message = f"-------------------------------------------------------------------\n*검색어 : {query}*\n제목: {article['title']}\n내용: {article['description']}\n링크: {article['link']}\n날짜: {article['date']}\n\n"
            else:
                message = f"-------------------------------------------------------------------\n제목: {article['title']}\n내용: {article['description']}\n링크: {article['link']}\n날짜: {article['date']}\n\n"
            messages.append(message)
        # send_slack_message("\n".join(messages))
    # 모든 메시지를 슬랙으로 전송
    if messages:
        send_slack_message("\n".join(messages))
        print(messages)

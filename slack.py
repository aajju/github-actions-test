import requests
import json
import api_url


def send_message(message, channel):
    webhook_urls = {
        "bid" : api_url.SLACK_WEBHOOK_NARA_URL,
        "project" : api_url.SLACK_WEBHOOK_PROJECT_URL
    }

    if channel in webhook_urls:
        webhook_url = webhook_urls[channel]

    payload = {"text": message}
    headers = {"Content-type": "application/json"}

    response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)

    if response.status_code == 200:
        print("메시지가 성공적으로 전송되었습니다.")
    else:
        print("메시지 전송 실패. 오류 코드:", response.status_code)

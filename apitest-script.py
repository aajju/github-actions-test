import requests
import os

# API URL (예시: JSON 데이터를 제공하는 API)
url = 'https://jsonplaceholder.typicode.com/todos/1'

# GET 요청 보내기
response = requests.get(url)

test_value = os.getenv("TEST_VARIABLES")
print(f"TEST_VARIABLES: {test_value}")

# 응답 상태 코드 확인 (200이면 성공)
if response.status_code == 200:
    data = response.json()  # JSON 형식으로 응답 데이터 파싱
    print("API Response Data:", data)  # 받은 데이터 출력
else:
    print(f"Failed to fetch data: {response.status_code}")  # 요청 실패 시 상태 코드 출력
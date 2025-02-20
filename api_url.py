# from dotenv import load_dotenv

import os

# load_dotenv()

JSON_KEYFILE = os.getenv("JSON_KEYFILE")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SPREADSHEET_LINK = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/"
API_KEY = os.getenv("API_KEY")
API_KEY2 = os.getenv("API_KEY2")
SLACK_WEBHOOK_NARA_URL = os.getenv("SLACK_WEBHOOK_NARA_URL")
SLACK_WEBHOOK_NAVER_URL = os.getenv("SLACK_WEBHOOK_NAVER_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")



# 발주예정 용역, 공사
URL_SCHEDULED_BID_SERVICE = "http://apis.data.go.kr/1230000/OrderPlanSttusService/getOrderPlanSttusListServcPPSSrch"
URL_SCHEDULED_BID_CONSTRUCTION = "http://apis.data.go.kr/1230000/OrderPlanSttusService/getOrderPlanSttusListCnstwkPPSSrch"

# 낙찰 용역, 공사
URL_SUCCESSBID_SERVICE = (
    # "https://apis.data.go.kr/1230000/ScsbidInfoService01/getScsbidListSttusServcPPSSrch01"
    "http://apis.data.go.kr/1230000/as/ScsbidInfoService/getScsbidListSttusServcPPSSrch"
)

URL_SUCCESSBID_CONSTRUCTION = (
    # "https://apis.data.go.kr/1230000/ScsbidInfoService01/getScsbidListSttusCnstwkPPSSrch01"
    "http://apis.data.go.kr/1230000/as/ScsbidInfoService/getScsbidListSttusCnstwkPPSSrch?"
)
# URL_SUCCESSBID_SERVICE = (
#     "https://apis.data.go.kr/1230000/ScsbidInfoService/getScsbidListSttusServc"
# )
# URL_SUCCESSBID_CONSTRUCTION = (
#     "https://apis.data.go.kr/1230000/ScsbidInfoService/getScsbidListSttusCnstwk"
# )

# 신규공고 용역, 공사
URL_NEWOPEN_SERVICE = "http://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoServcPPSSrch"
# URL_NEWOPEN_SERVICE = "https://apis.data.go.kr/1230000/BidPublicInfoService05/getBidPblancListInfoServcPPSSrch02"
URL_NEWOPEN_CONSTRUCTION = "http://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoCnstwkPPSSrch"
# URL_NEWOPEN_CONSTRUCTION = "https://apis.data.go.kr/1230000/BidPublicInfoService05/getBidPblancListInfoCnstwkPPSSrch02"

# 민간입찰공고 용역, 공사
URL_NEWOPEN_PRIVATE_SERVICE = (
    # "https://apis.data.go.kr/1230000/PrvtBidNtceService/getPrvtBidPblancListInfoServc"
    "http://apis.data.go.kr/1230000/ao/PrvtBidNtceService/getPrvtBidPblancListInfoServcPPSSrch?"
)
URL_NEWOPEN_PRIVATE_CONSTRUCTION = (
    # "https://apis.data.go.kr/1230000/PrvtBidNtceService/getPrvtBidPblancListInfoCnstwk"
    "http://apis.data.go.kr/1230000/ao/PrvtBidNtceService/getPrvtBidPblancListInfoCnstwkPPSSrch"
)

# 민간 낙찰
URL_SUCCESSBID_PRIVATE = (
    # "https://apis.data.go.kr/1230000/PrvtScsbidInfoService/getPrvtScsbidListSttus"
    "http://apis.data.go.kr/1230000/ao/PrvtScsbidInfoService/getPrvtScsbidListSttusPPSSrch?"
)

# naver_crawling
NAVER_API_URL = "http://openapi.naver.com/v1/search/news.json"


# 수자원공사 계약정보
URL_SUCCESSBID_KWATER_SERVICE = "http://apis.data.go.kr/B500001/ebid/cntrct3/servcList"
URL_SUCCESSBID_KWATER_CONSTRUCTION = (
    "http://apis.data.go.kr/B500001/ebid/cntrct3/cntrwkList"
)
URL_SUCCESSBID_KWATER_PRODUCT = "http://apis.data.go.kr/B500001/ebid/cntrct3/dmscptList"

# LH 계약정보
URL_SUCCESSBID_LH_SERVICE = f"http://openapi.ebid.lh.or.kr/ebid.com.openapi.service.OpenContractInfoList.dev?serviceKey={API_KEY2}"

# 공고 용역 우리 낙찰
URL_NEWOPEN_SERVICE_WITH_NUMBER = (
    "http://apis.data.go.kr/1230000/BidPublicInfoService05/getBidPblancListInfoServc02"
)
URL_NEWOPEN_OURCONSTRUCTION = "http://apis.data.go.kr/1230000/BidPublicInfoService05/getBidPblancListInfoCnstwk02"

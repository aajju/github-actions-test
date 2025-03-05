import requests
import api_url
import time
import main
import xml.etree.ElementTree as ET
import json
import pytz


from datetime import datetime, timedelta
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 한국 시간(KST) 기준으로 실행
kst = pytz.timezone('Asia/Seoul')
current_date = datetime.now(kst)

# 날짜 비교할 기준 값 (예: 3을 넣으면 어제~3일 전까지 포함)
days_range = 1

# 오늘 날짜 기준으로 시작 날짜 계산
start_date = current_date - timedelta(days=days_range)  # 입력한 범위만큼 과거로 설정


# 작년 12월과 내년 12월 계산
last_year_december = current_date.replace(year=current_date.year - 1, month=12)
next_year_december = current_date.replace(year=current_date.year + 1, month=12)

# 원하는 형식으로 날짜를 문자열로 변환
last_year_december_str = last_year_december.strftime("%Y%m")
next_year_december_str = next_year_december.strftime("%Y%m")

yesterday = current_date - timedelta(days=1)
yesterday_date = yesterday.date()
yesterday_month = yesterday.strftime("%Y%m")
yesterday_day = int(yesterday.strftime("%Y%m%d"))

inqry_bgn_dt = yesterday.strftime("%Y%m%d") + "0000"
inqry_end_dt = yesterday.strftime("%Y%m%d") + "2359"

one_month_ago = current_date - timedelta(days=28)
inqry_bgn_dt_1month = one_month_ago.strftime("%Y%m%d") + "0000"


required_keyword = "설계"  # Target keyword

bidNtceNos = []


def filter_items_bid(items, url):
    filtered_items = []

    search_keywords1 = ["용수", "이설", "상수", "하수", "도수", "오수", "우수관", "송수", "배수"]
    search_keywords2 = [
        # "건설",
        # "도로",
        # "주택",
        "지구",
        "택지",
        "단지",
        "조성사업",
        "개발사업",
        "과실전문생산단지",
    ]

    search_keywords = (
        search_keywords1
        + search_keywords2
        # + [
        #     "btl",
        #     "bto",
        #     "워터",
        # ]
    )

    instt_name = ["수자원", "토지", "주택", "상수", "하수", "맑은물"]

    if url == api_url.URL_SUCCESSBID_SERVICE:  # 낙찰 용역 필터링 (공고문에 키워드로 필터링)
        for item in items:
            bidNtceNo = item.get("bidNtceNo")

            bidNtceNm = item.get("bidNtceNm", "").lower()
            dminsttNm = item.get("dminsttNm", "")
            rgstDt = item.get("rgstDt", "")
            date = datetime.strptime(rgstDt, "%Y-%m-%d %H:%M:%S")
            date_only = date.date()

            if (
                (any(keyword in dminsttNm for keyword in instt_name))
                or (any(keyword in bidNtceNm for keyword in search_keywords))
                or ("원인자" in bidNtceNm)
            # ) :
            #  ) and (date_only == yesterday_date):
             ) and (start_date.date() <= date_only):
                bidNtceNos.append(bidNtceNo)
                # print(bidNtceNos)
                filtered_items.append(item)

    elif url == api_url.URL_SUCCESSBID_CONSTRUCTION:  # 낙찰 공사 필터링
        for item in items:
            rgstDt = item.get("rgstDt", "")
            date = datetime.strptime(rgstDt, "%Y-%m-%d %H:%M:%S")
            date_only = date.date()
            if (
                any(keyword in item.get("bidNtceNm", "") for keyword in search_keywords)
                # and date_only == yesterday_date
                and (start_date.date() <= date_only)
            ):
                filtered_items.append(item)

    elif url == api_url.URL_NEWOPEN_SERVICE:  # 신규공고 용역 필터링
        for item in items:
            # print(item)
            bidNtceNo = item.get("bidNtceNo")
            # bdgtAmt = int(float(item.get("presmptPrce", 0) or 0))  # 소수를 정수로 변환
            ntceKindNm = item.get("ntceKindNm")  # 취소 필터링
            bidNtceNm = item.get("bidNtceNm", "").lower()
            ntceInsttNm = item.get("ntceInsttNm", "")
            cntrctCnclsMthdNm = item.get("cntrctCnclsMthdNm", "")
            sucsfbidMthdNm = item.get("sucsfbidMthdNm", "")
            if (
                bidNtceNo not in [x.get("bidNtceNo") for x in filtered_items]
                and "취소" not in ntceKindNm   
                and "수의" not in cntrctCnclsMthdNm
                and (
                    (any(keyword in ntceInsttNm for keyword in instt_name))
                    or (any(keyword in bidNtceNm for keyword in search_keywords))
                    or any(
                        keyword in sucsfbidMthdNm
                        for keyword in [
                            "종합",
                        ]
                    )

                )
            ):
                filtered_items.append(item)
            else:
                existing_item = next(
                    (x for x in filtered_items if x.get("bidNtceNo") == bidNtceNo), None
                )
                if existing_item and item.get("bidNtceDt") > existing_item.get(
                    "bidNtceDt"
                ):
                    filtered_items.remove(existing_item)
                    filtered_items.append(item)  # for item in items:

    elif url == api_url.URL_NEWOPEN_CONSTRUCTION:  # 신규공고 공사 필터링
        for item in items:
            bidNtceNo = item.get("bidNtceNo")
            presmptPrce = int(float(item.get("presmptPrce", 0) or 0))  # 소수를 정수로 변환
            ntceKindNm = item.get("ntceKindNm")
            cntrctCnclsMthdNm = item.get("cntrctCnclsMthdNm", "").lower()
            sucsfbidMthdNm = item.get("sucsfbidMthdNm", "").lower()
            bidNtceNm = item.get("bidNtceNm", "")

            if (
                bidNtceNo not in [x.get("bidNtceNo") for x in filtered_items]
                and "취소" not in ntceKindNm   
                and (
                    presmptPrce > 85000000000  # 850억
                    or (
                        presmptPrce > 25000000000  # 250억
                        and (
                            any(
                                keyword in cntrctCnclsMthdNm
                                for keyword in [
                                    "pq",
                                    "기술",
                                    "등급",
                                ]
                            )
                            or (
                                any(
                                    keyword in sucsfbidMthdNm
                                    for keyword in ["기술", "종합", "일괄"]
                                )
                                and any(
                                    keyword in bidNtceNm for keyword in ["조성공사", "시설공사"]
                                )
                            )
                        )
                    )
                    or (
                        presmptPrce > 5000000000  # 50억
                        and any(keyword in bidNtceNm for keyword in search_keywords)
                    )
                )
            ):
                filtered_items.append(item)
            else:
                existing_item = next(
                    (x for x in filtered_items if x.get("bidNtceNo") == bidNtceNo), None
                )
                if existing_item and item.get("bidNtceDt") > existing_item.get(
                    "bidNtceDt"
                ):
                    filtered_items.remove(existing_item)
                    filtered_items.append(item)

    elif url in [
        api_url.URL_NEWOPEN_PRIVATE_SERVICE,  # 신규공고 민간용역
        api_url.URL_NEWOPEN_PRIVATE_CONSTRUCTION,  # 신규공고 민간공사
    ]:  # 신규공고 민간 필터링
        filtered_items_dict = {}
        for item in items:
            bidNtceNm = item.get("ntceNm", "").lower()
            bidNtceNo = item.get("bidNtceNo", "")  # 공고번호
            bidNtceOrd = item.get("bidNtceOrd", "")  # 공고차수

            if any(keyword in bidNtceNm for keyword in search_keywords):
                if bidNtceNo not in filtered_items_dict:
                    filtered_items_dict[bidNtceNo] = item
                else:
                    existing_item = filtered_items_dict[bidNtceNo]
                    existing_bidNtceOrd = existing_item.get("bidNtceOrd", "")
                    if bidNtceOrd > existing_bidNtceOrd:
                        filtered_items_dict[bidNtceNo] = item
        filtered_items = list(filtered_items_dict.values())

    elif url == api_url.URL_SUCCESSBID_PRIVATE:  # 낙찰 민간
        for item in items:
            bidNtceNm = item.get("bidNtceNm", "").lower()
            sucsfbidAmt = int(float(item.get("sucsfbidAmt", 0) or 0))  # 소수를 정수로 변환

            # sucsfbidAmt = item.get("sucsfbidAmt", "")
            # bidNtceNo = item.get("bidNtceNo", "")  # 공고번호
            # bidNtceOrd = item.get("bidNtceOrd", "")  # 공고차수
            bsnsDivNm = item.get("bsnsDivNm", "")
            if (
                any(keyword in bsnsDivNm for keyword in ["용역", "공사"])
                and any(keyword in bidNtceNm for keyword in search_keywords)
                and sucsfbidAmt > 100000000
            ):
                filtered_items.append(item)

    elif url in [
        api_url.URL_SUCCESSBID_KWATER_SERVICE,  # 낙찰 수자원 용역
    ]:
        kwater_items = items["item"]
        print("kwater filter function")
        # 딕셔너리 리스트가 한개일때 처리 필요???  처리 250305
        # 리스트가 아니면 리스트로 변환
        if not isinstance(kwater_items, list):
            kwater_items = [kwater_items]
        # 낙찰 수자원 용역 제대로
        for item in kwater_items:
            if (
                item["cntrctDe"] == yesterday_day
                and int(float(item["lastCtramt"].replace(",", "")) or 0) > 80000000
                and (keyword in item["ordgTit"] for keyword in ["설계", "계획", "타당성"])
            ):
                filtered_items.append(item)

        ## 낙찰 수자원 용역 일괄 뽑기
        # for item in kwater_items:
        #     if (
        #         int(float(item["lastCtramt"].replace(",", "")) or 0) > 65000000
        #         and required_keyword in item["ordgTit"]
        #     ):
        #         filtered_items.append(item)

    elif url in [
        api_url.URL_SUCCESSBID_KWATER_CONSTRUCTION,  # 낙찰 수자원 공사
    ]:
        kwater_items = items["item"]
        # 리스트가 아니면 리스트로 변환
        if not isinstance(kwater_items, list):
            kwater_items = [kwater_items]
        ## 낙찰 수자원 공사 제대로
        for item in kwater_items:
            if (
                item["cntrctDe"] == yesterday_day
                and int(float(item["lastCtramt"].replace(",", "")) or 0) > 2000000000
                and (keyword in item["ordgTit"] for keyword in ["설계", "계획", "타당성"])
            ):
                filtered_items.append(item)

        ## 낙찰 수자원 공사 일괄 뽑기
        # for item in kwater_items:
        #     if int(
        #         float(item["lastCtramt"].replace(",", "")) or 0
        #     ) > 2000000000 and any(
        #         keyword in item["ordgTit"] for keyword in search_keywords
        #     ):
        #         filtered_items.append(item)

    elif url == api_url.URL_SUCCESSBID_LH_SERVICE:  # LH 낙찰
        lh_items = items["item"]
        for item in lh_items:
            if (
                "용역" in item["cstrtn_job_gb_nm"]
                and required_keyword in item["ctrct_nm"]
            ) or ("공사" in item["cstrtn_job_gb_nm"] and "조성공사" in item["ctrct_nm"]):
                filtered_items.append(item)

    elif url in [
        api_url.URL_SCHEDULED_BID_SERVICE,
        api_url.URL_SCHEDULED_BID_CONSTRUCTION,
    ]:  # 발주예정 용역, 공사
        # print(items)
        for item in items:
            bsnsDivCd = item.get("bsnsDivCd", "")
            bizNm = item.get("bizNm", "")
            cntrctMthdNm = item.get("cntrctMthdNm", "")

            if any(keyword in bizNm for keyword in ["설계", "계획"]) and (bsnsDivCd == "05"):
                if any(keyword in bizNm for keyword in search_keywords) and (
                    int(float(item["sumOrderAmt"].replace(",", "")) or 0) > 100000000
                ):
                    filtered_items.append(item)
            if (bsnsDivCd == "03") and (cntrctMthdNm == "기술제안"):
                filtered_items.append(item)

        # print(filtered_items)

    return filtered_items

# 계획, 타당성 키워드
def filter_items_bid2(items, url):
    print("filter_items_bid2")
    filtered_items = []

    search_keywords = ["기본계획", "타당성"]
    # search_keywords1 = ["용수", "이설", "상수", "하수", "도수", "오수", "우수관", "송수", "배수"]


    if url == api_url.URL_SUCCESSBID_SERVICE:  # 낙찰 용역 필터링 (공고문에 키워드로 필터링)
        for item in items:
            bidNtceNo = item.get("bidNtceNo")

            bidNtceNm = item.get("bidNtceNm", "").lower()
            rgstDt = item.get("rgstDt", "")
            date = datetime.strptime(rgstDt, "%Y-%m-%d %H:%M:%S")
            date_only = date.date()

            if (
                (any(keyword in bidNtceNm for keyword in search_keywords))
            ) and "설계" not in bidNtceNm and (start_date.date() <= date_only) : # (date_only == yesterday_date):
                bidNtceNos.append(bidNtceNo)
                # print(bidNtceNos)
                filtered_items.append(item)

    elif url == api_url.URL_NEWOPEN_SERVICE:  # 신규공고 용역 필터링
        for item in items:
            bidNtceNo = item.get("bidNtceNo")
            # bdgtAmt = int(float(item.get("presmptPrce", 0) or 0))  # 소수를 정수로 변환
            ntceKindNm = item.get("ntceKindNm")  # 취소 필터링
            bidNtceNm = item.get("bidNtceNm", "").lower()
            ntceInsttNm = item.get("ntceInsttNm", "")
            cntrctCnclsMthdNm = item.get("cntrctCnclsMthdNm", "")
            sucsfbidMthdNm = item.get("sucsfbidMthdNm", "")
            if (
                bidNtceNo not in [x.get("bidNtceNo") for x in filtered_items]
                and "취소" not in ntceKindNm   
                and "설계" not in bidNtceNm
                and "수의" not in cntrctCnclsMthdNm
                and (any(keyword in bidNtceNm for keyword in search_keywords))
            ):
                filtered_items.append(item)
    return filtered_items


def get_data_bid(url, sign=True):
    NUM_OF_ROWS = 999

    # 요청 파라미터
    params = {
        "ServiceKey": api_url.API_KEY,
        "numOfRows": NUM_OF_ROWS,  # 가져올 항목 수
        "pageNo": 1,  # 페이지 번호
        "inqryDiv": 1,
        "type": "json",
        "inqryBgnDt": inqry_bgn_dt,
        "inqryEndDt": inqry_end_dt,
        # "inqryBgnDt": 202502210000,
        # "inqryEndDt": 202502242359,
    }

    if sign :
        if url in [
            api_url.URL_SCHEDULED_BID_SERVICE,
            api_url.URL_SCHEDULED_BID_CONSTRUCTION,
            api_url.URL_SUCCESSBID_SERVICE,
            api_url.URL_SUCCESSBID_CONSTRUCTION,
            api_url.URL_NEWOPEN_SERVICE,
            api_url.URL_NEWOPEN_CONSTRUCTION,
            api_url.URL_NEWOPEN_PRIVATE_SERVICE,
            api_url.URL_NEWOPEN_PRIVATE_CONSTRUCTION,
            api_url.URL_SUCCESSBID_PRIVATE,
            api_url.URL_SUCCESSBID_KWATER_SERVICE,
            api_url.URL_SUCCESSBID_KWATER_CONSTRUCTION,
            # api_url.URL_SUCCESSBID_KWATER_PRODUCT,
            api_url.URL_SUCCESSBID_LH_SERVICE,
        ]:
            items = []
            filtered_items = []

            if url in [api_url.URL_SUCCESSBID_SERVICE, api_url.URL_SUCCESSBID_CONSTRUCTION]:
                params["inqryBgnDt"] = inqry_bgn_dt_1month
                params["inqryDiv"] = 2  # 1: 공고게시일시,  2:개찰일시, 3:입찰공고번호
                if url == api_url.URL_SUCCESSBID_SERVICE:
                    params["presmptPrceBgn"] = 100000000  # 1억 이상
                    params["bidNtceNm"] = required_keyword

                elif url == api_url.URL_SUCCESSBID_CONSTRUCTION:
                    params["presmptPrceBgn"] = 2000000000  # 20억 이상

            elif url == api_url.URL_NEWOPEN_SERVICE:  # 신규공고_용역
                params["presmptPrceBgn"] = 300000000  # 3억 이상
                params["bidNtceNm"] = required_keyword

            elif url == api_url.URL_NEWOPEN_CONSTRUCTION:  # 신규공고_공사
                params["presmptPrceBgn"] = 5000000000  # 50억 이상

            elif url in [  # 수자원 계약정보
                api_url.URL_SUCCESSBID_KWATER_SERVICE,
                api_url.URL_SUCCESSBID_KWATER_CONSTRUCTION,
                # api_url.URL_SUCCESSBID_KWATER_PRODUCT,
            ]:
                # params["_type"] = params.pop("type")
                # params["ServiceKey"] = api_url.API_KEY2
                del params["inqryDiv"]
                del params["inqryBgnDt"]
                del params["inqryEndDt"]
                del params["type"]
                params["_type"] = "json"
                params["searchDt"] = yesterday_month
                # params["searchDt"] = 202502 # 20250225

            elif url == api_url.URL_SUCCESSBID_LH_SERVICE:  # LH 계약정보
                del params["ServiceKey"]
                del params["inqryDiv"]
                del params["inqryBgnDt"]
                del params["inqryEndDt"]
                del params["type"]
                # params["contractDtStart"] = 20250201
                # params["contractDtEnd"] = 20250225
                params["contractDtStart"] = yesterday_day
                params["contractDtEnd"] = yesterday_day

            elif url in [
                api_url.URL_SCHEDULED_BID_SERVICE,
                api_url.URL_SCHEDULED_BID_CONSTRUCTION,
            ]:  # 발주예정(용역)
                # params["orderBgnYm"] = yesterday_month
                params["bizNm"] = "설계"
                # params["orderBgnYm"] = last_year_december_str
                params["orderBgnYm"] = "202501"
                params["orderEndYm"] = next_year_december_str

            try:
                print(params)
                response = requests.get(url, params=params, verify=False, timeout=60)
                if response.status_code == 200:
                    if url == api_url.URL_SUCCESSBID_LH_SERVICE:
                        try:
                            encoding = response.encoding if response.encoding else "utf-8"
                            root = ET.fromstring(response.content.decode(encoding))
                            total_count = -1
                            # print(response.text)
                            total_count = int(
                                root.find(".//totalCount").text
                            )  # totalCount 추출

                            items_xml = root.findall(".//item")
                            temp_items = []

                            for item in items_xml:
                                data = {
                                    "bid_num": item.find("bidNum").text,
                                    "cstrtn_job_gb_nm": item.find("cstrtnJobGbNm").text,
                                    "ctrct_nm": item.find("ctrctNm").text.strip(),
                                    "ctrct_cntrctg_dt": item.find("ctrctCntrctgDt").text,
                                    "tndr_ctrct_med_nm": item.find("tndrCtrctMedNm").text,
                                    "ctrct_amt": item.find("ctrctAmt").text,
                                    "init_bgnwrk_dt": item.find("initBgnwrkDt").text,
                                    "finl_compwrk_dt": item.find("finlCompwrkDt").text,
                                    "ctrct_vndr_type_nm": item.find(
                                        "ctrctVndrTypeNm"
                                    ).text.strip(),
                                    "ctrct_vndr_nm": item.find("ctrctVndrNm").text.strip(),
                                    "ctrct_vndr_ceo_nm": item.find("ctrctVndrCeoNm").text,
                                    "ctrct_vndr_addr": item.find(
                                        "ctrctVndrAddr"
                                    ).text.strip(),
                                    "ctrct_taxregno": item.find("ctrctTaxregno").text,
                                    "revert_dept_nm": item.find(
                                        "revertDeptNm"
                                    ).text.strip(),
                                }
                                temp_items.append(data)
                            # JSON 생성
                            json_data = {"item": temp_items}

                            items_str = json.dumps(json_data, indent=4, ensure_ascii=False)

                            items = json.loads(items_str)
                            # print(items)
                        except (ET.ParseError, AttributeError) as e:
                            print(f"Error occurred while parsing XML: {e}")
                    else:
                        # print(response.text)
                        try:
                            data = response.json()
                            # print(data)
                            total_count = data["response"]["body"]["totalCount"]
                            items = data["response"]["body"]["items"]
                            # print(items)
                        except (KeyError, requests.exceptions.JSONDecodeError) as e:
                            print(f"Error occurred while parsing JSON: {e}")
                            total_count = -1  # 예외 발생 시 total_count를 -1으로 초기화
                            items = []  # items 키가 없는 경우 빈 리스트로 초기화
                    print("total count: ", total_count)

                    if total_count > 999 and url != api_url.URL_SUCCESSBID_LH_SERVICE:
                        num_of_pages = (total_count // NUM_OF_ROWS) + 1  # 총 페이지 수 계산
                        for page in range(2, num_of_pages + 1):
                            params["pageNo"] = page  # 페이지 번호 설정
                            response = requests.get(url, params=params, verify=False)
                            if response.status_code == 200:
                                data = response.json()
                                items += data["response"]["body"]["items"]
                            else:
                                print("API 호출 실패:", response.status_code)
                                return None
                    if items:
                        # print(type(items))
                        # print(items[0])
                        filtered_items = filter_items_bid(items, url)

                    if url == api_url.URL_SUCCESSBID_SERVICE:
                        data = get_data_w_number()
                        main.process_data_bid(data, "낙찰용역_w공고")
                    print("len(filtered_items):", len(filtered_items))
                else:
                    print("API 호출 실패:", response.status_code)
                    return None
            except requests.exceptions.Timeout:
                print("서버 응답 시간이 초과되었습니다. 요청이 실패했습니다.")
                return None

            # print(filtered_items)
            return filtered_items

        else:
            print("유효하지 않은 URL입니다.")
            return None

    if sign == False:
        items = []
        filtered_items = []

        if url in [api_url.URL_SUCCESSBID_SERVICE, api_url.URL_SUCCESSBID_CONSTRUCTION]:
            params["inqryBgnDt"] = inqry_bgn_dt_1month
            params["inqryDiv"] = 2  # 1: 공고게시일시,  2:개찰일시, 3:입찰공고번호
       
        elif url == api_url.URL_NEWOPEN_SERVICE:  # 신규공고_용역
                params["presmptPrceBgn"] = 300000000  # 3억 이상

        try:
            response = requests.get(url, params=params, verify=False, timeout=60)
            if response.status_code == 200 and response.text :
                # print(response.text)
                try:
                    data = response.json()
                    # print(data)
                    total_count = data["response"]["body"]["totalCount"]
                    items = data["response"]["body"]["items"]
                    # print(items)
                except (KeyError, requests.exceptions.JSONDecodeError) as e:
                    print(f"Error occurred while parsing JSON: {e}")
                    total_count = -1  # 예외 발생 시 total_count를 -1으로 초기화
                    items = []  # items 키가 없는 경우 빈 리스트로 초기화

                if total_count > 999 :
                    num_of_pages = (total_count // NUM_OF_ROWS) + 1  # 총 페이지 수 계산
                    for page in range(2, num_of_pages + 1):
                        params["pageNo"] = page  # 페이지 번호 설정
                        response = requests.get(url, params=params, verify=False)
                        if response.status_code == 200:
                            data = response.json()
                            items += data["response"]["body"]["items"]
                        else:
                            print("API 호출 실패:", response.status_code)
                            return None
                if items:
                    # print(type(items))
                    # print(items[0])
                    filtered_items = filter_items_bid2(items, url)

                print("len(filtered_items):", len(filtered_items))
            else:
                print("API 호출 실패:", response.status_code)
                return None
        except requests.exceptions.Timeout:
            print("서버 응답 시간이 초과되었습니다. 요청이 실패했습니다.")
            return None

        # print(filtered_items)
        return filtered_items

def get_data_scheduledbid_service():
    return get_data_bid(api_url.URL_SCHEDULED_BID_SERVICE)

# def get_data_scheduledbid_construction():
#     return get_data_bid(api_url.URL_SCHEDULED_BID_CONSTRUCTION)

def get_data_successbid_service():
    return get_data_bid(api_url.URL_SUCCESSBID_SERVICE)

def get_data_successbid_service_nodesign():
    return get_data_bid(api_url.URL_SUCCESSBID_SERVICE, sign=False)

def get_data_successbid_construction():
    return get_data_bid(api_url.URL_SUCCESSBID_CONSTRUCTION)

def get_data_newopen_service():
    return get_data_bid(api_url.URL_NEWOPEN_SERVICE)

def get_data_newopen_service_nodesign():
    return get_data_bid(api_url.URL_NEWOPEN_SERVICE, sign=False)

def get_data_newopen_construction():
    return get_data_bid(api_url.URL_NEWOPEN_CONSTRUCTION)


def get_data_newopen_private():
    data_service = get_data_bid(api_url.URL_NEWOPEN_PRIVATE_SERVICE)
    data_construction = get_data_bid(api_url.URL_NEWOPEN_PRIVATE_CONSTRUCTION)
    return data_service + data_construction


def get_data_successbid_private():
    return get_data_bid(api_url.URL_SUCCESSBID_PRIVATE)


# def get_data_our_newopen():
#       data_service = get_ourdata(api_url.URL_NEWOPEN_SERVICE_WITH_NUMBER)
#     # data_construction = get_ourdata(api_url.URL_NEWOPEN_OURCONSTRUCTION)
#     return data_service
#     # return data_service + data_construction


def get_data_successbid_kwater():
    # return get_data_successbid(api_url.URL_SUCCESSBID_KWATER_SERVICE)
    data_service = get_data_bid(api_url.URL_SUCCESSBID_KWATER_SERVICE)
    data_construction = get_data_bid(api_url.URL_SUCCESSBID_KWATER_CONSTRUCTION)
    # data_product = get_data_successbid(api_url.URL_SUCCESSBID_KWATER_PRODUCT)

    return data_construction + data_service  # + data_product
    # return data_service  # + data_product


def get_data_successbid_lh():
    return get_data_bid(api_url.URL_SUCCESSBID_LH_SERVICE)


def get_data_w_number():
    global bidNtceNos
    items = []  # 결과를 담을 빈 리스트
    for bidNtceNo in bidNtceNos:
        params = {
            "ServiceKey": api_url.API_KEY,
            "numOfRows": 10,  # 가져올 항목 수
            "pageNo": 1,  # 페이지 번호
            "inqryDiv": 2,  # 1: 공고게시일시,  2:공고번호
            "type": "json",
            "bidNtceNo": bidNtceNo,
        }
        response = requests.get(
            api_url.URL_NEWOPEN_SERVICE_WITH_NUMBER, params=params, verify=False
        )
        time.sleep(1)
        if response.status_code == 200:
            try:
                data = response.json()
                new_items = data["response"]["body"]["items"]
                items.extend(new_items)  # 각 new_item을 items 리스트에 추가합니다.
            except (KeyError, requests.exceptions.JSONDecodeError) as e:
                print(f"Error occurred while parsing JSON: {e}")

        else:
            print("API 호출 실패:", response.status_code)
            return None

    return items


# def get_data_newopen_service_with_number():
#     data_service = get_data_w_number(api_url.URL_NEWOPEN_SERVICE_WITH_NUMBER)
#     return data_service


import spreadsheet
import slack
import api
import datetime
import crawling
import time
import api_url


today = datetime.date.today().strftime("%Y-%m-%d")  # 오늘 날짜 가져오기 (YYYY-MM-DD 형식)
message_bid = f"*{today}*\n"
message_project = f"*{today}*\n"


def process_data_bid(data, category):
    global message_bid

    if data:
        # 스프레드시트에 데이터 저장
        if category == "낙찰정보_용역(설계)":
            sheet_index = 0
        elif category == "낙찰정보_용역(계획)":
            sheet_index = 0
        elif category == "낙찰정보_공사":
            sheet_index = 1
        elif category == "신규공고_용역(설계)":
            sheet_index = 3
        elif category == "신규공고_용역(계획)":
            sheet_index = 3
        elif category == "신규공고_공사":
            sheet_index = 4
        elif category == "신규공고_민간":
            sheet_index = 5
        elif category == "낙찰정보_민간":
            sheet_index = 2
        # elif category == "코위드원_용역":
        #     sheet_index = 6
        # elif category == "코위드원_공사":
        #     sheet_index = 7
        elif category == "낙찰용역_w공고":
            sheet_index = 7
        elif category == "낙찰정보_수자원":
            sheet_index = 8
        elif category == "낙찰정보_LH":
            sheet_index = 9
        elif category == "발주예정_용역":
            sheet_index = 6
        # elif category == "발주예정_공사":
        #     sheet_index = 6
        else:
            print(f"sheet_index error. category =={category}")
            return
        spreadsheet.save_data_bid(data, sheet_index)  # sheet1 = 0,  sheet2 = 1 ...
        message_bid += f"*{category}* 나라장터 정보를 스크랩했습니다 ({len(data)})\n"

    else:
        print(f"나라장터 {category} 데이터를 가져오는데 실패했습니다.")
        message_bid += f"*{category}* 나라장터 정보가 없습니다 \n"

    if category == "낙찰정보_민간":
        message_bid += f"{api_url.SPREADSHEET_LINK}"
        print(message_bid)
        slack.send_message(message_bid,"bid")


def main():

    # crawling.crawling()
    # time.sleep(1)

    # 낙찰 용역 스크랩
    data_successbid_service = api.get_data_successbid_service()
    process_data_bid(data_successbid_service, "낙찰정보_용역(설계)")
    time.sleep(1)
    
    # 낙찰 용역 스크랩(계획,타당성,ve 키워드)
    data_successbid_service_nodesign = api.get_data_successbid_service_nodesign()
    process_data_bid(data_successbid_service_nodesign, "낙찰정보_용역(계획)")
    time.sleep(1)

    # 낙찰 공사 스크랩
    data_successbid_construction = api.get_data_successbid_construction()
    process_data_bid(data_successbid_construction, "낙찰정보_공사")
    time.sleep(1)

    # 공고 용역 스크랩
    data_newopen_service = api.get_data_newopen_service()
    process_data_bid(data_newopen_service, "신규공고_용역(설계)")
    time.sleep(1)

    # 공고 용역 스크랩(계획,타당성,ve 키워드)
    data_newopen_service = api.get_data_newopen_service_nodesign()
    process_data_bid(data_newopen_service, "신규공고_용역(계획)")
    time.sleep(1)


    # 공고 공사 스크랩
    data_newopen_construction = api.get_data_newopen_construction()
    process_data_bid(data_newopen_construction, "신규공고_공사")
    time.sleep(1)

    # 공고 민간 용역, 공사
    data_newopen_private_service = api.get_data_newopen_private()
    process_data_bid(data_newopen_private_service, "신규공고_민간")
    time.sleep(1)

    # 낙찰 민간
    data_successbid_private = api.get_data_successbid_private()
    process_data_bid(data_successbid_private, "낙찰정보_민간")
    time.sleep(1)

    # # 낙찰 수자원공사
    # data_successbid_kwater = api.get_data_successbid_kwater()
    # process_data_bid(data_successbid_kwater, "낙찰정보_수자원")
    # time.sleep(1)

    # # 낙찰 LH
    # data_successbid_lh = api.get_data_successbid_lh()
    # process_data_bid(data_successbid_lh, "낙찰정보_LH")
    # time.sleep(1)

    # # 발주예정 용역
    # data_scheduledbid_service = api.get_data_scheduledbid_service()
    # process_data_bid(data_scheduledbid_service, "발주예정_용역")
    # time.sleep(1)



if __name__ == "__main__":
    main()

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import api_url
import time
from datetime import datetime


def get_yesterday_date():
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")


def get_spreadsheet(sheetid):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        api_url.JSON_KEYFILE, scope
    )
    client = gspread.authorize(credentials)
    return client.open_by_key(sheetid)



# 인증 및 연결
def save_data_bid(items, i):
    spreadsheet = get_spreadsheet(api_url.SPREADSHEET_ID)

    # 시트 열기
    worksheet = spreadsheet.get_worksheet(i)

    # items = data["response"]["body"]["items"]

    # 데이터 처리
    if i <= 1:  # 낙찰 처리
        print("낙찰 스프레드 시트!")

        for item in items:
            bidNtceNo = item["bidNtceNo"]  # 입찰공고번호
            rlOpengDt = item["rlOpengDt"]  # 실개찰일시
            fnlSucsfDate = item["fnlSucsfDate"]  # 최종낙찰일자
            rgstDt = item["rgstDt"]  # 등록일시
            # bidNtceOrd = item["bidNtceOrd"]  # 입찰공고차수
            # rbidNo = item["rbidNo"]  # 재입찰번호
            # ntceDivCd = item["ntceDivCd"]  # 공고구분코드 (1나라, 2연계)
            bidNtceNm = item["bidNtceNm"]  # 입찰공고명
            # prtcptCnum = item["prtcptCnum"]  # 참가업체수
            bidwinnrNm = item["bidwinnrNm"]  # 최종낙찰업체명
            # bidwinnrBizno = item["bidwinnrBizno"]  # 최종낙찰업체사업자번호
            # bidwinnrCeoNm = item["bidwinnrCeoNm"]  # 최종낙찰업체대표자명
            bidwinnrAdrs = item["bidwinnrAdrs"]  # 최종낙찰업체주소
            bidwinnrTelNo = item["bidwinnrTelNo"]  # 최종낙찰업체전화번호
            sucsfbidAmt = item["sucsfbidAmt"]  # 최종낙찰금액
            # sucsfbidRate = item["sucsfbidRate"]  # 최종낙찰률
            # dminsttCd = item["dminsttCd"]  # 수요기관코드
            dminsttNm = item["dminsttNm"]  # 수요기관명
            # fnlSucsfCorpOfcl = item["fnlSucsfCorpOfcl"]  # 최종낙찰업체담당자
            # linkInsttNm = item["linkInsttNm"]

            worksheet.append_row(
                [
                    bidNtceNo,
                    rlOpengDt,
                    fnlSucsfDate,
                    rgstDt,
                    bidNtceNm,
                    bidwinnrNm,
                    bidwinnrAdrs,
                    bidwinnrTelNo,
                    sucsfbidAmt,
                    dminsttNm,
                ]
            )

            # 분당 쓰기 제한을 위한 대기 시간 설정
            time.sleep(1)  # 1초 대기

    elif i == 3:  # 신규공고 용역
        print("공고 용역 스프레드 시트!")
        for item in items:
            worksheet.append_row(
                [
                    item["bidNtceNo"],  # 공고번호
                    # item["bidNtceOrd"],  # 공고 차수
                    # item["reNtceYn"],  # 재공고 여부
                    # item["rgstTyNm"],  # 등록유형
                    # item["ntceKindNm"],  # 공고종류
                    # item["intrbidYn"],  # 국제입찰
                    item["bidNtceDt"],  # 공고 날짜
                    # item["refNo"],  # 참조
                    item["bidNtceNm"],  # 입찰공고명
                    item["asignBdgtAmt"],  # 총예가
                    item["presmptPrce"],  # 추정 가격
                    item["ntceInsttNm"],  # 공고기관
                    item["dminsttNm"],  # 수요기관
                    item["cntrctCnclsMthdNm"],  # 계약방법
                    item["bidBeginDt"],  # 입찰개시일시
                    item["bidClseDt"],  # 입찰마감일시
                    # item["prearngPrceDcsnMthdNm"],  # 예가 방법 이름
                    # item["bidNtceDtlUrl"],  # 입찰 공고 상세 링크
                    item["srvceDivNm"],  # 용역 구분 관련..
                    item["cmmnSpldmdMethdNm"],  # 공동 수급
                    item["sucsfbidMthdNm"],  # 낙찰 방식
                    item["ntceInsttOfclNm"],  # 공고 담당자 이름
                    item["ntceInsttOfclTelNo"],  # 공고 담당자 전화번호
                    item["ntceInsttOfclEmailAdrs"],  # 공고 담당자 이메일 주소
                    # item["rgstDt"],  # 등록 일시
                    # item["ntceInsttCd"],  # 공고기관코드
                    # item["dminsttCd"],  # 수요기관코드
                    # item["bidMethdNm"],  # 입찰방식
                    # item["opengDt"],  # 개찰일시
                    # item["rbidPermsnYn"],  # 재입찰허용
                    # item["bidPrtcptLmtYn"],  # 입찰 참가 제한 여부
                    # item["opengPlce"],  # 개찰 장소
                    # item["bidNtceUrl"],
                    # item["crdtrNm"],  # 신용?
                    # item["ppswGnrlSrvceYn"],
                    # item["untyNtceNo"],
                    # item["dsgntCmptYn"],  # 설계 경쟁 여부
                    # item["arsltCmptYn"],  # 결과 경쟁 여부
                    # item["pqEvalYn"],  # PQ 심사 여부
                    # item["tpEvalYn"],
                    # item["ntceDscrptYn"],  # 공고 내용 여부
                    # item["orderPlanUntyNo"],  # 발주 계획 단위 번호
                    # item["bfSpecRgstNo"],  # 사전규격등록번호
                    # item["sucsfbidMthdCd"],  # 낙찰 방식 코드
                    # item["chgDt"],
                    # item["linkInsttNm"],
                    # item["indstrytyLmtYn"],  # 업종제한
                    # item["chgNtceRsn"],  # 변경공고 사요
                    # item["rbidOpengDt"],
                    # item["VAT"],  # 부가세
                ]
            )
            time.sleep(1)  # 1초 대기

    elif i == 4:  # 신규공고 공사
        print("공고 공사 스프레드 시트!")

        for item in items:
            worksheet.append_row(
                [
                    item["bidNtceNo"],  # 입찰 공고 번호
                    item["bidNtceDt"],  # 입찰 공고 날짜
                    item["bidClseDt"],  # 입찰 마감 일시
                    item["bidNtceNm"],  # 입찰 공고명
                    item["presmptPrce"],  # 추정 가격
                    # item["bdgtAmt"],  # 추정 금액
                    item["govsplyAmt"],  # 관급 금액
                    item["sucsfbidMthdNm"],  # 낙찰 방식
                    item["ntceInsttNm"],  # 공고 기관 이름
                    item["dminsttNm"],  # 수요 기관 이름
                    item["cntrctCnclsMthdNm"],  # 계약 방법
                    item["sucsfbidLwltRate"],  # 최종 낙찰율
                    item["bidNtceDtlUrl"],  # 입찰 공고 상세 링크
                    item["ntceInsttOfclNm"],  # 공고 담당자 이름
                    item["ntceInsttOfclTelNo"],  # 공고 담당자 전화번호
                    item["ntceInsttOfclEmailAdrs"],  # 공고 담당자 이메일 주소
                    # item["bidNtceOrd"],  # 입찰 공고 차수
                    # item["reNtceYn"],  # 재공고 여부
                    # item["rgstTyNm"],  # 등록 유형
                    # item["ntceKindNm"],  # 공고 종류
                    # item["intrbidYn"],  # 국제입찰 여부
                    # item["refNo"],  # 참조 번호
                    # item["ntceInsttCd"],  # 공고 기관 코드
                    # item["dminsttCd"],  # 수요 기관 코드
                    # item["bidMethdNm"],  # 입찰 방식 이름
                    # item["dsgntCmptYn"],  # 설계 경쟁 여부
                    # item["exctvNm"],  # 집행 관 이름
                    # item["bidQlfctRgstDt"],  # 입찰 참가자 자격 등록 마감 일시
                    # item["bidBeginDt"],  # 입찰 개시 일시
                    # item["opengDt"],  # 개찰 일시
                    # item["dtlsBidYn"],  # 상세 입찰 여부
                    # item["bidPrtcptLmtYn"],  # 입찰 참가 제한 여부
                    # item["prearngPrceDcsnMthdNm"],  # 예가 방법 이름
                    # item["totPrdprcNum"],  # 총 예가
                    # item["drwtPrdprcNum"],  # 추첨 예가
                    # item["aplBssCntnts"],  # 적격 심사 평가 기준
                    # item["indstrytyEvlRt"],  # 업종 평가 비율
                    # item["mainCnsttyNm"],  # 주 업종 이름
                    # item["mainCnsttyCnstwkPrearngAmt"],  # 주 업종 공사 예비금액
                    # item["opengPlce"],  # 개찰 장소
                    # item["arsltCmptYn"],  # 결과 경쟁 여부
                    # item["pqEvalYn"],  # PQ 심사 여부
                    # item["ntceDscrptYn"],  # 공고 내용 여부
                    # item["orderPlanUntyNo"],  # 발주 계획 단위 번호
                    # item["rgstDt"],  # 등록 일시
                ]
            )

            time.sleep(1)  # 1초 대기

    elif i == 5:  # 신규공고_민간(용역&공사)
        print("공고 민간용역 스프레드 시트!")
        for item in items:
            worksheet.append_row(
                [
                    item["bidNtceNo"],  # 공고번호
                    # item["bidNtceOrd"],  # 공고 차수
                    item["nticeDt"],  # 공고 날짜
                    item["bidBeginDt"],  # 입찰개시일시
                    item["bidClseDt"],  # 입찰마감일시
                    item["bidNtceClsfc"],  # 입찰분류(공사, 용역 등)
                    # item["ntceDivNm"],  # 공고 구분
                    # item["refNo"],  # 참조
                    item["ntceNm"],  # 입찰공고명
                    item["sucsfbidMthdNm"],  # 낙찰 방식
                    item["asignBdgtAmt"],  # 총예가
                    item["ntceInsttNm"],  # 공고기관
                    item["ofclNm"],  # 공고 담당자 이름
                    item["ofclTelNo"],  # 공고 담당자 전화번호
                    item["ofclEmail"],  # 공고 담당자 이메일 주소
                    # item["bidMethdNm"],  # 입찰방식
                    # item["opengDt"],  # 개찰일시
                    # item["opengPlce"],  # 개찰 장소
                    # item["rgstDt"],  # 등록 일시
                    item["vatInclsnYnNm"],  # 부가세
                ]
            )
            time.sleep(1)  # 1초 대기

    elif i == 2:  # 낙찰 민간
        print("낙찰 민간 스프레드 시트!")
        for item in items:
            worksheet.append_row(
                [
                    item["bidNtceNo"],  # 공고번호
                    item["bsnsDivNm"],  # 입찰분류(공사, 용역 등)
                    # item["bidNtceOrd"],  # 공고 차수
                    get_yesterday_date(),  # 오늘 날짜
                    item["rlOpengDt"],  # 개찰일시
                    # item["rbidNo"],  # 재공고번호
                    # item["prtcptCnum"],  # 참가업체수
                    # item["sucsfbidRate"],  # 최종낙찰률
                    item["bidNtceNm"],  # 입찰공고명
                    item["sucsfbidAmt"],  # 낙찰가
                    item["dminsttNm"],  # 수요기관
                    # item["dminsttCd"],  # 수요기관코드
                    item["bidwinnrNm"],  # 낙찰업체명
                    item["bidwinnrTelNo"],  # 낙찰업체 전화번호
                    item["bidwinnrAdrs"],  # 낙찰업체 주소
                ]
            )
            time.sleep(1)  # 1초 대기

    elif i == 7:  # 신규공고 공사
        print("i == 7")

        for item in items:
            worksheet.append_row(
                [
                    item["bidNtceNo"],  # 공고번호
                    item["bidNtceOrd"],  # 공고 차수
                    # item["reNtceYn"],  # 재공고 여부
                    # item["rgstTyNm"],  # 등록유형
                    # item["ntceKindNm"],  # 공고종류
                    # item["intrbidYn"],  # 국제입찰
                    item["bidNtceDt"],  # 공고 날짜
                    item["refNo"],  # 참조
                    item["bidNtceNm"],  # 입찰공고명
                    item["asignBdgtAmt"],  # 총예가
                    item["presmptPrce"],  # 추정 가격
                    item["ntceInsttNm"],  # 공고기관
                    item["dminsttNm"],  # 수요기관
                    item["cntrctCnclsMthdNm"],  # 계약방법
                    item["bidBeginDt"],  # 입찰개시일시
                    item["bidClseDt"],  # 입찰마감일시
                    item["prearngPrceDcsnMthdNm"],  # 예가 방법 이름
                    # item["bidNtceDtlUrl"],  # 입찰 공고 상세 링크
                    item["srvceDivNm"],  # 용역 구분 관련..
                    item["cmmnSpldmdMethdNm"],  # 공동 수급
                    item["sucsfbidMthdNm"],  # 낙찰 방식
                    item["ntceInsttOfclNm"],  # 공고 담당자 이름
                    item["ntceInsttOfclTelNo"],  # 공고 담당자 전화번호
                    item["ntceInsttOfclEmailAdrs"],  # 공고 담당자 이메일 주소
                    # item["rgstDt"],  # 등록 일시
                    # item["ntceInsttCd"],  # 공고기관코드
                    # item["dminsttCd"],  # 수요기관코드
                    # item["bidMethdNm"],  # 입찰방식
                    # item["opengDt"],  # 개찰일시
                    # item["rbidPermsnYn"],  # 재입찰허용
                    # item["bidPrtcptLmtYn"],  # 입찰 참가 제한 여부
                    # item["opengPlce"],  # 개찰 장소
                    # item["bidNtceUrl"],
                    # item["crdtrNm"],  # 신용?
                    # item["ppswGnrlSrvceYn"],
                    # item["untyNtceNo"],
                    # item["dsgntCmptYn"],  # 설계 경쟁 여부
                    # item["arsltCmptYn"],  # 결과 경쟁 여부
                    # item["pqEvalYn"],  # PQ 심사 여부
                    # item["tpEvalYn"],
                    # item["ntceDscrptYn"],  # 공고 내용 여부
                    # item["orderPlanUntyNo"],  # 발주 계획 단위 번호
                    # item["bfSpecRgstNo"],  # 사전규격등록번호
                    # item["sucsfbidMthdCd"],  # 낙찰 방식 코드
                    # item["chgDt"],
                    # item["linkInsttNm"],
                    # item["indstrytyLmtYn"],  # 업종제한
                    # item["chgNtceRsn"],  # 변경공고 사요
                    # item["rbidOpengDt"],
                    # item["VAT"],  # 부가세
                ]
            )

            time.sleep(1)  # 1초 대기
        # print(items)

    elif i == 8:  # 낙찰 수자원공사
        print("낙찰 수자원공사 스프레드 시트!")
        # print(items)
        for item in items:
            # print(item)
            worksheet.append_row(
                [
                    item.get("cntrctDe", ""),  #
                    item.get("cntrctDeptNm", ""),  #
                    item.get("cntrctDivNm", ""),  #
                    item.get("cntrctEntrpsNm", ""),  #
                    item.get("ctrmthdNm", ""),  #
                    item.get("lastCtramt", ""),  #
                    item.get("lmttMthNm", ""),  #
                    item.get("ordgNo", ""),  #
                    item.get("ordgTit", ""),  #
                    item.get("strwrkDe", ""),  #
                ]
            )
            time.sleep(1)  # 1초 대기

    elif i == 9:  # 낙찰 LH
        print("낙찰 LH 스프레드 시트!")
        # print(items)
        for item in items:
            # print(item)
            worksheet.append_row(
                [
                    item.get("bid_num", ""),  # 공고번호
                    item.get("cstrtn_job_gb_nm", ""),  # 업무구분
                    item.get("ctrct_cntrctg_dt", ""),  # 계약체결일
                    item.get("ctrct_nm", ""),  # 공고명
                    item.get("ctrct_amt", ""),  # 계약금액
                    item.get("ctrct_vndr_nm", ""),  #
                    item.get("ctrct_vndr_type_nm", ""),  #
                    # item.get("ctrct_vndr_ceo_nm", ""),  #
                    # item.get("ctrct_vndr_addr", ""),  #
                    # item.get("ctrct_taxregno", ""),  #
                    item.get("revert_dept_nm", ""),  #
                    item.get("init_bgnwrk_dt", ""),  #
                    item.get("finl_compwrk_dt", ""),  #
                    item.get("tndr_ctrct_med_nm", ""),  # 계약방법
                ]
            )
            time.sleep(1)  # 1초 대기

    elif i == 6:  # 발주예정 용역
        print("공고 용역 스프레드 시트!")
        for item in items:
            # print(item)
            worksheet.append_row(
                [
                    item["bsnsTyNm"],  # [업무유형명]
                    item["bsnsDivNm"],  # [업무구분명] 물품, 외자, 공사, 용역
                    item["nticeDt"],  # 게시일시
                    item["bizNm"],  # 발주계획의 사업명
                    item["sumOrderAmt"],  # 합계발주금액
                    item["orderYear"],  # 발주년도
                    item["orderMnth"],  # 발주월
                    item["totlmngInsttNm"],  # 총괄기관명
                    item["orderInsttNm"],  # 발주기관명
                    item["jrsdctnDivNm"],  # [소관구분명]
                    item["deptNm"],  # 담당부서명
                    item["ofclNm"],  # 담당자명
                    item["telNo"],  # 담당자 전화번호
                    item["orderPlanSno"],  # 발주계획순번
                    item["prcrmntMethd"],  # [조달방식] 자체조달 or 중앙조달
                    item["cnsttyDivNm"],  # 공종구분명 (일반용역)
                    item["cntrctMthdNm"],  # 계약방법명
                    item["orderPlanUntyNo"],  # 발주계획통합번호
                    item["bidNtceNoList"],  # 입찰공고번호목록
                    # item["bsnsDivCd"],  # [업무구분] 1물품, 2외자, 3공사, 5용역
                    # item["bsnsTyCd"],  # [업무유형] 1신규, 2장기, 나머지=해당없음
                    # item["orderInsttCd"],  # 발주기관코드
                    # item["jrsdctnDivCd"],  # [소관구분코드] 01국가, 02지자체, 51공기업 등
                    # item["cnstwkRgnNm"],  # 공사지역명
                    # item["orderContrctAmt"],  # 발주도급금액
                    # item["orderGovsplyMtrcst"],  # 발주관급자재비
                    # item["orderEtcAmt"],  # 발주기타금액
                    # item["agrmntYn"],  # 협정여부
                    # item["usgCntnts"],  # 용도
                    # item["qtyCntnts"],  # 수량
                    # item["unit"],  # 단위
                    # item["prdctClsfcNo"],  # 물품분류번호
                    # item["dtilPrdctClsfcNo"],  # 세부품명번호
                    # item["prdctClsfcNoNm"],  # 품명
                    # item["ntceNticeYn"],  # 공고게시여부
                    # item["cnstwkMngNo"],  # 공사관리번호
                    # item["orderOrd"],  # 차수
                    # item["sumOrderDolAmt"],  # 달러금액
                    # item["rcritRgstNo"],  # 모집등록번호
                    # item["specItemNm1"],  # 규격항목명1
                    # # item["specItemNm2"],
                    # # item["specItemNm3"],
                    # # item["specItemNm4"],
                    # # item["specItemNm5"],
                    # item["specItemCntnts1"],  # 규격항목내용1
                    # # item["specItemCntnts2"],
                    # # item["specItemCntnts3"],
                    # # item["specItemCntnts4"],
                    # # item["specItemCntnts5"],
                    # item["bdgtDivCd"],  # 예산구분코드
                    # item["cnstwkPrdCntnts"],  # 공사기간내용
                    # item["orderThtmContrctAmt"],  # 차도급금액
                    # item["orderNtntrsAuxAmt"],  # 국고보조금금액
                    # item["dtilPrdctClsfcNoNm"],  # 세부품명
                    # item["specCntnts"],  # 규격내용
                    # item["dsgnDocRdngPlceNm"],  # 설계서 열람장소
                    # item["dsgnDocRdngPrdCntnts"],  # 설계서 열람기간
                    # item["rmrkCntnts"],  # 비고내용
                    # item["chgDt"],  # 변경일시
                ]
            )
            time.sleep(1)  # 1초 대기

    print("데이터가 스프레드시트에 저장되었습니다.")


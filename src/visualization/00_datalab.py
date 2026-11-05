import requests
import pandas as pd

url = "https://datalab.visitkorea.or.kr/visualize/getTempleteData.do"

form_data = {
    "SGG_CD": "26",
    "BASE_YM1": "202607",
    "BASE_YM2": "202608",
    "srchAreaDate": "1",
    "tabDIV": "1",
    "sggIntgYnFlag": "N",
    "qid": "LN_10_01_002",
    "dnname": "국가별 외국인 방문 현황",
}

response = requests.post(
    url,
    data=form_data
)

data = response.json()

df = pd.DataFrame(data["list"])
df
# DPTR_REGN_NM: 출발지역명
# DPTR_REGN_DTL_NM: 출발지역 상세명
# DTL_TOU_NUM: 상세 관광객 수
# DTL_TOU_NUM_SQRT: 관광객 수 제곱근
# TOT_DPTR_REGN_NM_RATE: 전체 출발지역 대비 비율


form_data = {
    "SGG_CD": "26",
    "BASE_YM1": "202509",
    "BASE_YM2": "202608",
    "srchAreaDate": "1",
    "tabDiv": "2",
    "sggIntgYnFlag": "N",
    "qid": "LN_10_02_002",
    "dnname": "업종별 관광소비 추이",
}

response = requests.post(
    url,
    data=form_data
)

data = response.json()
df = pd.DataFrame(data["list"])
df

form_data = {
    "SGG_CD": "26",
    "BASE_YM1": "202509",
    "BASE_YM2": "202608",
    "srchAreaDate": "1",
    "tabDiv": "2",
    "sggIntgYnFlag": "N",
    "qid": "LN_10_02_004",
    "dnname": "국가별 관광소비 현황",
}

response = requests.post(
    url,
    data=form_data
)

data = response.json()
df = pd.DataFrame(data["list"])
df


form_data = {
    "SGG_CD": "26",
    "BASE_YM1": "202509",
    "BASE_YM2": "202608",
    "srchAreaDate": "1",
    "tabDiv": "2",
    "sggIntgYnFlag": "N",
    "qid": "LN_11_01_012",
    "dnname": "외국인 간편결제 업종별 관광소비 추이",
}

response = requests.post(
    url,
    data=form_data
)

data = response.json()
df = pd.DataFrame(data["list"])
df


form_data = {
    "SGG_CD": "26",
    "BASE_YM1": "202509",
    "BASE_YM2": "202608",
    "srchAreaDate": "1",
    "tabDiv": "2",
    "sggIntgYnFlag": "N",
    "qid": "LN_11_01_013",
    "dnname": "외국인 간편결제 국적별 관광소비",
}

response = requests.post(
    url,
    data=form_data
)

data = response.json()
df = pd.DataFrame(data["list"])
df


form_data = {
    "SGG_CD": "26",
    "BASE_YM1": "202507",
    "BASE_YM2": "202606",
    "tabDiv": "2",
    "srchAreaDate": "1",
    "dispYn": "Y",
    "touDivCd": "2",
    "srchTypeText": "",
    "sggIntgYnFlag": "N",
    "sggIntgYnFlag2": "N",
    "yearOverGlobal": "N",
    "qid": "LN_04_01_008",
    "dnname": "방문자 거주지 분포",
}


response = requests.post(
    url,
    data=form_data
)

data = response.json()
df = pd.DataFrame(data["list"])
df

form_data = {
    "SGG_CD": "26",
    "BASE_YM1": "202507",
    "BASE_YM2": "202606",
    "tabDiv": "2",
    "srchAreaDate": "1",
    "dispYn": "Y",
    "touDivCd": "2",
    "srchTypeText": "",
    "sggIntgYnFlag": "N",
    "sggIntgYnFlag2": "N",
    "yearOverGlobal": "N",
    "qid": "LN_02_01_004",
    "dnname": "방문자 성연령별 분포",
}
response = requests.post(
    url,
    data=form_data
)

data = response.json()
df = pd.DataFrame(data["list"])
df


form_data = {
    "SGG_CD": "26",
    "BASE_YM1": "202507",
    "BASE_YM2": "202606",
    "tabDiv": "2",
    "srchAreaDate": "1",
    "dispYn": "Y",
    "touDivCd": "2",
    "srchTypeText": "",
    "sggIntgYnFlag": "N",
    "sggIntgYnFlag2": "N",
    "yearOverGlobal": "N",
    "qid": "LN_04_01_009",
    "dnname": "방문자 수(연인원) 추이",
    "P_BASE_YM1": "202407",
    "P_BASE_YM2": "202506",
    "P_GAP": "12",
}


response = requests.post(
    url,
    data=form_data
)

data = response.json()
df = pd.DataFrame(data["list"])
df

form_data = {
    "SGG_CD": "26",
    "SGG_NM": "부산광역시",
    "BASE_YM1": "202507",
    "BASE_YM2": "202606",
    "tabDiv": "6",
    "srchAreaDate": "1",
    "dispYn": "Y",
    "touDivCd": "2",
    "srchTypeText": "",
    "sggIntgYnFlag": "N",
    "sggIntgYnFlag2": "N",
    "yearOverGlobal": "N",
    "qid": "LN_03_01_038",
    "dnname": "인기관광지_전체",
}


response = requests.post(
    url,
    data=form_data
)

data = response.json()
df = pd.DataFrame(data["list"])
df

form_data = {
    "SGG_CD": "26",
    "SGG_NM": "부산광역시",
    "BASE_YM1": "202507",
    "BASE_YM2": "202606",
    "tabDiv": "6",
    "srchAreaDate": "1",
    "dispYn": "Y",
    "touDivCd": "2",
    "srchTypeText": "",
    "sggIntgYnFlag": "N",
    "sggIntgYnFlag2": "N",
    "yearOverGlobal": "N",
    "qid": "LN_03_01_064",
    "dnname": "내국인 관심 관광지",
}

response = requests.post(
    url,
    data=form_data
)

data = response.json()
df = pd.DataFrame(data["list"])
df


form_data = {
    "SGG_CD": "26",
    "SGG_NM": "부산광역시",
    "BASE_YM1": "202507",
    "BASE_YM2": "202606",
    "tabDiv": "6",
    "srchAreaDate": "1",
    "dispYn": "Y",
    "touDivCd": "2",
    "srchTypeText": "",
    "sggIntgYnFlag": "N",
    "sggIntgYnFlag2": "N",
    "yearOverGlobal": "N",
    "qid": "LN_03_01_060",
    "dnname": "(영어권) 외국인 관심 관광지",
}
response = requests.post(
    url,
    data=form_data
)

data = response.json()
df = pd.DataFrame(data["list"])
df

form_data = {
    "SGG_CD": "26",
    "SGG_NM": "부산광역시",
    "BASE_YM1": "202507",
    "BASE_YM2": "202606",
    "tabDiv": "6",
    "srchAreaDate": "1",
    "dispYn": "Y",
    "touDivCd": "2",
    "srchTypeText": "",
    "sggIntgYnFlag": "N",
    "sggIntgYnFlag2": "N",
    "yearOverGlobal": "N",
    "qid": "LN_03_01_061",
    "dnname": "(일본어) 외국인 관심 관광지",
}

response = requests.post(
    url,
    data=form_data
)

data = response.json()
df = pd.DataFrame(data["list"])
df

form_data = {
    "SGG_CD": "26",
    "SGG_NM": "부산광역시",
    "BASE_YM1": "202507",
    "BASE_YM2": "202606",
    "tabDiv": "6",
    "srchAreaDate": "1",
    "dispYn": "Y",
    "touDivCd": "2",
    "srchTypeText": "",
    "sggIntgYnFlag": "N",
    "sggIntgYnFlag2": "N",
    "yearOverGlobal": "N",
    "qid": "LN_03_01_062",
    "dnname": "(중간체) 외국인 관심 관광지",
}

response = requests.post(
    url,
    data=form_data
)

data = response.json()
df = pd.DataFrame(data["list"])
df

form_data = {
    "SGG_CD": "26",
    "SGG_NM": "부산광역시",
    "BASE_YM1": "202507",
    "BASE_YM2": "202606",
    "tabDiv": "6",
    "srchAreaDate": "1",
    "dispYn": "Y",
    "touDivCd": "2",
    "srchTypeText": "",
    "sggIntgYnFlag": "N",
    "sggIntgYnFlag2": "N",
    "yearOverGlobal": "N",
    "qid": "LN_03_01_063",
    "dnname": "(중번체) 외국인 관심 관광지",
}

response = requests.post(
    url,
    data=form_data
)

data = response.json()
df = pd.DataFrame(data["list"])
df

form_data = {
    "POI_ID": "11AD57F6BA1BABAC6B4E63EF7DDE916C",
    "CNTRL_TAR_NM": "",
    "SGG_CD": "26710",
    "CATE_NM_LARGE": "관광지",
    "BASE_YM1": "202507",
    "BASE_YM2": "202606",
    "currentIndex": "1",
    "pageSize": "10",
    "recordCountPerPage": "10",
    "srchAreaDate": "1",
}


response = requests.post(
    url,
    data=form_data
)
response.text
data = response.json()
df = pd.DataFrame(data["list"])
df

form_data = {
    "SGG_CD": "26",
    "SGG_NM": "부산광역시",
    "BASE_YM1": "202507",
    "BASE_YM2": "202606",
    "tabDiv": "6",
    "srchAreaDate": "1",
    "dispYn": "Y",
    "touDivCd": "2",
    "srchTypeText": "",
    "sggIntgYnFlag": "N",
    "sggIntgYnFlag2": "N",
    "yearOverGlobal": "N",
    "qid": "LN_03_012_001_001",
    "dnname": "주요 유료관광지점 입장객 수_전체",
}

response = requests.post(
    url,
    data=form_data
)
response.text
data = response.json()
df = pd.DataFrame(data["list"])
df

form_data = {
    "SGG_CD": "26",
    "SGG_NM": "부산광역시",
    "BASE_YM1": "202507",
    "BASE_YM2": "202606",
    "tabDiv": "6",
    "srchAreaDate": "1",
    "dispYn": "Y",
    "touDivCd": "2",
    "srchTypeText": "",
    "sggIntgYnFlag": "N",
    "sggIntgYnFlag2": "N",
    "yearOverGlobal": "N",
    "qid": "LN_03_012_001_002",
    "dnname": "주요 유료관광지점 입장객 수_내국인",
}

response = requests.post(
    url,
    data=form_data
)
response.text
data = response.json()
df = pd.DataFrame(data["list"])
df

url = "https://datalab.visitkorea.or.kr/visualize/getGridData.do"
form_data = {
    "SGG_CD": "26",
    "SGG_NM": "",
    "BASE_YM1": "202401",
    "BASE_YM2": "202501",
    "TAB_DIV": "7",
    "srchGrdTyp": "MICE_HDMT_REGN_AVG_CNSM_AMT_SUM_1",
    "tabDiv": "7",
    "srchEventDivCd": "20",
    "srchRsdeDivCd": "10002",
    "fileWriteYn": "N",
    "qid": "BY_TH_MICE_004_004",
    "srchAgrtDivCd": "",
}

response = requests.post(url, data=form_data)
data = response.json()
df = pd.DataFrame(data["list"])
df

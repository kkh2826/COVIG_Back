from time import strptime
from warnings import catch_warnings
from rest_framework.views import APIView
from django.http import JsonResponse

from django.conf import settings

import requests
import xmltodict

import datetime as DT
from dateutil.relativedelta import relativedelta as RD

import json

# Create your views here.

def InitResult():
    result = {
        'data': None,
        'success': False,
        'message': ''
    }

    return result

def DecideInvalidTime():
    
    isInvalidTime = False
    now = DT.datetime.now()

    if now.hour < 10:
        isInvalidTime = True
        if now.hour == 9 and now.minute < 31:
            isInvalidTime = isInvalidTime = True
        

class CovidBasicInfo(APIView):
    '''
        Covid-19정보를 가져온다.
    '''

    API_KEY = settings.COVID_DATA_API_KEY

    def get(self, request):

        result = InitResult()

        url = "http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson"

        currentDate = DT.datetime.now().date()

        str_CurrentDate = DT.datetime.strftime(currentDate, '%Y%m%d')
        str_StartDate = DT.datetime.strftime(currentDate - RD(months=1) - RD(days=1), '%Y%m%d')
        str_EndDate = str_CurrentDate

        parameter = {
            'serviceKey': requests.utils.unquote(self.API_KEY),
            'startCreateDt': str_StartDate,
            'endCreateDt': str_EndDate
        }
        
        # 공공 API 가져오기
        try:
            response = requests.get(url, params=parameter, headers={'User-agent': 'Mozilla/5.0'})
            content = response.text
        except requests.exceptions.Timeout as TO:
            result['message'] = "TimeOut Error : " + TO.strerror
        except requests.exceptions.ConnectionError as CE:
            result['message'] = "Connection Error : " + CE.strerror
        else:
            result['success'] = True

        # XML 형태이기 때문에 Parsing 작업
        dict_data = xmltodict.parse(content)
        dict_data = dict_data['response']['body']['items']['item']

        # API 속성은 총 누적에 대한 개념
        # 일일 확진자 수 / 사망자 수 차이를 구해 속성 생성
        for index in range(len(dict_data)):
            if index == len(dict_data) - 1:
                dict_data[index]['DiffDecideCnt'] = 0
                dict_data[index]['DiffDeathCnt'] = 0
            else:
                dict_data[index]['DiffDecideCnt'] = int(dict_data[index]['decideCnt']) - int(dict_data[index + 1]['decideCnt'])
                dict_data[index]['DiffDeathCnt'] = int(dict_data[index]['deathCnt']) - int(dict_data[index + 1]['deathCnt'])

        # 1개월이 최대치이기 때문에 1개월 + 1일에 대한 데이터는 삭제
        dict_data.pop()

        # 요일별 데이터에 대한 Key값을 만들기 위한 단계 (KEY : 해당 날짜)
        for index in range(len(dict_data)):
            covidDateInfo = dict()
            key = dict_data[index]['stateDt']
            covidDateInfo[key] = dict_data[index]
            dict_data[index] = covidDateInfo

        result['data'] = dict_data

        return JsonResponse(result)


class CovidRegionInfo(APIView):
    '''
        지역별 코로나 감염 정보를 가져온다
    '''

    API_KEY = settings.COVID_DATA_API_KEY

    def get(self, request):

        result = InitResult()
        invalidTime = '09:31:00'
        isInvalidTime = False

        url = "http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19SidoInfStateJson"

        now = DT.datetime.now()
        now_time = now.strftime("%H:%M:%S")

        isInvalidTime = True if now_time < invalidTime else False

        currentDate = now.date()
        str_CurrentDate = DT.datetime.strftime(currentDate - RD(days=1), '%Y%m%d') if isInvalidTime == True else DT.datetime.strftime(currentDate, '%Y%m%d')

        prevDate = DT.datetime.strptime(str_CurrentDate, '%Y%m%d') - DT.timedelta(days=1)
        str_PrevCurrentDate = DT.datetime.strftime(prevDate, '%Y%m%d')
        
        
        parameter = {
            'serviceKey': requests.utils.unquote(self.API_KEY),
            'startCreateDt': str_PrevCurrentDate,
            'endCreateDt': str_CurrentDate
        }

        # 공공 API 가져오기
        try:
            response = requests.get(url, params=parameter, headers={'User-agent': 'Mozilla/5.0'})
            content = response.text
        except requests.exceptions.Timeout as TO:
            result['message'] = "TimeOut Error : " + TO.strerror
        except requests.exceptions.ConnectionError as CE:
            result['message'] = "Connection Error : " + CE.strerror
        else:
            result['success'] = True

        # XML 형태이기 때문에 Parsing 작업
        dict_data = xmltodict.parse(content)
        dict_data = dict_data['response']['body']['items']['item']

        seperateIdx = int(len(dict_data)/2)

        # 사망자 수 차이를 구하기 위한 필드 추가 작업
        for idx in range(seperateIdx):
            dict_data[idx]["diffDeathCnt"] = int(dict_data[idx]['deathCnt']) - int(dict_data[idx + seperateIdx]['deathCnt'])

        dict_data = dict_data[:seperateIdx]

        result['data'] = dict_data

        return JsonResponse(result)
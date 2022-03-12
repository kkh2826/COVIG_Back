from rest_framework.views import APIView
from rest_framework.response import Response

from django.conf import settings

import requests
import xmltodict
import json

# Create your views here.

class CovidBasicInfo(APIView):
    '''
        Covid-19정보를 가져온다.
    '''

    API_KEY = settings.COVID_DATA_API_KEY

    def get(self, request):
        url = "http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson"
        parameter = {
            'serviceKey': requests.utils.unquote(self.API_KEY)
        }
        
        response = requests.get(url, params=parameter, headers={'User-agent': 'Mozilla/5.0'})
        content = response.text

        dict_data = xmltodict.parse(content)
        dict_data = dict_data['response']['body']

        jsonString = json.dumps(dict_data, indent=4)

        return Response(json.loads(jsonString))
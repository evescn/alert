from django.shortcuts import render

# rest_ful 接口风格
from rest_framework.views import APIView
from rest_framework.response import Response
import datetime

# Create your views here.
class Alert(APIView):

    def post(self, request):
        print(request.data)
        return Response({'status': '200'})

class Mail(APIView):

    def post(self, request):
        print(request.data)
        return Response({'status': '200'})
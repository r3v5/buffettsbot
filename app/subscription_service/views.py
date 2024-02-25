from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import HttpResponse, HttpRequest
from rest_framework import status
from .serializers import TelegramUserSerializer


class TelegramUserAPIView(APIView):
    permission_classes = [AllowAny]


    def post(self, request: HttpRequest) -> HttpResponse:
        serializer = TelegramUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            res = {
                "status": status.HTTP_201_CREATED,
                "data": serializer.data
            }
            return Response(res, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
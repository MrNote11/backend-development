from config.modules.utils import incoming_request_checks, api_response
from config.modules.exceptions import raise_serializer_error_msg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import (LoginSerializerIn, SignupSerializerIn, RequestOTPSerializerIn, ConfirmOTPSerializerIn, 
                          ChangePasswordSerializerIn, ForgetPasswordSerializerIn, UserSerializerOut, GetSerializer,
                          PostSerializer, UpdateSerializer) 
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse
from drf_yasg import openapi
from .models import TierAmountDb
from django.db import transaction
from rest_framework.exceptions import  NotFound
from asgiref.sync import sync_to_async

def welcome_message(request):
    return HttpResponse("Welcome to the API, Built by Thales")


class LoginAPIView(APIView):
    permission_classes = []

    @swagger_auto_schema(request_body=LoginSerializerIn,responses={200: openapi.Response(description="Login successful")} )
    def post(self, request):
        status_, data = incoming_request_checks(request)
        if not status_:
            return Response(
                api_response(message=data, status=False),
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = LoginSerializerIn(data=data, context={"request": request})
        serializer.is_valid() or raise_serializer_error_msg(errors=serializer.errors)
        user = serializer.save()
        return Response(
            api_response(
                message="Login successful",
                status=True,
                data={
                    "userData": UserSerializerOut(
                        user, context={"request": request}
                    ).data,
                    "accessToken": AccessToken.for_user(user),
                },
            )
        )



class SignupAPIView(APIView):
    permission_classes = []
    
    @swagger_auto_schema(
        request_body=SignupSerializerIn,
        responses={200: openapi.Response(description="Signup successful")},
    )
    def post(self, request):
        status_, data = incoming_request_checks(request)
        if not status_:
            return Response(
                api_response(message=data, status=False),
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = SignupSerializerIn(data=data, context={"request": request})
        serializer.is_valid() or raise_serializer_error_msg(errors=serializer.errors)
        response = serializer.save()
        return Response(api_response(message=response, status=True))



class RequestOTPView(APIView):
    permission_classes = []
    @swagger_auto_schema(
        request_body=RequestOTPSerializerIn,
        responses={200: openapi.Response(description="OTP sent to your phone number")},
    )
    def post(self, request):
        status_, data = incoming_request_checks(request)
        if not status_:
            return Response(
                api_response(message=data, status=False),
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RequestOTPSerializerIn(data=data, context={"request": request})
        serializer.is_valid() or raise_serializer_error_msg(errors=serializer.errors)
        response = serializer.save()
        return Response(
            api_response(
                message="OTP sent to you phone number", data=response, status=True
            )
        )


class ConfirmOTPView(APIView):
    permission_classes = []
    
    @swagger_auto_schema(
        request_body=ConfirmOTPSerializerIn,
        responses={200: openapi.Response(description="OTP verified successfully")},
    )
    def post(self, request):
        status_, data = incoming_request_checks(request)
        if not status_:
            return Response(
                api_response(message=data, status=False),
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ConfirmOTPSerializerIn(data=data, context={"request": request})
        serializer.is_valid() or raise_serializer_error_msg(errors=serializer.errors)
        response = serializer.save()
        return Response(
            api_response(
                message="OTP verified successfully", data=response, status=True
            )
        )


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        request_body=ChangePasswordSerializerIn,
        responses={200: openapi.Response(description="Password changed successfully")},
    )

    def post(self, request):
        status_, data = incoming_request_checks(request)
        if not status_:
            return Response(
                api_response(message=data, status=False),
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ChangePasswordSerializerIn(data=data, context={"request": request})
        serializer.is_valid() or raise_serializer_error_msg(errors=serializer.errors)
        response = serializer.save()
        return Response(api_response(message=response, status=True))



class ResetPasswordAPIView(APIView):
    permission_classes = []

    @swagger_auto_schema(
        request_body=ForgetPasswordSerializerIn,
        responses={200: openapi.Response(description="Password reset successfully")},
    )
    def post(self, request):
        status_, data = incoming_request_checks(request)
        if not status_:
            return Response(
                api_response(message=data, status=False),
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = ForgetPasswordSerializerIn(data=data, context={"request": request})
        serializer.is_valid() or raise_serializer_error_msg(errors=serializer.errors)
        response = serializer.save()
        return Response(api_response(message=response, status=True))


class AccountTierPostViews(APIView):
    permission_classes = [AllowAny]
    
    async def post(self, request):
        form = PostSerializer(data=request.data)
        is_valid = await sync_to_async(form.is_valid)(raise_exception=True)
        if is_valid:
           await sync_to_async(form.save)()
           return Response({
                "message": "successful",
                "data":form.data,
            }, status=201)
        
accountierpost = AccountTierPostViews.as_view()        
        
        
        
class AccountTierGetViews(APIView):
    permission_classes=[AllowAny]
    async def get(self, request):
        data = await sync_to_async(GetSerializer)()
        return Response({
            "data": data.data,
            
        }, status=200)
       
       
accountierget = AccountTierGetViews.as_view()        
       
       
       
        
class AccountTierUpdateView(APIView):
    permission_classes=[AllowAny]
    async def patch(self, request, pk):
        try:
            instance = await sync_to_async(TierAmountDb.objects.get)(pk=pk)
        except TierAmountDb.DoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer =UpdateSerializer(instance, data=request.data, partial=True)
        is_valid = await sync_to_async(serializer.is_valid)(raise_exception=True)
        if is_valid:
           await sync_to_async(serializer.save)()
           return Response({'message': 'Updated successfully', 'data': serializer.data}, status=200)
        return Response(serializer.errors, status=400)

accountierupdate = AccountTierUpdateView.as_view()          
    


class AccountTierDeleteView(APIView):
    permission_classes = [AllowAny]
    async def delete(self, request, pk):
        try:
            check = await sync_to_async(TierAmountDb.objects.get)(pk=pk)
        except TierAmountDb.DoesNotExist:
            return Response({'error': 'Reservation not found-'}, status=status.HTTP_404_NOT_FOUND)

        # user = request.user

        # like = PostLike.objects.filter(post=reservation, user=user).first()
        # if not like:
        #     return Response({'message': 'Reservation not liked yet'}, status=status.HTTP_400_BAD_REQUEST)

        check = await sync_to_async(check.delete)()
        if check:
            return Response({'message': 'deleted'}, status=status.HTTP_200_OK)
    

            
accountierdelete = AccountTierDeleteView.as_view()            
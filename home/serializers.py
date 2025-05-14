from rest_framework import serializers
from .models import UserProfile, User, UserOTP, SiteSetting, TierAmountDb
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from config.modules.utils import incoming_request_checks, api_response,log_request,format_phone_number,get_site_details,encrypt_text,decrypt_text,generate_random_otp,get_next_minute
from config.modules.tmsaas import TMSaaSAPI
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404 
from config.modules.exceptions import InvalidRequestException ,raise_serializer_error_msg
from django.contrib.auth.password_validation import validate_password 



class SiteSettingSerilaizerOut(serializers.ModelSerializer):
    class Meta:    
        model = SiteSetting
        fields = "__all__" 



class UserProfileSerializerOut(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    phone_number = serializers.SerializerMethodField()
    user_account = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    # gender = ChoiceFieldWithLabel(choices=GENDER_TYPE_CHOICES)

    def get_username(self, obj):
        return obj.user.username
       
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    def get_phone_number(self, obj):
        if obj.phoneNumber:
            return obj.phoneNumber[3:]
        return None

    

    def get_email(self, obj):
        return f"{obj.user.email}"
    
    # def get_gender(self, obj):
    #     return obj.gender or None
    def get_gender(self, obj):
        return obj.gender or None
    
    class Meta:
        model = UserProfile
        exclude = ["user", "image"]
        depth = 1



class UserSerializerOut(serializers.ModelSerializer):
    
    profilePicture = serializers.SerializerMethodField()
    profileDetail = UserProfileSerializerOut(source="userprofile")
   
    def get_profilePicture(self, obj):
        image = None
        if obj.userprofile.image:
            request = self.context.get("request")
            image = request.build_absolute_uri(obj.userprofile.image.url)
        return image

    

    class Meta:
        model = User
        exclude = ["is_staff", "is_active", "is_superuser", "password"]


class LoginSerializerIn(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def create(self, validated_data):
        username = validated_data.get("username")
        password = validated_data.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            raise InvalidRequestException(
                api_response(message="Invalid email or password", status=False)
            )

        
        return user

class SignupSerializerIn(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    phoneNo = serializers.CharField(required=False)
    otp = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    other_name = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)

    def create(self, validated_data):
        uname = validated_data.get("username")
        pword = validated_data.get("password")
        phone_no = validated_data.get("phoneNo")
        otp = validated_data.get("otp")
        first_name = validated_data.get("first_name")
        last_name = validated_data.get("last_name")
        email = validated_data.get("email")
        other_name = validated_data.get("other_name")
        address = validated_data.get("address")
        gender = validated_data.get("gender")
        
        
        
        # Check if user with same username already exist
        if User.objects.filter(username__iexact=uname).exists():
            raise InvalidRequestException(
                api_response(message="Username is taken", status=False)
            )

        if UserProfile.objects.filter(email=email).exists():
            raise InvalidRequestException(
                api_response(
                    message="Customer with this email already registered", status=False
                )
            )

        try:
            validate_password(password=pword)
        except Exception as err:
            log_request(f"Password Validation Error:\nError: {err}")
            raise InvalidRequestException(api_response(message=err, status=False))
               

        phone = format_phone_number(phone_no)

        # Compare OTP
        # Decrypt OTP
        if not UserOTP.objects.filter(phoneNumber=phone).exists():
            raise InvalidRequestException(
                api_response(message="Please request new OTP", status=False)
            )

        user_otp = UserOTP.objects.filter(phoneNumber=phone).last()
        new_otp = decrypt_text(user_otp.otp)
        if new_otp != str(otp):
            raise InvalidRequestException(
                api_response(message="You have submitted an invalid OTP", status=False)
            )

        # Create User
        user, _ = User.objects.create_user(username=uname,email=email,first_name=first_name,last_name=last_name)
        user.set_password(raw_password=pword)
        user.save()

        

        UserProfile.objects.create(
            user=user,
            otherName=other_name,
            gender=gender,
            phoneNumber=phone, 
            address=address
        )   
        
        
        return "Onboarding process completed"


def log_sms_response_to_server(response):
    # Log the response details to your server
    log_request(f"TMSaaS SMS response - Status Code: {response.status_code}")
    log_request(f"TMSaaS SMS response - Headers: {response.headers}")
    log_request(f"TMSaaS SMS response - Body: {response.text}")


class RequestOTPSerializerIn(serializers.Serializer):

    def create(self, validated_data):
        
      
        
        phone_no = format_phone_number(phone_number)
        log_request(f"Creating OTP for phone number: {phone_no}")
        expiry = get_next_minute(timezone.now(), 15)
        random_otp = generate_random_otp()
        log_request(random_otp)
        encrypted_otp = encrypt_text(random_otp)

        user_otp, _ = UserOTP.objects.get_or_create(phoneNumber=phone_no)
        log_request(f"OTP creation status: {_}")
        user_otp.otp = encrypted_otp
        user_otp.expiry = expiry
        user_otp.save()

        # Send OTP to user
        # Thread(target=send_token_to_email, args=[user_detail]).start()
        # Send via TMSaaS

        bank = get_site_details()

        new_content = f"Dear {first_name},Your password reset token is {random_otp}. It expires in 10 minutes."
        log_request(new_content)

        TMSaaSAPI.send_tmsaas_sms(bank,new_content,phone_no,log_sms_response_to_server)

        Thread(target=send_tmsaas_sms, args=[bank, new_content, phone_number, log_sms_response_to_server]).start()

        return {
            "otp": random_otp,
            "hint": "data object containing OTP will be removed when sms service start working",
        }


class ConfirmOTPSerializerIn(serializers.Serializer):
    otp = serializers.CharField()
    phoneNumber = serializers.CharField()

    def create(self, validated_data):
        phone_number = validated_data.get("phoneNumber")
        otp = validated_data.get("otp")

        phone = format_phone_number(phone_number)

        try:
            user_otp = UserOTP.objects.get(phoneNumber=phone)
        except UserOTP.DoesNotExist:
            response = api_response(
                message="Request not valid, please request another OTP", status=False
            )
            raise InvalidRequestException(response)

        if otp != decrypt_text(user_otp.otp):
            response = api_response(message="Invalid OTP", status=False)
            raise InvalidRequestException(response)

        # If OTP has expired
        if timezone.now() > user_otp.expiry:
            response = api_response(
                message="OTP has expired, kindly request for another one", status=False
            )
            raise InvalidRequestException(response)

        return {}

class ChangePasswordSerializerIn(serializers.Serializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    currentPassword = serializers.CharField()
    newPassword = serializers.CharField()

    def create(self, validated_data):
        user = validated_data.get("user")
        old_password = validated_data.get("currentPassword")
        new_password = validated_data.get("newPassword")

        if not check_password(password=old_password, encoded=user.password):
            raise InvalidRequestException(
                api_response(message="Incorrect old password", status=False)
            )

        try:
            validate_password(password=new_password)
        except Exception as err:
            log_request(f"Password Validation Error:\nError: {err}")
            raise InvalidRequestException(api_response(message=err, status=False))

        if old_password == new_password:
            raise InvalidRequestException(
                api_response(message="Passwords cannot be same", status=False)
            )

        user.password = make_password(password=new_password)
        user.save()

        return "Password Change Successful"


class ForgetPasswordSerializerIn(serializers.Serializer):
    username = serializers.CharField()
    otp = serializers.CharField()
    password = serializers.CharField()

    def create(self, validated_data):
        username = validated_data.get("username")
        otp = validated_data.get("otp")
        new_password = validated_data.get("password")

        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            raise InvalidRequestException(
                api_response(message="User not found", status=False)
            )

        try:
            validate_password(password=new_password)
        except Exception as err:
            log_request(f"Password Validation Error:\nError: {err}")
            raise InvalidRequestException(api_response(message=err, status=False))

        try:
            user_otp = UserOTP.objects.get(phoneNumber=user.userprofile.phoneNumber)
        except UserOTP.DoesNotExist:
            raise InvalidRequestException(
                api_response(message="OTP request is required", status=False)
            )

        if timezone.now() > user_otp.expiry:
            raise InvalidRequestException(
                api_response(message="OTP is expired", status=False)
            )

        decrypted_otp = decrypt_text(user_otp.otp)
        if str(decrypted_otp) != str(otp):
            raise InvalidRequestException(
                api_response(message="You have submitted an invalid OTP", status=False)
            )

        user.password = make_password(password=new_password)
        user.save()
        
        return "Password Reset Successful"

class NewUserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = UserProfile
        fields = ["otherName", "gender", "dob", "phoneNumber","nin", "address","first_name", "last_name","full_name"]

    def get_first_name(self,obj):
        return obj.user.first_name
    
    def get_last_name(self,obj):
        return obj.user.last_name
    
    def get_full_name(self,obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    
    
    
class DashBoardWithDrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = TierAmountDb
        fields = ['withdrawl']
        
        def validate_withdrawl(self, validated_data):
            request = self.context.get("request")
            user = request.user
            
            withdrawl=validated_data['withdrawl']
            check = TierAmountDb.objects.get(user)
            if withdrawl > check.balance:
                raise serializers.ValidationError("you cant withdrawl that large ammount")
            return user
            
            
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = TierAmountDb
        fields = "__all__"
        

class GetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TierAmountDb
        fields = "__all__"   
        
        
class UpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TierAmountDb
        fields = ["tier_choice", "minimum_balance", "maximum_balance"]
        
    def update(self, instance, validated_data):
        # user_data = validated_data.get('user')
        if validated_data:
            instance.tier_choice = validated_data.get('tier_choice', instance.tier_choice)
            instance.minimum_balance = validated_data.get('minimum_balance', instance.minimum_balance)
            instance.maximum_balance = validated_data.get('maximum_balance', instance.maximum_balance)
            instance.save()
            return instance


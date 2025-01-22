from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from rest_framework.decorators import permission_classes , api_view
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from datetime import timedelta , datetime
import hashlib
import time
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import CustomUser
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    ChangePasswordSerializer,
)

class UserAccountView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, action=None, uidb64=None, token=None):
        """
        Handles user account-related actions such as registration, login, 
        password reset requests, password resets, and logout.

        Available actions:
        - 'register': Register a new user.
        - 'login': Login an existing user and provide JWT tokens.
        - 'password_reset_request': Send a password reset email to the user.
        - 'password_reset_confirm': Confirm password reset and save the new password.
        - 'logout': Log out the user and clear session tokens.

        Args:
            request: The HTTP request object.
            action: The action to be performed (register, login, etc.).
            uidb64: The user ID encoded in base64 (used in password reset).
            token: The token used for confirming password reset.

        Returns:
            Response: The API response, with success or error messages.
        """
        if action == "register":
            return self.register(request)
        elif action == "login":
            return self.login(request)
        elif action == "reset-password":
            return self.password_reset_request(request)
        elif action == "change-password":
            self.permission_classes = [IsAuthenticated]
            return self.change_password(request)
        else:
            return Response({"error": "Invalid action"}, status=400)
        
    def get(self, request, action=None, uidb64=None, token=None):
        """
            Handles the GET request for user account-related actions.
        """
        if action == "verify-email":
            return self.verify_email(request, token)
        else:
            return Response({"error": "Invalid action"}, status=400)
        
    @extend_schema(summary="User Registration", description="Register a new user by providing email, username, and password.")
    def register(self, request):
        """
        Registers a new user and sends a verification email.

        Args:
            request: The HTTP request object containing user data (email, password, etc.).

        Returns:
            Response: The API response with a success or error message.
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            # Registration logic
            email = serializer.validated_data['email']
            token = hashlib.sha256(f"{email}{time.time()}".encode('utf-8')).hexdigest()

            # Create the user
            user = CustomUser.objects.create_user(
                email=email,
                username=serializer.validated_data['username'],
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                password=serializer.validated_data['password'],
                is_email_verified = False,
                email_verification_token = token 
            )
            user.is_active = True
            user.save()
    

            current_site = get_current_site(request)
            link = f'http://{current_site}/accounts/verify-email/{token}'
            subject = "Verify your Email"
            message = f"Click the link below to verify your account:\n{link}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({
                'message': 'User registered successfully. Check your email for verification.',
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)}
                , status=200)
                
        return Response(serializer.errors, status=400)
    
    def verify_email(self, request, token):
        try:
            user = CustomUser.objects.get(email_verification_token = token)
            if user:
                user.is_email_verified = True
                user.email_verification_token = None
                user.save()
    
            return Response({
               'message':'Email successfully verified. You can now log in.',
               }, 
                status=200)
        except DjangoUnicodeDecodeError:
            return Response({'message':'Invalid token'}, status=400)
    
    def login(self, request):
        """
        Logs in an existing user and provides JWT access and refresh tokens.

        Args:
            request: The HTTP request object containing email and password.

        Returns:
            Response: The API response with access and refresh tokens or errors.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data

            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            return Response({
                'message': 'Login successful.',
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh)
            }, status=200)
        return Response(serializer.errors, status=400)
    
    def password_reset_request(self, request):
        """
        Sends a password reset link to the user's email.

        Args:
            request: The HTTP request object containing the user's email.

        Returns: 
            Response: The API response with a success message or errors.
        """
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.user
            token = PasswordResetTokenGenerator().make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            current_site = get_current_site(request)
            link = f'http://{current_site}/accounts/reset-password-confirm/{uid}/{token}/'
            send_mail("Reset Password", f"Click the link to reset your password: {link}", settings.DEFAULT_FROM_EMAIL, [user.email])
            return Response({"message": "Password reset link sent to your email."}, status=200)
        return Response(serializer.errors, status=400)

    
    def change_password(self, request):
      """Change User Password with Old passwor"""
      serializer = ChangePasswordSerializer(data=request.data , context={"user":request.user})
      if serializer.is_valid():
         return Response({'msg':"password Change Successfully"} , status=200)
      
      return Response(serializer.errors , status = 200)



class ResetAccountView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, action=None, uidb64=None, token=None):
        """
        Handles user account-related actions such as registration, login, 
        password reset requests, password resets, and logout.

        Available actions:
    
        - 'password_reset_request': Send a password reset email to the user.
        - 'password_reset_confirm': Confirm password reset and save the new password.

        Args:
            request: The HTTP request object.
            action: The action to be performed (register, login, etc.).
            uidb64: The user ID encoded in base64 (used in password reset).
            token: The token used for confirming password reset.

        Returns:
            Response: The API response, with success or error messages.
        """
    
        if action == "reset-password-confirm":
            return self.password_reset_confirm(request, uidb64, token)
        else:
            return Response({"error": "Invalid action"}, status=400)

    def password_reset_confirm(self, request, uidb64, token):
        """
        Confirms the password reset process by setting the new password.

        Args:
            request: The HTTP request object containing the new password.
            uidb64: The user ID encoded in base64 (from the password reset link).
            token: The token used for confirming password reset.

        Returns:
            Response: The API response with a success message or errors.
        """
        serializer = PasswordResetSerializer(data=request.data, context={'uid': uidb64, 'token': token})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password reset successful."}, status=200)
        return Response(serializer.errors, status=400)
    
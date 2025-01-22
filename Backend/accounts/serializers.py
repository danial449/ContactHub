from rest_framework import serializers
from .models import CustomUser
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import smart_str
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import random
import re


class LoginSerializer(serializers.Serializer):
    
    """
    Serializer for user login. Validates the email and password and authenticates the user.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email').lower()
        password = attrs.get('password')

        # Authenticate the user
        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError('Invalid email or password.')

        return user

class RegisterSerializer(serializers.ModelSerializer):

  """
    Serializer for user registration. Validates user input, including username, email, and password.
    Provides custom validation and username suggestions.
    """
  
  password2 = serializers.CharField(write_only=True)
  username = serializers.CharField(validators=[RegexValidator(regex='^(?=.*[a-zA-Z])[a-zA-Z0-9_]*$', message="Username must only contain letters, aphanumeric and underscores.")])

  class Meta:
    model = CustomUser
    fields = ['email' , 'username' , 'first_name' , 'last_name', 'password', 'password2']
  
  def validate(self, attrs):

    """
      Validates the provided password and confirms if the passwords match.
    """

    if attrs['password'] != attrs['password2']:
      raise serializers.ValidationError({"password" : "Password do not match"})
    
    if not re.match(r'^(?=.*[a-zA-Z])(?=.*[0-9])(?=.*[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]).{8,}$', attrs['password'] or len(attrs['password']) < 8):
      raise serializers.ValidationError(
        "Password must be at least 8 characters long, contain at least one letter, one number, and one special character.")
    
    return attrs

  
  def get_suggested_usernames(self , username):

    """
      Generates a list of suggested usernames if the provided username is already taken.
    """

    suggested_username = []
    base_username = username

    for _ in range(5):
      random_numbers = random.randint(1000 , 9999)
      new_username = f"{base_username}{random_numbers}"

      if not CustomUser.objects.filter(username=new_username).exists():
        suggested_username.append(new_username)
    
    return suggested_username

  def validate_username(self , username):

    """
      Checks if the username is already taken and provides suggestions if so.
    """
    
    if CustomUser.objects.filter(username=username).exists():
      suggested_username = self.get_suggested_usernames(username)
      raise serializers.ValidationError(f"This username is already taken. Suggested usernames: {', '.join  (suggested_username)}")
    
    return username
  
  def validate_email(self, value):
        
        """
        Ensures the email domain is valid and belongs to allowed domains.
        """

        allowed_domains = ['gmail.com', 'yahoo.com']
        domain = value.split('@')[-1].lower()
        if domain not in allowed_domains:
            raise serializers.ValidationError(f"Enter a valid email address.")
        return value
  

  
  # def create(self, validated_data):
  #   validated_data.pop('password2', None)
  #   request = self.context.get('request')  # Pass request for AllAuth compatibility

  #   user = CustomUser.objects.create(
  #     email = validated_data['email'],
  #     username = validated_data['username'],
  #     first_name = validated_data['first_name'],
  #     last_name = validated_data['last_name'],
  #     password = validated_data['password']
  #   )
  #   return user



class PasswordResetRequestSerializer(serializers.Serializer):
    
    """
    Serializer to handle password reset requests. Validates if the email exists in the system.
    """

    email = serializers.EmailField()

    def validate_email(self, email):
        try:
            # Check if email is associated with a user
            self.user = CustomUser.objects.get(email=email)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Account not found.")
        return email
    
class PasswordResetSerializer(serializers.Serializer):
    
    """
    Serializer to handle password reset. Validates the reset token and new password.
    """

    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        uid = self.context.get('uid')
        token = self.context.get('token')
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        try:
            user_id = smart_str(urlsafe_base64_decode(uid))
            self.user = CustomUser.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            raise serializers.ValidationError("Invalid user.")

        if not PasswordResetTokenGenerator().check_token(self.user, token):
            raise serializers.ValidationError("Invalid or expired token.")
            
        # Check if the new password matches the old password
        if self.user.check_password(new_password):
            raise serializers.ValidationError("New password cannot be the same as the old password.")

        # Additional password validation (if needed)
        if new_password != confirm_password:
           raise serializers.ValidationError({"password" : "Password do not match"})
    
        if not re.match(r'^(?=.*[a-zA-Z])(?=.*[0-9])(?=.*[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]).{8,}$', new_password):
           raise serializers.ValidationError("Password must be at least 8 characters long, contain at least one letter, one number, and one special character.")
           
        
        return attrs

    def save(self):
        
        """
        Resets the user's password with the validated new password.
        """

        self.user.set_password(self.validated_data['new_password'])
        self.user.save()

class ChangePasswordSerializer(serializers.Serializer):

  """
    Serializer to handle password changes for authenticated users.
  """
  
  old_password = serializers.CharField(max_length=200 , write_only=True)
  new_password = serializers.CharField(max_length=200 , write_only=True)
  confirm_password = serializers.CharField(max_length=200 , write_only=True)
  
  def validate(self, data):
     """
        Validates the old password, ensures the new password matches the confirmation,
        and checks if the new password meets security requirements.
      """
     
     old_password = data.get('old_password')
     new_password = data.get('new_password')
     confirm_password = data.get('confirm_password')
     user = self.context.get('user')

     if not check_password(old_password, user.password):
        raise serializers.ValidationError("Old password is not correct.")
     if new_password != confirm_password:
        raise serializers.ValidationError("Password and Confirm password not match.")
     if new_password == old_password:
        raise serializers.ValidationError("New password must be differnet from old ones.")
     if not re.match(r'^(?=.*[a-zA-Z])(?=.*[0-9])(?=.*[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]).{8,}$', new_password):
           raise serializers.ValidationError("Password must be at least 8 characters long, contain at least one letter, one number, and one special character.")
     user.set_password(new_password)
     user.save()
      
     return data
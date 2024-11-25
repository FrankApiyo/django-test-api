from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group, User
from django.conf import settings
from rest_framework import permissions, viewsets

import boto3
import uuid
import os
from botocore.client import Config

from users.quickstart.serializers import (
    GroupSerializer,
    UserSerializer,
    UserProfileSerializer,
)
from users.quickstart.models import UserProfile


def get_s3_client():
    aws_endpoint_url = getattr(settings, "AWS_S3_ENDPOINT_URL", None)
    signature_version = getattr(settings, "AWS_S3_SIGNATURE_VERSION", "s3v4")
    s3_config = Config(
        signature_version=signature_version,
        region_name=getattr(settings, "AWS_S3_REGION_NAME", None),
    )
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    return boto3.client(
        "s3",
        config=s3_config,
        endpoint_url=aws_endpoint_url,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )


def generate_s3_key():
    return str(uuid.uuid4())


def upload_to_s3(file, bucket_name):
    s3 = get_s3_client()
    key = f"profile_pictures/{generate_s3_key()}"
    s3.upload_fileobj(file, bucket_name, key)
    return key


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        user = request.user  # Get the authenticated user
        user_profile = get_object_or_404(UserProfile, user=user)

        # Generate a pre-signed S3 URL for the profile picture
        if not user_profile.profile_picture:
            return Response({"error": "No profile picture found"}, status=404)

        s3_client = get_s3_client()

        bucket_name = settings.BUCKET_NAME
        key = user_profile.profile_picture

        try:
            presigned_url = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": key},
                ExpiresIn=3600,  # URL expires in 1 hour
            )
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        # Return the pre-signed URL in the response
        return Response({"profile_picture_url": presigned_url})

    def create(self, request, *args, **kwargs):
        user = request.user

        # Check if the user already has a profile
        user_profile, created = UserProfile.objects.get_or_create(user=user)

        # Handle file upload
        file = request.FILES.get("profile_picture")
        if not file:
            no_file = {"error": "No file provided"}
            return Response(no_file, status=status.HTTP_400_BAD_REQUEST)

        bucket_name = settings.BUCKET_NAME

        # Upload the file to S3
        file_key = upload_to_s3(file, bucket_name)

        # Save the file key to the profile
        user_profile.profile_picture = file_key
        user_profile.save()

        data = self.serializer_class(user_profile).data
        return Response(data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited
    """

    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

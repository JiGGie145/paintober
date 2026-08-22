from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OrganizerProfile
from .serializers import LoginSerializer, LogoutSerializer, OrganizerSerializer, RegisterSerializer

User = get_user_model()


def organizer_for_user(user):
    profile, _ = OrganizerProfile.objects.get_or_create(user=user)
    return profile


def token_response(user):
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "organizer": OrganizerSerializer(organizer_for_user(user)).data,
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User(
            username=serializer.validated_data["email"],
            email=serializer.validated_data["email"],
            first_name=serializer.validated_data.get("first_name", ""),
        )
        user.set_password(serializer.validated_data["password"])
        user.save()
        organizer_for_user(user)
        return Response(token_response(user), status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower().strip()
        user = authenticate(request, username=email, password=serializer.validated_data["password"])
        if user is None or not user.is_active:
            return Response({"detail": "Invalid email or password."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(token_response(user))


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = serializer.validated_data.get("refresh")
        if refresh:
            try:
                RefreshToken(refresh).blacklist()
            except TokenError:
                pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(OrganizerSerializer(organizer_for_user(request.user)).data)

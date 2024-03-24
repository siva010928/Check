from django.contrib.auth import login, get_user_model
from django.shortcuts import redirect
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken

from app.google_login_server_flow.service import (
    GoogleRawLoginFlowService,
)


def get_tokens_for_user(user, google_user_result):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        # **google_user_result
    }


User = get_user_model()


class PublicApi(APIView):
    authentication_classes = ()
    permission_classes = ()


class GoogleLoginRedirectApi(PublicApi):
    def get(self, request, *args, **kwargs):
        google_login_flow = GoogleRawLoginFlowService()

        authorization_url, state = google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"] = state
        request.session.modified = True
        request.session.save()

        return redirect(authorization_url)


class GoogleLoginApi(PublicApi):
    class InputSerializer(serializers.Serializer):
        code = serializers.CharField(required=False)
        error = serializers.CharField(required=False)
        state = serializers.CharField(required=False)

    def get(self, request, *args, **kwargs):
        input_serializer = self.InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get("code")
        error = validated_data.get("error")
        state = validated_data.get("state")

        if error is not None:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)

        if code is None or state is None:
            return Response({"error": "Code and state are required."}, status=status.HTTP_400_BAD_REQUEST)

        # session_state = request.session.get("google_oauth2_state")
        # print("session_state", session_state)
        # print("state", state)
        # if session_state is None:
        #     return Response({"error": "CSRF check failed."}, status=status.HTTP_400_BAD_REQUEST)
        #
        # del request.session["google_oauth2_state"]
        # request.session.modified = True
        #
        # if state != session_state:
        #     return Response({"error": "CSRF check failed."}, status=status.HTTP_400_BAD_REQUEST)

        google_login_flow = GoogleRawLoginFlowService()

        google_tokens = google_login_flow.get_tokens(code=code)

        id_token_decoded = google_tokens.decode_id_token()
        user_info = google_login_flow.get_user_info(google_tokens=google_tokens)

        user_email = id_token_decoded["email"]
        user = User.objects.filter(email=user_email).first()

        if user is None:
            user = User.objects.create(
                name=user_info.get('name'),
                email=user_email
            )

        result = {
            "id_token_decoded": id_token_decoded,
            "user_info": user_info,
        }
        tokens = get_tokens_for_user(user, result)
        return JsonResponse(tokens, status=status.HTTP_200_OK)


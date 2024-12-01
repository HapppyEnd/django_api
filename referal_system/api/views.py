import string
from random import choice, randint

from api.permissions import IsAdminOrIsSelf
from api.serializers import AuthSerializer, ReferralSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User

REFERENCE_CODE = 'reference_code'
ME = 'me'
EMPTY = 'Empty'
NOT_FOUND = 'Not Found'
ALREADY_USED = 'Already Used'
YOURSELF_CODE = 'Can not use your invite code.'
VERIFIED_CODE = 'verified_code'
PHONE_NUMBER = 'phone_number'
REFRESH = 'refresh'
ACCESS = 'access'
INVITE_CODE_LENGHT = 6


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = ReferralSerializer

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=[IsAdminOrIsSelf], url_path=ME)
    def get_profile_or_add_referral(self, request):
        user = User.objects.get(pk=request.user.pk)
        if request.method == 'GET':
            return Response(
                ReferralSerializer(user).data,
                status=status.HTTP_200_OK)
        reference_code = request.data.get(REFERENCE_CODE)
        if not reference_code:
            return Response({REFERENCE_CODE: EMPTY},
                            status=status.HTTP_400_BAD_REQUEST)

        if not User.objects.filter(invite_code=reference_code).exists():
            return Response({REFERENCE_CODE: NOT_FOUND},
                            status=status.HTTP_404_NOT_FOUND)

        if user.reference_code:
            return Response({REFERENCE_CODE: ALREADY_USED},
                            status=status.HTTP_400_BAD_REQUEST)

        if reference_code == user.invite_code:
            return Response(
                {REFERENCE_CODE: YOURSELF_CODE},
                status=status.HTTP_400_BAD_REQUEST)

        user.reference_code = reference_code
        user.save()
        return Response({REFERENCE_CODE: reference_code},
                        status=status.HTTP_200_OK)


class AuthViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]

    @classmethod
    def get_invite_code(cls):
        characters = string.ascii_letters + string.digits
        while True:
            invite_code = ''.join(
                choice(characters) for _ in range(INVITE_CODE_LENGHT))
            if not User.objects.filter(invite_code=invite_code).exists():
                return invite_code

    def create(self, request, *args, **kwargs):
        phone_number = request.data.get(PHONE_NUMBER)
        verified_code = request.data.get(VERIFIED_CODE)
        user, _ = User.objects.get_or_create(phone_number=phone_number)

        if verified_code:
            if user.verified_code == verified_code:
                if not user.invite_code:
                    user.invite_code = self.get_invite_code()
                user.verified_code = None
                user.save()
                refresh = RefreshToken.for_user(user)
                return Response({REFRESH: str(refresh),
                                 ACCESS: str(refresh.access_token)},
                                status=status.HTTP_200_OK)

        verify_code = randint(1000, 9999)
        user.verified_code = verify_code
        user.save()
        serializer = AuthSerializer(user)
        return Response(serializer.data)

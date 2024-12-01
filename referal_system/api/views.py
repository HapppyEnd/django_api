import string
import time
from random import choice, randint

from api.permissions import IsAdminOrIsSelf
from api.serializers import AuthSerializer, ReferralSerializer
from drf_spectacular.utils import OpenApiResponse, extend_schema
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


@extend_schema(tags=['User'])
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = ReferralSerializer

    @extend_schema(
        summary=("Получение профиля пользователя или добавление "
                 "реферального кода"),
        description=(
            "Этот метод позволяет пользователю получить свой профиль или "
            "добавить реферальный код. "
            "При GET-запросе возвращается информация о пользователе."
            "При выполнении PATCH-запроса пользователь может добавить "
            "реферальный код, если он еще не был использован и не совпадает "
            "с его собственным инвайт-кодом. "
            "Если реферальный код не передан или недействителен, возвращаются "
            "соответствующие ошибки."
        ),
        request=ReferralSerializer,
        responses={
            200: OpenApiResponse(
                response=ReferralSerializer,
                description=("Профиль пользователя или реферальный код "
                             "успешно добавлен.")),
            400: OpenApiResponse(
                description="Ошибки валидации: реферальный код не передан, "
                "уже использован или совпадает с собственным инвайт-кодом."),
            404: OpenApiResponse(description="Реферальный код не найден.")
        }
    )
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

    @extend_schema(
        summary="Получение списка всех пользователей",
        description="Возвращает список всех пользователей в системе.",
        responses={
            200: OpenApiResponse(
                response=ReferralSerializer(many=True),
                description="Список пользователей успешно получен."
            )
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Получение пользователя по ID",
        description="Возвращает информацию о пользователе по указанному ID.",
        responses={
            200: OpenApiResponse(
                response=ReferralSerializer,
                description="Пользователь успешно найден."
            ),
            404: OpenApiResponse(
                description="Пользователь с указанным ID не найден."
            )
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


@extend_schema(tags=['Authentication'])
class AuthViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny, ]
    http_method_names = ['post', ]

    @classmethod
    def get_invite_code(cls):
        characters = string.ascii_letters + string.digits
        while True:
            invite_code = ''.join(
                choice(characters) for _ in range(INVITE_CODE_LENGHT))
            if not User.objects.filter(invite_code=invite_code).exists():
                return invite_code

    @extend_schema(
        summary="Регистрация и авторизация пользователя",
        description=(
            "Этот метод позволяет пользователю зарегистрироваться и "
            "авторизоваться по номеру телефона. "
            "При успешной авторизации пользователь получает 4-значный "
            "проверочный код. "
            "Если проверочный код совпадает с сохраненным, пользователь "
            "получает инвайт-код. "
            "Если код не был предоставлен, система генерирует новый код и "
            "отправляет его пользователю."
        ),
        request=AuthSerializer,
        responses={
            200: OpenApiResponse(
                response=AuthSerializer,
                description="Пользователь авторизован и получил инвайт-код."),
            400: OpenApiResponse(
                description=("Ошибки валидации. Возможно, неверный номер "
                             "телефона или проверочный код."))
        }
    )
    def create(self, request):
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
        time.sleep(randint(1, 2))
        user.verified_code = verify_code
        user.save()
        serializer = AuthSerializer(user)
        return Response(serializer.data)

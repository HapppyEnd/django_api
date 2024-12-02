from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from users.models import User


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(region='RU')

    class Meta:
        model = User
        fields = ('phone_number',)


class UserReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone_number',)


class AuthSerializer(serializers.ModelSerializer):
    verified_code = serializers.CharField(max_length=4, required=False)

    class Meta:
        model = User
        fields = ('verified_code',)


class ReferralSerializer(serializers.ModelSerializer):
    referral = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'phone_number', 'invite_code', 'reference_code', 'referral')

    def get_referral(self, obj):
        referrals = User.objects.filter(reference_code=obj.invite_code)
        return UserReferenceSerializer(referrals, many=True).data

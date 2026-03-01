import phonenumbers
from rest_framework import serializers
from .models import Candidate

class CandidateSerializer(serializers.ModelSerializer):

    dob = serializers.DateField(
        input_formats=["%d/%m/%Y", "%Y-%m-%d"],
        format="%d/%m/%Y",
        required=False,
        allow_null=True
    )

    class Meta:
        model = Candidate
        fields = "__all__"
        read_only_fields = ("status", "attempt_count", "picked_at")

    def validate_phone_number(self, value):
        try:
            parsed = phonenumbers.parse(value, None)

            if not phonenumbers.is_valid_number(parsed):
                raise serializers.ValidationError("Invalid phone number")

            # Normalize to international format
            return phonenumbers.format_number(
                parsed,
                phonenumbers.PhoneNumberFormat.E164
            )

        except Exception:
            raise serializers.ValidationError("Invalid phone number format")
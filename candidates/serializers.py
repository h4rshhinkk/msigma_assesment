import phonenumbers
from rest_framework import serializers
from .models import Candidate
from batches.models import CandidateAttempt
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

    def validate_email(self, value):
        return value.lower()

class CandidateSearchSerializer(serializers.ModelSerializer):

    currentStatus = serializers.CharField(source="status")
    attemptCount = serializers.IntegerField(source="attempt_count")
    lastAttemptAt = serializers.SerializerMethodField()

    class Meta:
        model = Candidate
        fields = [
            "id",
            "name",
            "email",
            "currentStatus",
            "attemptCount",
            "lastAttemptAt",
        ]

    def get_lastAttemptAt(self, obj):
        last_attempt = CandidateAttempt.objects.filter(
            candidate=obj
        ).order_by("-created_at").first()

        return last_attempt.created_at if last_attempt else None
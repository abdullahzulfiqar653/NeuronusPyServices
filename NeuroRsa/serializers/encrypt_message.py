import pgpy
from rest_framework import serializers

from NeuroRsa.utils import encrypt_message
from NeuroRsa.models.recipient import Recipient


class EncryptMessageSerializer(serializers.Serializer):
    message = serializers.CharField(allow_blank=True)
    recipient_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Recipient.objects.all(),
        write_only=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if getattr(request, "user", None):
            if getattr(request.user, "recipients", None):
                self.fields["recipient_ids"].queryset = request.user.recipients.all()

    def validate_recipient_ids(self, recipient_ids):
        if not recipient_ids:
            raise serializers.ValidationError("At least one Recipient required.")
        return recipient_ids

    def validate_message(self, message):
        if not message:
            raise serializers.ValidationError("Message content cannot be empty.")
        if len(message) > 446:
            raise serializers.ValidationError(
                "Message content cannot be greater then 446 characters."
            )
        return message

    def create(self, validated_data):
        message = validated_data.get("message")
        recipients = validated_data.get("recipient_ids")
        try:
            print("\n🔐 Encrypting message for recipients...\n")
            print(f"message: {message}")
            public_key, _ = pgpy.PGPKey.from_blob(recipients[0].public_key)
            pgp_message = pgpy.PGPMessage.new(message)
            print(f"pgp_message: {pgp_message}")
            encrypted_message = public_key.encrypt(pgp_message)
            print(f"encrypted_message: {encrypted_message}")
        except Exception as e:  # noqa
            print(e)
            raise serializers.ValidationError(
                {"error": ["public key cannot be used to encrypt the message."]}
            )
        return {"message": encrypted_message}

import pgpy
import secrets

from rest_framework import serializers
from django.contrib.auth.models import User

from main.utils import hash_passphrase
from NeuroRsa.utils import generate_keypair
from NeuroRsa.models.keypair import KeyPair


class KeyPairSerializer(serializers.ModelSerializer):
    passphrase = serializers.CharField(
        write_only=True,
        required=False,
        min_length=8,
        allow_null=True,
        max_length=64,
    )

    class Meta:
        model = KeyPair
        fields = ["id", "name", "email", "passphrase", "private_key", "public_key"]
        read_only_fields = ["private_key", "public_key"]

    def validate_name(self, name):
        user = self.context.get("request").user
        if KeyPair.objects.filter(user_id=user, name=name).exists():
            raise serializers.ValidationError(
                "An keypair with this name already exists."
            )
        return name

    def create(self, validated_data):
        user = self.context["request"].user
        email = validated_data.get("email", "")
        passphrase = validated_data.get("passphrase")
        passphrase_bytes = passphrase.encode("utf-8") if passphrase else None

        name = validated_data.get("name") or f"pair_{secrets.token_hex(3)}"
        # private_key, public_key = generate_keypair(passphrase_bytes)

        # Generate a new PGP key
        key = pgpy.PGPKey.new(pgpy.constants.PubKeyAlgorithm.RSAEncryptOrSign, 4096)

        # Create a user ID
        user_id = pgpy.PGPUID.new(name, email=email)

        # Bind the user ID to the key
        key.add_uid(user_id, usage={pgpy.constants.KeyFlags.Sign, pgpy.constants.KeyFlags.EncryptCommunications},
                    hashes=[pgpy.constants.HashAlgorithm.SHA256],
                    ciphers=[pgpy.constants.SymmetricKeyAlgorithm.AES256],
                    compression=[pgpy.constants.CompressionAlgorithm.ZLIB])

        print("\n🔹 PUBLIC KEY (Upload This to PGP Websites) 🔹\n")
        public_key = str(key.pubkey)
        print("\n🔒 PRIVATE KEY (DO NOT SHARE!) 🔒\n")
        private_key = str(key)
        print("\n✅ PGP keys generated successfully!")

        key_pair = KeyPair.objects.create(
            user=user,
            name=name,
            email=email,
            passphrase=passphrase,
            private_key=private_key,
            public_key=public_key
        )
        return key_pair

    def update(self, instance, validated_data):
        validated_data.pop("passphrase", None)
        return super().update(instance, validated_data)


class MainKeyPairSerializer(serializers.Serializer):
    """
    This Serializer is used to create a main keypair for every user in this
    application or for the users of other applicatiuons as well.
    """

    private_key = serializers.CharField(read_only=True)
    public_key = serializers.CharField(read_only=True)
    pass_phrase = serializers.CharField(write_only=True)

    def validate(self, attrs):
        pass_phrase = attrs.get("pass_phrase")
        if User.objects.filter(username=pass_phrase).exists():
            raise serializers.ValidationError(
                {"msg": "User already have main keypair."}
            )
        return super().validate(attrs)

    def create(self, validated_data):
        pass_phrase = validated_data["pass_phrase"]
        hash = hash_passphrase(pass_phrase)
        user, _ = User.objects.get_or_create(username=pass_phrase)
        user.set_password(hash)
        user.save()

        private_key, public_key = generate_keypair()
        KeyPair.objects.create(
            user=user,
            is_main=True,
            name=f"main_{secrets.token_hex(3)}",
            public_key=public_key.decode("utf-8"),
            private_key=private_key.decode("utf-8"),
        )
        return {
            "public_key": public_key.decode("utf-8"),
            "private_key": private_key.decode("utf-8"),
        }

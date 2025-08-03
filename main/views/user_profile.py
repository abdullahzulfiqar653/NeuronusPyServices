from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import NotFound
from main.models.user_profile import UserProfile
from main.serializers.user_profile import UserProfileSerializer


class UserProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer

    def get_object(self):
        try:
            return self.request.user.profile
        except UserProfile.DoesNotExist:
            raise NotFound("User profile not found.")

    @swagger_auto_schema(
        operation_summary="Retrieve user profile",
        operation_description=(
            "Returns the authenticated user's profile details including:\n\n"
            "- `id`: Unique profile ID\n"
            "- `image`: Profile image URL\n"
            "- `address`: User's address\n"
            "- `features_data`: Additional data stored in profile\n"
            "- `url`: Absolute URL to the profile"
        ),
        responses={
            200: UserProfileSerializer,
            404: "User profile not found.",
        },
    )
    def get(self, request, *args, **kwargs):
        """Handles retrieving the user profile."""
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update user profile",
        operation_description=(
            "Allows users to update their profile.\n\n"
            "**Fields that can be updated:**\n"
            "- `image`: (optional) New profile image. Will be uploaded to S3 and stored via URL."
        ),
        request_body=UserProfileSerializer,
        responses={
            200: "Profile updated successfully.",
            400: "Invalid input data.",
            404: "User profile not found.",
        },
    )
    def put(self, request, *args, **kwargs):
        """Handles updating user profile details."""
        return super().put(request, *args, **kwargs)

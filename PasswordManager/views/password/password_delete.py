from rest_framework import generics, status
from rest_framework.response import Response
from PasswordManager.serializers.password_delete import PasswordDeleteSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class BulkPasswordDeleteView(generics.CreateAPIView):
    serializer_class = PasswordDeleteSerializer

    @swagger_auto_schema(
        operation_summary="Bulk delete password entries",
        operation_description=(
            """
            **Bulk Delete Passwords**

            Allows deletion of multiple saved password entries by sending their IDs.

            **Request Body Example:**
            ```json
            {
              "passwords": [1, 2, 3]
            }
            ```

            - Each ID must belong to a password saved by the currently authenticated user.
            - Unauthorized or invalid IDs will be rejected.
            """
        ),
        request_body=PasswordDeleteSerializer,
        responses={
            200: openapi.Response(
                description="Passwords deleted successfully",
                examples={
                    "application/json": {
                        "message": "Passwords deleted successfully"
                    }
                },
            ),
            400: "Invalid or unauthorized password IDs",
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.delete_passwords()
            return Response(
                {"message": "Passwords deleted successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

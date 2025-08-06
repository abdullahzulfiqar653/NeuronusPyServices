from rest_framework import generics, status
from rest_framework.response import Response
from PasswordManager.serializers.password_delete import PasswordDeleteSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class BulkPasswordDeleteView(generics.CreateAPIView):
    serializer_class = PasswordDeleteSerializer

    @swagger_auto_schema(
        operation_summary="Bulk delete password entries",
        operation_description="""
            This endpoint allows an authenticated user to delete multiple saved passwords at once.

            **Authentication Required**

            ###  Request Body
            Provide a list of `password` IDs that you want to delete. These IDs **must belong to the current user**.

            ```json
            {
              "passwords": [1, 5, 12]
            }
            ```

            ###  Validation Rules
            - Each password ID must belong to the authenticated user.
            - If any password ID is invalid or unauthorized, the entire request will be rejected.

            ###  URL Params
            None — this endpoint expects only a POST request body.

            ###  Response Examples
            - ✅ **Success**: All passwords deleted
            ```json
            {
              "message": "Passwords deleted successfully"
            }
            ```

            - ❌ **Error**: Invalid/unauthorized IDs
            ```json
            {
              "passwords": [
                "Invalid ID or password does not belong to the user."
              ]
            }
            ```
            """,
        request_body=PasswordDeleteSerializer,
        responses={
            200: openapi.Response(
                description="Passwords deleted successfully",
                examples={
                    "application/json": {"message": "Passwords deleted successfully"}
                },
            ),
            400: openapi.Response(
                description="Invalid or unauthorized password IDs",
                examples={
                    "application/json": {
                        "passwords": ["This field is required."],
                    }
                },
            ),
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

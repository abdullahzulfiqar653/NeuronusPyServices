from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView
from main.serializers.file_url import FileUrlSerializer
from rest_framework.parsers import MultiPartParser, FormParser


class FileUrlCreateAPIView(CreateAPIView):
    """
    **Request:**
    - Accepts the following **form-data parameters**:

      | Parameter | Required | Description |
      |-----------|----------|-------------|
      | file      | ✅ Yes   | The file that will be uploaded. |
      | public    | ❌ No    | If true, the file will be publicly accessible. Default is true. |

    **Headers:**
    - Authorization: Token your_auth_token *(Required)*

    **Response:**
    - Returns a **pre-signed URL** that the client can use to upload the file directly to S3.
    """

    permission_classes = []
    serializer_class = FileUrlSerializer
    parser_classes = [MultiPartParser, FormParser]  # 👈 necessary for file uploads

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="file",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,  # 👈 tells swagger to show file picker
                required=True,
                description="The file to upload",
            ),
            openapi.Parameter(
                name="public",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_BOOLEAN,
                required=False,
                description="Whether the file is public (default: true)",
            ),
        ],
        responses={200: FileUrlSerializer},
        consumes=["multipart/form-data"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

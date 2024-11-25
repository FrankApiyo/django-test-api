from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.contrib.auth.models import User


class UserProfileTestCase(TestCase):
    def setUp(self):
        # create a user for authentication
        self.user_credentials = {"username": "bob", "password": "password123"}

        self.user = User.objects.create(**self.user_credentials)
        self.user.set_password(self.user_credentials["password"])
        self.user.save()
        login_successful = self.user.check_password(self.user_credentials["password"])
        self.client.login(**self.user_credentials)
        assert login_successful, "Login failed during setup."

        self.url = reverse("user_profile")

    def test_upload_profile_picture(self):
        file_path = "./profile.jpeg"
        with open(file_path, "rb") as f:
            uploaded_file = SimpleUploadedFile(
                f.name, f.read(), content_type="image/jpeg"
            )

        response = self.client.post(
            self.url,
            {
                "profile_picture": uploaded_file,
            },
            format="mulitpart",
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn("profile_picture", response.data)
        self.assertTrue(
            response.data["profile_picture"].startswith("profile_pictures/")
        )

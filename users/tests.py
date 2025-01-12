from datetime import date
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from users.models import Profile
from users.forms import UserUpdateForm, ProfileUpdateForm


USER_NAME = 'testuser'
USER_NAME_NEW = 'newusername'
EMAIL = 'newemail@example.com'
USER_PASSWORD = 'testpass'
PHONE_NUMBER = '1234567890'
PHONE_NUMBER_NEW = '0987654321'


@pytest.fixture
def user1():
    user = get_user_model().objects.create(username=USER_NAME, password=USER_PASSWORD)
    return user


@pytest.fixture
def profile_user1(user1):
    profile_user = Profile.objects.create(user=user1, date_of_birth=date.today(), phone_number=PHONE_NUMBER)
    profile_user.save()
    return profile_user


@pytest.mark.django_db()
class TestProfileModel:
    def test_profile_creation(self, profile_user1):
        new_profile = Profile.objects.get(user=profile_user1.user)
        assert new_profile.phone_number == PHONE_NUMBER

    def test_profile_image(self, profile_user1):
        new_profile = Profile.objects.get(user=profile_user1.user)
        assert str(new_profile.image) == 'default.jpg'

    def test_profile_string_representation(self, profile_user1):
        new_profile = Profile.objects.get(user=profile_user1.user)
        assert str(new_profile) == USER_NAME

    def test_update_profile(self, profile_user1):
        assert profile_user1.phone_number == PHONE_NUMBER
        profile_user1.phone_number = PHONE_NUMBER_NEW
        profile_user1.save()
        updated_profile = Profile.objects.get(user=profile_user1.user)
        assert updated_profile.phone_number == PHONE_NUMBER_NEW

    def test_delete_profile(self, profile_user1):
        profile_user1.delete()
        assert profile_user1 not in Profile.objects.all()

    def test_delete_user_deletes_profile(self, profile_user1):
        profile_user1.user.delete()
        assert profile_user1 not in Profile.objects.all()

    def test_static_profile(self):
        password = 'dannyPassword'
        user = get_user_model().objects.filter(username='Danny').first()
        profile = Profile.objects.filter(user=user).first()
        assert profile.user == user
        assert profile.user.check_password(password)


@pytest.mark.django_db
class TestProfileUpdate:
    def test_profile_update_view(self, client, user1, profile_user1):
        # Login the user
        client.force_login(user1)

        url = reverse('profile')
        response = client.get(url)
        assert response.status_code == 200
        assert isinstance(response.context['u_form'], UserUpdateForm)
        assert isinstance(response.context['p_form'], ProfileUpdateForm)

        data = {
            'username': USER_NAME_NEW,
            'email': EMAIL,
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert response.url == reverse('profile')
        updated_user = get_user_model().objects.get(username=USER_NAME_NEW)
        assert updated_user.email == EMAIL
        updated_profile = Profile.objects.get(user=updated_user)
        assert updated_profile.phone_number == PHONE_NUMBER  # Assert that phone_number is not changed

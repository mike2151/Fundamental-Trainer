from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from .models import SiteUser

class SignUpView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect("/")
        else:
            return render(request, "users/signup.html", {})
    def post(self, request, *args, **kwargs):
        email = self.request.POST.get('email', '')
        password = self.request.POST.get('password', '')
        password2 = self.request.POST.get('password2', '')
        first_name = self.request.POST.get('first_name', '')
        last_name = self.request.POST.get('last_name', '')

        error_messages = []
        if len(first_name) == 0:
            error_messages.append("No first name given")

        if len(last_name) == 0:
            error_messages.append("No last name given")

        if password != password2:
            error_messages.append("passwords do not match")

        if len(password) < 8:
            error_messages.append("password length must be at least 8 characters")

        email_taken = True
        try:
            curr_user = SiteUser.objects.get(email=email)
            if curr_user is not None:
                if not curr_user.is_active:
                    email_taken = False
                    curr_user.delete()
        except SiteUser.DoesNotExist:
            email_taken = False

        if email_taken:
            error_messages.append("email taken")

        if len(error_messages) > 0:
            return render(request, "users/signup.html", {"error_messages": error_messages})

        # TODO: Handle Email Verification
        user = SiteUser.objects.create_user(username=email, email=email, password=password, first_name=first_name, last_name=last_name)


        return HttpResponseRedirect("/login/?status=confirm")

class LoginView(View):
    template_name = 'users/login.html'
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect("/")
        else:
            message_to_render = ''
            message_color = "red"
            message = str(request.GET.get('status', ''))
            if message == "activated":
                message_to_render = "Your account is now activated. Please log in to proceed."
            elif message == "invalid_activation":
                message_to_render = "The account activation link does not exist or has expired. Please try signing up again."
                message_color = "green"
            elif message == "confirm":
                message_to_render = "Please check and confirm your email to proceed. You may need to check spam."

            return render(request, self.template_name, {"message": message_to_render, "message_color": message_color})
    def post(self, request,  *args, **kwargs):
        email = self.request.POST.get('email', '')
        password = self.request.POST.get('password', '')
        user = authenticate(request=request, username=email, password=password)
        if user:
            if user.is_active:
                login(request, user)
                if user.is_from_company:
                    return HttpResponseRedirect("/interview_questions")
                else:
                    return HttpResponseRedirect("/questions/answer")
        return render(request, self.template_name, {"message": "Invalid email/password combination", "message_color": "red"})

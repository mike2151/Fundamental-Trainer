from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect
from .models import SiteUser
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage

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

        # email verification
        user = SiteUser.objects.create_user(is_active=False, username=email, email=email, password=password, first_name=first_name, last_name=last_name)

        current_site = get_current_site(request)
        mail_subject = 'Please Confirm Your Email For Fundamental Trainer'
        message = render_to_string('users/acc_active_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })
        email_obj = EmailMessage(
            mail_subject, message, to=[email]
        )
        email_obj.send()
        return HttpResponseRedirect("/login/?status=confirm")


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = SiteUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, SiteUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponseRedirect("/login/?status=activated")
    else:
        return HttpResponseRedirect("/login/?status=invalid_activation")

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
                return HttpResponseRedirect("/")
        return render(request, self.template_name, {"message": "Invalid email/password combination", "message_color": "red"})

class AccountView(View):
    template_name = 'users/account.html'
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/login')
        return render(request, self.template_name, {})
    def post(self, request, *args, **kwargs):
        first_name = self.request.POST.get('first_name', '')
        last_name = self.request.POST.get('last_name', '')

        message = ""
        if len(first_name) == 0:
            message = "No first name given. "

        if len(last_name) == 0:
            message += "No last name given. "

        if len(message) == 0:
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.save()
            return render(request, self.template_name, {"message": "Your account has been successfully been updated", "message_color": "green"})
        else:
            return render(request, self.template_name, {"message": message, "message_color": "red"})


class DeleteAccountView(View):
    template_name = 'users/delete.html'
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/login')
        return render(request, self.template_name, {})
    def post(self, request, *args, **kwargs):
        user = request.user
        logout(request)
        user.delete()
        return HttpResponseRedirect("/")

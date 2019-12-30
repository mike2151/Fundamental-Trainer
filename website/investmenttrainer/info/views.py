from django.shortcuts import render
from django.views import View

class HomePageView(View):
    template = "info/home.html"
    def get(self, request, *args, **kwargsa):
        return render(request, self.template, {})

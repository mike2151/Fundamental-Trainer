from django.shortcuts import render
from django.views import View
from investmenttrainer.utils import caching

class HomePageView(View):
    template = "info/home.html"
    def get(self, request, *args, **kwargsa):
        stats_questions = caching.get_value("num_questions")
        stats_challenges = caching.get_value("num_types_challenges")
        stats_securities = caching.get_value("num_securities")
        
        if stats_questions is None:
            stats_questions = 0
        if stats_challenges is None:
            stats_challenges = 0
        if stats_securities is None:
            stats_securities = 0

        stats_minutes = stats_questions * 15
        return render(request, self.template, {
            'stats_questions': stats_questions,
            'stats_challenges': stats_challenges,
            'stats_securities': stats_securities,
            'stats_minutes': stats_minutes
        })

class TermsConditionsView(View):
    template = "info/terms_conditions.html"
    def get(self, request, *args, **kwargsa):
        return render(request, self.template, {})

class AboutView(View):
    template = "info/about.html"
    def get(self, request, *args, **kwargsa):
        return render(request, self.template, {})


class NoAuthView(View):
    template = "info/noauth.html"
    def get(self, request, *args, **kwargsa):
        return render(request, self.template, {})

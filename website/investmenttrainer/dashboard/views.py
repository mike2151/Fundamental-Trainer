from django.shortcuts import render
from django.views import View
from investmenttrainer.utils import caching
from django.shortcuts import redirect
import json

class DashboardView(View):
    template_name = "dashboard/home.html"
    def get(self ,request, *args, **kwargs):
        if not request.user.is_authenticated:
            redirect("/")
        challenge_types = caching.get_value("challenge_types")
        challenge_types_url = [c.lower().replace(" ", "_") for c in challenge_types]

        challenge_key = 'premium_ids' if request.user.is_premium else 'free_ids'
        user_stats = {} if len(request.user.stats) < 3 else json.loads(request.user.stats)[challenge_key]

        user_history = {} if len(request.user.history) < 3 else json.loads(request.user.history)[challenge_key]

        return render(request, self.template_name, {"challenge_types": challenge_types, "challenge_types_url": challenge_types_url, "stats": user_stats, "history": user_history})


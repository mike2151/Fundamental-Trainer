from django.shortcuts import render
from django.views import View
import json
from .models import Challenge
from django.shortcuts import redirect
from random import shuffle
from django.http import JsonResponse
from investmenttrainer.utils import caching
import random
from django.db.models import Max

class ChallengeView(View):
    template_name = "challenge/challenge.html"
    def get(self, request, *args, **kwargs):
        challenge = Challenge.objects.get(display_id=self.kwargs.get('pk'))
        challenge_type = challenge.time_label_url
        sections = ["About", "Historic Data", "Technicals", "Financial Statements"]
        return render(request, self.template_name, {"challenge": challenge, 'sections': sections, "challenge_type": challenge_type})
    def post(self, request, *args, **kwargs):
        challenge = Challenge.objects.get(display_id=self.kwargs.get('pk'))
        user_guess = int(request.POST.get("guess", -1))
        if user_guess not in [0,1]:
            return JsonResponse({"success": False})
        correct = user_guess == challenge.result
        if not request.user.is_authenticated:
            return JsonResponse({"success": True, "correct": correct})
        user = request.user
        # mark completed
        challenge_key = 'premium_ids' if user.is_premium else 'free_ids'
        challenge_type = challenge.time_label_url
        completed_challenges = {}
        completed_challenges_content = user.completed_challenges
        if len(completed_challenges_content) > 0:
            cc_json = json.loads(completed_challenges_content)
            if challenge_key in cc_json:
                if challenge_type in cc_json[challenge_key]:
                    completed_challenges = cc_json
        if challenge_key not in completed_challenges:
            completed_challenges[challenge_key] = {}
        if challenge_type not in completed_challenges[challenge_key]:
            completed_challenges[challenge_key][challenge_type] = []
        completed_challenges[challenge_key][challenge_type] =  completed_challenges[challenge_key][challenge_type]  + [challenge.display_id]
        user.completed_challenges = json.dumps(completed_challenges)
        # add to stats
        stats = {}
        stats_content = user.stats
        if len(stats_content) > 0:
            s_json = json.loads(stats_content)
            if challenge_key in s_json:
                if challenge_type in s_json[challenge_key]:
                    stats = s_json
        if challenge_key not in stats:
            stats[challenge_key] = {}
        if challenge_type not in stats[challenge_key]:
            stats[challenge_key][challenge_type] = {"correct": 0, "incorrect": 0}
        if correct:
            stats[challenge_key][challenge_type]["correct"] += 1
        else:
            stats[challenge_key][challenge_type]["incorrect"] += 1
        user.stats = json.dumps(stats)
        # add to history
        history = {}
        h_content = user.history
        if len(h_content) > 0:
            h_json = json.loads(h_content)
            if challenge_key in h_json:
                if challenge_type in h_json[challenge_key]:
                    history = h_json
        if challenge_key not in history:
            history[challenge_key] = {}
        if challenge_type not in history[challenge_key]:
            history[challenge_key][challenge_type] = []
        new_entry = {}
        new_entry["name"] = challenge.stock_ticker + ": " + challenge.window_date.strftime('%m %d, %Y')
        new_entry["correct"] = correct
        new_entry["id"] = challenge.display_id

        history[challenge_key][challenge_type].insert(0, new_entry)
        user.history = json.dumps(history)

        user.save()

        return JsonResponse({"success": True, "correct": correct})

class ListChallengeView(View):
    def get(self, request, *args, **kwargs):
        challenges = []
        if (not request.user.is_authenticated) or (not request.user.is_premium):
            challenges = Challenge.objects.filter(is_premium=False)
        else:
            challenges = Challenge.objects.all()
        return render(request, "challenge/list.html", {"challenges": challenges})

class OutOfChallengesView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "challenge/out.html", {})

class NextChallengeView(View):
    NUM_UPCOMING_CHALLENGES = 10
    def get_random_challenge(self):
        max_id = Challenge.objects.all().aggregate(max_id=Max("id"))['max_id']
        while True:
            pk = random.randint(1, max_id)
            challenge = Challenge.objects.filter(pk=pk).first()
            if challenge:
                return challenge
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            # return a random challenge
            random_challenge = self.get_random_challenge()
            next_challenge_id = random_challenge.display_id
            return redirect("/challenge/" + str(next_challenge_id))
        user = self.request.user
        challenge_key = 'premium_ids' if user.is_premium else 'free_ids'
        challenge_type = self.kwargs.get('challenge_type')

        next_challenge_id = -1
        # see if there is a next challenge we can serve up
        user_upcoming_challenges_body = '{"free_ids": {}, "premium_ids": {}}' if len(user.upcoming_challenges) == 0 else user.upcoming_challenges
        upcoming_challenges = json.loads(user_upcoming_challenges_body)
        if len(upcoming_challenges[challenge_key]) > 0 and challenge_type in upcoming_challenges[challenge_key] and  len(upcoming_challenges[challenge_key][challenge_type]) > 0:
            next_challenge_id = upcoming_challenges[challenge_key][challenge_type][0]
            upcoming_challenges[challenge_key][challenge_type] = upcoming_challenges[challenge_key][challenge_type][1:]
        # add more challenges
        if challenge_type not in upcoming_challenges[challenge_key] or len(upcoming_challenges[challenge_key][challenge_type]) < 2:
            completed_challenges = {"free_ids": {challenge_type: []}, "premium_ids": {challenge_type: []}} if len(user.completed_challenges) == 0 else json.loads(user.completed_challenges)
            already_completed_challenges = completed_challenges[challenge_key][challenge_type]
            num_already_completed = len(already_completed_challenges)

            challenge_queryset = Challenge.objects.filter(time_label_url=challenge_type) if user.is_premium else Challenge.objects.filter(is_premium=False, time_label_url=challenge_type)
            num_total_challenges = challenge_queryset.count()

            num_challenges_to_add = min(self.NUM_UPCOMING_CHALLENGES, num_total_challenges - num_already_completed)

            if num_challenges_to_add == 0:
                return redirect('/challenge/out')

            if challenge_type not in upcoming_challenges[challenge_key]:
                upcoming_challenges[challenge_key][challenge_type] = []
            shuffled_challenges = list(challenge_queryset)
            shuffle(shuffled_challenges)
            curr_idx = 0
            for _ in range(num_challenges_to_add):
                while True:
                    challenge = shuffled_challenges[curr_idx].display_id
                    if not challenge in already_completed_challenges:
                        upcoming_challenges[challenge_key][challenge_type].append(challenge)
                        break
                    curr_idx += 1
            if next_challenge_id == -1:
                next_challenge_id = upcoming_challenges[challenge_key][challenge_type][0]
                upcoming_challenges[challenge_key][challenge_type] = upcoming_challenges[challenge_key][challenge_type][1:]

        # update upcoming challenges
        user.upcoming_challenges = json.dumps(upcoming_challenges)
        user.save()

        return redirect("/challenge/" + str(next_challenge_id))


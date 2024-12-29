# views.py
from .models import Habit, UserScore
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.shortcuts import render
from django.utils import timezone
import numpy as np
from io import BytesIO
import base64
from django.http import HttpResponse

class HabitListView(LoginRequiredMixin, ListView):
    model = Habit
    template_name = "habit_list.html"
    context_object_name = "habits"

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["score"] = UserScore.objects.get_or_create(user=self.request.user, date=timezone.now())[0].score
        context["user"] = self.request.user
        return context


class HabitCreateView(LoginRequiredMixin, CreateView):
    model = Habit
    fields = ["name", "points"]
    template_name = "habit_create.html"
    success_url = "/"  # Redirect URL after successful form submission

    def form_valid(self, form):
        # Set the owner to the current user
        form.instance.owner = self.request.user
        return super().form_valid(form)


class HabitUpdateView(LoginRequiredMixin, UpdateView):
    model = Habit
    fields = ["name", "points"]
    template_name = "habit_update.html"
    success_url = "/"  # Redirect URL after successful form submission

    def get_queryset(self):
        return Habit.objects.filter(
            id=self.kwargs["pk"],
            owner=self.request.user,
        )


class HabitDeleteView(LoginRequiredMixin, DeleteView):
    model = Habit
    success_url = "/"
    template_name = "habit_confirm_delete.html"

    def get_queryset(self):
        return Habit.objects.filter(
            id=self.kwargs["pk"],
            owner=self.request.user,
        )


class CompleteTask(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        habit = Habit.objects.get(pk=kwargs["pk"], owner=request.user)
        userscore = UserScore.objects.get_or_create(
            user=request.user,
            date=timezone.now(),
        )[0]
        userscore.score += habit.points
        userscore.save()
        return redirect("your_score")


class IncompleteTask(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        habit = Habit.objects.get(pk=kwargs["pk"], owner=request.user)
        userscore = UserScore.objects.get_or_create(
            user=request.user,
            date=timezone.now(),
        )[0]
        userscore.score -= habit.points
        userscore.save()
        return redirect("your_score")


class HabitCardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        habit = Habit.objects.get(pk=kwargs["pk"], owner=request.user)
        return render(
            request=request,
            template_name="habit_card.html",
            context={
                "habit": habit,
            },
        )

class YourScoreView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        userscore = UserScore.objects.get_or_create(
            user=request.user,
            date=timezone.now(),
        )[0]
        return render(
            request=request,
            template_name="score.html",
            context={
                "score": userscore,
            },
        )

class HeatmapView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        userscores = UserScore.objects.filter(user=request.user)
        # https://www.youtube.com/watch?v=KpjWXZqAUcQ
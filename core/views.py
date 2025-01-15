# views.py
from .models import Habit, UserScore
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum
from django.db.models import Max, Min


class HabitListView(LoginRequiredMixin, ListView):
    model = Habit
    template_name = "habit_list.html"
    context_object_name = "habits"

    def get_queryset(self):
        return Habit.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_score"] = UserScore.objects.get_or_create(
            user=self.request.user, date=timezone.now()
        )[0]
        context["user"] = self.request.user
        context["calendar_data"] = get_calendar_data(self.request.user)
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
        userscore.accomplished_habits.add(habit)
        userscore.save()
        return redirect("habit_card", pk=habit.pk)


class IncompleteTask(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        habit = Habit.objects.get(pk=kwargs["pk"], owner=request.user)
        userscore = UserScore.objects.get_or_create(
            user=request.user,
            date=timezone.now(),
        )[0]
        userscore.score -= habit.points
        userscore.accomplished_habits.remove(habit)
        userscore.save()
        return redirect("habit_card", pk=habit.pk)


class HabitCardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        habit = Habit.objects.get(pk=kwargs["pk"], owner=request.user)
        response = render(
            request=request,
            template_name="habit_card.html",
            context={
                "habit": habit,
                "user_score": UserScore.objects.get_or_create(
                    user=self.request.user, date=timezone.now()
                )[0],
            },
        )
        response.headers['HX-Trigger'] = 'habitUpdated'
        return response


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
                "user_score": userscore,
            },
        )


def get_calendar_data(user):
    end_period = datetime.now().date()
    start_period = end_period - timedelta(days=365)

    # Get daily scores
    daily_scores = (
        UserScore.objects.filter(
            user=user, date__gte=start_period, date__lte=end_period
        )
        .values("date")
        .annotate(total_score=Sum("score"))
        .order_by("date")
    )

    # Get max absolute score for normalization
    max_score = max(
        abs(daily_scores.aggregate(Max("total_score"))["total_score__max"] or 0),
        abs(daily_scores.aggregate(Min("total_score"))["total_score__min"] or 0),
    )

    scores_dict = {
        item["date"].strftime("%Y-%m-%d"): item["total_score"] for item in daily_scores
    }

    dates = [
        (start_period + timedelta(days=x)).strftime("%Y-%m-%d") for x in range(366)
    ]

    calendar_data = [
        {
            "date": date,
            "score": scores_dict.get(date, 0),
            "intensity": abs(scores_dict.get(date, 0)) / max_score if max_score else 0,
        }
        for date in reversed(dates)
    ]
    return calendar_data


class HeatmapView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        calendar_data = get_calendar_data(request.user)
        return render(request, "heatmap.html", {"calendar_data": calendar_data})

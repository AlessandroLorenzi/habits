# urls.py
from django.urls import path
from .views import (
    HabitCreateView,
    HabitListView,
    HabitDeleteView,
    HabitUpdateView,
    CompleteTask,
    IncompleteTask,
    HabitCardView,
    YourScoreView,
    HeatmapView,
)

urlpatterns = [
    path("", HabitListView.as_view(), name="habit_list"),
    path("new/", HabitCreateView.as_view(), name="habit_create"),
    path("edit/<int:pk>/", HabitUpdateView.as_view(), name="habit_update"),
    path("delete/<int:pk>/", HabitDeleteView.as_view(), name="habit_delete"),
    path("habit-card/<int:pk>/", HabitCardView.as_view(), name="habit_card"),
    path("complete/<int:pk>/", CompleteTask.as_view(), name="complete_task"),
    path("incomplete/<int:pk>/", IncompleteTask.as_view(), name="incomplete_task"),
    path("score/", YourScoreView.as_view(), name="your_score"),
    path("heatmap/", HeatmapView.as_view(), name="heatmap"),
]

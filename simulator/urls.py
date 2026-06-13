from django.urls import path
from .views import SimulatorView, SimulatorRecalculateView

app_name = 'simulator'
urlpatterns = [
    path('simulator/', SimulatorView.as_view(), name='index'),
    path('api/simulator/recalculate/', SimulatorRecalculateView.as_view(), name='recalculate'),
]

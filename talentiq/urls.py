"""
URL configuration for talentiq project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/',      admin.site.urls),

    # ── HR PORTAL ──
    path('hr/',         include('candidates.urls',        namespace='candidates')),
    path('hr/',         include('jobs.urls',              namespace='jobs')),
    path('hr/',         include('resume_processing.urls', namespace='resumes')),
    path('hr/',         include('matching.urls',          namespace='matching')),
    path('hr/',         include('search.urls',            namespace='search')),
    path('hr/',         include('analytics.urls',         namespace='analytics')),
    path('hr/',         include('simulator.urls',         namespace='simulator')),
    path('hr/',         include('reports.urls',           namespace='reports')),

    # ── CANDIDATE PORTAL ──
    path('candidate/',  include('candidate_portal.urls',  namespace='portal')),

    # ── Root redirect ──
    path('',            lambda req: __import__('django.shortcuts',
                        fromlist=['redirect']).redirect('/hr/dashboard/')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from rest_framework import generics
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

from .forms import CustomUserCreationForm
from .models import Article, Journalist, Publisher
from .serializers import JournalistSerializer, PublisherSerializer, \
    ArticleSerializer


# ------------- Helper role checks -------------
def is_editor(user):
    return user.is_authenticated and user.role == 'editor'

def is_journalist(user):
    return user.is_authenticated and user.role == 'journalist'

def is_reader(user):
    return user.is_authenticated and user.role == 'reader'


# ------------- Home Page -------------
def home(request):
    context = {}
    if request.user.is_authenticated:
        if request.user.role == 'editor':
            context['dashboard_url'] = 'editor_dashboard'
            context['dashboard_label'] = 'Editor Dashboard'
        elif request.user.role == 'journalist':
            context['dashboard_url'] = 'journalist_dashboard'
            context['dashboard_label'] = 'Journalist Dashboard'
        elif request.user.role == 'reader':
            context['dashboard_url'] = 'subscriptions'
            context['dashboard_label'] = 'My Subscriptions'
    # no else needed; context blank for anonymous
    return render(request, 'newsapp/home.html', context)


# ------------- Role-Based Dashboards -------------
@login_required
@user_passes_test(is_editor)
def editor_dashboard(request):
    # Show all articles not approved yet
    articles = Article.objects.filter(approved=False)
    return render(request, 'newsapp/editor_dashboard.html', {'articles': articles})

@login_required
@user_passes_test(is_journalist)
def journalist_dashboard(request):
    # Show all articles by this journalist
    articles = request.user.published_articles.all()
    return render(request, 'newsapp/journalist_dashboard.html', {'articles': articles})

@login_required
@user_passes_test(is_reader)
def subscriptions(request):
    publishers = request.user.subscriptions_publishers.all()
    journalists = request.user.subscriptions_journalists.all()
    return render(request, 'newsapp/subscriptions.html', {
        'publishers': publishers,
        'journalists': journalists,
    })


# ------------- Article Approval (Editor) -------------
@login_required
@user_passes_test(is_editor)
def approve_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        article.approved = True
        article.save()
        return redirect('editor_dashboard')
    return render(request, 'newsapp/approve_article.html', {'article': article})


# ------------- Article List, Profile, Signup -------------
def article_list(request):
    articles = Article.objects.filter(approved=True)
    return render(request, 'newsapp/article_list.html', {'articles': articles})

@login_required
def profile(request):
    return render(request, 'newsapp/profile.html')

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


# ------------- REST API views (unchanged) -------------
class ArticleListView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.role == 'reader':
            publishers = user.subscriptions_publishers.all()
            journalists = user.subscriptions_journalists.all()
            return Article.objects.filter(
                approved=True
            ).filter(
                publisher__in=publishers
            ) | Article.objects.filter(
                approved=True
            ).filter(
                journalist__in=journalists
            )
        return Article.objects.filter(approved=True)

class JournalistListView(generics.ListAPIView):
    queryset = Journalist.objects.all()
    serializer_class = JournalistSerializer

class PublisherListView(generics.ListAPIView):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

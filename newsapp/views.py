from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from rest_framework import generics

from .forms import CustomUserCreationForm
from .models import Article, Journalist, Publisher
from .serializers import ArticleSerializer, JournalistSerializer, PublisherSerializer
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

def home(request):
    return render(request, 'newsapp/home.html')

def article_list(request):
    articles = Article.objects.filter(approved=True)
    return render(request, 'newsapp/article_list.html', {'articles': articles})

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # or wherever you want to redirect
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'newsapp/profile.html')

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

@login_required
@permission_required('newsapp.change_article', raise_exception=True)
def approve_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        article.approved = True
        article.save()
        return redirect('article_list')  # Adjust as needed
    return render(request, 'newsapp/approve_article.html', {'article': article})

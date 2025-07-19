from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.db.models import QuerySet
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from rest_framework import generics
from .forms import ArticleForm
from .forms import CustomUserCreationForm
from .models import Article, Journalist, Publisher
from .serializers import JournalistSerializer, PublisherSerializer, \
    ArticleSerializer

# ------------- Helper role checks -------------
def is_editor(user):
    """
    Determines if the given user has the role of an editor.

    This function checks if a user is logged in (authenticated)
    and whether their role is specifically set to 'editor'. It
    returns a boolean value indicating whether the user meets
    both criteria.

    :param user: The user instance to check.
    :type user: Any
    :return: True if the user is authenticated and has a role
        of 'editor', otherwise False.
    :rtype: bool
    """
    return user.is_authenticated and user.role == 'editor'

def is_journalist(user):
    """
    Determines if a user is a journalist by checking their authentication
    status and role. The function evaluates the provided user object to
    determine whether they are authenticated and have the specific
    role "journalist".

    :param user: The user object to be evaluated. It should have
        `is_authenticated` and `role` attributes.
    :type user: Any
    :return: Returns `True` if the user is authenticated and their role
        is 'journalist'. Otherwise, returns `False`.
    :rtype: bool
    """
    return user.is_authenticated and user.role == 'journalist'

def is_reader(user):
    """
    Determines whether the given user has the role of 'reader' and
    is authenticated.

    This function evaluates if the specified user object possesses a
    role labeled as 'reader' and has passed the authentication process. It
    verifies both of these conditions before returning a boolean indicating
    the user's eligibility.

    :param user: The user object to be evaluated, typically representing
    a user  in the system.
    :type user: Any
    :return: True if the user is authenticated and has the 'reader' role,
        otherwise False.
    :rtype: bool
    """
    return user.is_authenticated and user.role == 'reader'

# ------------- Home Page -------------
def home(request: HttpRequest) -> HttpResponse:
    """
    Renders the home page for the user based on their authentication
    status and role. It dynamically determines the appropriate dashboard
    URL and label depending on whether the user is logged in and their
    specific role. The context remains empty for anonymous users who are
    not authenticated.

    :param request: HttpRequest object representing the HTTP request
        sent by the client. It contains metadata about the request and user
        session information.
    :type request: HttpRequest
    :return: HttpResponse object representing the rendered home page
        with the appropriate context for the user based on their role,
        or an empty context for anonymous users.
    :rtype: HttpResponse
    """
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
def editor_dashboard(request: HttpRequest) -> HttpResponse:
    """
    Handles requests to display the editor's dashboard page.
    The dashboard shows a list of articles that have not been approved yet.
    Access to this view is restricted to logged-in users with "editor"
    privileges.

    :param request: HTTP request object containing metadata about
        the request.
    :type request: HttpRequest
    :return: HTTP response rendering the editor dashboard with
        unapproved articles.
    :rtype: HttpResponse
    """
    # Show all articles not approved yet
    articles = Article.objects.filter(approved=False)
    return render(request,
                  'newsapp/editor_dashboard.html',
                  {'articles': articles})

@login_required
@user_passes_test(is_journalist)
def journalist_dashboard(request: HttpRequest) -> HttpResponse:
    """
    Handles the journalist dashboard view, displaying a list of
    approved articles and a flag indicating whether unapproved articles
    exist.

    :param request: The HTTP request object containing user session and
        request-specific data.
    :type request: HttpRequest
    :return: An HTTP response object rendering the journalist dashboard
        template with context data.
    :rtype: HttpResponse
    """
    articles = request.user.journalist_articles.filter(approved=True)
    has_unapproved_articles = request.user.journalist_articles.filter(
        approved=False).exists()
    return render(
        request,
        'newsapp/journalist_dashboard.html', {
        'articles': articles,
        'has_unapproved_articles': has_unapproved_articles
    })

@login_required
@user_passes_test(is_reader)
def subscriptions(request: HttpRequest) -> HttpResponse:
    """
    Handles rendering of the subscriptions page for a logged-in user.
    The page displays the list of publishers and journalists to whom the
    user is
    subscribed. Access to this view is restricted to authorized users with
    specific permissions.

    :param request: The HTTP request object containing metadata about the
        request and the authenticated user.
    :type request: HttpRequest
    :return: An HTTP response object rendering the subscriptions page.
    :rtype: HttpResponse
    """
    publishers = request.user.subscriptions_publishers.all()
    journalists = request.user.subscriptions_journalists.all()
    return render(
        request, 'newsapp/subscriptions.html', {
        'publishers': publishers,
        'journalists': journalists,
    })

# ------------- Article Approval (Editor) -------------
@login_required
@user_passes_test(is_editor)
def approve_article(request: HttpRequest, article_id: int) -> HttpResponse:
    """
    Approve an article submitted by a user. This view is restricted to
    editors and requires the user to be logged in. If the request method is
    POST, the
    article's approval status is updated and the user is redirected to the
    editor dashboard. Otherwise, a template for approving the article is
    rendered.

    :param request: The HTTP request object provided by Django.
    :param article_id: The ID of the article to be approved.
    :return: An HTTP response redirecting to the editor dashboard
        if the article is approved, or rendering the approval
        template otherwise.
    """
    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        article.approved = True
        article.save()
        return redirect('editor_dashboard')
    return render(
        request,
        'newsapp/approve_article.html',
        {'article': article}
    )

# ------------- Article List, Profile, Signup -------------
def article_list(request: HttpRequest) -> HttpResponse:
    """
    Retrieves and renders a list of approved articles.

    This function queries the Article model for entries marked as approved
    and renders them using the 'newsapp/article_list.html' template. The
    result is a dynamically generated web page displaying the list of
    articles.

    :param request: The HTTP request object, representing the client's
        request to the server.
    :return: An HttpResponse instance containing the rendered article list
        page.
    """
    articles = Article.objects.filter(approved=True)
    return render(
        request, 'newsapp/article_list.html',
        {'articles': articles})

@login_required
def profile(request: HttpRequest) -> HttpResponse:
    """
    Handles the profile view for a logged-in user.

    This function processes the HTTP request to display the user's profile
    page. It requires the user to be authenticated before granting access
    to the profile page. The function renders the `profile.html` template
    from the `newsapp` directory for the logged-in user.

    :param request: The HTTP request object that contains metadata about the
        request, including the user session.
    :type request: HttpRequest

    :return: HTTP response containing the rendered profile page.
    :rtype: HttpResponse
    """
    return render(request, 'newsapp/profile.html')

def signup(request: HttpRequest) -> HttpResponse:
    """
    Handles the user signup process. Renders a signup form to the user
    and processes it upon form submission. If the form submission is valid,
    the user is created and
    redirected to the login page. Otherwise, the signup form is displayed
    again with validation errors.

    :param request: HttpRequest object containing metadata about the
        request.
    :return: HttpResponse object with the rendered signup form or a
        redirection to the login page if the signup is successful.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(
        request,
        'registration/signup.html',
        {'form': form})


# ------------- REST API views (unchanged) -------------
class ArticleListView(generics.ListAPIView):
    """
    Provides a list view for articles with specific filtering logic
    based on user authentication and subscriptions.
    This view is designed to display approved articles tailored to the
    user's subscription preferences when authenticated,
    or all approved articles when unauthenticated.

    Specifically, for authenticated users with the role of 'reader',
    the view will filter articles published by the publishers or
    journalists to whom the user has subscribed. If a user is not
    authenticated, the view defaults to returning all approved articles.

    :ivar serializer_class: The serializer class for the articles.
    :type serializer_class: type

    """
    serializer_class = ArticleSerializer

    def get_queryset(self) -> QuerySet[Article]:
        """
        Retrieves a queryset of `Article` objects based on the user's
        authentication status and subscriptions. If the user is
        authenticated and their role is 'reader', the queryset is filtered
        to include articles from publishers or
        journalists the user is subscribed to. If the user is not
        authenticated or does not have a 'reader' role, only approved
        articles are returned.

        :returns: A filtered queryset of articles based on user
            subscriptions or approved status.
        :rtype: QuerySet[Article]
        """
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
    """
    Represents a read-only view for listing journalists.

    This class-based view is used to fetch and return a list of all
    journalists using the specified serializer class to format the data.
    It extends the Django REST framework's `ListAPIView` to leverage
    pagination, filtering, and other functionalities for listing objects.

    :ivar queryset: Queryset specifying all journalist objects to be listed.
                    Fetches all instances of the `Journalist` model.
    :type queryset: QuerySet
    :ivar serializer_class: Serializer class used to serialize the data for
                            journalist objects.
    :type serializer_class: type
    """
    queryset = Journalist.objects.all()
    serializer_class = JournalistSerializer


class PublisherListView(generics.ListAPIView):
    """
    Handles the retrieval and listing of Publisher objects.

    This class-based view provides functionality to fetch and
    return a list of Publisher objects using Django's REST framework. It
    supports generic listing operations and utilizes a specified serializer
    for formatting the response data.

    :ivar queryset: Queryset defining the Publisher objects to be listed.
    :type queryset: QuerySet
    :ivar serializer_class: The serializer class used to serialize the
        Publisher objects.
    :type serializer_class: type
    """
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class SignUpView(CreateView):
    """
    View for user sign-up functionality.

    This class-based view handles the user registration process.
    It utilizes a form class to validate user input, a success URL to
    redirect users upon successful registration, and a specified template
    to render the registration page. The view is designed to integrate
    seamlessly with Django's authentication
    system.

    :ivar form_class: Specifies the form class used for user creation.
    :type form_class: django.forms.Form
    :ivar success_url: URL to redirect to after successful user registration.
    :type success_url: str
    :ivar template_name: Template used to render the user registration page.
    :type template_name: str
    """
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


@login_required
@user_passes_test(is_journalist)
def submit_article(request: HttpRequest) -> HttpResponse:
    """
    Allows a journalist user to submit an article. If the HTTP method
    is POST, the submitted data is validated and saved as a new article
    with the current user set as the journalist. If the method is not POST,
    an empty article
    submission form is displayed. Only accessible to authenticated users who
    have been verified as journalists.

    :param request: The HTTP request object containing metadata about
                    the request and the submitted data in case of POST.
                    It should be an instance of HttpRequest.
    :return: If the request method is POST and the submitted data is valid,
             redirects to the journalist's dashboard. Otherwise, renders
             the article submission form template with a blank or invalid
             form context as HttpResponse.
    """
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.journalist = request.user
            article.save()
            return redirect('journalist_dashboard')
    else:
        form = ArticleForm()
    return render(request,
                  'newsapp/submit_article.html',
                  {'form': form})

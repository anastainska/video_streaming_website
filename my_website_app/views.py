from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from .models import Show, Folder
from .forms import *


# Create your views here.

def home_screen_view(request):
    context = {}
    shows = Show.objects.all()
    context['shows'] = shows
    return render(request, 'home.html', context)


def registration_view(request):
    context = {}
    if request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            account = form.save()
            login(request, account)
            return redirect('shows')
        else:
            context['registration_form'] = form
    else:
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'register.html', context)


def logout_view(request):
    logout(request)
    return redirect('shows')


def login_view(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        return redirect('shows')
    if request.POST:
        form = UserAuthenticationForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)
            if user:
                login(request, user)
                return redirect('shows')
    else:
        form = UserAuthenticationForm()

    context['login_form'] = form
    return render(request, 'login.html', context)


def account_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    context = {}

    if request.POST:
        form = AccountUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.initial = {
                "email": request.POST['email'],
                "username": request.POST['username'],
                "date_of_birth": request.POST['date_of_birth']
            }
            form.save()
            context['success_message'] = "Updated changes! :)"
    else:
        form = AccountUpdateForm(
            initial={
                "email": request.user.email,
                "username": request.user.username,
                "date_of_birth": request.user.date_of_birth
            }
        )
    context['account_form'] = form
    return render(request, 'account.html', context)


def favourite_add(request, show_id):
    show = Show.objects.get(id=show_id)
    folder, created = Folder.objects.get_or_create(id_subscriber=request.user.subscriber, name='Favourites')
    folder.favourites.add(show)
    return redirect('show', pk=show_id)


def remove_from_favorites(request, show_id):
    show = Show.objects.get(id=show_id)
    folder = Folder.objects.get(name='Favourites', id_subscriber=request.user.subscriber)
    folder.favourites.remove(show)
    return redirect('favourites')


def favourite_list(request):
    folder, created = Folder.objects.get_or_create(id_subscriber=request.user.subscriber, name='Favourites')
    favourites = folder.favourites.all()
    return render(request, 'favourites.html', {'favourites': favourites})


class ShowListView(ListView):
    model = Show
    context_object_name = 'shows'


class ShowDetail(DetailView):
    model = Show
    context_object_name = 'show'


class ShowCreate(CreateView):
    model = Show
    fields = '__all__'
    success_url = reverse_lazy('shows')


class ShowUpdate(UpdateView):
    model = Show
    fields = '__all__'
    success_url = reverse_lazy('shows')


class ShowDelete(DeleteView):
    model = Show
    context_object_name = 'show'
    success_url = reverse_lazy('shows')

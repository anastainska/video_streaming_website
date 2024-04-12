from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.core.paginator import Paginator
from .models import Show, Folder, Category
from .forms import *
from django.contrib import messages, auth
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

# Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


# Create your views here.

def home_screen_view(request):
    logo_object = Logo.objects.first()  # Assuming you have only one logo
    context = {'logo_object': logo_object}
    return render(request, 'base.html', context)



def movies(request, category_slug=None):
    categories = None
    shows = None

    if category_slug is not None:
        categories = get_object_or_404(Category, slug=category_slug)
        shows = Show.objects.filter(category=categories)
        paginator = Paginator(shows, 6)
        page = request.GET.get('page')
        paged_shows = paginator.get_page(page)
        show_count = shows.count
    else:
        shows = Show.objects.all()
        paginator = Paginator(shows, 2)
        page = request.GET.get('page')
        paged_shows = paginator.get_page(page)
        show_count = shows.count()
    context = {
        'shows': paged_shows,
        'show_count': show_count,
    }
    return render(request, 'movies.html', context)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            shows = Show.objects.filter(title__icontains=keyword)
            show_count = shows.count()
    context = {
        'shows': shows,
        'show_count': show_count,
    }
    return render(request, 'movies.html', context)


def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = Subscriber.objects.create_user(username=username, email=email, password=password)
            user.save()

            favourites_folder = Folder.objects.create(name='Favourites', id_subscriber=user.subscriber)

            # Create user profile
            profile = SubscriberProfile()
            profile.user = user
            profile.profile_picture = 'default/default-user.png'
            profile.save()

            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(request, 'Please check your email for a verification link.')
            return redirect('/login/?command=verification&email='+email)
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'register.html', context)


def logout_view(request):
    logout(request)
    return redirect('shows')


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            # messages.success(request, 'You are now logged in.')
            return redirect('shows')
        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('login')
    return render(request, 'login.html')


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
    request.user.subscriber.save()
    return redirect('show', pk=show_id)


def remove_from_favorites(request, show_id):
    show = Show.objects.get(id=show_id)
    folder = Folder.objects.get(name='Favourites', id_subscriber=request.user.subscriber)
    folder.favourites.remove(show)
    request.user.subscriber.save()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def favourite_list(request):
    folder, created = Folder.objects.get_or_create(id_subscriber=request.user.subscriber, name='Favourites')
    favourites = folder.favourites.all()
    return render(request, 'favourites.html', {'favourites': favourites})


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Subscriber._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Subscriber.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Subscriber.objects.filter(email=email).exists():
            user = Subscriber.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgot_password')
    return render(request, 'forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Subscriber._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Subscriber.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('login')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Subscriber.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('reset_password')
    return render(request, 'reset_password.html')


@login_required(login_url='/login/')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Subscriber.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # auth.logout(request)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password.')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match.')
            return redirect('change_password')
    return render(request, 'change_password.html')


def submit_review(request, show_id):
    url = request.META.get('HTTP_REFERER')
    if request.method =='POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, show__id=show_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.show_id = show_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)


@login_required(login_url='/login/')
def edit_profile(request):
    user_profile = get_object_or_404(SubscriberProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            # Save user form without committing to update user's username
            user = user_form.save(commit=False)
            new_username = user_form.cleaned_data['username']
            if Subscriber.objects.exclude(pk=request.user.pk).filter(username=new_username).exists():
                messages.error(request, 'This username is already taken. Please choose a different one.')
            else:
                # Save user form with new username
                user.save()
                profile_form.save()
                messages.success(request, 'Your profile has been updated.')
                return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_profile': user_profile,
    }
    return render(request, 'edit_profile.html', context)


class ShowListView(ListView):
    model = Show
    context_object_name = 'shows'


class ShowDetail(DetailView):
    model = Show
    context_object_name = 'show'
    template_name = 'show_detail.html'  # Replace with the actual template name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the reviews related to the show
        show = self.get_object()
        reviews = ReviewRating.objects.filter(show=show).order_by('-updated_at')

        context['reviews'] = reviews

        # Check if 'Favourites' folder exists for the current user
        if self.request.user.is_authenticated:
            favourites_folder = get_object_or_404(Folder, name='Favourites', id_subscriber=self.request.user.subscriber)
        else:
            favourites_folder = None

        # Pass the 'Favourites' folder to the template
        context['favourites_folder'] = favourites_folder

        return context


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

import os

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.utils.text import slugify

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import Blog, UploadedFile
from .forms import BlogForm, validate_upload, RegisterForm, LoginForm

from .auth_utils import (
    set_auth_cookies,
    clear_auth_cookies,
    decode_token,
    TokenError
)

from .decorators import token_required

def home(request):
    query = request.GET.get('q', '').strip()

    blogs = Blog.objects.all()

    if query:
        blogs = blogs.filter(
            Q(title__icontains=query)
        )

    return render(
        request,
        'blog/home.html',
        {
            'blogs': blogs,
            'query': query
        }
    )


def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)

    return render(
        request,
        'blog/blog_detail.html',
        {
            'blog': blog
        }
    )

@token_required
def blog_add(request):
    authors = Blog.objects.values_list(
        'author',
        flat=True
    ).distinct()

    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)

        if form.is_valid():
            blog = form.save(commit=False)

            base_slug = slugify(blog.title)
            slug = base_slug
            counter = 1

            while Blog.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            blog.slug = slug
            blog.save()

            messages.success(request, "Blog added successfully!")
            return redirect('home')

    else:
        form = BlogForm()

    return render(
        request,
        'blog/blog_form.html',
        {
            'form': form,
            'page_title': 'Add Blog Post',
            'authors': authors,   # ADD THIS
        }
    )



@token_required
def blog_edit(request, slug):

    blog = get_object_or_404(
        Blog,
        slug=slug
    )


    if request.method == 'POST':

        form = BlogForm(
            request.POST,
            request.FILES,
            instance=blog
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Blog updated successfully!"
            )

            return redirect(
                'blog_detail',
                slug=blog.slug
            )


    else:

        form = BlogForm(
            instance=blog
        )


    return render(
        request,
        'blog/blog_form.html',
        {
            'form': form,
            'page_title': 'Edit Blog Post',
            'blog': blog
        }
    )



# ==========================
# DELETE BLOG (LOGIN REQUIRED)
# ==========================

@token_required
def blog_delete(request, slug):

    blog = get_object_or_404(
        Blog,
        slug=slug
    )


    if request.method == 'POST':

        blog.delete()

        messages.success(
            request,
            "Blog deleted successfully!"
        )

        return redirect('home')


    return render(
        request,
        'blog/blog_delete.html',
        {
            'blog': blog
        }
    )



# ==========================
# ABOUT
# ==========================

def about(request):
    return render(
        request,
        'blog/about.html'
    )



# ==========================
# CONTACT
# ==========================

def contact(request):

    if request.method == 'POST':

        messages.success(
            request,
            'Thanks for reaching out!'
        )

        return redirect('contact')


    return render(
        request,
        'blog/contact.html'
    )



# ==========================
# FILE UPLOAD (LOGIN REQUIRED)
# ==========================

@token_required
def index(request):

    if request.method == 'POST':

        uploaded_files = request.FILES.getlist(
            'files'
        )


        if not uploaded_files:

            messages.error(
                request,
                'Please choose files.'
            )

            return redirect('file:index')


        success_count = 0


        for f in uploaded_files:

            try:

                validate_upload(f)


            except ValidationError as e:

                messages.error(
                    request,
                    e.message
                )

                continue


            UploadedFile.objects.create(
                file=f,
                original_name=f.name
            )

            success_count += 1



        if success_count:

            messages.success(
                request,
                f"Uploaded {success_count} files successfully."
            )


        return redirect('file:index')



    files = UploadedFile.objects.all()


    return render(
        request,
        'file/index.html',
        {
            'files': files
        }
    )



# ==========================
# DELETE FILE (LOGIN REQUIRED)
# ==========================

@token_required
def delete_file(request, pk):

    uploaded_file = get_object_or_404(
        UploadedFile,
        pk=pk
    )


    if request.method == 'POST':

        name = uploaded_file.filename()

        uploaded_file.file.delete(
            save=False
        )

        uploaded_file.delete()


        messages.success(
            request,
            f"{name} deleted."
        )


    return redirect('file:index')



# ==========================
# DOWNLOAD FILE
# ==========================

def download_file(request, pk):

    uploaded_file = get_object_or_404(
        UploadedFile,
        pk=pk
    )


    if not uploaded_file.file or not os.path.exists(
        uploaded_file.file.path
    ):

        raise Http404(
            "File not found"
        )


    return FileResponse(
        uploaded_file.file.open('rb'),
        as_attachment=True,
        filename=uploaded_file.original_name
    )



# ==========================
# AUTHENTICATION
# ==========================

def register_view(request):

    if request.method == 'POST':

        form = RegisterForm(
            request.POST
        )

        if form.is_valid():

            user = form.save()

            response = redirect(
                'home'
            )

            set_auth_cookies(
                response,
                user
            )

            messages.success(
                request,
                "Account created."
            )

            return response


    else:

        form = RegisterForm()



    return render(
        request,
        'blog/register.html',
        {
            'form': form
        }
    )



def login_view(request):

    next_url = (
        request.GET.get('next')
        or request.POST.get('next')
        or 'home'
    )


    if request.method == 'POST':

        form = LoginForm(
            request.POST
        )


        if form.is_valid():

            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )


            if user:

                response = redirect(
                    next_url
                )

                set_auth_cookies(
                    response,
                    user
                )


                messages.success(
                    request,
                    "Login successful."
                )


                return response



    else:

        form = LoginForm()



    return render(
        request,
        'blog/login.html',
        {
            'form': form,
            'next': next_url
        }
    )



def logout_view(request):

    response = redirect(
        'home'
    )

    clear_auth_cookies(
        response
    )

    messages.success(
        request,
        "Logged out."
    )

    return response


# ==========================
# REFRESH TOKEN
# ==========================

def refresh_view(request):

    next_url = request.GET.get(
        'next',
        'home'
    )

    refresh_token = request.COOKIES.get(
        settings.REFRESH_TOKEN_COOKIE
    )

    try:
        payload = decode_token(
            refresh_token,
            'refresh'
        )

        user = User.objects.get(
            id=payload.get('user_id')
        )

        response = redirect(
            next_url
        )

        set_auth_cookies(
            response,
            user
        )

        messages.success(
            request,
            "Session refreshed."
        )

        return response


    except (TokenError, User.DoesNotExist):

        messages.error(
            request,
            "Refresh token expired. Please login again."
        )

        return redirect(
            'login'
        )
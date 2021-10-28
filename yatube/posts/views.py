from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import PostForm
from .models import Group, Post, User
from .post_settings import PAGINATOR_SET


def index(request):
    """View функция для главной страницы."""
    post_list = Post.objects.all()
    paginator = Paginator(post_list, PAGINATOR_SET)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """View функция для страницы сообщества."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, PAGINATOR_SET)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    """View функция для страницы профиля."""
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    count = posts.count()
    paginator = Paginator(posts, PAGINATOR_SET)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'count': count,
        'author': author,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """View функция для страницы поста."""
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    count = author.posts.all().count()
    context = {
        'count': count,
        'author': author,
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """View функция для создания нового поста."""
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(
            reverse('posts:profile', args=(request.user.username,)))
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


def post_edit(request, post_id):
    """View функция для редактирования поста."""
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect(reverse('posts:post_detail', args=(post_id,)))
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        post = form.save()
        return redirect(reverse('posts:post_detail', args=(post_id,)))
    data = {'text': post.text, 'group': post.group}
    form = PostForm(initial=data)
    return render(
        request, 'posts/create_post.html',
        {'form': form, 'post': post}
    )

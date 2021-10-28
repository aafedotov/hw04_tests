from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import PostForm
from .models import Group, Post, User
from .post_settings import PAGINATOR_SET


def pagination(request, to_pagination):
    paginator = Paginator(to_pagination, PAGINATOR_SET)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj

def index(request):
    """View функция для главной страницы."""
    posts = Post.objects.all()
    page_obj = pagination(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)

def group_posts(request, slug):
    """View функция для страницы сообщества."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = pagination(request, posts)
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
    page_obj = pagination(request, posts)
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
    return render(request, 'posts/create_post.html', {'form': form})

def post_edit(request, post_id):
    """View функция для редактирования поста."""
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
    # для Ревьювера: не понял Ваш комментарий к этому if:
    # "Может стоит это сделать после проверки на автора?"
        return redirect(reverse('posts:post_detail', args=(post_id,)))
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        post = form.save()
        return redirect(reverse('posts:post_detail', args=(post_id,)))
        # для Ревьювера: без reverse ничего не работает ((
        # Ваш комментарий: 
        # "redirect внутри применяет reverse к адресу, так что не стоит делать это вручную"
    return render(
        request, 'posts/create_post.html',
        {'form': form, 'post': post}
    )

from django.shortcuts import get_object_or_404, render
from .models import Post, Category, Comment, UserProfile
from .querysets import published_posts, select_related_posts
from .forms import PostForm, CommentForm, UserProfileForm
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model

User = get_user_model()

DEFAULT_POST_COUNT = 5


class PostListView(ListView):
    model = Post
    ordering = ['-pub_date'][:DEFAULT_POST_COUNT]
    paginate_by = 10
    template_name = 'blog/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_list'] = self.get_queryset()[:DEFAULT_POST_COUNT]
        return context


def post_detail(request, pk):
    template = 'blog/detail.html'
    post = get_object_or_404(
        select_related_posts(published_posts(Post.objects)).filter(pk=pk)
    )
    comments = Comment.objects.filter(post=post)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()

    else:
        form = CommentForm()
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    post_list = select_related_posts(published_posts(Post.objects.filter(
        category=category
    )))
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    context = {
        'category': category,
        'post_list': post_list,
        'posts': posts
    }
    return render(request, template, context)


class PostMixin:
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create.html'


class PostFormMixin:
    form_class = PostForm


class PostCreateView(PostMixin, PostFormMixin, CreateView):
    pass


class PostUpdateView(PostMixin, PostFormMixin, UpdateView):
    pass


class PostDeleteView(PostMixin, DeleteView):
    pass


class CommentMixin:
    model = Comment
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/comments.html'


class CommentFormMixin:
    form_class = CommentForm


class CommentListView(CommentMixin, ListView):
    ordering = ['-pub_date']


class CommentCreateView(CommentMixin, CommentFormMixin, CreateView):
    pass


class CommentUpdateView(CommentMixin, CommentFormMixin, UpdateView):
    pass


class CommentDeleteView(CommentMixin, DeleteView):
    pass


class ProfileMixin:
    model = UserProfile
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/profile.html'


class ProfileFormMixin:
    form_class = UserProfileForm


class ProfileDetailView(ProfileMixin, DetailView):
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['get_full_name'] = (
            self.object.get_full_name()
        )
        return context


class ProfileCreateView(ProfileMixin, ProfileFormMixin, CreateView):
    pass


class ProfileUpdateView(ProfileMixin, ProfileFormMixin, UpdateView):
    pass


class ProfileDeleteView(ProfileMixin, DeleteView):
    pass

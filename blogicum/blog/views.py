from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator

from .models import Post, Category, Comment, User
from .forms import PostForm, CommentForm, UserEditForm


def paginate_posts(posts, request, pagination_num=10):
    paginator = Paginator(posts, pagination_num)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


class PostAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return hasattr(obj, 'author') and obj.author == self.request.user


class CommentAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return hasattr(
            obj, 'author') and obj.author == self.request.user


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = Post.objects.apply_filters()
        context['page_obj'] = paginate_posts(posts, self.request)
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_object(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])

        if post.author != self.request.user:
            post = get_object_or_404(Post.objects.apply_filters(
                with_published=True), id=self.kwargs['post_id'])
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )

    page_obj = category.posts.all().apply_filters(
        with_related=False
    )
    page_obj = paginate_posts(page_obj, request)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, template, context)


class PostMixin:
    model = Post
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/create.html'


class PostFormMixin:
    form_class = PostForm


class PostCreateView(LoginRequiredMixin, PostMixin, PostFormMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username})


class PostUpdateView(
    PostAuthorMixin,
    PostMixin,
    PostFormMixin,
    UpdateView
):
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        super().form_valid(form)
        return redirect(self.get_success_url())

    def handle_no_permission(self):
        return redirect('blog:post_detail', self.kwargs['post_id'])

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class PostDeleteView(
    PostAuthorMixin,
    PostMixin,
    PostFormMixin, DeleteView
):
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.object)
        return context


class CommentMixin:
    model = Comment
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/comment.html'


class CommentFormMixin:
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'


class CommentListView(CommentMixin, ListView):
    context_object_name = 'comments'

    def get_post(self):
        return get_object_or_404(Post, id=self.kwargs['post_id'])

    def get_queryset(self):
        post = self.get_post()
        return post.comments.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.get_post()
        if self.request.user.is_authenticated:
            context['form'] = CommentForm()
        return context


class CommentCreateView(LoginRequiredMixin, CommentMixin,
                        CommentFormMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class CommentUpdateView(CommentAuthorMixin,
                        CommentMixin, CommentFormMixin, UpdateView):

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class CommentDeleteView(
    CommentAuthorMixin,
    CommentMixin,
    CommentFormMixin,
    DeleteView
):

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class ProfileMixin:
    model = User
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/profile.html'


class ProfileFormMixin:
    form_class = UserCreationForm


class ProfileDetailView(ProfileMixin, DetailView):
    context_object_name = 'profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.object

        posts = author.posts.all().apply_filters(
            with_published=(author != self.request.user)
        )

        context['form'] = CommentForm()
        context['page_obj'] = paginate_posts(posts, self.request)
        return context


class ProfileUpdateView(

    LoginRequiredMixin, ProfileMixin,
    UpdateView
):
    context_object_name = 'profile'
    template_name = 'blog/user.html'
    form_class = UserEditForm

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username})

from django.shortcuts import get_object_or_404, render, redirect
from .models import Post, Category, Comment
from .querysets import published_posts, select_related_posts
from .forms import PostForm, CommentForm, UserRegistrationForm, UserEditForm
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from datetime import datetime
from django.http import Http404
from django.utils.timezone import now

User = get_user_model()

DEFAULT_POST_COUNT = 5


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        obj = self.get_object()  # Получение объекта пользователя
        if hasattr(obj, 'author'):
            return obj.author == self.request.user
        # Если это редактирование профиля (то есть объект типа User)
        if isinstance(obj, type(self.request.user)):
            return obj == self.request.user
        # Если ни один из вариантов не сработал — запретить доступ
        return False


class PostListView(ListView):
    model = Post
    ordering = ['-pub_date'][:DEFAULT_POST_COUNT]
    paginate_by = 10
    template_name = 'blog/index.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=datetime.now()
        ).with_comment_count().order_by('-pub_date')


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        if not post.is_published and self.request.user != post.author:
            raise Http404("Пост снят с публикации и недоступен.")
        if not post.category.is_published and self.request.user != post.author:
            raise Http404("Категория снята с публикации, доступ ограничен.")
        if post.pub_date > now() and self.request.user != post.author:
            raise Http404("Этот пост еще не опубликован.")
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Записываем в переменную form пустой объект формы.
        context['form'] = CommentForm()
        # Запрашиваем все поздравления для выбранного дня рождения.
        context['comments'] = (
            # Дополнительно подгружаем авторов комментариев
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

    post_list = select_related_posts(published_posts(Post.objects.filter(
        category=category
    ).with_comment_count())).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'post_list': post_list,
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
    slug_url_kwarg = 'post_id'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username})


class PostUpdateView(
    OnlyAuthorMixin,
    PostMixin,
    PostFormMixin,
    UpdateView
):
    slug_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        super().form_valid(form)
        return redirect(self.get_success_url())

    def get_object(self, queryset=None):
        return get_object_or_404(Post, id=self.kwargs['post_id'])

    def handle_no_permission(self):
        post = self.get_object()  # Убедитесь, что у нас есть объект поста
        return redirect('blog:post_detail', post_id=post.id)

    def get_success_url(self):
        # URL отредактированного поста
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


class PostDeleteView(
    OnlyAuthorMixin,
    PostMixin,
    PostFormMixin, DeleteView
):
    slug_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        return get_object_or_404(Post, id=self.kwargs['post_id'])

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


class CommentListView(CommentMixin, ListView):
    slug_url_kwarg = 'post_id'
    ordering = ['created_at']
    context_object_name = 'comments'

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return post.comments.all().order_by('created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, id=self.kwargs['post_id'])
        if self.request.user.is_authenticated:
            context['form'] = CommentForm()
        return context


class CommentCreateView(LoginRequiredMixin, CommentMixin,
                        CommentFormMixin, CreateView):
    slug_url_kwarg = 'post_id'
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs['post_id']})


class CommentUpdateView(OnlyAuthorMixin,
                        CommentMixin, CommentFormMixin, UpdateView):
    def get_object(self, queryset=None):
        comment = get_object_or_404(Comment, id=self.kwargs['comment_id'])
        return comment

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.post.pk})


class CommentDeleteView(
    OnlyAuthorMixin,
    CommentMixin,
    CommentFormMixin,
    DeleteView
):
    def get_object(self):
        comment = get_object_or_404(Comment, id=self.kwargs['comment_id'])
        return comment

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.post.pk})


class ProfileMixin:
    model = User
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/profile.html'


class ProfileFormMixin:
    form_class = UserRegistrationForm


class ProfileDetailView(ProfileMixin, DetailView):
    context_object_name = "profile"
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comment'] = (
            self.object.comments.select_related('author')).all()
        posts = Post.objects.filter(author=self.object).select_related(
            'author',
            'location',
            'category'
        ).with_comment_count().order_by('-pub_date')

        context['page_obj'] = Paginator(posts, 10).get_page(
            self.request.GET.get('page'))
        return context


class ProfileUpdateView(

    OnlyAuthorMixin, LoginRequiredMixin, ProfileMixin,
    UpdateView
):
    context_object_name = 'profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    template_name = 'blog/user.html'
    login_url = reverse_lazy('login')
    form_class = UserEditForm

    def get_object(self):
        if not self.request.user.is_authenticated:
            return redirect(self.login_url)
        # Проверяем, совпадает ли профиль с пользователем
        username = self.kwargs.get('username')
        if not username or self.request.user.username != username:
            return redirect('blog:profile',
                            username=self.request.user.username)
        # Возвращаем текущего пользователя
        return self.request.user

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect(self.login_url)
        return redirect('blog:profile', username=self.request.user.username)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.request.user.username})

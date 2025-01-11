from django.shortcuts import get_object_or_404, render, redirect

from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from django.urls import reverse_lazy, reverse

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import Post, Category, Comment, User

from .forms import PostForm, CommentForm, UserRegistrationForm, UserEditForm


DEFAULT_POST_COUNT = 5
pagination_num = 10


class AuthorCheck:
    def test(self, obj, user):
        if hasattr(obj, 'author'):
            return obj.author == user
        return False


class ProfileCheck:
    def test(self, obj, user):
        if isinstance(obj, type(user)):
            return obj == user
        return False


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        obj = self.get_object()  # Получение объекта пользователя
        checks = [AuthorCheck(), ProfileCheck()]  # Список всех проверок
        # Проверяем каждую проверку
        for check in checks:
            if check.test(obj, self.request.user):
                return True
        # Если ни одна из проверок не прошла, доступ запрещен
        return False


class PostListView(ListView):
    model = Post
    paginate_by = pagination_num
    template_name = 'blog/index.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.apply_filters(
            with_published=True,
            with_comment_count=True,
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'post_id'

    def get_object(self):
        post_id = self.kwargs.get('post_id')

        if self.request.user.is_authenticated:
            post = get_object_or_404(Post, id=self.kwargs['post_id'])
            if post and post.author == self.request.user:
                return post

        filtered_posts = Post.objects.filter(
            id=post_id).apply_filters(with_published=True)
        post = get_object_or_404(filtered_posts, id=self.kwargs['post_id'])
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            context['form'] = CommentForm()
            context['comments'] = (
                self.object.comments.select_related('author')
            )
        else:
            context['form'] = CommentForm()
            context['comments'] = Comment.objects.none()
        return context


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    page_number = request.GET.get('page')

    page_obj = category.posts.all().apply_filters(
        with_published=True,
        with_comment_count=True,
        with_pagination=True,
        page_number=page_number,
        pagination_num=pagination_num)
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
    slug_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username})


class PostUpdateView(
    OnlyAuthorMixin,
    PostMixin,
    PostFormMixin,
    UpdateView
):
    slug_url_kwarg = 'post_id'
    slug_field = 'id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        super().form_valid(form)
        return redirect(self.get_success_url())

    def handle_no_permission(self):
        post_id = self.kwargs['post_id']
        return redirect('blog:post_detail', post_id=post_id)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class PostDeleteView(
    OnlyAuthorMixin,
    PostMixin,
    PostFormMixin, DeleteView
):
    slug_url_kwarg = 'post_id'
    slug_field = 'id'

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
    context_object_name = 'comments'

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return post.comments.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, id=self.kwargs['post_id'])
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


class CommentUpdateView(OnlyAuthorMixin,
                        CommentMixin, CommentFormMixin, UpdateView):
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class CommentDeleteView(
    OnlyAuthorMixin,
    CommentMixin,
    CommentFormMixin,
    DeleteView
):
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class ProfileMixin:
    model = User
    success_url = reverse_lazy('blog:index')
    template_name = 'blog/profile.html'


class ProfileFormMixin:
    form_class = UserRegistrationForm


class ProfileDetailView(ProfileMixin, DetailView):
    context_object_name = 'profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_object(self):
        username = self.kwargs.get('username')
        author = get_object_or_404(User, username=username)
        return author

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.object

        page_number = self.request.GET.get('page')

        if self.request.user.is_authenticated and author == self.request.user:
            posts = author.posts.all().apply_filters(
                with_comment_count=True,
                with_pagination=True,
                with_related=True,
                page_number=page_number,
                pagination_num=pagination_num
            )

        else:
            posts = author.posts.all().apply_filters(
                with_published=True,
                with_comment_count=True,
                with_pagination=True,
                with_related=True,
                page_number=page_number,
                pagination_num=pagination_num
            )

        if self.object:
            context['form'] = CommentForm()
            context['page_obj'] = posts
        return context


class ProfileUpdateView(

    OnlyAuthorMixin, LoginRequiredMixin, ProfileMixin,
    UpdateView
):
    context_object_name = 'profile'
    slug_field = 'username'
    template_name = 'blog/user.html'
    form_class = UserEditForm

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username})

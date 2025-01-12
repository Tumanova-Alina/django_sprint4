from django.core.paginator import Paginator
from django.utils import timezone
from django.db import models
from django.db.models import Count

PAGINATION_NUM = 10


class PostQuerySet(models.QuerySet):

    def apply_filters(
            self, with_published=True,
            with_related=True,
            with_comment_count=True
    ):
        posts = self

        if with_published:
            posts = posts.filter(
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True
            )

        if with_related:
            posts = posts.select_related(
                'category', 'author', 'location'
            )

        if with_comment_count:
            posts = posts.annotate(comment_count=Count('comments')
                                   ).order_by('-pub_date',)

        return posts


def paginate_posts(posts, request, pagination_num=PAGINATION_NUM):
    paginator = Paginator(posts, pagination_num)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)

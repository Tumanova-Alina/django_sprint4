from django.core.paginator import Paginator

from django.utils import timezone

from django.db import models

from django.db.models import Count


class PostQuerySet(models.QuerySet):

    def apply_filters(
            self, with_published=False,
            with_related=False,
            with_comment_count=False,
            with_pagination=False,
            page_number=None,
            pagination_num=None
    ):
        queryset = self

        if with_published:
            queryset = queryset.filter(
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True
            )

        if with_related:
            queryset = queryset.select_related(
                'category', 'author', 'location'
            )

        if with_comment_count:
            queryset = queryset.annotate(comment_count=Count('comments'))

        if with_pagination:
            paginator = Paginator(queryset, pagination_num)
            queryset = paginator.get_page(page_number)

        return queryset

    class Meta:
        ordering = ('-pub_date',)

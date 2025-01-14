from django.utils import timezone
from django.db import models
from django.db.models import Count


class PostQuerySet(models.QuerySet):

    def apply_filters(
            self, with_published=True,
    ):
        posts = self

        if with_published:
            posts = posts.filter(
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True
            )

        posts = posts.with_related().with_comment_count()
        return posts

    def with_related(self):
        return self.select_related(
            'category', 'author', 'location'
        )

    def with_comment_count(self):
        return self.annotate(comment_count=Count('comments')
                             ).order_by('-pub_date',)

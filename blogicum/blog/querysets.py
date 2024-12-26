from django.utils import timezone


def published_posts(queryset):
    return queryset.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )


def select_related_posts(queryset):
    return queryset.select_related('category')

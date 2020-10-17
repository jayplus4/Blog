from django import template
from django.db.models import Count

from ..models import Post

register = template.Library()

@register.simple_tag
def total_posts():
	return Post.published.count()

@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
	latest_posts = Post.published.order_by("-publish")[:count]
	return {'latest_posts': latest_posts}

@register.inclusion_tag('blog/post/top_posts.html')
def show_top_stories(count=5):
	top_stories = Post.published.annotate(comments_count=Count('comments')).order_by('-comments_count', '-publish')[:count]
	return {"top_stories": top_stories}
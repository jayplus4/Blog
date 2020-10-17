from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.db.models import Count

from taggit.models import Tag

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, SearchForm


def post_list(request, tag_slug=None):
	posts = Post.published.all()
	page = request.GET.get('page')
	tag = None

	if tag_slug:
		tag = get_object_or_404(Tag, slug=tag_slug)
		posts = posts.filter(tags__in=[tag])


	paginator = Paginator(posts, 8)	# 1 posts in each page

	try:
		posts = paginator.page(page)
	except PageNotAnInteger:
		# if page is not an integer deliver first page
		posts = paginator.page(1)
	except EmptyPage:
		# If page is out of range deliver last page of results
		posts = paginator.page(paginator.num_pages)

	return render(request, "blog/post/list.html", {"posts": posts,
												   "tag": tag})

def post_detail(request, year, month, day, slug):
	post = get_object_or_404(Post, slug=slug, 
								   status="published", 
								   publish__year=year, 
								   publish__month=month, 
								   publish__day=day)
	# List of active comments for this post
	comments = post.comments.filter(active=True)

	# List of similar posts
	post_tags_ids = post.tags.values_list('id', flat=True)
	similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)

	similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')

	new_comment = None
	if request.method == "POST":
		# A Comment was posted
		comment_form = CommentForm(request.POST)
		if comment_form.is_valid():
			# Create comment object but don't save to database yet
			new_comment = comment_form.save(commit=False)
			# Assign the current post to the comment
			new_comment.post = post
			# save the comment to the database
			new_comment.save()
	else:
		comment_form = CommentForm()

	return render(request, "blog/post/detail.html", {"post": post,
													 "comments": comments,
													 "new_comment": new_comment,
													 "comment_form": comment_form,
													 'similar_posts': similar_posts})

def post_share(request, post_id):
	post = get_object_or_404(Post, id=post_id, status="published")
	sent = False

	if request.method == "POST":
		# Form was submitted
		form = EmailPostForm(request.POST)
		if form.is_valid():
			# Form fields passed validation
			cd = form.cleaned_data
			
			
			post_url = request.build_absolute_uri(post.get_absolute_url())
			print(post_url)
			subject = f"{cd['name']} ({cd['email']}) recommeds you reading {post.title}"
			message = f"Read '{post.title}' at {post_url}\n\n{cd['name']}'s comments: {cd['comments']}"
			send_mail(subject, message, 'admin@myblog.com', [cd['to']])
			sent = True
	else:
		form = EmailPostForm()

	return render(request, "blog/post/share.html", {'email_form': form,
													'post': post,
													'sent': sent})

def post_search(request):
	form = SearchForm()
	print("Testing".center(50, "."))
	print(request.GET)
	query = request.GET.get("query", None)
	results = []
	
	if query:
		form = SearchForm(request.GET)
		if form.is_valid():
			query = form.cleaned_data['query']
			results = Post.published.filter(body__contains=query)
	return render(request, "blog/post/search.html", {'form': form, 
													 'query': query, 
													 'results': results})


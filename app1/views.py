
from django.shortcuts import render, redirect
from .forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm, LikeCommForm
from .models import UserModel, SessionToken, PostModel, LikeModel, CommentModel, LikeComm
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
from django.utils import timezone
from project3.settings import *
from imgurpython import ImgurClient
from django.core.mail import send_mail

def signup_view(request):
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			name = form.cleaned_data['name']
			email = form.cleaned_data['email']
			password = form.cleaned_data['password']
			#saving data to DB
			user = UserModel(name=name, password=make_password(password), email=email, username=username)
			user.save()
			subject = 'Welcome to Social Kids'
			message = 'Thanks for joining Social Kids, the only place where kids can have fun online'
			from_email = EMAIL_HOST_USER
			to_email = [user.email]
			send_mail(subject, message, from_email, to_email, fail_silently=True)
			return render(request, 'success.html')
			return redirect('login/')
	else:
		form = SignUpForm()
	return render(request, 'index.html', {'form' : form})


def login_view(request):
	response_data = {}
	if request.method == "POST":
		form = LoginForm(request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = UserModel.objects.filter(username=username).first()

			if user:
				if check_password(password, user.password):
					token = SessionToken(user=user)
					token.create_token()
					token.save()
					response = redirect("/feed")
					response.set_cookie(key='session_token', value=token.session_token)
					return response
				else:
					response_data['message'] = 'Incorrect Password! Please try again!'
	elif request.method == 'GET':
		form = LoginForm()

	response_data['form'] = form
	return render(request, 'login.html', response_data)


def post_view(request):
	user = check_validation(request)

	if user:
		if request.method == 'POST':
			form = PostForm(request.POST, request.FILES)
			if form.is_valid():
				image = form.cleaned_data.get('image')
				caption = form.cleaned_data.get('caption')
				post = PostModel(user=user, image=image, caption=caption)
				post.save()

				path = str(post.image.url)

				client = ImgurClient("618bd3e5af61044", "a1e66dde5bb5b602df49616207d8c85e790e692f")
				post.image_url = client.upload_from_path(path, config=None, anon=True)['link']
				post.save()
				return redirect('/feed/')

		else:
			form = PostForm()
		return render(request, 'post.html', {'form' : form})
	else:
		return redirect('/login/')


def feed_view(request):
	user = check_validation(request)
	if user:
		posts = PostModel.objects.all().order_by('created_on')
		
		for post in posts:
			existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
			if existing_like:
				post.has_liked = True
		return render(request, 'feed.html', {'posts': posts})
	else:

		return redirect('/login/')
	  
def like_view(request):
	user = check_validation(request)
	if user and request.method == 'POST':
		form = LikeForm(request.POST)
		if form.is_valid():
			post_id = form.cleaned_data.get('post').id
			existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()
			if not existing_like:
				LikeModel.objects.create(post_id=post_id, user=user)
				poster = PostModel.objects.filter(id=post_id).first()
				subject = "Your photo was liked"
				message = "Your photo was liked by " + user.username
				from_email = EMAIL_HOST_USER
				to_email = [poster.user.email]
				send_mail(subject, message, from_email, to_email, fail_silently=True)
			else:
				existing_like.delete()
				poster = PostModel.objects.filter(id=post_id).first()
				subject = "Your photo was unliked"
				message = "Your photo was unliked by " + user.username
				from_email = EMAIL_HOST_USER
				to_email = [poster.user.email]
				send_mail(subject, message, from_email, to_email, fail_silently=True)
			return redirect('/feed/')
	else:
		return redirect('/login/')

def comment_view(request):
	user = check_validation(request)
	if user and request.method == 'POST':
		form = CommentForm(request.POST)
		if form.is_valid():
			post_id = form.cleaned_data.get('post').id
			comment_text = form.cleaned_data.get('comment_text')
			comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
			comment.save()
			poster = PostModel.objects.filter(id=post_id).first()
			subject = "Comment on your photo"
			message = str(user.username) + " commented on your photo " + comment_text
			from_email = EMAIL_HOST_USER
			to_email = [poster.user.email]
			send_mail(subject, message, from_email, to_email, fail_silently=True)
			return redirect('/feed/')
		else:
			return redirect('/feed/')
	else:
		return redirect('/login')
	  
	  
#For validating the session
def check_validation(request):
	if request.COOKIES.get('session_token'):
		session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
		if session:
			time_to_live = session.created_on + timedelta(days=1)
			if time_to_live > timezone.now():
				return session.user
	else:
		return None
def log_out(request):
	if request.COOKIES.get('session_token'):
		response = redirect("/feed")
		response.set_cookie(key='session_token', value=None)
		return response
	else:
		return None
def search(request):
	if "q" in request.GET:
		q = request.GET["q"]
		posts = PostModel.objects.filter(user__username__icontains=q)
		return render(request, "feed.html", {"posts": posts, "query": q})
	return render(request, "feed.html")

def like_comm(request):
	user = check_validation(request)
	if user and request.method == 'POST':
		form = LikeCommForm(request.POST)
		if form.is_valid():
			comment_id = form.cleaned_data.get('comment').id
			existing_like = LikeComm.objects.filter(comment_id=comment_id, user=user).first()
			if not existing_like:
				LikeComm.objects.create(comment_id=comment_id, user=user,)
			else:
				existing_like.delete()
			return redirect('/feed/')
	else:
		return redirect('/login/')
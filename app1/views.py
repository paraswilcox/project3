
from django.shortcuts import render, redirect
from .forms import SignUpForm, LoginForm, PostForm, LikeForm, CommentForm, LikeCommForm
from .models import UserModel, SessionToken, PostModel, LikeModel, CommentModel, LikeComm
from django.contrib.auth.hashers import make_password, check_password
from datetime import timedelta
from django.utils import timezone
from project3.settings import *
from imgurpython import ImgurClient
from django.core.mail import send_mail

# this the view defined for handling sign up.Only Post method is valid
# a user must submit a valid form to get signed up. If succesful user will be redirected to 
# log in page via a success page
# username > 4 characters
# password > 5 characters
# name not empty
# a valid email
# user will be sent a welcome email on the emal address specified
# it uses django send_mail fxn
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

# This view handles the login.html
# the user with only valid credentials and requesting with post method can log in
# a session is created upon log in and user is redirected to feeds page
# invalid username/password combination would result in back to the log in page
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

# if user is logged in then only it can post(tested by check_validation fxn)
# method should be post method otherwise he/she would be redirected to log in page
# it makes use of form to upload image and its caption
# the image is stored locally first then
# using imgur api the image is stored online 
# it requires client id and secret to do so
# after posting the user is directed to his/her feeds page
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

# this view handles the feeds a user sees 
# only logged in user can see feeds otherwise asked to login
# which is handled by check_validation fxn
# a post model is created which lists all the posts in the database
# then likes are rendered for these posts which sets a posts has_liked attribute to True
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
# this is the like view
# this view makes the fxnality of liking a post 
# it does so by making  a like model attaching it with a usermodel and postmodel
# if a post has existing like then clicking the like buton will unlike it and vice versa
# in both the cases the owner of the post gets email notifying him/her of the event
# the device must be connected to internet to make this happen
# otherwise the mail will not be sent. 
# As fail_silently attribute is set to true any error in send_mail fxn will not
# halt the website(to diagonose set it to False)  	  
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
# This view makes commenting on a post happen
# this does so by making a comment model and attaching it with a usermodel and a post model
# the post id is the primary key of the post in this case the foreign key
# as above the user of the post will be notified if someone commented on the post via email
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
	  
	  
# For validating the session
# if a user is legitimate then he/she will have the session token
# the session is valid for 24 hrs
def check_validation(request):
	if request.COOKIES.get('session_token'):
		session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
		if session:
			time_to_live = session.created_on + timedelta(days=1)
			if time_to_live > timezone.now():
				return session.user
	else:
		return None
# This fxn logs out a user
# It Does so by making the token value = None
# the user is redirected to logout page
# if accidently or by deliberately a user goes back
# then any action will require him/her to log in again
def log_out(request):
	if request.COOKIES.get('session_token'):
		response = redirect("/feed")
		response.set_cookie(key='session_token', value=None)
		return response
	else:
		return None
# This view adds fxnality of filtering posts by username
# it does so by accepting a query
# and if the query contains anything like a username
# it filters the post which have foreign key user with that username
# the user then is redirected to feeds page
def search(request):
	if "q" in request.GET:
		q = request.GET["q"]
		posts = PostModel.objects.filter(user__username__icontains=q)
		return render(request, "feed.html", {"posts": posts, "query": q})
	return render(request, "feed.html")
# It is the view which handles the fxnality of upvoting n a comment
# It does so by making fxnality same as of the the like view 
# except the fact that it does so on a comment
# it attaches the like with a comment with a comment id (primary key generated by django)
# if a user has not upvoted then it adds a upvote 
# and if already upvoted then removes the vote
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
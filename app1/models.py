from django.db import models
import uuid
# a user model with following fields
# it will store the user details
class UserModel(models.Model):
	email = models.EmailField(max_length=254, blank=False, unique=True)
	name = models.CharField(max_length=120, blank=False)
	username = models.CharField(max_length=120, blank=False)
	password = models.CharField(max_length=40)
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)
# A session model
# it will store the session details with user field 
# a foreign key which is the above defined model
# it has a method create_token which assigns an unique value to session token
class SessionToken(models.Model):
	user = models.ForeignKey(UserModel)
	session_token = models.CharField(max_length=255)
	last_request_on = models.DateTimeField(auto_now=True)
	created_on = models.DateTimeField(auto_now_add=True)
	is_valid = models.BooleanField(default=True)

	def create_token(self):
		self.session_token = uuid.uuid4()
# This is used to store post in database
# user is above defined usermodel
# image is the image to post
# image url is the url of image uploaded on imgur
# an attribute has_liked is false by default
# created on and updatd on are datefields 
# which corresponds to the creation and updation of the post
# it has two properties (i)like_count which is the length of likemodels asociated with the post
# (ii)comments which is the comments on the post
class PostModel(models.Model):
	user = models.ForeignKey(UserModel)
	image = models.FileField(upload_to='user_images')
	image_url = models.CharField(max_length=255)
	caption = models.CharField(max_length=240)
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)
	has_liked = False


	@property
	def like_count(self):
		return len(LikeModel.objects.filter(post=self))

	@property
	def comments(self):
		return CommentModel.objects.filter(post=self).order_by('-created_on')
# like model is used to store a like in database
# it is just a count hence need to be only associated with the post and the user
# created_on updated_on are another datetime fields 
class LikeModel(models.Model):
	user = models.ForeignKey(UserModel)
	post = models.ForeignKey(PostModel)
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)
# just as like model it needs to be associated with the post and user
# but like is just a count and comment has text associated with it
# and comment has attribute upvoted to show the upvotees on it
# by default it is set to False
# it has propery upvote which is the count of upvotes associated with it
class CommentModel(models.Model):
	user = models.ForeignKey(UserModel)
	post = models.ForeignKey(PostModel)
	comment_text = models.CharField(max_length=555)
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)
	upvoted = False
	
	@property
	def upvote(self):
		return len(LikeComm.objects.filter(comment=self))
# it the like model for the comments to store upvotes associated with the comments
# it is just a count so only needs to be associated with the user and post
# and no attribute of own
class LikeComm(models.Model):
	user = models.ForeignKey(UserModel)
	comment = models.ForeignKey(CommentModel)
		
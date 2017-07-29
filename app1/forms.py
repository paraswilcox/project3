from django import forms
from .models import UserModel, PostModel, LikeModel, CommentModel, LikeComm
# it is the signup form which extends the django forms class
class SignUpForm(forms.ModelForm,):
	class Meta:
		model = UserModel
		fields=['email','username','name','password']
# it is the log in form which extends the django forms class
class LoginForm(forms.ModelForm):
	class Meta:
		model = UserModel
		fields = ['username', 'password']
# it is the post form form which extends the django forms class
class PostForm(forms.ModelForm):
	class Meta:
		model = PostModel
		fields=['image', 'caption']
# it is the like form which extends the django forms class
class LikeForm(forms.ModelForm):
	class Meta:
		model = LikeModel
		fields=['post']

# it is the comment form which extends the django forms class
class CommentForm(forms.ModelForm):
	class Meta:
		model = CommentModel
		fields = ['comment_text', 'post']
# it is the like comment form which extends the django forms class
class LikeCommForm(forms.ModelForm):
	class Meta:
		model = LikeComm
		fields = ['comment']
			
from django import forms
from .models import UserModel, PostModel, LikeModel, CommentModel
class SignUpForm(forms.ModelForm,):
	def clean_username(self):
		username = self.cleaned_data["username"]
		if len(username) < 4 :
			raise forms.ValidationError("username must be less than 4 characters")
		if not username:
			raise forms.ValidationError("username cannot be empty")
	def clean_name(self):
		name = self.cleaned_data["name"]
		if not name:
			raise forms.ValidationError("name cannot be empty")	
	def clean_email(self):
		email = self.cleaned_data["email"]
		if not email:
			raise forms.ValidationError("email cannot be empty")
	class Meta:
		model = UserModel
		fields=['email','username','name','password']

class LoginForm(forms.ModelForm):
	class Meta:
		model = UserModel
		fields = ['username', 'password']

class PostForm(forms.ModelForm):
	class Meta:
		model = PostModel
		fields=['image', 'caption']

class LikeForm(forms.ModelForm):
	class Meta:
		model = LikeModel
		fields=['post']


class CommentForm(forms.ModelForm):
	class Meta:
		model = CommentModel
		fields = ['comment_text', 'post']
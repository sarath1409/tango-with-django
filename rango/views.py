# password123
from django.shortcuts import render
from rango.models import Category,Page
# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
import requests


def decode_url(url_string):
	return url_string.replace('_',' ')

def encode_url(name_string):
	return name_string.replace(' ','_')

def index(request):
	request.session.set_test_cookie()
	context = RequestContext(request)

	category_list = Category.objects.order_by('-likes')[:5]
	context_dict = {'categories': category_list}
	for category in category_list:
		category.url = encode_url(category.name)

	view_list = Page.objects.order_by('-views')[:5]
	context_dict['page_views'] = view_list
	cat_list = get_category_list()
	context_dict['cat_list'] = cat_list
	# response = render(request,'rango/index.html', context_dict, context)
	# visits = int(request.COOKIES.get('visits', '1'))
	# if 'last_visit' in request.COOKIES.keys():
	# 	print('Entered')
	# 	last_visit = request.COOKIES['last_visit']
	# 	last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
	# 	if (datetime.now() - last_visit_time).days > 0:
	# 		response.set_cookie('visits', visits+1)
	# 		response.set_cookie('last_visit', datetime.now())
	# else:
	# 	response.set_cookie('last_visit', datetime.now())
	# 	response.set_cookie('visits', visits)
	# return response
	if request.session.get('last_visit'):
		last_visit_time = request.session.get('last_visit')
		visits = request.session.get('visits', 0)
		if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
			request.session['visits'] = visits + 1
			request.session['last_visit'] = str(datetime.now())
	else:
		request.session['last_visit'] = str(datetime.now())
		request.session['visits'] = 1

	return render(request,'rango/index.html', context_dict, context)
	text = '<p>Rango Says: Here is the about page.</p><a href="/rango/about">About</a>'
	return HttpResponse(text)

def about(request):
	context = RequestContext(request)
	context_dict = {}
	cat_list = get_category_list()
	context_dict['cat_list'] = cat_list
	visits = int(request.COOKIES.get('visits', '0'))
	response = render(request,'rango/about.html', context_dict, context)
	if 'last_visit' in request.COOKIES.keys():
		print('Entered')
		last_visit = request.COOKIES['last_visit']
		last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
		visits = visits+1
		# response.set_cookie('visits', visits)
		# if (datetime.now() - last_visit_time).days > 0:
		# 	response.set_cookie('visits', visits)
		response.set_cookie('last_visit', datetime.now())
	else:
		response.set_cookie('last_visit', datetime.now())
		response.set_cookie('visits', visits)
	
	context_dict['visit_count'] = visits
	response = render(request,'rango/about.html', context_dict, context)

	return response

	# return render(request,'rango/about.html',context_dict,context)

	# text = '<p>Hello</p><a href="/rango/">Home</a>'
	# return HttpResponse(text)

def category(request, category_name_url):
	context = RequestContext(request)
	category_name = decode_url(category_name_url)
	context_dict = {'category_name': category_name}
	cat_list = get_category_list()
	context_dict['cat_list'] = cat_list
	try:
		category = Category.objects.get(name=category_name)
		pages = Page.objects.filter(category=category)
		context_dict['pages'] = pages
		context_dict['category'] = category
		context_dict['category_name_url'] = category_name_url
	except Category.DoesNotExist:
		pass


	try:
		category = Category.objects.get(name__iexact=category_name)
		context_dict['category'] = category
		pages = Page.objects.filter(category=category).order_by('-views')
		context_dict['pages'] = pages
	except Category.DoesNotExist:
		pass
	if request.method == 'POST':
		query = request.POST.get('query',False) #.strip()
		if query:
			result_list = run_query(query)
			context_dict['result_list'] = result_list
	return render(request,'rango/category.html', context_dict, context)

def page(request, page_name_url):
	context = RequestContext(request)
	page_name = decode_url(page_name_url)
	context_dict = {}
	cat_list = get_category_list()
	context_dict['cat_list'] = cat_list
	try:
		pages = Page.objects.get(title=page_name)
		context_dict['pages'] = pages
	except Page.DoesNotExist:
		pass
	return render(request,'rango/page.html', context_dict, context)

from rango.forms import CategoryForm
def add_category(request):
	context_dict = {}
	context = RequestContext(request)
	cat_list = get_category_list()
	context_dict['cat_list'] = cat_list
	if request.method == 'POST':
		form = CategoryForm(request.POST)
		if form.is_valid():
			form.save(commit=True)
			return index(request)
		else:
			print (form.errors)
	else:
		form = CategoryForm()
	context_dict['form'] = form
	return render(request,'rango/add_category.html', context_dict, context)

from rango.forms import PageForm
def add_page(request, category_name_url):
	context = RequestContext(request)
	category_name = decode_url(category_name_url)
	if request.method == 'POST':
		form = PageForm(request.POST)
		if form.is_valid():
			page = form.save(commit=False)
			cat = Category.objects.get(name=category_name)
			page.category = cat
			page.views = 0
			page.save()
			return category(request, category_name_url)
		else:
			print (form.errors)
	else:
		form = PageForm()
	context_dict = {'category_name_url': category_name_url,'category_name': category_name, 'form': form}
	cat_list = get_category_list()
	context_dict['cat_list'] = cat_list
	return render(request, 'rango/add_page.html',context_dict,context)

from rango.forms import UserForm, UserProfileForm
def register(request):
	if request.session.test_cookie_worked():
		print(">>>> TEST COOKIE WORKED!")
		request.session.delete_test_cookie()
	context = RequestContext(request)
	registered = False
	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)
		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			user.set_password(user.password)
			user.save()
			profile = profile_form.save(commit=False)
			profile.user = user
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
			profile.save()
			registered = True
		else:
			print (user_form.errors, profile_form.errors)
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()
	context_dict = {'user_form': user_form, 'profile_form': profile_form, 'registered':registered}
	cat_list = get_category_list()
	context_dict['cat_list'] = cat_list

	return render(request,'rango/register.html',context_dict, context)

def user_login(request):

	context = RequestContext(request)
	context_dict = {}
	cat_list = get_category_list()
	context_dict['cat_list'] = cat_list
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect('/rango/')
			else:
				return HttpResponse("Your Rango account is disabled.")
		else:
			print("Invalid login details: {0}, {1}".format(username,password))
			return HttpResponse("Invalid login details supplied.")
	else:
		return render(request,'rango/login.html', context_dict, context)

# def some_view(request):
# 	if not request.user.is_authenticated():
# 		return HttpResponse("You are logged in.")
# 	else:
# 		return HttpResponse("You are not logged in.")

@login_required
def restricted(request):
	return HttpResponse("Since you're logged in, you can see this text!")

from django.contrib.auth import logout

@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect('/rango/')

from rango.bing_search import run_query	
def generic_search(request):
	context = RequestContext(request)
	context_dict = {}
	cat_list = get_category_list()
	context_dict['cat_list'] = cat_list
	result_list = []
	if (request.method == 'POST'):
		query = request.POST['query'].strip()
	if query:
		# Run our Bing function to get the results list!
		result_list = run_query(query)
		context_dict['result_list'] = result_list
		return render(request,'rango/generic_search.html', context_dict,context)

def get_category_list():
	cat_list = Category.objects.all()
	for cat in cat_list:
		cat.url = encode_url(cat.name)
	return cat_list

from django.contrib.auth.models import User
@login_required
def profile(request):
	context = RequestContext(request)
	cat_list = get_category_list()
	context_dict = {'cat_list': cat_list}
	u = User.objects.get(username=request.user)
	try:
		up = UserProfile.objects.get(user=u)
	except:
		up = None
		context_dict['user'] = u
		context_dict['userprofile'] = up
	return render_to_response('rango/profile.html', context_dict, context)

def track_url(request):
	context = RequestContext(request)
	page_id = None
	url = '/rango/'
	if request.method == 'GET':
		if 'page_id' in request.GET:
			page_id = request.GET['page_id']
			try:
				page = Page.objects.get(id=page_id)
				page.views = page.views + 1
				page.save()
				url = page.url
			except:
				pass
	return redirect(url)

@login_required
def like_category(request):
	context = RequestContext(request)
	cat_id = None
	if request.method == 'GET':
		cat_id = request.GET['category_id']
		likes = 0
	if cat_id:
		category = Category.objects.get(id=int(cat_id))
		if category:
			likes = category.likes + 1
			category.likes = likes
			category.save()
	return HttpResponse(likes)
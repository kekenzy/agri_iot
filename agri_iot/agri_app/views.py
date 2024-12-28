from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.http import Http404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_object_or_404, get_list_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# from famischeapp.model.dao.user import UserDao
# from famischeapp.model.dao.family import FamilyDao
# from famischeapp.model.form.user_form import UserInfo
# from famischeapp.model.form.family_form import FamilyInfo
# from famischeapp.model.form.login_user_form import UserForm, UserProfileForm, LoginForm

# Create your views here.

def index(request):
    return render(request, "index.html", context={"title": "Hello!!"})

# @login_required
# def register(request):
#     user_form = UserForm(request.POST or None)
#     user_profile_form = UserProfileForm(request.POST or None, request.FILES or None)
#     if user_form.is_valid() and user_profile_form.is_valid():
#         user = user_form.save(commit=False)
#         try:
#             validate_password(user_form.cleaned_data.get('password'), user)
#         except ValidationError as e:
#             user_form.add_error('password', e)
#             return render(request, "user/user_form.html", context={
#                 "user_form": user_form,
#                 "profile_form": user_profile_form, 
#             })
            
#         user.set_password(user.password)
#         user.save()
#         profile = user_profile_form.save(commit=False)
#         profile.user = user
#         profile.save()

#     return render(request, "user/user_form.html", context={
#             "user_form": user_form,
#             "profile_form": user_profile_form, 
#         })

# def home2(request, first_name):
#     name = first_name
#     fruits = ["Apple", "Orange", "Lemon"]
#     my_info = {"name": "Kenji", "age": 45}
#     status = 10
#     return render(
#         request,
#         "home2.html",
#         context={
#             "my_name": name,
#             "fruits": fruits,
#             "my_info": my_info,
#             "status": status,
#             },
#    )
# def home(request):
#     return render(request, "home.html")

# def families(request):
#     # family_list = get_list_or_404(FamilyDao, pk__gt=10)
#     family_list = FamilyDao.get_all_family()
#     return render(request, "families.html", context={"families": family_list})

# def family(request, id):
#     if id == 0:
#         raise Http404

#     family = get_object_or_404(FamilyDao, pk=id)
#     # try:
#     #     family = get_object_or_404(FamilyDao, pk=id)
#     #     # family = FamilyDao.get_family_by_id(id)
#     # except Exception as e:
#     #     url = reverse("famischeapp:families")
#     #     return HttpResponseRedirect(url)
#     #     # return redirect("famischeapp:families")

#     user_list = list()
#     try:
#         user_list = list(UserDao.get_user_by_family(family.id))
#     except Exception as e:
#         print(e)
#     # print(user_list)
#     return render(request, "family_detail.html", context={"family": family, "user_list": user_list})

# def sample1(request):
#     user_list = UserDao.get_all_user()
#     return render(request, "sample1.html", {"user_list": user_list})


# def user_page(request, user_name, number):
#     return HttpResponse(f"<h1>{user_name} is {number} years old</h1>")

# def to_google(request):
#     return redirect('https://www.google.com')

# def family_form(request):
#     if request.method == 'POST':
#         form = FamilyInfo(request.POST)
#         if form.is_valid():
#             FamilyDao.add_family(form.cleaned_data['name'])
#             # print(
#             #     f"fir'st_name: {form.cleaned_data['name']}"
#             # )
#             url = reverse("famischeapp:families")
#             return HttpResponseRedirect(url)
#     else:
#         form = FamilyInfo()
#     return render(request, "family_form.html", context={'family_form': form})

# def user_form(request, id):
#     print('user_form')
#     family = FamilyDao.get_family_by_id(id)
#     if request.method == 'POST':
#         form = UserInfo(request.POST)
#         if form.is_valid():
#             data = form.cleaned_data
#             print('xxx')
#             UserDao.add_user(data['first_name'], family, data['email'])
#             # print(
#             #     f"first_name: {form.cleaned_data['first_name']}, last_name {form.cleaned_data['last_name']}"
#             # )
#             url = reverse("famischeapp:family", kwargs={"id": id})
#             return HttpResponseRedirect(url)
#     else:
#         # inital_values={'first_name': 'mt', 'last_name': family.name, 'email': 'dd'}
#         form = UserInfo()
#     return render(request, "user_form.html", context={'user_form': form, 'family_name': family.name})

# class Country:
#     def __init__(self, name, population, capital) -> None:
#         self.name = name
#         self.population = population
#         self. capital = capital

# def sample2(request):
#     country = Country('Japan', 200000, 'Tokyo')
#     return render(request, 'sample2.html', context={
#         'country': country
#     })

# def page_not_found(request, exception):
#     return render(request, '404.html', status=404)

# def server_error(request):
#     print("server error")
#     return render(request, '500.html', status=500)

# def user_login(request):
#     login_form = LoginForm(request.POST or None)
#     if login_form.is_valid():
#         username = login_form.cleaned_data.get('username')
#         password = login_form.cleaned_data.get('password')
#         print(username)
#         print(password)
#         user = authenticate(username=username, password=password)
#         if user:
       
#             if user.is_active:
#                 login(request, user)
#                 return redirect('famischeapp:home')
#             else:
#                 return HttpResponse('アカウントがアクティブではないです')
#         else:
#             return HttpResponse('ユーザもしくはパスワードが間違っています')

#     return render(request, 'user/login.html', context={
#         'login_form': login_form
#     })

# @login_required
# def user_logout(request):
#     logout(request)
#     return redirect('famischeapp:user_login')
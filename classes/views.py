from django.shortcuts import render, redirect 
from django.contrib import messages 
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse
from .models import Classroom, Student
from .forms import ClassroomForm, UserRegister, UserLogIn, StudentForm

def classroom_list(request):
	classrooms = Classroom.objects.all()
	context = {
		"classrooms": classrooms,
	}
	return render(request, 'classroom_list.html', context)


def classroom_detail(request, classroom_id):
	classroom = Classroom.objects.get(id=classroom_id)
	students = Student.objects.filter(classroom = classroom).order_by('name', '-exam_grade')
	context = {
		"classroom": classroom,
		"students": students,
	}
	return render(request, 'classroom_detail.html', context)


def classroom_create(request):
	if request.user.is_authenticated:
		form = ClassroomForm()
		if request.method == "POST":
			form = ClassroomForm(request.POST, request.FILES or None)
			if form.is_valid():
				classroom = form.save(commit=False)
				classroom.teacher = request.user
				classroom.save()
				messages.success(request, "Successfully Created!")
				return redirect('classroom-list')
			print (form.errors)
		context = {
		"form": form,
		}
	else:
		return redirect('user-login')
	return render(request, 'create_classroom.html', context)


def classroom_update(request, classroom_id):
	classroom = Classroom.objects.get(id=classroom_id)
	form = ClassroomForm(instance=classroom)
	if request.method == "POST":
		form = ClassroomForm(request.POST, request.FILES or None, instance=classroom)
		if form.is_valid():
			form.save()
			messages.success(request, "Successfully Edited!")
			return redirect('classroom-list')
		print (form.errors)
	context = {
	"form": form,
	"classroom": classroom,
	}
	return render(request, 'update_classroom.html', context)


def classroom_delete(request, classroom_id):
	classroom = Classroom.objects.get(id=classroom_id)
	if not (classroom.teacher == request.user or request.user.is_staff):
		return HttpResponse("<h1> YOU HAVE NO ACCESS </h1>")
	else:
		Classroom.objects.get(id=classroom_id).delete()
		messages.success(request, "Successfully Deleted!")
		return redirect('classroom-list')

def user_register(request):
	form = UserRegister()
	if request.method == "POST":
		form = UserRegister(request.POST)
		if form.is_valid():
			user = form.save(commit=False)

			user.set_password(user.password)
			user.save()

			login(request, user)
			return redirect("classroom-list")
	context = {
	"form" : form,
	}

	return render(request, 'user_register.html' ,context)

def user_login(request):
	form=UserLogIn()
	if request.method == 'POST':
		form = UserLogIn(request.POST)
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']

			auth_user = authenticate(username=username, password=password)
			if auth_user is not None:
				login(request, auth_user)
				return redirect('classroom-list')

	context = {
		"form":form
	}
	return render(request, 'login.html', context)

def user_logout(request):
    logout(request)
    return redirect('user-login')

def student_create(request, classroom_id):
	classroom = Classroom.objects.get(id=classroom_id)
	if not (classroom.teacher == request.user or request.user.is_staff):
		return HttpResponse("<h1> YOU HAVE NO ACCESS </h1>")
	else:
		form = StudentForm()
		classroom = Classroom.objects.get(id=classroom_id)
		if request.method == "POST":
			form = StudentForm(request.POST)
			if form.is_valid():
				student = form.save(commit=False)
				student.classroom = classroom
				student.save()
				return redirect ('classroom-detail', classroom_id)
		context = {
			"form": form, 
			"classroom" : classroom
		}
		return render(request, 'student_add.html', context)

def student_delete(request, classroom_id, student_id):
	student = Student.objects.get(id=student_id)
	student.delete()
	return redirect('classroom-detail', classroom_id)

def student_update(request, classroom_id, student_id):
	classroom = Classroom.objects.get(id=classroom_id)
	if not (classroom.teacher == request.user or request.user.is_staff):
		return HttpResponse("<h1> YOU HAVE NO ACCESS </h1>")
	else:
		student = Student.objects.get(id=student_id)
		form = StudentForm(instance=student)
		if request.method == "POST":
			form = StudentForm(request.POST, request.FILES, instance = student)
			if form.is_valid():
				form.save()
				return redirect('classroom-detail', classroom_id)
		context = {
			"form": form,
			"student": student,
			"classroom": classroom
		}
		return render(request, "update_student.html", context)
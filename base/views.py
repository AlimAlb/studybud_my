from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.models import User
from .models import Room, Topic, Telegram  
from .forms import RoomForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
#keygen func
import uuid

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home') 

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username,
                            password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()
    key = str(uuid.uuid4())
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            Telegram.objects.create(user = user,
            key = key,
            authorised_flag = False
            )

            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')

    return render(request, 'base/login_register.html', {'form': form})



def home(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    rooms = None
    my_stocks_count = Room.objects.filter(participants = request.user).count()
    if q == "-1":
        rooms = Room.objects.filter(participants = request.user)
    else:
        rooms = Room.objects.filter(
            Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )
    key = None
    if(request.user.is_authenticated):
        key = Telegram.objects.get(user = request.user)
    
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms': rooms, 'topics': topics,
               "room_counter": room_count, 'room_messages': room_messages,
               'key': key.key,
                "my_stocks_count": my_stocks_count
               }
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    context = {"room": room, 'room_messages': room_messages, 'participants':participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms,
               'room_messages':room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)

# Create your views here.
@login_required(login_url='login')
def add_stock(request, pk):
    room = Room.objects.get(id=pk)
    room.participants.add(request.user)
    return redirect('home')


@login_required(login_url='login')
def delete_stock(request, pk):  
    room = Room.objects.get(id=pk)
    room.participants.remove(request.user)
    return redirect('home')


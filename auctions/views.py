from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max
from .models import *
from django.shortcuts import redirect

def get_bid_data(objects_list):
    bid_data=[]
    for objects in objects_list:
        try:
            bid_data_temp=bids.objects.filter(placed_on=objects).aggregate(Max('bid'))["bid__max"]
        except bids.DoesNotExist:
            bid_data_temp=None
        if bid_data_temp is None:
            bid_data_temp=objects.primary_bid
        bid_data+=[bid_data_temp]
    return bid_data

def index(request):
    
    bids_data=get_bid_data(active_list.objects.filter(status=True))
    if request.user.is_authenticated: 
        watchlist_list=request.user.watchlists.all()
    else:
       watchlist_list=None
    
    return render(request, "auctions/index.html",{
            "active_lists":active_list.objects.filter(status=True),
            "bids":bids_data,
            "watchlist_list":watchlist_list
        })



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create_list(request):
    if request.method == "POST":
        
        
        
        if request.POST["image"] == '':
            image = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/480px-No_image_available.svg.png"
        else:
            image=request.POST["image"]
        if request.POST["group"] == "None":
            listing = active_list(title=request.POST["title"],description=request.POST["description"],owner=request.user,primary_bid=request.POST["bid"],image=image)
        else:
            group=groups.objects.get(id=int(request.POST["group"]))
            listing = active_list(title=request.POST["title"],description=request.POST["description"],owner=request.user,primary_bid=request.POST["bid"],belongs_to=group,image=image)
        listing.save()
        
        return HttpResponseRedirect(reverse("index"))
    
    return render(request,"auctions/create_list.html",{
        "group_list":groups.objects.all()
    })

def listing_page(request,id):
    listing_data=active_list.objects.get(pk=int(id))
    message=None
    try:
        bid_data=bids.objects.filter(placed_on=listing_data).aggregate(Max('bid'))["bid__max"]
    except bids.DoesNotExist:
        bid_data=None
    if bid_data is None:
            bid_data=listing_data.primary_bid
    
    if request.user == listing_data.owner:
       
        close_option = True
        
    else:
        close_option=False
        
    if request.user.is_authenticated: 
        watchlist_list=request.user.watchlists.all()
    else:
       watchlist_list=None
    
    if request.method=="POST":
            if int(request.POST["bid"])>bid_data:
                bid=bids(placed_on=listing_data,bid=int(request.POST["bid"]),bidded_by=request.user)
                
                bid.save()
                return HttpResponseRedirect(reverse("listing_page",args=(id,)))
            else:
                message="Bid needs to be bigger then current Bid"


    
    return render(request,"auctions/view_list.html",{
        "listing_details":listing_data,
        "comments_list":listing_data.comment_by_users.all(),
        "message":message,
        "bid_data":bid_data,
        "close_option":close_option,
        "watchlist_list":watchlist_list
     })

def comment_view(request,id):
    if request.method == "GET":
        return HttpResponseRedirect(reverse(index))
    elif request.method =="POST":
        current_list=active_list.objects.get(pk=int(id))
        comment_data=comments(text=request.POST["comment_text"],comment_by=request.user,comment_on=current_list)
        comment_data.save()
        return HttpResponseRedirect(reverse("listing_page",args=(id,)))

def watchlist_view(request):
    watchlist_list=request.user.watchlists.all()
    if request.method == "POST":
        if request.POST["todo"] == str("add"):
            watchlist_object=request.user.watchlists.add(active_list.objects.get(pk=int(request.POST["id"])))
        elif str(request.POST["todo"]) == str("remove"):
            watchlist_object=active_list.objects.get(pk=int(request.POST["id"]))
            request.user.watchlists.remove(watchlist_object)
        
            
        return HttpResponseRedirect(reverse("listing_page",args=(request.POST["id"],)))
    
    return render(request,"auctions/watchlist.html",{
        "watchlists":watchlist_list
    })

def cateogry(request,name=None):
    if name is None:
        print(groups.objects.all())
        return render(request,"auctions/catogery.html",{
            "group_lists":groups.objects.all(),
            "grouplist":True
        })
    else:
        group=groups.objects.get(text=str(name))
        bids_data=get_bid_data(active_list.objects.filter(status=True,belongs_to=group))
        return render(request,"auctions/catogery.html",{
            "item_lists":group.items.filter(status=True),
            "group":group,
            "bids":bids_data,
            "grouplist":False
        })

def close(request,id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            listing = active_list.objects.get(pk=int(id))
            listing.status=False
            try:
                bid_data=bids.objects.filter(placed_on=listing).aggregate(Max('bid'))["bid__max"]
                bid_data=bids.objects.get(placed_on=listing,bid=bid_data)
            except bids.DoesNotExist:
                bid_data=None
            if bid_data is None:
                bid_data=bids(placed_on=listing,bid=listing.primary_bid,bidded_by=listing.owner)
                bid_data.save()
            
            listing.won_by=bid_data
            listing.save()

    return HttpResponseRedirect(reverse(index))

def mylist(request):
    bids_data=get_bid_data(active_list.objects.filter(owner=request.user))
    if request.user.is_authenticated: 
        watchlist_list=request.user.watchlists.all()
    else:
        watchlist_list=None
    
    return render(request, "auctions/mylist.html",{
            "active_lists":active_list.objects.filter(owner=request.user),
            "bids":bids_data,
            "watchlist_list":watchlist_list
        })

def wonlist(request):
    won_list=[]
    for bid_list in bids.objects.filter(bidded_by=request.user):
        won_list+=active_list.objects.filter(won_by=bid_list)
    
    return render(request,"auctions/won_list.html",{
        "wonlists":won_list
    })
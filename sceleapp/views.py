from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.forms.models import model_to_dict
import json


from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from sceleapp.forms import RegisterForm, UserPostForm, UserReplyForm

from sceleapp.models import Gamification, UserBadge, UserPost, UserReply, Badge, Notif, PostLike, GivenPostLike, ReplyLike, GivenReplyLike

# Create your views here.

def get_notif(user, is_gamified):
    notifs = Notif.objects.filter(receiver=user, is_gamified=is_gamified)
    return notifs

@login_required
def dashboard(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    return render(request, 'dashboard.html', {'logged_in': True, 'user_fullname': user.get_full_name(), 'is_gamified': is_gamified})

def login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                usname = form.cleaned_data.get('username')
                psword = form.cleaned_data.get('password')
                user = authenticate(username=usname, password=psword)
                if user is not None:
                    auth_login(request, user)
                    messages.info(request, f"You are logged in as {usname}")
                    return redirect("dashboard") # url link
                else:
                    messages.error(request, "Invalid usernameor password")
            else:
                messages.error(request, "Invalid usernameor password")
        else:
            form = AuthenticationForm()
        return render(request, 'auth/login.html', {'form': form})

@login_required
def logout(request):
    auth_logout(request)
    return redirect('login')

# sourcecode: https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                form.save()
                # uname = form.cleaned_data.get('username')
                # raw_password = form.cleaned_data.get('password1')
                return redirect('login')
        else:
            form = RegisterForm()
        return render(request, 'auth/register.html', {'form': form})

@login_required
def view_profile(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    if is_gamified:
        badges = UserBadge.objects.filter(owner=user)
        latest_badge = badges.last()
        reversed_badges = list(badges)
        reversed_badges.reverse()
        return render(request, 'profile.html', 
            {'logged_in': True, 'user': user, 
            'user_fullname': user.get_full_name(), 
            'is_gamified': is_gamified,
            'badges': reversed_badges,
            'latest_badge': latest_badge})
    else:
        return render(request, 'profile.html', 
            {'logged_in': True, 'user': user, 
            'user_fullname': user.get_full_name(), 
            'is_gamified': is_gamified})

@login_required
def view_course(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    notifs = get_notif(user, is_gamified)
    new_notif_count = notifs.filter(is_new=True).count()
    context = {'logged_in': True, 'user': user, 
            'user_fullname': user.get_full_name(), 
            'is_gamified': is_gamified,
            'notifs': notifs,
            'new_notif_count': new_notif_count}
    if is_gamified:
        badges = UserBadge.objects.filter(owner=user)
        latest_badge = badges.last()
        context['badges'] = badges
        context['latest_badge'] = latest_badge
        return render(request, 'course.html', context)
    else:
        return render(request, 'course.html', context)

@login_required
def view_course_badges(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    badges = Badge.objects.all()
    return render(request, 'course-badges.html',
        {'logged_in': True, 'user': user,
        'user_fullname': user.get_full_name(),
        'is_gamified': is_gamified,
        'badges': badges})

@login_required
def view_badge_detail(request, code):
    user = request.user
    badge = UserBadge.objects.get(owner=user, badge__code=code)
    return render(request, 'badge-detail.html', 
        {'logged_in': True, 'user': user,
        'user_fullname': user.get_full_name(),
        'badge': badge})

@login_required
def view_forum(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    posts = list(UserPost.objects.all())
    len_posts = len(posts)
    if len_posts > 0:
        sort_post(posts, 0, len_posts-1)
        posts.reverse()
        return render(request, 'forum.html', 
            {'logged_in': True, 'user': user,
            'user_fullname': user.get_full_name(),
            'is_gamified': is_gamified,
            'posts': posts})
    return render(request, 'forum.html', 
        {'logged_in': True, 'user': user,
        'user_fullname': user.get_full_name(),
        'is_gamified': is_gamified})


def swap(posts, i, j):
    temp = posts[i]
    posts[i] = posts[j]
    posts[j] = temp

# This function takes last element as pivot, places 
# the pivot element at its correct position in sorted 
# array, and places all smaller (smaller than pivot) 
# to left of pivot and all greater elements to right 
# of pivot 
# ref: https://www.geeksforgeeks.org/python-program-for-quicksort/
def partition(posts, low, high):
    i = low - 1                     # index of smaller element
    pivot_post = posts[high]
    if has_replies(pivot_post):
        pivot = get_last_reply(pivot_post).created_at
    else:
        pivot = pivot_post.created_at

    for j in range(low, high):
        # If current element is smaller than or equal to pivot
        if has_replies(posts[j]):
            last_reply_created = get_last_reply(posts[j]).created_at
            if last_reply_created < pivot:
                i += 1
                swap(posts, i, j)
        else:
            if posts[j].created_at < pivot:
                i += 1
                swap(posts, i, j)

    i += 1
    swap(posts, i, high)
    return i

# posts --> list to be sorted, 
# low  --> Starting index 
# high  --> Ending index 
# ref: https://www.geeksforgeeks.org/python-program-for-quicksort/
def sort_post(posts, low, high):
    if low < high:
        # pi is partitioning index, arr[p] is now at right place
        pi = partition(posts, low, high)
        # Separately sort elements before partition and after partition
        sort_post(posts, low, pi-1)
        sort_post(posts, pi+1, high)
    
def has_replies(parent):
    if type(parent) is UserPost:
        replies = UserReply.objects.filter(user_post=parent)
    else:
        replies = UserReply.objects.filter(host_reply=parent)
    if replies.count() > 0:
        return True
    return False

def get_last_reply(post):
    replies = UserReply.objects.filter(user_post=post)
    last_reply = replies.last()
    deepest = []
    for rep in replies:
        deepest = get_deepest_replies(deepest, rep)
    for reply in deepest:
        if reply.created_at > last_reply.created_at:
            last_reply = reply
    return last_reply

def get_deepest_replies(deepest_replies, rep):
    replies = UserReply.objects.filter(host_reply=rep)
    if replies.count() == 0:
        deepest_replies.append(rep)
    else:
        for reply in replies:
            get_deepest_replies(deepest_replies, reply)
    return deepest_replies

@login_required
def view_post(request, id):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    post_id = int(id)
    post = UserPost.objects.get(id=post_id)
    context = {'logged_in': True, 'user': user,
            'user_fullname': user.get_full_name(),
            'is_gamified': is_gamified,
            'post': post}
    if has_replies(post):
        # reps = UserReply.objects.filter(user_post=post)
        replies = get_replies([], post, 1)
        context['replies'] = replies
    return render(request, 'post.html', context)

class Reply:
    def __init__(self, obj, lv, parent):
        self.obj = obj
        self.lv = lv
        self.parent = parent
        self.comp_id = 'rep-' + str(lv) + '-' + str(obj.id)

def get_reply_box(reply, parent):
    tags = '''
        <div class="box-item" id={{reply.comp_id}}>
            <div class="box-item__main-content">
                {% if reply.obj.creator == user %}
                    <a href="{% url \'profile\' %}">
                        <img src="{% static 'img/user-icon.png' %}" alt="user-icon">
                    </a>
                {% else %}
                    <img src="{% static 'img/user-icon.png' %}" alt="user-icon">
                {% endif %}
            </div>
        </div>
            '''
    return tags

def get_replies(all_replies, parent, lv):
    if type(parent) is UserPost:
        replies = UserReply.objects.filter(user_post=parent)
    else:
        replies = UserReply.objects.filter(host_reply=parent)
    
    for rep in replies:
        reply = Reply(rep, lv, parent)
        all_replies.append(reply)
        if has_replies(rep):
            get_replies(all_replies, rep, lv+1)
    return all_replies

@login_required
def add_post(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    if request.method == 'POST':
        form = UserPostForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            msg = form.cleaned_data.get('msg')
            permalink = "a"
            newPost = UserPost()
            newPost.subject = subject
            newPost.msg = msg
            newPost.permalink = permalink
            newPost.is_gamified = is_gamified
            newPost.creator = user
            print(newPost)
            newPost.save()
        return redirect('forum')
    else:
        form = UserPostForm()
        return render(request, 'add-post.html', 
            {'logged_in': True, 'user': user,
            'user_fullname': user.get_full_name(),
            'is_gamified': is_gamified,
            'form': form})

@login_required
def add_reply(request, post_id, parent_type, parent_id):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    post = UserPost.objects.get(id=post_id)
    if parent_type == '0':
        parent = UserPost.objects.get(id=parent_id)
    else:
        parent = UserReply.objects.get(id=parent_id)
    
    if request.method == 'POST':
        form = UserReplyForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            msg = form.cleaned_data.get('msg')
            permalink = "a"
            newRep = UserReply()
            newRep.subject = subject
            newRep.msg = msg
            newRep.permalink = permalink
            newRep.is_gamified = is_gamified
            newRep.creator = user
            if parent_type == '0':
                newRep.user_post = post
            else:
                newRep.host_reply = UserReply.objects.get(id=parent_id)
            newRep.save()
        return redirect('post', id=post.id)
    else:
        form = UserReplyForm()
        return render(request, 'add-reply.html',
            {'logged_in': True, 'user': user,
            'user_fullname': user.get_full_name(),
            'is_gamified': is_gamified,
            'parent': parent,
            'parent_type': parent_type, 
            'post': post,
            'form': form})

def create_new_postlike(userpost, isgamified):
    postlike = PostLike()
    postlike.user_post = userpost
    postlike.quantity = 1
    postlike.is_gamified = isgamified
    return postlike

def record_postliker(liker, postlike):
    postliker_rec = GivenPostLike()
    postliker_rec.liker = liker
    postliker_rec.post_like = postlike
    postliker_rec.save()
    return postliker_rec

def create_new_replylike(userreply, isgamified):
    replylike = ReplyLike()
    replylike.user_reply = userreply
    replylike.quantity = 1
    replylike.is_gamified = isgamified
    return replylike

def record_replyliker(liker, replylike):
    repliker_rec = GivenReplyLike()
    repliker_rec.liker = liker
    repliker_rec.reply_like = replylike
    repliker_rec.save()
    return repliker_rec

def add_like(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    res = dict()
    data = request.POST
    like_type = data['like_type']
    obj_id = int(data['obj_id'])
    
    if like_type == 'p':
        userpost = UserPost.objects.get(id=obj_id)
        postlikes = PostLike.objects.all()
        if postlikes:
            try:
                postlike = postlikes.get(user_post=userpost)
                postlike.quantity += 1
            except ObjectDoesNotExist:
                postlike = create_new_postlike(userpost, is_gamified)
        else:
            postlike = create_new_postlike(userpost, is_gamified)
        postlike.save()
        record_liker = record_postliker(user, postlike)
        print('liker: ', record_liker)
        dict_postlike = model_to_dict(postlike)
        res['postlike'] = json.dumps(dict_postlike)
    else:
        userreply = UserReply.objects.get(id=obj_id)
        replylikes = ReplyLike.objects.all()
        if replylikes:
            try:
                replylike = replylikes.get(user_reply=userreply)
                replylike.quantity += 1
            except ObjectDoesNotExist:
                replylike = create_new_replylike(userreply, is_gamified)
        else:
            replylike = create_new_replylike(userreply, is_gamified)
        replylike.save()
        record_liker = record_replyliker(user, replylike)
        print('liker: ', record_liker)
        dict_replylike = model_to_dict(replylike)
        res['replylike'] = dict_replylike
    return JsonResponse({'res': res})
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
from django.core import serializers

from sceleapp.forms import RegisterForm, UserPostForm, UserReplyForm

from sceleapp.models import Gamification, UserBadge, UserPost, UserReply, Badge, Notif, PostLike, GivenPostLike, ReplyLike, GivenReplyLike, UserParticipation, UserActivity, PostNotif

# Create your views here.

def get_notif(user, is_gamified):
    notifs = Notif.objects.filter(receiver=user, is_gamified=is_gamified)
    return notifs

@login_required
def dashboard(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    if is_gamified:
        update_user_participation_has_been_liked(user)
    user_activity = UserActivity.objects.get(user=user, is_gamified=is_gamified)
    context = { 'logged_in': True, 
                'user_fullname': user.get_full_name(), 
                'is_gamified': is_gamified}
    return render(request, 'dashboard.html', context)

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

def initiate_user_participation_obj(user):
    participation = UserParticipation()
    participation.user = user
    participation.save()

def initiate_user_activity_record(user):
    activity = UserActivity()
    activity.user = user
    activity.save()
    activity2 = UserActivity()
    activity2.user = user
    activity2.is_gamified = True
    activity2.save()

# sourcecode: https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                initiate_user_participation_obj(user)
                initiate_user_activity_record(user)
                return redirect('login')
        else:
            form = RegisterForm()
        return render(request, 'auth/register.html', {'form': form})

@login_required
def view_profile(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    user_activity = UserActivity.objects.get(user=user, is_gamified=is_gamified)
    context = { 'logged_in': True, 'user': user, 
                'user_fullname': user.get_full_name(), 
                'is_gamified': is_gamified,
                'user_activity': user_activity}
    if is_gamified:
        update_user_participation_has_been_liked(user)
        badges = UserBadge.objects.filter(owner=user)
        latest_badge = badges.last()
        reversed_badges = list(badges)
        reversed_badges.reverse()
        context['badges'] = reversed_badges
        context['latest_badge'] = latest_badge
        return render(request, 'profile.html', context)
    else:
        return render(request, 'profile.html', context)

def count_postlikes_earned(user):
    postlikes_earned_count = 0
    postlikes = PostLike.objects.filter(post_owner=user)
    if postlikes.count() > 0:
        for postlike in postlikes:
            postlikes_earned_count += postlike.quantity
        return postlikes_earned_count
    return 0

def count_replylikes_earned(user):
    replylikes_earned_count = 0
    replylikes = ReplyLike.objects.filter(reply_owner=user)
    if replylikes.count() > 0:
        for replylike in replylikes:
            replylikes_earned_count += replylike.quantity
        return replylikes_earned_count
    return 0

# def populate_activity_results(user, context, is_gamified):
#     posts = UserPost.objects.filter(creator=user, is_gamified=is_gamified)
#     posts_count = posts.count()
#     context['posts_count'] = posts_count

#     replies = UserReply.objects.filter(creator=user, is_gamified=is_gamified)
#     replies_count = replies.count()
#     context['replies_count'] = replies_count

#     postlikes_given_count = GivenPostLike.objects.filter(liker=user, is_gamified=is_gamified).count()
#     replylikes_given_count = GivenReplyLike.objects.filter(liker=user, is_gamified=is_gamified).count()
#     likes_given_count = postlikes_given_count + replylikes_given_count
#     context['likes_given_count'] = likes_given_count

#     grades = 0
#     if posts_count > 0:
#         for post in posts:
#             grades += post.grade
#     if replies_count > 0:
#         for reply in replies:
#             grades += reply.grade
#     context['grades'] = grades

#     return context

def has_first_3_likes(user):
    user_activity = UserActivity.objects.get(user=user, is_gamified=True)
    return user_activity.likes_earned_count >= 3



@login_required
def view_course(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    notifs = get_notif(user, is_gamified)
    new_notif_count = notifs.filter(is_new=True).count()
    user_activity = UserActivity.objects.get(user=user, is_gamified=is_gamified)

    context = {'logged_in': True, 'user': user, 
            'user_fullname': user.get_full_name(), 
            'is_gamified': is_gamified,
            'notifs': notifs,
            'new_notif_count': new_notif_count,
            'user_activity': user_activity}

    # context = populate_activity_results(user, context, is_gamified)

    if is_gamified:
        update_user_participation_has_been_liked(user)
        badges = UserBadge.objects.filter(owner=user)
        latest_badge = badges.last()
        context['badges'] = badges
        context['latest_badge'] = latest_badge

        # postlikes_earned_count = count_postlikes_earned(user)
        # replylikes_earned_count = count_replylikes_earned(user)
        # likes_earned_count = postlikes_earned_count + replylikes_earned_count
        # context['likes_earned_count'] = likes_earned_count
        
    return render(request, 'course.html', context)

# TODO if not gamified: redirect error page
@login_required
def view_course_badges(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    update_user_participation_has_been_liked(user)
    badges = Badge.objects.all()
    return render(request, 'course-badges.html',
        {'logged_in': True, 'user': user,
        'user_fullname': user.get_full_name(),
        'is_gamified': is_gamified,
        'badges': badges})

# TODO if not gamified: redirect error page
@login_required
def view_badge_detail(request, code):
    user = request.user
    badge = UserBadge.objects.get(owner=user, badge__code=code)
    update_user_participation_has_been_liked(user)
    return render(request, 'badge-detail.html', 
        {'logged_in': True, 'user': user,
        'user_fullname': user.get_full_name(),
        'badge': badge})

@login_required
def view_forum(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    if is_gamified:
        update_user_participation_has_been_liked(user)
    posts = list(UserPost.objects.filter(is_gamified=is_gamified))
    print('posts:', posts)
    len_posts = len(posts)
    if len_posts > 0:
        sort_post(posts, 0, len_posts-1)
        posts.reverse()
        print('posts:', posts)
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
    if has_replies(pivot_post, pivot_post.is_gamified):
        pivot = get_last_reply(pivot_post).created_at
    else:
        pivot = pivot_post.created_at

    for j in range(low, high):
        # If current element is smaller than or equal to pivot
        if has_replies(posts[j], posts[j].is_gamified):
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
    
def has_replies(parent, is_gamified):
    if type(parent) is UserPost:
        replies = UserReply.objects.filter(user_post=parent, is_gamified=is_gamified)
    else:
        replies = UserReply.objects.filter(host_reply=parent, is_gamified=is_gamified)
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
    if is_gamified:
        update_user_participation_has_been_liked(user)
    post_id = int(id)
    # try catch kalo post query dengan is_gamified tidak ditemukan -> error page
    post = UserPost.objects.get(id=post_id)
    # add_post_notif(post, is_gamified, user)
    try:
        total_likes = PostLike.objects.get(user_post=post, is_gamified=is_gamified).quantity
        user_has_liked = has_liked_post(user, post)
    except ObjectDoesNotExist:
        total_likes = 0
        user_has_liked = False
    context = {'logged_in': True, 'user': user,
            'user_fullname': user.get_full_name(),
            'is_gamified': is_gamified,
            'post': post,
            'total_likes': total_likes,
            'user_has_liked': user_has_liked}
    if has_replies(post, is_gamified):
        # reps = UserReply.objects.filter(user_post=post)
        replies = get_replies([], post, 1, is_gamified)
        context['replies'] = replies
    return render(request, 'post.html', context)

class Reply:
    def __init__(self, obj, lv, parent):
        self.obj = obj
        self.lv = lv
        self.parent = parent
        self.comp_id = str(obj.id)

def get_all_replies(all_replies, parent, is_gamified):
    if type(parent) is UserPost:
        replies = UserReply.objects.filter(user_post=parent, is_gamified=is_gamified)
    else:
        replies = UserReply.objects.filter(host_reply=parent, is_gamified=is_gamified)
    
    for reply in replies:
        all_replies.append(reply)
        if has_replies(reply, reply.is_gamified):
            get_all_replies(all_replies, reply, reply.is_gamified)
    return all_replies

def get_replies(all_replies, parent, lv, is_gamified):
    if type(parent) is UserPost:
        replies = UserReply.objects.filter(user_post=parent, is_gamified=is_gamified)
    else:
        replies = UserReply.objects.filter(host_reply=parent, is_gamified=is_gamified)
    
    for rep in replies:
        reply = Reply(rep, lv, parent)
        all_replies.append(reply)
        if has_replies(rep, rep.is_gamified):
            get_replies(all_replies, rep, lv+1, is_gamified)
    return all_replies

# ('p', 'Create a post'),
# ('r', 'Create a reply'),
# ('l', 'Give a like'),
# ('n', 'Receive 3 likes'),

def assign_user_badge(code, user):
    user_badge = UserBadge()
    badge = Badge.objects.get(code=code)
    user_badge.owner = user
    user_badge.badge = badge
    return user_badge

def update_user_participation_has_been_liked(user):
    user_participation = UserParticipation.objects.get(user=user)
    if not user_participation.has_been_liked_3_times:
        if has_first_3_likes(user):
            update_user_participation(user, 'liked')

def update_user_participation(user, activity_type, obj=None):
    user_participation = UserParticipation.objects.get(user=user)
    if activity_type == 'p':
        user_participation.has_posted = True
        user_badge = assign_user_badge('p1', user)
        user_badge.user_post = obj
    elif activity_type == 'r':
        user_participation.has_replied = True
        user_badge = assign_user_badge('p2', user)
        user_badge.user_reply = obj
    elif activity_type == 'lp':
        user_participation.has_liked = True
        user_badge = assign_user_badge('p3', user)
        user_badge.user_post = obj
    elif activity_type == 'lr':
        user_participation.has_liked = True
        user_badge = assign_user_badge('p3', user)
        user_badge.user_reply = obj
    else:
        user_participation.has_been_liked_3_times = True
        user_badge = assign_user_badge('p4', user)
        # TODO: kasih link ke <= 3 post/reply doi yg dpt pertama kali like dari orang lain
        # kasih atribut created_at di tiap given_post_like & given_reply_like
        # ambil masing2 3 item pertama, terus dari <= 6 itu ambil 3 pertama -> return 3 pertama tsb
    user_participation.save()
    user_badge.save()

def update_user_activity_record(user, activity_type, is_gamified):
    activity = UserActivity.objects.get(user=user, is_gamified=is_gamified)
    if activity_type == 'ap':       # add post
        activity.post_count += 1
    elif activity_type == 'dp':     # delete post
        activity.post_count -= 1
    elif activity_type == 'ar':     # add reply
        activity.reply_count += 1
    elif activity_type == 'dr':     # delete reply
        activity.reply_count -= 1
    elif activity_type == 'lga':    # like give add
        activity.likes_given_count += 1
    elif activity_type == 'lgs':    # like give sub (unlike)
        activity.likes_given_count -= 1
    elif activity_type == 'lea':    # like earned add (has been liked)
        activity.likes_earned_count += 1
    elif activity_type == 'les':    # like earned sub (has been unliked)
        activity.likes_earned_count -= 1
    activity.save()

def add_post_notif(post, is_gamified, creator):
    creator_fullname = creator.get_full_name()
    all_users = User.objects.exclude(id=creator.id)
    for user in all_users:
        try:
            # notif baru dengan tipe post yang dimiliki user
            notif = Notif.objects.get(notif_type='p', is_new=True, receiver=user)
            post_notif = PostNotif.objects.get(notif=notif)
            post_notif.post_quantity += 1
            post_notif.save()

            notif.title = 'Terdapat {0} post baru'.format(post_notif.post_quantity)
            notif.desc = 'Terdapat {0} post baru yang belum Anda buka'.format(post_notif.post_quantity)
            notif.user_post = None
            notif.save()

        except ObjectDoesNotExist:
            notif = Notif()
            notif.title = 'Terdapat sebuah post baru oleh {0}'.format(creator_fullname)
            notif.desc = '{0} telah membuat sebuah post yang berjudul "{1}"'.format(creator_fullname, post.subject)
            notif.notif_type = 'p'
            notif.is_gamified = is_gamified
            notif.img_loc = 'p'
            notif.user_post = post
            notif.receiver = user
            notif.save()

            post_notif = PostNotif()
            post_notif.notif = notif
            post_notif.post_quantity = 1
            post_notif.save()

@login_required
def add_post(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    if is_gamified:
        update_user_participation_has_been_liked(user)
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
            newPost.save()
            update_user_activity_record(user, 'ap', is_gamified)

            add_post_notif(newPost, is_gamified, user)

            if is_gamified:
                user_participation = UserParticipation.objects.get(user=user)
                if not user_participation.has_posted:
                    update_user_participation(user, 'p', newPost)

        return redirect('forum')
    else:
        form = UserPostForm()
        return render(request, 'add-post.html', 
            {'logged_in': True, 'user': user,
            'user_fullname': user.get_full_name(),
            'is_gamified': is_gamified,
            'form': form})

def get_post(reply):
    if reply.user_post:
        return reply.user_post
    else:
        return get_post(reply.host_reply)

@login_required
def add_reply(request, post_id, parent_type, parent_id):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    if is_gamified:
        update_user_participation_has_been_liked(user)
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
            update_user_activity_record(user, 'ar', is_gamified)
            user_participation = UserParticipation.objects.get(user=user)
            if not user_participation.has_replied:
                update_user_participation(user, 'r', newRep)
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

@login_required
def edit_post(request, id):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    if is_gamified:
        update_user_participation_has_been_liked(user)
    post = UserPost.objects.get(id=id)
    if request.method == 'POST':
        form = UserPostForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            msg = form.cleaned_data.get('msg')
            post.subject = subject
            post.msg = msg
            post.save()
        return redirect('post', id=id)
    else:
        form = UserPostForm(instance=post)
        return render(request, 'edit-post.html', 
            {'logged_in': True, 'user': user,
            'user_fullname': user.get_full_name(),
            'is_gamified': is_gamified,
            'form': form})

@login_required
def edit_reply(request, id):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    if is_gamified:
        update_user_participation_has_been_liked(user)
    reply = UserReply.objects.get(id=id)
    post = get_post(reply)
    if reply.user_post:
        parent = reply.user_post
    else:
        parent = reply.host_reply
    
    if request.method == 'POST':
        form = UserReplyForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            msg = form.cleaned_data.get('msg')
            reply.subject = subject
            reply.msg = msg
            reply.save()
        return redirect('post', id=post.id)
    else:
        form = UserReplyForm(instance=reply)
        return render(request, 'edit-reply.html',
            {'logged_in': True, 'user': user,
            'user_fullname': user.get_full_name(),
            'is_gamified': is_gamified,
            'parent': parent,
            'post': post,
            'form': form})

def delete_post(user, obj_id):
    post = UserPost.objects.get(id=obj_id)
    is_gamified = post.is_gamified
    if has_replies(post, post.is_gamified):
        all_replies = get_all_replies([], post, is_gamified)
        reversed_replies = [rep for rep in reversed(all_replies)]
        for rep in reversed_replies:
            update_user_activity_record(user, 'dr', rep.is_gamified)
            rep.delete()
    post.delete()

    if is_gamified:
        update_user_participation_has_been_liked(user)
    return JsonResponse({'response':'sukses'})

def delete_reply(user, obj_id):
    reply = UserReply.objects.get(id=obj_id)
    is_gamified = reply.is_gamified
    reply.delete()
    if is_gamified:
        update_user_participation_has_been_liked(user)
    return JsonResponse({'response':'sukses'})

@login_required
def delete_item(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    data = request.POST
    obj_id = int(data['obj_id'])
    item_type = data['item_type']
    if item_type == 'p':
        update_user_activity_record(user, 'dp', is_gamified)
        return delete_post(user, obj_id)
    update_user_activity_record(user, 'dr', is_gamified)
    return delete_reply(user, obj_id)

def has_liked_post(user, post):
    postlike = PostLike.objects.get(user_post=post)
    try:
        user_has_liked = GivenPostLike.objects.get(post_like=postlike, liker=user)
        return True
    except ObjectDoesNotExist:
        return False

def create_new_postlike(user, userpost, isgamified):
    postlike = PostLike()
    postlike.user_post = userpost
    postlike.quantity = 1
    postlike.is_gamified = isgamified
    # postlike.post_owner = user
    return postlike

def record_postliker(liker, postlike):
    postliker_rec = GivenPostLike()
    postliker_rec.liker = liker
    postliker_rec.post_like = postlike
    postliker_rec.is_gamified = postlike.is_gamified
    postliker_rec.save()
    return postliker_rec

def create_new_replylike(user, userreply, isgamified):
    replylike = ReplyLike()
    replylike.user_reply = userreply
    replylike.quantity = 1
    replylike.is_gamified = isgamified
    # replylike.reply_owner = user
    return replylike

def record_replyliker(liker, replylike):
    repliker_rec = GivenReplyLike()
    repliker_rec.liker = liker
    repliker_rec.reply_like = replylike
    repliker_rec.is_gamified = replylike.is_gamified
    repliker_rec.save()
    return repliker_rec

# TODO if not gamified: redirect to error page
@login_required
def add_like(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    data = request.POST
    like_type = data['like_type']
    obj_id = int(data['obj_id'])
    
    if like_type == 'p':
        userpost = UserPost.objects.get(id=obj_id)
        postlikes = PostLike.objects.all()

        # create/update postlike quantity
        try:
            postlike = PostLike.objects.all().get(user_post=userpost)
            postlike.quantity += 1
        except ObjectDoesNotExist:
            postlike = create_new_postlike(user, userpost, is_gamified)
        postlike.save()

        # add user likes given
        update_user_activity_record(user, 'lga', is_gamified)

        # add post_owner likes earned 
        post_owner = userpost.creator
        update_user_activity_record(post_owner, 'lea', is_gamified)

        # update whether user has posted or not yet
        user_participation = UserParticipation.objects.get(user=user)
        if not user_participation.has_liked:
            update_user_participation(user, 'lp', userpost)

        # update whether user has been liked 3 times
        if not user_participation.has_been_liked_3_times:
            if has_first_3_likes(user):
                update_user_participation(user, 'liked')
        
        record_liker = record_postliker(user, postlike)
        dict_postlike = model_to_dict(postlike)
        return JsonResponse({'likes': dict_postlike})
    else:
        userreply = UserReply.objects.get(id=obj_id)
        replylikes = ReplyLike.objects.all()
        try:
            replylike = replylikes.get(user_reply=userreply)
            replylike.quantity += 1
        except ObjectDoesNotExist:
            replylike = create_new_replylike(user, userreply, is_gamified)
        replylike.save()
        
        update_user_activity_record(user, 'lga', is_gamified)

        # add reply_owner likes earned
        reply_owner = userreply.creator
        update_user_activity_record(reply_owner, 'lea', is_gamified)

        # update whether user has replied or not yet
        user_participation = UserParticipation.objects.get(user=user)
        if not user_participation.has_liked:
            update_user_participation(user, 'lr', userreply)

        # update whether user has been liked 3 times
        if not user_participation.has_been_liked_3_times:
            if has_first_3_likes(user):
                update_user_participation(user, 'liked')

        record_liker = record_replyliker(user, replylike)
        dict_replylike = model_to_dict(replylike)
        return JsonResponse({'likes': dict_replylike})

# TODO if not gamified: redirect error page
@login_required
def unlike(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    update_user_participation_has_been_liked(user)
    data = request.POST
    like_type = data['like_type']
    obj_id = int(data['obj_id'])
    new_quantity = 0
    owner = None

    if like_type == 'p':
        userpost = UserPost.objects.get(id=obj_id)
        postlike = PostLike.objects.get(user_post=userpost)
        owner = userpost.creator
        if postlike.quantity > 1:
            postlike.quantity -= 1
            postlike.save()
            new_quantity = postlike.quantity
            GivenPostLike.objects.get(liker=user, post_like=postlike).delete()
        else:
            postlike.delete()
    else:
        userreply = UserReply.objects.get(id=obj_id)
        replylike = ReplyLike.objects.get(user_reply=userreply)
        owner = userreply.creator
        if replylike.quantity > 1:
            replylike.quantity -= 1
            replylike.save()
            new_quantity = replylike.quantity
            GivenReplyLike.objects.get(liker=user, reply_like=replylike).delete()
        else:
            replylike.delete()
    update_user_activity_record(user, 'lgs', is_gamified)
    update_user_activity_record(owner, 'les', is_gamified)
    
    return JsonResponse({'new_quantity': new_quantity})

# TODO if not gamified: redirect error page
@login_required
def view_likers(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    update_user_participation_has_been_liked(user)
    data = request.POST
    like_type = data['like_type']
    obj_id = int(data['obj_id'])
    likers = dict()

    if like_type == 'p':
        userpost = UserPost.objects.get(id=obj_id)
        postlike = PostLike.objects.get(user_post=userpost)
        recorded_likes = GivenPostLike.objects.filter(post_like=postlike)
        for obj in recorded_likes:
            liker = obj.liker.get_full_name()
            # rec = model_to_dict(obj)
            likers[obj.id] = liker
    else:
        userreply = UserReply.objects.get(id=obj_id)
        replylike = ReplyLike.objects.get(user_reply=userreply)
        recorded_likes = GivenReplyLike.objects.filter(reply_like=replylike)
        for obj in recorded_likes:
            liker = obj.liker.get_full_name()
            likers[obj.id] = liker
    
    return JsonResponse({'response': likers})

################ NOTIF AREA ################

@login_required
def view_notification_page(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    all_notif = Notif.objects.filter(receiver=user, is_gamified=is_gamified)
    has_notif = True if all_notif.count() > 0 else False
    print('all_notif:', all_notif)
    print('has_notif:', has_notif)
    context = {'logged_in': True, 'user': user,
            'user_fullname': user.get_full_name(),
            'is_gamified': is_gamified,
            'all_notif': all_notif,
            'has_notif': has_notif}
    return render(request, 'notifications.html', context)
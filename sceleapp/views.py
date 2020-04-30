from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.forms.models import model_to_dict
import json
import pytz
import logging

from django.utils import timezone
from django.templatetags.static import static
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers

from sceleapp.forms import RegisterForm, UserPostForm, UserReplyForm

from sceleapp.models import Gamification, UserBadge, UserPost, UserReply, Badge, Notif, PostLike, GivenPostLike, ReplyLike, GivenReplyLike, UserParticipation, UserActivity, PostNotif, ReplyNotif, LikeNotif

# Create your views here.

def get_notif(user, is_gamified):
    notifs = Notif.objects.filter(receiver=user, is_gamified=is_gamified)
    return notifs

@login_required
def error_post_not_found_with_context(request, context):
    return render(request, 'errors/post-not-found.html', context)

@login_required
def error_reply_not_found_with_context(request, context):
    return render(request, 'errors/reply-not-found.html', context)

@login_required
def error_post_not_found(request):
    user = request.user
    is_gamified = Gamification.objects.first().is_gamified
    if is_gamified:
        update_user_participation_has_been_liked(user)
    user_activity = UserActivity.objects.get(user=user, is_gamified=is_gamified)
    notifs = get_notif(user, is_gamified)
    new_notif_count = notifs.filter(is_new=True, is_notifpage_viewed=False).count()
    context = { 'logged_in': True, 
                'user_fullname': user.get_full_name(), 
                'is_gamified': is_gamified,
                'new_notif_count': new_notif_count}
    return render(request, 'errors/post-not-found.html', context)

@login_required
def dashboard(request):
    try:
        user = request.user
        is_gamified = Gamification.objects.first().is_gamified
        if is_gamified:
            update_user_participation_has_been_liked(user)
        user_activity = UserActivity.objects.get(user=user, is_gamified=is_gamified)
        notifs = get_notif(user, is_gamified)
        new_notif_count = notifs.filter(is_new=True, is_notifpage_viewed=False).count()
        context = { 'logged_in': True, 
                    'user_fullname': user.get_full_name(), 
                    'is_gamified': is_gamified,
                    'new_notif_count': new_notif_count}
        return render(request, 'dashboard.html', context)
    except Exception as e:
        logging.getLogger("error_logger").error(repr(e))

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
    try:
        user = request.user
        is_gamified = Gamification.objects.first().is_gamified
        update_grades(user, is_gamified)
        user_activity = UserActivity.objects.get(user=user, is_gamified=is_gamified)
        notifs = get_notif(user, is_gamified)
        new_notif_count = notifs.filter(is_new=True, is_notifpage_viewed=False).count()
        context = { 'logged_in': True, 'user': user, 
                    'user_fullname': user.get_full_name(), 
                    'is_gamified': is_gamified,
                    'user_activity': user_activity,
                    'new_notif_count': new_notif_count}
        if is_gamified:
            update_user_participation_has_been_liked(user)
            badges = UserBadge.objects.filter(owner=user)
            latest_badge = badges.last()
            reversed_badges = list(badges)
            reversed_badges.reverse()
            user_activity = update_bonus(user)
            context['badges'] = reversed_badges
            context['latest_badge'] = latest_badge
            context['user_activity'] = user_activity
            return render(request, 'profile.html', context)
        else:
            return render(request, 'profile.html', context)
    except Exception as e:
        logging.getLogger("error_logger").error(repr(e))

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

def update_grades(user, is_gamified):
    user_activity = UserActivity.objects.get(user=user, is_gamified=is_gamified)
    posts = UserPost.objects.filter(creator=user, is_gamified=is_gamified)
    replies = UserReply.objects.filter(creator=user, is_gamified=is_gamified)
    grades = 0
    
    if posts.count() > 0:
        for post in posts:
            grades += post.grade
    if replies.count() > 0:
        for reply in replies:
            grades += reply.grade
    user_activity.grades = grades
    user_activity.save()

# TODO
def update_bonus(user):
    user_activity = UserActivity.objects.get(user=user, is_gamified=True)
    user_badges = UserBadge.objects.filter(owner=user)
    bonuses = 0
    if user_badges.count() > 0:
        for badge in user_badges:
            bonuses += 5
    user_activity.bonuses = bonuses
    user_activity.save()
    return user_activity

@login_required
def view_course(request):
    try:
        user = request.user
        is_gamified = Gamification.objects.first().is_gamified
        update_grades(user, is_gamified)
        user_activity = UserActivity.objects.get(user=user, is_gamified=is_gamified)
        notifs = get_notif(user, is_gamified)
        new_notif_count = notifs.filter(is_new=True, is_notifpage_viewed=False).count()
        context = {'logged_in': True, 'user': user, 
                'user_fullname': user.get_full_name(), 
                'is_gamified': is_gamified,
                'notifs': notifs,
                'new_notif_count': new_notif_count,
                'user_activity': user_activity}

        if is_gamified:
            update_user_participation_has_been_liked(user)
            badges = UserBadge.objects.filter(owner=user)
            latest_badge = badges.last()
            user_activity = update_bonus(user)
            context['badges'] = badges
            context['latest_badge'] = latest_badge
            context['user_activity'] = user_activity
            
        return render(request, 'course.html', context)
    except Exception as e:
        logging.getLogger("error_logger").error(repr(e))

# TODO if not gamified: redirect error page
@login_required
def view_course_badges(request):
    try:
        user = request.user
        update_user_participation_has_been_liked(user)
        badges = Badge.objects.all()
        notifs = get_notif(user, True)
        new_notif_count = notifs.filter(is_new=True, is_notifpage_viewed=False).count()
        return render(request, 'course-badges.html',
            {'logged_in': True, 'user': user,
            'user_fullname': user.get_full_name(),
            'is_gamified': True,
            'badges': badges,
            'new_notif_count': new_notif_count})
    except Exception as e:
        logging.getLogger("error_logger").error(repr(e))

# TODO if not gamified: redirect error page
@login_required
def view_badge_detail(request, code):
    try:
        user = request.user
        update_user_participation_has_been_liked(user)
        notifs = get_notif(user, True)
        new_notif_count = notifs.filter(is_new=True, is_notifpage_viewed=False).count()

        badge = UserBadge.objects.get(owner=user, badge__code=code)
        context = {'logged_in': True, 'user': user,
                'user_fullname': user.get_full_name(),
                'badge': badge,
                'new_notif_count': new_notif_count}
        badge_type = ""
        if badge.user_post:
            post = badge.user_post
            created_at = timezone.localtime(post.created_at, timezone.get_fixed_timezone(420))
            formatedDate = created_at.strftime("%B %d, %Y, %H:%M")
            badge_type = "Post"
            context['item'] = badge.user_post
            context['created_at'] = formatedDate
        elif badge.user_reply:
            reply = badge.user_reply
            post = get_post(reply)
            post_url = reverse('post', kwargs={'id': post.id})
            reply_url = post_url + '#' + str(reply.id)
            created_at = timezone.localtime(reply.created_at, timezone.get_fixed_timezone(420))
            formatedDate = created_at.strftime("%B %d, %Y, %H:%M")
            badge_type = "Reply"
            context['badge_post'] = post
            context['item'] = reply
            context['item_url'] = reply_url
            context['created_at'] = formatedDate
        context['badge_type'] = badge_type

        return render(request, 'badge-detail.html', context)
    except Exception as e:
        logging.getLogger("error_logger").error(repr(e))

@login_required
def view_forum(request):
    try:
        user = request.user
        is_gamified = Gamification.objects.first().is_gamified
        if is_gamified:
            update_user_participation_has_been_liked(user)
        notifs = get_notif(user, is_gamified)
        new_notif_count = notifs.filter(is_new=True, is_notifpage_viewed=False).count()
        posts = list(UserPost.objects.filter(is_gamified=is_gamified))
        context = {'logged_in': True, 'user': user,
            'user_fullname': user.get_full_name(),
            'is_gamified': is_gamified,
            'new_notif_count': new_notif_count}
        
        len_posts = len(posts)
        if len_posts > 0:
            sort_post(posts, 0, len_posts-1)
            posts.reverse()
            context['posts'] = posts
        return render(request, 'forum.html', context)
    except Exception as e:
        logging.getLogger("error_logger").error(repr(e))


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
    try:
        user = request.user
        is_gamified = Gamification.objects.first().is_gamified
        if is_gamified:
            update_user_participation_has_been_liked(user)
        post_id = int(id)
        notifs = get_notif(user, is_gamified)
        new_notif_count = notifs.filter(is_new=True, is_notifpage_viewed=False).count()
        context = {'logged_in': True, 'user': user,
                    'user_fullname': user.get_full_name(),
                    'is_gamified': is_gamified,
                    'new_notif_count': new_notif_count}
        # try catch kalo post query dengan is_gamified tidak ditemukan -> error page
        try:
            post = UserPost.objects.get(id=post_id)
            created_at = timezone.localtime(post.created_at, timezone.get_fixed_timezone(420))
            formatedDate = created_at.strftime("%B %d, %Y, %H:%M")
            # add_post_notif(post, is_gamified, user)
            try:
                total_likes = PostLike.objects.get(user_post=post, is_gamified=is_gamified).quantity
                user_has_liked = has_liked_post(user, post)
            except ObjectDoesNotExist:
                total_likes = 0
                user_has_liked = False
            context['post'] = post
            context['formatedDate'] = formatedDate
            context['total_likes'] = total_likes
            context['user_has_liked'] = user_has_liked

            if has_replies(post, is_gamified):
                # reps = UserReply.objects.filter(user_post=post)
                replies = get_replies([], post, 1, is_gamified)
                context['replies'] = replies
            return render(request, 'post.html', context)
        except ObjectDoesNotExist:
            return error_post_not_found_with_context(request, context)
    except Exception as e:
        logging.getLogger("error_logger").error(repr(e))

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

def assign_user_badge(code, user):
    user_badge = UserBadge()
    badge = Badge.objects.get(code=code)
    user_badge.owner = user
    user_badge.badge = badge
    return user_badge

def add_participation_badge_notif(user, code, obj=None):
    notif = Notif()
    notif.notif_type = 'b'
    notif.is_gamified = True
    notif.receiver = user

    if code == 'p1':
        # post_url = reverse('post', kwargs={'id': obj.id})
        notif.title = 'Anda berhasil mendapatkan "<b>Initiator</b>" badge!'
        notif.desc = 'Anda berhasil mendapatkan "<b>Initiator</b>" badge karena telah mencoba memulai sebuah diskusi!'
        notif.img_loc = 'img/badges/participation/initiator-badge.png'
        notif.user_post = obj
    elif code == 'p2':
        notif.title = 'Anda berhasil mendapatkan "<b>Commentator</b>" badge!'
        notif.desc = 'Anda berhasil mendapatkan "<b>Commentator</b>" badge karena telah mencoba menghidupkan diskusi!'
        notif.img_loc = 'img/badges/participation/commentator-badge.png'
        notif.user_reply = obj
    elif code == 'p3':
        notif.title = 'Anda berhasil mendapatkan "<b>Appreciator</b>" badge!'
        notif.img_loc = 'img/badges/participation/appreciator-badge.png'
        if type(obj) is UserPost:
            notif.desc = 'Anda berhasil mendapatkan "<b>Appreciator</b>" badge karena telah mencoba mengapresiasi post dari pengguna lain!'
            notif.user_post = obj
        else:
            notif.desc = 'Anda berhasil mendapatkan "<b>Appreciator</b>" badge karena telah mencoba mengapresiasi reply dari pengguna lain!'
            notif.user_post = obj
    else:
        notif.title = 'Anda berhasil mendapatkan "<b>Noticeable</b>" badge!'
        notif.desc = 'Anda berhasil mendapatkan "<b>Noticeable</b>" badge karena telah mendapatkan apresiasi berupa 3 buah likes dari pengguna lain!'
        notif.img_loc = 'img/badges/participation/noticeable-badge.png'
    notif.save()


def update_user_participation_has_been_liked(user):
    user_participation = UserParticipation.objects.get(user=user)
    if not user_participation.has_been_liked_3_times:
        if has_first_3_likes(user):
            update_user_participation(user, 'liked')
            add_participation_badge_notif(user, 'p4')

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

def add_like_notif(liked_obj, is_gamified, liker):
    liker_name = liker.get_full_name()
    liked_obj_owner = liked_obj.creator

    if liker != liked_obj_owner:
        try:
            if type(liked_obj) is UserPost:
                notif = Notif.objects.get(notif_type='l', is_gamified=is_gamified, is_new=True, user_post=liked_obj, receiver=liked_obj_owner)
                obj_type = 'post'
            else:
                notif = Notif.objects.get(notif_type='l', is_gamified=is_gamified, is_new=True, user_reply=liked_obj, receiver=liked_obj_owner)
                obj_type = 'reply'

            like_notif = LikeNotif.objects.get(notif=notif)
            like_notif.like_quantity += 1
            like_notif.save()

            notif.title = 'Terdapat <b>{0} likes</b> pada {1} Anda yang berjudul "{2}"'.format(like_notif.like_quantity, obj_type, liked_obj.subject)
            notif.desc = 'Terdapat {0} likes baru pada {1} Anda yang berjudul "{2}"'.format(like_notif.like_quantity, obj_type, liked_obj.subject)
            notif.created_at = timezone.now()
            notif.save()

        except ObjectDoesNotExist:
            notif = create_new_notif_for_liked_obj(liked_obj, liker_name, is_gamified, liked_obj_owner)
            like_notif = create_new_like_notif(notif)

def create_new_notif_for_liked_obj(liked_obj, liker_name, is_gamified, liked_obj_owner):
    notif = Notif()
    if type(liked_obj) is UserPost:
        notif.user_post = liked_obj
        obj_type = 'post'
    else:
        notif.user_reply = liked_obj
        obj_type = 'reply'

    notif.title = '{0} <b>menyukai</b> {1} Anda yang berjudul "{2}"'.format(liker_name, obj_type, liked_obj.subject)
    notif.desc = '{0} telah menyukai sebuah {1} Anda yang berjudul "{2}"'.format(liker_name, obj_type, liked_obj.subject)
    notif.notif_type = 'l'
    notif.is_gamified = is_gamified
    notif.img_loc = 'l'
    notif.receiver = liked_obj_owner
    notif.save()
    return notif

def create_new_like_notif(notif):
    like_notif = LikeNotif()
    like_notif.notif = notif
    like_notif.like_quantity = 1
    like_notif.save()
    return like_notif

def add_reply_notif(parent, reply, is_gamified, reply_creator):
    reply_creator_fullname = reply_creator.get_full_name()
    parent_creator = parent.creator
    parent_type = ''
    
    if reply_creator != parent_creator:
        try:
            if type(parent) is UserPost:
                notif = Notif.objects.get(notif_type='r', is_new=True, user_post=parent, receiver=parent_creator)
                parent_type = 'post'
            else:
                notif = Notif.objects.get(notif_type='r', is_new=True, user_reply=parent, receiver=parent_creator)
                parent_type = 'reply'
            
            reply_notif = update_reply_notif(notif)
            notif = update_notif_for_reply(notif, reply_notif, parent_type, parent)
        
        except ObjectDoesNotExist:
            notif = create_new_notif_for_reply(parent, parent_creator, reply_creator_fullname, is_gamified)
            reply_notif = create_new_reply_notif(notif, reply)

def update_reply_notif(notif):
    reply_notif = ReplyNotif.objects.get(notif=notif)
    reply_notif.rep_quantity += 1
    reply_notif.reply = None
    reply_notif.save()
    return reply_notif

def update_notif_for_reply(notif, reply_notif, parent_type, parent):
    notif.title = 'Terdapat <b>{0} komentar baru</b> pada {1} Anda yang berjudul "{2}"'.format(reply_notif.rep_quantity, parent_type, parent.subject)
    notif.desc = 'Terdapat {0} komentar baru yang belum Anda buka pada {1} Anda yang berjudul "{2}"'.format(reply_notif.rep_quantity, parent_type, parent.subject)
    notif.created_at = timezone.now()
    notif.is_notifpage_viewed = False
    notif.save()
    return notif

def create_new_notif_for_reply(parent, parent_creator, reply_creator_fullname, is_gamified):
    notif = Notif()
    if type(parent) is UserPost:
        notif.user_post = parent
        parent_type = 'post'
    else:
        notif.user_reply = parent
        parent_type = 'reply'

    notif.title = '{0} <b>mengomentari</b> {1} Anda yang berjudul "{2}"'.format(reply_creator_fullname, parent_type, parent.subject)
    notif.desc = '{0} telah mengomentari sebuah {1} Anda yang berjudul "{2}"'.format(reply_creator_fullname, parent_type, parent.subject)
    notif.notif_type = 'r'
    notif.is_gamified = is_gamified
    notif.img_loc = 'r'
    notif.receiver = parent_creator
    notif.save()
    return notif

def create_new_reply_notif(notif, reply):
    reply_notif = ReplyNotif()
    reply_notif.notif = notif
    reply_notif.rep_quantity = 1
    reply_notif.reply = reply
    reply_notif.save()
    return reply_notif


def add_post_notif(post, is_gamified, creator):
    creator_fullname = creator.get_full_name()
    all_users = User.objects.exclude(id=creator.id)
    for user in all_users:
        print('user:', user.get_full_name())
        try:
            # notif baru dengan tipe post yang dimiliki user
            notif = Notif.objects.get(notif_type='p', is_new=True, receiver=user, is_gamified=is_gamified)
            post_notif = update_post_notif(notif)
            notif = update_notif_for_post(notif, post_notif)

        except ObjectDoesNotExist:
            notif = create_new_notif_for_post(creator_fullname, post, is_gamified, user)
            post_notif = create_new_post_notif(notif)

def update_post_notif(notif):
    post_notif = PostNotif.objects.get(notif=notif)
    post_notif.post_quantity += 1
    post_notif.save()
    return post_notif

def update_notif_for_post(notif, post_notif):
    notif.title = 'Terdapat <b>{0} post baru</b>'.format(post_notif.post_quantity)
    notif.desc = 'Terdapat {0} post baru yang belum Anda buka'.format(post_notif.post_quantity)
    notif.user_post = None
    notif.created_at = timezone.now()
    notif.is_notifpage_viewed = False
    notif.save()
    return notif

def create_new_notif_for_post(creator_fullname, post, is_gamified, user):
    notif = Notif()
    notif.title = 'Terdapat sebuah <b>post baru</b> oleh {0}'.format(creator_fullname)
    notif.desc = '{0} telah membuat sebuah post yang berjudul "{1}"'.format(creator_fullname, post.subject)
    notif.notif_type = 'p'
    notif.is_gamified = is_gamified
    notif.img_loc = 'p'
    notif.user_post = post
    notif.receiver = user
    notif.save()
    return notif

def create_new_post_notif(notif):
    post_notif = PostNotif()
    post_notif.notif = notif
    post_notif.post_quantity = 1
    post_notif.save()
    return post_notif

@login_required
def add_post(request):
    try:
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
                        add_participation_badge_notif(user, 'p1', newPost)

            return redirect('forum')
        else:
            notifs = get_notif(user, is_gamified)
            new_notif_count = notifs.filter(is_new=True, is_notifpage_viewed=False).count()
            form = UserPostForm()
            return render(request, 'add-post.html', 
                {'logged_in': True, 'user': user,
                'user_fullname': user.get_full_name(),
                'is_gamified': is_gamified,
                'form': form,
                'new_notif_count': new_notif_count})
    except Exception as e:
        logging.getLogger("error_logger").error(repr(e))

def get_post(reply):
    if reply.user_post:
        return reply.user_post
    else:
        return get_post(reply.host_reply)

@login_required
def add_reply(request, post_id, parent_type, parent_id):
    try:
        user = request.user
        is_gamified = Gamification.objects.first().is_gamified
        if is_gamified:
            update_user_participation_has_been_liked(user)
        try:
            post = UserPost.objects.get(id=post_id)
            if parent_type == '0':
                parent = UserPost.objects.get(id=parent_id)
            else:
                try:
                    parent = UserReply.objects.get(id=parent_id)
                except ObjectDoesNotExist:
                    return error_reply_not_found_with_context(request, 
                        {'logged_in': True, 'user': user,
                        'user_fullname': user.get_full_name(),
                        'is_gamified': is_gamified})
            
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
                        newRep.save()
                        add_reply_notif(post, newRep, is_gamified, user)
                    else:
                        newRep.host_reply = parent
                        newRep.save()
                        add_reply_notif(parent, newRep, is_gamified, user)
                    
                    update_user_activity_record(user, 'ar', is_gamified)
                    user_participation = UserParticipation.objects.get(user=user)
                    if not user_participation.has_replied and user != parent.creator:
                        update_user_participation(user, 'r', newRep)
                        add_participation_badge_notif(user, 'p2', newRep)
                return redirect('post', id=post.id)
            else:
                notifs = get_notif(user, is_gamified)
                new_notif_count = notifs.filter(is_new=True, is_notifpage_viewed=False).count()
                subject = 'Re: ' + parent.subject
                data = {'subject': subject}
                form = UserReplyForm(initial=data)
                return render(request, 'add-reply.html',
                    {'logged_in': True, 'user': user,
                    'user_fullname': user.get_full_name(),
                    'is_gamified': is_gamified,
                    'parent': parent,
                    'parent_type': parent_type, 
                    'post': post,
                    'form': form,
                    'new_notif_count': new_notif_count})
        except ObjectDoesNotExist:
            return error_post_not_found_with_context(request, 
                {'logged_in': True, 'user': user,
                'user_fullname': user.get_full_name(),
                'is_gamified': is_gamified})
    except Exception as e:
        logging.getLogger("error_logger").error(repr(e))

@login_required
def edit_post(request, id):
    try:
        user = request.user
        is_gamified = Gamification.objects.first().is_gamified
        if is_gamified:
            update_user_participation_has_been_liked(user)
        try:
            post = UserPost.objects.get(id=id)
        except ObjectDoesNotExist:
            return error_reply_not_found_with_context(request, 
                {'logged_in': True, 'user': user,
                'user_fullname': user.get_full_name(),
                'is_gamified': is_gamified})
        
        if request.method == 'POST':
            form = UserPostForm(request.POST)
            if form.is_valid():
                subject = form.cleaned_data.get('subject')
                msg = form.cleaned_data.get('msg')
                post.subject = subject
                post.msg = msg
                post.created_at = timezone.now()
                post.save()
            return redirect('post', id=id)
        else:
            notifs = get_notif(user, is_gamified)
            new_notif_count = notifs.filter(is_new=True, is_notifpage_viewed=False).count()
            form = UserPostForm(instance=post)
            return render(request, 'edit-post.html', 
                {'logged_in': True, 'user': user,
                'user_fullname': user.get_full_name(),
                'is_gamified': is_gamified,
                'form': form,
                'new_notif_count': new_notif_count})
    except Exception as e:
        logging.getLogger("error_logger").error(repr(e))

@login_required
def edit_reply(request, id):
    try:
        user = request.user
        is_gamified = Gamification.objects.first().is_gamified
        if is_gamified:
            update_user_participation_has_been_liked(user)
        try:
            reply = UserReply.objects.get(id=id)
        except ObjectDoesNotExist:
            return error_reply_not_found_with_context(request, 
                {'logged_in': True, 'user': user,
                'user_fullname': user.get_full_name(),
                'is_gamified': is_gamified})
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
                reply.created_at = timezone.now()
                reply.save()
            return redirect('post', id=post.id)
        else:
            notifs = get_notif(user, is_gamified)
            new_notif_count = notifs.filter(is_new=True, is_notifpage_viewed=False).count()
            form = UserReplyForm(instance=reply)
            return render(request, 'edit-reply.html',
                {'logged_in': True, 'user': user,
                'user_fullname': user.get_full_name(),
                'is_gamified': is_gamified,
                'parent': parent,
                'post': post,
                'form': form,
                'new_notif_count': new_notif_count})
    except Exception as e:
        logging.getLogger("error_logger").error(repr(e))

def delete_post(user, obj_id):
    post = UserPost.objects.get(id=obj_id)
    is_gamified = post.is_gamified
    if has_replies(post, post.is_gamified):
        all_replies = get_all_replies([], post, is_gamified)
        reversed_replies = [rep for rep in reversed(all_replies)]
        for rep in reversed_replies:
            update_user_activity_record(rep.creator, 'dr', rep.is_gamified)
            rep.delete()
    post.delete()
    update_user_activity_record(user, 'dp', is_gamified)
    if is_gamified:
        update_user_participation_has_been_liked(user)
    return JsonResponse({'response':'sukses'})

def delete_reply(user, obj_id):
    reply = UserReply.objects.get(id=obj_id)
    is_gamified = reply.is_gamified
    if has_replies(reply, is_gamified):
        all_replies = get_all_replies([], reply, is_gamified)
        reversed_replies = [rep for rep in reversed(all_replies)]
        for rep in reversed_replies:
            update_user_activity_record(rep.creator, 'dr', rep.is_gamified)
            rep.delete()
    reply.delete()
    update_user_activity_record(user, 'dr', is_gamified)
    if is_gamified:
        update_user_participation_has_been_liked(user)
    return JsonResponse({'response':'sukses'})

@login_required
def delete_item(request):
    try:
        user = request.user
        is_gamified = Gamification.objects.first().is_gamified
        data = request.POST
        obj_id = int(data['obj_id'])
        item_type = data['item_type']
        if item_type == 'p':
            return delete_post(user, obj_id)
        return delete_reply(user, obj_id)
    except Exception as e:
        logging.getLogger("error_logger").error(repr(e))

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
    try:
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

            # update notif
            add_like_notif(userpost, is_gamified, user)

            # add post_owner likes earned and user likes given
            post_owner = userpost.creator
            if user != post_owner:
                update_user_activity_record(user, 'lga', is_gamified)
                update_user_activity_record(post_owner, 'lea', is_gamified)

            # update whether user has liked or not yet
            user_participation = UserParticipation.objects.get(user=user)
            if not user_participation.has_liked and user != post_owner:
                update_user_participation(user, 'lp', userpost)
                add_participation_badge_notif(user, 'p3', userpost)

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

            # update notif
            add_like_notif(userreply, is_gamified, user)
            
            # add reply_owner likes earned & user likes given
            reply_owner = userreply.creator
            if user != reply_owner:
                update_user_activity_record(user, 'lga', is_gamified)
                update_user_activity_record(reply_owner, 'lea', is_gamified)

            # update whether user has replied or not yet
            user_participation = UserParticipation.objects.get(user=user)
            if not user_participation.has_liked and user != reply_owner:
                update_user_participation(user, 'lr', userreply)
                add_participation_badge_notif(user, 'p3', userreply)

            # update whether user has been liked 3 times
            if not user_participation.has_been_liked_3_times:
                if has_first_3_likes(user):
                    update_user_participation(user, 'liked')

            record_liker = record_replyliker(user, replylike)
            dict_replylike = model_to_dict(replylike)
            return JsonResponse({'likes': dict_replylike})
    except Exception as e:
        logging.getLogger("error_logger").error(repr(e))

# TODO if not gamified: redirect error page
@login_required
def unlike(request):
    try:
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
        
        if user != owner:
            update_user_activity_record(user, 'lgs', is_gamified)
            update_user_activity_record(owner, 'les', is_gamified)
        
        return JsonResponse({'new_quantity': new_quantity})
    except Exception as e:
        logging.getLogger("error_logger").error(repr(e))

# TODO if not gamified: redirect error page
@login_required
def view_likers(request):
    try:
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
    except Exception as e:
        logging.getLogger("error_logger").error(repr(e))

################ NOTIF AREA ################

@login_required
def view_notification_page(request):
    try:
        user = request.user
        is_gamified = Gamification.objects.first().is_gamified
        all_notif = Notif.objects.filter(receiver=user, is_gamified=is_gamified)
        print('notif count:', all_notif.count())
        has_notif = False
        if all_notif.count() > 0:
            has_notif = True
            for notif in all_notif:
                make_notif_is_viewed_in_notifpage(notif)

        context = {'logged_in': True, 'user': user,
                'user_fullname': user.get_full_name(),
                'is_gamified': is_gamified,
                'all_notif': all_notif,
                'has_notif': has_notif}
        return render(request, 'notifications.html', context)
    except Exception as e:
        logging.getLogger("error_logger").error(repr(e))

def make_notif_is_not_new(notif):
    notif.is_new = False
    notif.save()

def make_notif_is_viewed_in_notifpage(notif):
    notif.is_notifpage_viewed = True
    notif.save()

@login_required
def open_and_update_notif_item(request):
    try:
        user = request.user
        is_gamified = Gamification.objects.first().is_gamified
        data = request.POST
        print('data:', data)
        obj_id = int(data['obj_id'])
        notif = Notif.objects.get(id=obj_id)
        res = dict()
        notif_type = notif.notif_type

        if notif_type == 'p':
            if notif.user_post:
                post = notif.user_post
                res = setup_res(res, 'post', post)
            else:
                res['page'] = 'forum'
        elif notif_type == 'r':
            reply_notif = ReplyNotif.objects.get(notif=notif)
            # Mengomentari sebuah reply
            if reply_notif.reply:
                new_reply = reply_notif.reply
                res = setup_res(res, 'reply', new_reply)
            # Terdapat > 1 reply pada sebuah post
            elif notif.user_post:
                parent_post = notif.user_post
                res = setup_res(res, 'post', parent_post)
            # Terdapat > 1 reply pada sebuah reply
            else:
                parent_reply = notif.user_reply
                res = setup_res(res, 'reply', parent_reply)
        elif notif_type == 'l':
            if notif.user_post:
                liked_post = notif.user_post
                res = setup_res(res, 'post', liked_post)
            else:
                liked_reply = notif.user_reply
                res = setup_res(res, 'reply', liked_reply)
        elif notif_type == 'b':
            if notif.is_new:
                res = setup_modal_res(res, notif)
            if notif.user_post:
                badged_post = notif.user_post
                res = setup_res(res, 'post', badged_post)
            elif notif.user_reply:
                badged_post = notif.user_reply
                res = setup_res(res, 'reply', badged_post)

        if notif.is_new:
            make_notif_is_not_new(notif)

        return JsonResponse({'res': res})
    except Exception as e:
        logging.getLogger("error_logger").error(repr(e))

def setup_modal_res(res, notif):
    res['title'] = notif.title
    res['desc'] = notif.desc
    res['img_loc'] = static(notif.img_loc)
    res['is_badge'] = True
    return res

def setup_res(res, page_type, redirect_obj):
    res['id'] = redirect_obj.id
    res['page'] = page_type
    if type(redirect_obj) is UserReply:
        parent_post = get_post(redirect_obj)
        res['post_id'] = parent_post.id
    return res

def prepare_res(res, obj_id, page_type, parent_post_id=None):
    if parent_post_id:
        res['post_id'] = parent_post_id
    res['id'] = obj_id
    res['page'] = page_type
    return res
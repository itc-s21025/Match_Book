from itertools import chain
from operator import attrgetter

from django.contrib.auth.decorators import login_required, user_passes_test
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from Matching.forms import ProfileForm, DirectMessageForm, BookThoughtsForm
from Matching.models import Profile, DirectMessage, Matching, Notification, NotificationMatching, BookThoughts
from django.db.models import Q


# Create your views here.
def has_profile(user):
    return Profile.objects.filter(create_by=user).exists()


@login_required
@user_passes_test(has_profile, login_url='/matching/create_profile/')
def top(request):
    user_profile = request.user.profile
    user_gender = request.user.profile.sex
    matching_profiles = Profile.objects.filter(
        Q(approaching__approached=user_profile, approaching__approved=True) |
        Q(approached__approaching=user_profile, approached__approved=True)
    )

    # 異性のプロフィールを取得
    if user_gender == 'male':
        opposite_gender = 'female'
    elif user_gender == 'female':
        opposite_gender = 'male'
    else:
        # その他の性別の場合、適切な処理を行ってください
        opposite_gender = None

    if opposite_gender:
        # 異性のプロフィールを取得
        opposite_gender_profiles = Profile.objects.filter(sex=opposite_gender).exclude(pk__in=matching_profiles)

        query = request.GET.get('q')

        if query:
            # キーワードがある場合、モデルから検索を行う
            results = opposite_gender_profiles.filter(Q(like_book__icontains=query) |
                                                      Q(favorite_author=query))  # name は検索対象のフィールド

            context = {'results': results, 'query': query}

            return render(request, 'top.html', context)

        query2 = request.GET.get('q2')
        if query2:
            # キーワードがある場合、モデルから検索を行う
            results2 = opposite_gender_profiles.filter(Q(favorite_book_category__contains=query2))

            context = {'results2': results2, 'query2': query2}

            return render(request, 'top.html', context)
        context = {
            'opposite_gender_profiles': opposite_gender_profiles,

        }

        return render(request, 'top.html', context)


    else:
        # 適切な処理を行ってください
        pass


@login_required
def matched_list(request):
    user_profile = request.user.profile
    # ログインユーザーに関連する通知を取得
    notifications = NotificationMatching.objects.filter(user=request.user.profile)

    user_gender = request.user.profile.sex
    matching_profiles = Profile.objects.filter(
        Q(approaching__approached=user_profile, approaching__approved=True) |
        Q(approached__approaching=user_profile, approached__approved=True)
    )

    # 異性のプロフィールを取得
    if user_gender == 'male':
        opposite_gender = 'female'
    elif user_gender == 'female':
        opposite_gender = 'male'
    else:
        # その他の性別の場合、適切な処理を行ってください
        opposite_gender = None

    if opposite_gender:
        # 異性のプロフィールを取得
        opposite_gender_profiles = Profile.objects.filter(sex=opposite_gender).filter(pk__in=matching_profiles)

        context = {
            'opposite_gender_profiles': opposite_gender_profiles,
            'notifications': notifications
        }

        return render(request, 'matched_list.html', context)
    else:
        # 適切な処理を行ってください
        pass


@login_required
def profile_detail(request, profile_id):
    request_user = request.user.profile
    matching_profiles = Profile.objects.filter(
        Q(approaching__approached=profile_id, approaching__approved=True) |
        Q(approached__approaching=profile_id, approached__approved=True)
    )

    thoughts = BookThoughts.objects.filter(create_by_id=profile_id)
    profile = get_object_or_404(Profile, pk=profile_id)
    matching = Matching.objects.filter(Q(approaching=request.user.profile) & Q(approached=profile_id)).exists()

    return render(request, 'profile_detail.html', {'profile': profile, 'user': profile_id,
                                                   'request_user': request_user, 'matching': matching,
                                                   'thoughts': thoughts, 'matching_profile': matching_profiles})

def send_liked(request):
    return render(request, 'liked_page.html')

@login_required
def send_like(request, approached_user_id):
    # ログインユーザーが指定したユーザーに「いいね」を送信
    approached_user = Profile.objects.get(pk=approached_user_id)

    # すでにマッチングしている場合は何もせずリダイレクト
    if Matching.objects.filter(approaching=request.user.profile, approached=approached_user, approved=True).exists():
        return redirect('top')

    # マッチング情報を作成
    matching_instance = Matching(approaching=request.user.profile, approached=approached_user)
    matching_instance.save()
    Notification.objects.create(user=approached_user, message=f'{request.user.profile.nickname}がいいねを送りました。')

    # 相手からも「いいね」があればマッチング成立
    if Matching.objects.filter(approaching=approached_user, approached=request.user.profile).exists():
        matching_instance.approved = True
        matching_instance.save()
        # マッチング成立時の通知を作成
        NotificationMatching.objects.create(user=approached_user,
                                            message=f'{request.user.profile}とのマッチングが成立しました！')
        NotificationMatching.objects.create(user=request.user.profile,
                                            message=f'{approached_user}とのマッチングが成立しました！')

        # マッチング成立時の処理（例: メッセージを送る画面にリダイレクト）
        return redirect('send_liked')

    return redirect('send_liked')


@login_required
def send_direct_message(request, receiver_id):
    request_user = request.user.profile
    receiver = Profile.objects.get(pk=receiver_id)
    messages_sent = DirectMessage.objects.filter(sender=request.user.profile, receiver=receiver)
    messages_received = DirectMessage.objects.filter(receiver=request.user.profile, sender=receiver)
    all_messages = sorted(
        chain(messages_sent, messages_received),
        key=attrgetter('created_at'),
        reverse=False
    )

    if request.method == 'POST':
        form = DirectMessageForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            direct_message = DirectMessage(sender=request.user.profile, receiver=receiver, message=message)
            direct_message.save()
            return redirect('send_direct_message', receiver_id)
    else:
        form = DirectMessageForm()

    context = {
        'form': form,
        'request_user': request_user,
        'receiver': receiver,
        'messages_sent': messages_sent,
        'messages_received': messages_received,
        'all_messages': all_messages,
    }
    return render(request, 'send_direct_message.html', context)


@login_required
def direct_messages(request, receiver_id):
    receiver = get_object_or_404(Profile, pk=receiver_id)
    messages_sent = DirectMessage.objects.filter(sender=request.user.profile, receiver=receiver)
    messages_received = DirectMessage.objects.filter(receiver=request.user.profile, sender=receiver)

    # 送信と受信のメッセージを一つのリストにまとめ、日付の新しい順にソート
    all_messages = sorted(
        chain(messages_sent, messages_received),
        key=attrgetter('created_at'),
        reverse=True
    )

    context = {
        'all_messages': all_messages,
    }
    return render(request, 'direct_messages.html', context)


def get_notifications(request):
    user_notifications = Notification.objects.filter(user=request.user.profile.pk)
    notifications_data = [{'message': notification.message, 'created_at': notification.created_at} for notification in
                          user_notifications]
    return JsonResponse(notifications_data, safe=False)


@login_required
def show_notifications(request):
    matching = Matching.objects.filter(approached=request.user.profile.pk)
    context = {'matching': matching}
    return render(request, 'notifications.html', context)


@login_required
def show_notifications_matching(request):
    # ログインユーザーに関連する通知を取得
    notifications = NotificationMatching.objects.filter(user=request.user.profile)
    context = {'notifications': notifications}

    return render(request, 'notifications_matching.html', context)


# google book api 取得view
def get_book_info(query):
    # Google Books APIエンドポイント
    max_results = '&maxresults=1'
    url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{query + max_results}'

    # APIリクエスト
    response = requests.get(url)
    data = response.json()

    # 必要な情報を抽出
    books = []
    for item in data.get('items', []):
        book_info = {
            'title': item['volumeInfo']['title'],
            'authors': item['volumeInfo'].get('authors', []),
            'description': item['volumeInfo'].get('description', ''),
            'image_link': item['volumeInfo'].get('imageLinks', {}).get('thumbnail', ''),
        }
        books.append(book_info)

    return books


# 本のタイトル検索view
@login_required
def book_search(request):
    if request.method == 'POST':
        query = request.POST.get('query', '')

        books = get_book_info(query)
        context = {'books': books}

        return render(request, 'book_search_form.html', context)

    return render(request, 'book_search_form.html')


# 本の感想投稿view
@login_required
def book_thoughts_form(request):
    book_title = ""
    book_author = ""
    book_description = ""
    book_image_url = ""
    if request.method == 'POST':
        query = request.POST.get('query', '')
        books = get_book_info(query)
        books = books[0]
        book_title = books.get('title')
        book_author = ', '.join(books.get('authors', []))
        book_description = books.get('description')
        book_image_url = books.get('image_link')

    if request.method == 'POST':
        form = BookThoughtsForm(request.POST)
        if form.is_valid():
            book_thoughts = form.save(commit=False)
            book_thoughts.create_by = request.user.profile
            book_thoughts.save()
            messages.success(request, '本の感想が投稿されました。')
            return redirect('top')
    else:
        form = BookThoughtsForm()

    return render(request,
                  'book_thoughts_form.html',
                  {'form': form, 'books': book_title,
                   'book_author': book_author,
                   'book_description': book_description, 'book_image_url': book_image_url})


# profile作成view
@method_decorator(login_required, name='dispatch')
class CreateProfileView(CreateView):
    form_class = ProfileForm

    template_name = 'create_profile.html'

    success_url = reverse_lazy('top')

    def form_valid(self, form):
        profile = form.save(commit=False)
        profile.create_by = self.request.user
        profile.save()
        return super().form_valid(form)


# 本の感想一覧view
@login_required()
def book_thoughts_list(request):
    thoughts = BookThoughts.objects.all()

    context = {
        'thoughts': thoughts,
    }

    return render(request, 'book_thoughts_list.html', context)


# 本の感想詳細view
def book_thoughts_detail(request, thought_id):
    thought = get_object_or_404(BookThoughts, id=thought_id)

    context = {
        'thought': thought,
    }

    return render(request, 'book_thoughts_detail.html', context)

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from Matching.forms import ProfileForm, DirectMessageForm
from Matching.models import Profile, DirectMessage, Matching
from django.db.models import Q


# Create your views here.
@login_required()
def top(request):
    user_gender = request.user.profile.sex

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
        opposite_gender_profiles = Profile.objects.filter(sex=opposite_gender)

        context = {
            'opposite_gender_profiles': opposite_gender_profiles,
        }

        return render(request, 'top.html', context)
    else:
        # 適切な処理を行ってください
        pass


@login_required()
def profile_detail(request, profile_id):
    request_user = request.user.profile.pk
    profile = get_object_or_404(Profile, pk=profile_id)
    matching = Matching.objects.filter(Q(approaching=request.user.profile.pk) & Q(approached=profile_id)).exists()

    return render(request, 'profile_detail.html', {'profile': profile, 'user': profile_id,
                                                   'request_user': request_user, 'matching': matching})


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

    # 相手からも「いいね」があればマッチング成立
    if Matching.objects.filter(approaching=approached_user, approached=request.user.profile).exists():
        matching_instance.approved = True
        matching_instance.save()

        # マッチング成立時の処理（例: メッセージを送る画面にリダイレクト）
        return redirect('top')

    return redirect('top')


@login_required
def send_direct_message(request, receiver_id):
    receiver = Profile.objects.get(pk=receiver_id)

    if request.method == 'POST':
        form = DirectMessageForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            direct_message = DirectMessage(sender=request.user.profile, receiver=receiver, message=message)
            direct_message.save()
            return redirect('direct_messages')
    else:
        form = DirectMessageForm()

    context = {
        'form': form,
        'receiver': receiver,
    }
    return render(request, 'send_direct_message.html', context)


@login_required
def direct_messages(request):
    messages_sent = DirectMessage.objects.filter(sender=request.user.profile)
    messages_received = DirectMessage.objects.filter(receiver=request.user.profile)

    context = {
        'messages_sent': messages_sent,
        'messages_received': messages_received,
    }
    return render(request, 'direct_messages.html', context)

from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


# Create your models here.


class Profile(models.Model):
    create_by = models.OneToOneField(settings.AUTH_USER_MODEL,
                                     on_delete=models.CASCADE)
    nickname = models.CharField("ニックネーム", max_length=20)
    created_at = models.DateTimeField("登録日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True, blank=True, null=True)
    age = models.PositiveSmallIntegerField(
        "年齢", validators=[MinValueValidator(18, '18歳未満は登録できません'),
                            MaxValueValidator(100, '100歳を超えて登録はできません')])
    SEX = [
        ('male', '男性'),
        ('female', '女性'),
    ]
    sex = models.CharField("性別", max_length=16, choices=SEX)
    introduction = models.TextField("自己紹介", max_length=1000)
    favorite_book_category = models.TextField("好きな本のカテゴリ", max_length=100)
    like_book = models.TextField("好きな本", max_length=256)
    favorite_author = models.TextField("好きな作家", max_length=1000)

    def __str__(self):
        return self.nickname


class Matching(models.Model):
    approaching = models.ForeignKey(
        Profile, related_name='approaching',
        on_delete=models.CASCADE
    )
    approached = models.ForeignKey(
        Profile, related_name='approached',
        on_delete=models.CASCADE
    )
    approved = models.BooleanField(verbose_name="マッチング許可", default=False)
    created_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)

    class Meta:
        unique_together = (('approaching', 'approached'),)

    def __str__(self):
        return str(self.approaching) + ' like to ' + str(self.approached)


class DirectMessage(models.Model):
    sender = models.ForeignKey(
        Profile, related_name='sender',
        on_delete=models.CASCADE
    )
    receiver = models.ForeignKey(
        Profile, related_name='receiver',
        on_delete=models.CASCADE
    )
    message = models.CharField(verbose_name="メッセージ", max_length=200)
    created_at = models.DateTimeField(verbose_name="登録日時", auto_now_add=True)

    def __str__(self):
        return str(self.sender) + ' --- send to ---> ' + str(self.receiver)


class Notification(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

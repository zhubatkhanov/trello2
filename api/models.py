from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.exceptions import ValidationError


class User(AbstractUser):
    
    SUBSCRIPTIONS = (
        ('FREE', 'FREE'),
        ('PREMIUM', 'PREMIUM')
    )
    
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    subscription = models.CharField(
        max_length=10,
        choices=SUBSCRIPTIONS,
        default='FREE'
    )


class Board(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        user = self.user
        if user.board_set.count() >= 3 and self.user.subscription == 'FREE':
            raise ValidationError('Only 3 boards are allowed for FREE subscription')
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.name} by user {self.user}'
    
    
class ListCard(models.Model):
    Colors = (
        ('Red', 'Red'),
        ('Blue', 'Blue'),
        ('Green', 'Green'),
        ('Yellow', 'Yellow'),
        ('Default', 'Default')
    )
    
    title = models.CharField(max_length=255, unique=True)
    color = models.CharField(
        max_length = 10,
        choices = Colors,
        default = 'Default'
    )
    position = models.IntegerField()
    board_id = models.ForeignKey(Board, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if self.board_id.user.subscription == 'FREE' and self.color != 'Default':
            raise ValidationError('You cannot change the list color with a free subscription!')
        return super().save(*args, **kwargs)
    
    def move_position(self, new_position):
        old_position = self.position
        self.position = new_position
        other_lists = ListCard.objects.filter(board_id=self.board_id, position__gte=new_position).exclude(pk=self.pk)
        if new_position < old_position:
            other_lists.update(position=models.F('position') + 1)
        else:
            other_lists.update(position=models.F('position') - 1)
        self.save()
        

class Card(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    position = models.IntegerField()
    external_link = models.URLField(blank=True, null=True)
    
    list_id = models.ForeignKey(ListCard, on_delete=models.CASCADE)



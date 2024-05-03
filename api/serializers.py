from rest_framework import serializers
from .models import User, Board, ListCard, Card
from django.db.models import Max

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'subscription')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    # При создании пользователя хэшируем пароль
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    

class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ('id', 'name', 'created_date', 'user')
        

class ListCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListCard
        fields = ('id', 'title', 'color', 'position', 'board_id')
        extra_kwargs = {
            'position': {'read_only': True}
        }
    
    # При создании новой доски автоматический присваиваем позицию
    def create(self, validated_data):
        board_id = validated_data['board_id']
        max_position = ListCard.objects.filter(board_id=board_id).aggregate(Max('position'))['position__max'] or 0
        validated_data['position'] = max_position + 1
        return super().create(validated_data)
    

class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ('id', 'title', 'description', 'position', 'list_id', 'external_link')
        
    def create(self, validated_data):
        list_id = validated_data['list_id']
        max_position = Card.objects.filter(list_id=list_id).aggregate(Max('position'))['position__max'] or 0
        validated_data['position'] = max_position + 1
        return super().create(validated_data)
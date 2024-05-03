from rest_framework.views import APIView
from .serializers import UserSerializer, BoardSerializer, ListCardSerializer, CardSerializer
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import User, Board, ListCard, Card
import jwt, datetime
from rest_framework import status
from .pkg import checkJWT

# Для регистраций пользователя
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
# Логин и сохранения токена в куки
class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        
        user = User.objects.filter(email = email).first()
        
        if user is None:
            raise AuthenticationFailed('User not found!')
        
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')
        
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }
        
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        
        response = Response()
        
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token                 
        }
        
        return response
        
# Информация о пользователя, везде используем куки
class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if checkJWT(request) == False:
            raise AuthenticationFailed("Unauthenticated")
        
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        
        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        
        return Response(serializer.data)
    
# Используется для частичного обновления данныз пользователя, например тип подписки
class UserDetailView(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
        
    def patch(self, request, pk):
        if checkJWT(request) == False:
            raise AuthenticationFailed("Unauthenticated")
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# Выход из системы
class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response
    
### Board Views
# Создание новой доски, все апи точки доступны только для авторизованных пользователей, проверяем через куки
class BoardListCreate(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed("Unauthenticated")
        
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except:
            raise AuthenticationFailed("Unauthenticated")
        
        user = User.objects.filter(id=payload['id']).first()        
        
        boards = Board.objects.filter(user=user.id)
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)
    
    def post(self, request):

        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed("Unauthenticated")
        
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except:
            raise AuthenticationFailed("Unauthenticated")
        
        user = User.objects.filter(id=payload['id']).first() 
        
        request.data['user'] = user.id
        
        serializer = BoardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
# CRUD операций 
class BoardDetail(APIView):
    def get_object(self, pk):
        try:
            return Board.objects.get(pk=pk)
        except Board.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request, pk):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed("Unauthenticated")
        
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except:
            raise AuthenticationFailed("Unauthenticated")
        
        user = User.objects.filter(id=payload['id']).first()
         
        board = self.get_object(pk)
        if board.user.id != user.id:
            return Response({"error": "There are no boards with this ID"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = BoardSerializer(board)
        return Response(serializer.data)

    def put(self, request, pk):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed("Unauthenticated")
        
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except:
            raise AuthenticationFailed("Unauthenticated")
        
        user = User.objects.filter(id=payload['id']).first()
        request.data['user'] = user.id 
        board = self.get_object(pk)
        if board.user.id != user.id:
            return Response({"error": "There are no boards with this ID"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = BoardSerializer(board, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed("Unauthenticated")
        
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except:
            raise AuthenticationFailed("Unauthenticated")
        
        user = User.objects.filter(id=payload['id']).first() 
        board = self.get_object(pk)
        if board.user.id != user.id:
            return Response({"error": "There are no boards with this ID"}, status=status.HTTP_400_BAD_REQUEST)
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    
### List Views
class ListCardListCreate(APIView):
    
    def get(self, request):
        
        if checkJWT(request) == False:
            raise AuthenticationFailed("Unauthenticated")
        
        lists = ListCard.objects.all()
        serializer = ListCardSerializer(lists, many=True)
        return Response(serializer.data)
    
    def post(self, request):

        if checkJWT(request) == False:
            raise AuthenticationFailed("Unauthenticated")
        
        serializer = ListCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
class ListCardDetail(APIView):
    def get_object(self, pk):
        try:
            return ListCard.objects.get(pk=pk)
        except ListCard.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request, pk):
        if checkJWT(request) == False:
            raise AuthenticationFailed("Unauthenticated")
        list = self.get_object(pk)
        serializer = ListCardSerializer(list)
        return Response(serializer.data)

    def put(self, request, pk):
        if checkJWT(request) == False:
            raise AuthenticationFailed("Unauthenticated")
        list = self.get_object(pk)
        serializer = ListCardSerializer(list, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if checkJWT(request) == False:
            raise AuthenticationFailed("Unauthenticated")
        list = self.get_object(pk)
        list.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
### Move Position in List
class MoveListView(APIView):
    def get_object(self, pk):
        try:
            return ListCard.objects.get(pk=pk)
        except ListCard.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND
        
    def put(self, request, pk):
        if checkJWT(request) == False:
            raise AuthenticationFailed("Unauthenticated")
        list = self.get_object(pk)
        new_position = request.data.get('position', None)
        if new_position is None:
            return Response({'error': 'New position is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        list.move_position(new_position)
        return Response({'message': 'List moved successfully'}, status=status.HTTP_200_OK)

        
### Card Views
        
class CardListCreate(APIView):
    
    def get(self, request):
        
        if checkJWT(request) == False:
            raise AuthenticationFailed("Unauthenticated")
        
        cards = Card.objects.all()
        serializer = CardSerializer(cards, many=True)
        return Response(serializer.data)
    
    def post(self, request):

        if checkJWT(request) == False:
            raise AuthenticationFailed("Unauthenticated")
        
        serializer = CardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class CardDetail(APIView):
    def get_object(self, pk):
        try:
            return Card.objects.get(pk=pk)
        except Card.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND

    def get(self, request, pk):
        if checkJWT(request) == False:
            raise AuthenticationFailed("Unauthenticated")
        card = self.get_object(pk)
        serializer = CardSerializer(card)
        return Response(serializer.data)

    def put(self, request, pk):
        if checkJWT(request) == False:
            raise AuthenticationFailed("Unauthenticated")
        card = self.get_object(pk)
        serializer = CardSerializer(card, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if checkJWT(request) == False:
            raise AuthenticationFailed("Unauthenticated")
        card = self.get_object(pk)
        card.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
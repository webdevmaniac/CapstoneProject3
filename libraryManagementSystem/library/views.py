from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Book
from .serializers import BookSerializer
from .models import User
from .serializers import UserSerializer
from .models import Book, Transaction
from .serializers import BookSerializer, TransactionSerializer
from rest_framework.permissions import IsAuthenticated

class BookView(APIView):
    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckoutView(APIView):
    def post(self, request):
        book_id = request.data['book_id']
        user_id = request.data['user_id']
        book = Book.objects.get(id=book_id)
        user = User.objects.get(id=user_id)
        if book.number_of_copies > 0:
            transaction = Transaction.objects.create(user=user, book=book)
            book.number_of_copies -= 1
            book.save()
            return Response({'message': 'Book checked out successfully'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Book is not available'}, status=status.HTTP_400_BAD_REQUEST)

class ReturnView(APIView):
    def post(self, request):
        transaction_id = request.data['transaction_id']
        transaction = Transaction.objects.get(id=transaction_id)
        book = transaction.book
        book.number_of_copies += 1
        book.save()
        transaction.return_date = datetime.date.today()
        transaction.save()
        return Response({'message': 'Book returned successfully'}, status=status.HTTP_201_CREATED)


class AvailableBooksView(APIView):
    def get(self, request):
        available_books = Book.objects.filter(number_of_copies__gt=0)
        serializer = BookSerializer(available_books, many=True)
        return Response(serializer.data)

class SearchBooksView(APIView):
    def get(self, request):
        query = request.GET.get('query')
        books = Book.objects.filter(title__icontains=query) | Book.objects.filter(author__icontains=query) | Book.objects.filter(isbn__icontains=query)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

class LoginView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        user = User.objects.get(username=username)
        if user.check_password(password):
            return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

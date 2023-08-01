from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view,APIView
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Task
from .serializers import TaskSerializers
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import MultiPartParser,FormParser
import csv



@api_view(['GET'])
def apiOverview(request):
    api_urls = {
        'Create and List':'/task',
        'Read, Update, delete' : '/task<int:pk>',
        'Import CSV file': '/csvimp',
        'Export CSV file': '/csvexp'
    }
    
    return Response(api_urls)

    
class TaskListCreateView(ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializers
    renderer_classes = [JSONRenderer]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        #search functionality
        search_query = self.request.query_params.get('search',None)
        if search_query:
            queryset = queryset.filter(title__icontains=search_query) | queryset.filter(description__icontains=search_query)
        
        #ordering
        order_by = self.request.query_params.get('order_by',None)
        if order_by:
            queryset = queryset.order_by(order_by)
        
        #filter
        is_completed = self.request.query_params.get('is_completed',None)
        if is_completed:
            queryset = queryset.filter(completed=is_completed)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({"data": serializer.data }, status=status.HTTP_200_OK)
    

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
         serializer.save()
         return Response({"data":serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)


class TaskRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializers
    renderer_classes = [JSONRenderer]

    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)
        except:
            return Response({'message':'Invalid id'},status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"data": serializer.data}, status=status.HTTP_200_OK)
            return Response({'message':'Something went wrong'},status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'message':'Invalid id'},status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({'message':'deleted successfully'},status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({'message':'invalid id'},status=status.HTTP_404_NOT_FOUND)


class ExportCsvFileView(APIView):
   
    def get(self, request, *args, **kwargs):
        queryset = Task.objects.all()
        serializer = TaskSerializers(queryset, many=True)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="tasks.csv'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Title', 'Description', 'Completed'])

        for task in serializer.data:
            writer.writerow([task['id'], task['title'], task['description'], task['completed']])
        return response
    

class ImportCsvFileView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES["file"]
        try:
            decoded_file = file.read().decode()
            csv_reader = csv.DictReader(decoded_file.splitlines())
            data = list(csv_reader)
            
            serializer = TaskSerializers(data=data, many=True)
            if not serializer.is_valid():
                return Response(serializer.errors)
                
            for row in serializer.data:
                    
                title = row["title"]
                description = row["description"]
                completed = row["completed"]
                Task.objects.create(title=title, description=description, completed=completed)
            return Response({"message": "Uploaded Successfully"}, status=status.HTTP_200_OK)

            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


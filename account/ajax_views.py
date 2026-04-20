# account/ajax_views.py
from django.http import JsonResponse
from django.urls import reverse
from .models import Student
from django.contrib.auth.decorators import login_required

@login_required
def ajax_update_student_profile_picture(request):
    if request.method == "POST" and request.FILES.get('photo'):
        try:
            student_id = request.POST.get('student_id')
            student = Student.objects.get(pk=student_id)
            student.photo = request.FILES['photo']
            student.save()
            return JsonResponse({'status': 'success', 'url': student.photo.url})
        except Exception as e:
            # This ensures even an error returns JSON
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
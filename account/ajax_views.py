import json
import base64
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import Student

@login_required
@require_POST
def ajax_update_student_profile_picture(request):
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        image_data = data.get('image')

        if not image_data:
            return JsonResponse({'status': 'error', 'message': 'No image provided'}, status=400)

        format, imgstr = image_data.split(';base64,') 
        ext = format.split('/')[-1] 
        data_file = ContentFile(base64.b64decode(imgstr), name=f"student_{student_id}.{ext}")

        student = get_object_or_404(Student, id=student_id)
        student.photo = data_file 
        student.save()

        return JsonResponse({'status': 'success', 'url': student.photo.url})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def ajax_update_user_profile_picture(request):
    try:
        data = json.loads(request.body)
        image_data = data.get('image')

        if not image_data:
            return JsonResponse({'status': 'error', 'message': 'No image data.'}, status=400)

        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        data_file = ContentFile(base64.b64decode(imgstr), name=f"user_{request.user.id}.{ext}")

        profile = request.user.profile
        profile.profile_picture = data_file
        profile.save()

        return JsonResponse({'status': 'success', 'url': profile.profile_picture.url})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
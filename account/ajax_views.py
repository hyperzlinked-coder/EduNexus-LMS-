import json
import base64
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import Student, AdminProfile, Teacher

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
def ajax_update_admin_profile_picture(request):
    try:
        data = json.loads(request.body)
        image_data = data.get('image')

        if not image_data:
            return JsonResponse({'status': 'error', 'message': 'No image data.'}, status=400)

        # 1. I-decode ang Base64 image
        format, imgstr = image_data.split(';base64,')
        ext = format.split('/')[-1]
        data_file = ContentFile(base64.b64decode(imgstr), name=f"admin_{request.user.id}.{ext}")

        # 2. Gamitin ang tamang related_name ('admin_profile')
        # Gumamit ng get_or_create para hindi mag-error kung wala pang profile row
        profile, created = AdminProfile.objects.get_or_create(user=request.user)

        # 3. Gamitin ang tamang field name ('photo' imbes na 'profile_picture')
        profile.photo = data_file
        profile.save()

        return JsonResponse({
            'status': 'success', 
            'url': profile.photo.url  # Siguraduhing .photo.url ang gamit
        })

    except Exception as e:
        # Ito ang magpapakita sa console kung bakit nag-error (e.g. RelatedObjectDoesNotExist)
        print(f"Error updating profile: {e}") 
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    

@login_required
def ajax_update_teacher_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('photo'):
        try:
            # Get the teacher profile for the logged-in user
            teacher = request.user.teacher_profile
            teacher.photo = request.FILES['photo']
            teacher.save()
            
            return JsonResponse({
                'success': True,
                'new_photo_url': teacher.photo.url
            })
        except Teacher.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Teacher profile not found.'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request.'})  

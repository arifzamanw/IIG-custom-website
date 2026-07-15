from django.shortcuts import render, get_object_or_404, redirect
from .models import Job
from .forms import JobApplicationForm
from main.utils.bitrix_api import notify_hr_via_chat
from django.urls import reverse
def career_page(request):
    jobs = Job.objects.filter(is_active=True)  # Only active jobs
    return render(request, 'career/career_page.html', {'jobs': jobs})

def apply_for_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            job_application = form.save(commit=False)
            job_application.job = job
            job_application.save()
            cover_letter = job_application.cover_letter 
            job_link = reverse('apply_for_job', kwargs={'job_id': job.id}) 
            notify_hr_via_chat(
                full_name=job_application.name,
                phone=job_application.phone,
                email=job_application.email,
                job_title=job.title,
                resume_file=request.FILES.get('resume'),
                 job_link=job_link,
                cover_letter=cover_letter
                
            )


            return redirect('job_application_success')

    else:
        form = JobApplicationForm()

    return render(request, 'career/job_application.html', {'job': job, 'form': form})

def job_application_success(request):
    return render(request, 'career/job_application_success.html')

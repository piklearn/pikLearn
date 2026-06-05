from courses.models import Course
from django.views.generic import DetailView
from dal import autocomplete


class CourseAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        
        qs = Course.objects.all()  # به دست آوردن همه دوره‌ها


        query = self.request.GET.get('query', '')  # به دست آوردن query از URL
        if query:  
            qs = qs.filter(title__icontains=query)
        # فیلتر براساس ورودی کاربر
        # print("query:",self.q)
        # if self.q:  # اگر ورودی وجود داشته باشد
        #     qs = qs.filter(title__icontains=self.q)  # جستجو در عنوان

        return qs

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/detail.html'

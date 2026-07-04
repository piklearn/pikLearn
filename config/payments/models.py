from django.db import models
from users.models import CustomUser
from courses.models import Course

class Purchase(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='purchases')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='purchases')
    purchase_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=0, default=0)  # Changed to 0 decimal places
    payment_method = models.CharField(max_length=50, default='online')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)  # Made optional for now
    is_paid = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
    
    class Meta:
        verbose_name_plural = 'خرید ها'
        verbose_name = 'خرید'

class Discount(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='discounts')
    discount_code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.discount_code

    class Meta:
        verbose_name_plural = 'تخفیفات'
        verbose_name = 'تخفیف'
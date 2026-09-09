from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Expenses(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    amount = models.IntegerField()

    

    category_obj = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category_obj.name if self.category_obj else "No Category"

class Income(models.Model):
    user= models.ForeignKey(
        User,
        on_delete= models.CASCADE
        )
    amount = models.IntegerField()
    source = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.source

class Category(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
class Budget(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    amount = models.IntegerField()
    month = models.CharField(max_length=7)

    def __str__(self):
        return f"{self.month} - {self.amount}"
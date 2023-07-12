from django.db import models

class User(models.Model):
    name = models.CharField(max_length=30)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20)

    # 모델의 주요 정보를 나타내는 필드에 __str__ 를 사용하는것이 좋다.
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'users'
    

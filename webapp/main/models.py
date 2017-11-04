from django.db import models

class File(models.Model):
    file = models.FileField(upload_to='./')
    name = models.CharField(max_length = 20)

    def __str__(self):
        return self.name
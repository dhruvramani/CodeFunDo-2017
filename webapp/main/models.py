from django.db import models

class File(models.Model):
    file = models.FileField(upload_to='./')
    name = models.CharField(max_length = 20)

    def __str__(self):
        return self.name

class Image(models.Model):
    Iid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    imagepath = models.CharField(max_length=255)
    weight = models.DecimalField(max_digits=4, decimal_places=4, default="")
    warehouse = models.CharField(max_length=200)

    def __str__(self):
        return str(self.Iid)+ " " + str(self.name)
from django.db import models

# Create your models here.

class Yazar(models.Model):
    isim = models.CharField(max_length=100)
    soyisim = models.CharField(max_length=100)
    biyografi = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.isim}-{self.soyisim}" 
    


class Makale(models.Model):
    yazar = models.ForeignKey(Yazar, on_delete=models.CASCADE, related_name="makaleler")
    baslik = models.CharField(max_length=150)
    aciklama = models.CharField(max_length=250)
    metin = models.TextField()
    sehir = models.CharField(max_length=100)
    yayinlanma_tarihi = models.DateField()
    aktif = models.BooleanField(default=True)
    yaratilma_tarihi = models.DateTimeField(auto_now_add=True)
    güncellenme_tarihi = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.baslik

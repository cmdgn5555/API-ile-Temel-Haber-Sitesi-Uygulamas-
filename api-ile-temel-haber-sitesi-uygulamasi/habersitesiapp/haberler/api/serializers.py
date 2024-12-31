from rest_framework import serializers
from haberler.models import Makale, Yazar
from datetime import datetime, timedelta
from django.utils.timesince import timesince
from datetime import date
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator
import pytz  # zaman dilimi yönetimi için


# Model Serializerlar


class MakaleSerializer(serializers.ModelSerializer):
    
    makalenin_yayinlanma_tarihi_üzerinden_gecen_süre = serializers.SerializerMethodField()
    makalenin_son_güncellenme_tarihi_üzerinden_gecen_süre = serializers.SerializerMethodField()
    makalenin_son_gecerlilik_tarihine_kalan_gün_sayisi = serializers.SerializerMethodField()
    yazar_sehir_isimlerini_birlestir = serializers.SerializerMethodField()

    # Makale modelinin yazar alanı ilişkili olduğu Yazar modelinin str metodunu döndürür
    #yazar = serializers.StringRelatedField()
    
    # yazar = YazarSerializer(read_only=True) 

    yazar = serializers.PrimaryKeyRelatedField(queryset=Yazar.objects.all())
    
    
    # Eğer veritabanında zaten mevcut olan bir şehir ismi için hata verdirtiyoruz
    sehir = serializers.CharField(  
        validators = [
            UniqueValidator(
                queryset=Makale.objects.all(),
                message="Bu şehir adı zaten mevcut!!"
            )
        ]
    )

    class Meta:
        model = Makale
        fields = "__all__"
        #fields = ["yazar", "baslik", "aciklama"]
        #exclude = ["yazar", "baslik", "aciklama"]
        read_only_fields = ["id", "yaratilma_tarihi", "güncellenme_tarihi"]
        
        # Eğer veritabanında zaten var olan yazar başlık kombinasyonu için hata verdirtiyoruz
        validators = [
            UniqueTogetherValidator(
                queryset=Makale.objects.all(),
                fields=["yazar", "baslik"],
                message = "Bu yazar başlık kombinasyonu zaten mevcut!!" 
            )
        ]
    
    
    def get_makalenin_yayinlanma_tarihi_üzerinden_gecen_süre(self, obj):
        simdi = datetime.now()
        yayinlanma = obj.yayinlanma_tarihi

        if obj.aktif == True:
            zaman_farki = timesince(yayinlanma, simdi)
            return zaman_farki
        else:
            return "Aktif olmayan makalelerde yayınlanma tarihi üzerinden geçen süre gösterilemez.."
    

    def get_makalenin_son_güncellenme_tarihi_üzerinden_gecen_süre(self, obj): 
        simdi = datetime.now(pytz.UTC)
        son_güncellenme = obj.güncellenme_tarihi

        if obj.aktif == True:
            zaman_farki = timesince(son_güncellenme, simdi)
            return zaman_farki
        else:
            return "Aktif olmayan makalelerde son güncellenme tarihi üzerinden geçen süre gösterilemez.."
    

    def get_makalenin_son_gecerlilik_tarihine_kalan_gün_sayisi(self, obj):
        son_tarih = date(2026, 1, 1)

        if son_tarih < date.today():
            return "Makalenin son geçerlilik tarihi bugünün tarihinden daha eski bir tarih olamaz.."
        
        else:
        
            if obj.aktif == True:
                kalan_gün_sayisi = (son_tarih - date.today()).days
                return f"{kalan_gün_sayisi} gün"
            else:
                return "Aktif olmayan makalelerde kalan gün sayısı gösterilemez.."
    

    def get_yazar_sehir_isimlerini_birlestir(self, obj):
        if obj.aktif == True:
            return f"{obj.yazar} - {obj.sehir}"
        else:
            return "Aktif olmayan makalelerde yazar şehir isimleri birleştirilemez.."
    

    def validate_yayinlanma_tarihi(self, tarihdegeri):
        bugün = date.today()
        if tarihdegeri > bugün:
            raise serializers.ValidationError("Yayınlanma tarihi ileri bir tarih olamaz..")
        return tarihdegeri



class YazarSerializer(serializers.ModelSerializer):
    # Burada makale bilgisi eklemeden yazar yaratmanın yolunu açıyoruz
    # makaleler = MakaleSerializer(many=True, read_only=True)

    makaleler = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name="makale-detayi"
    )

    class Meta:
        model = Yazar
        fields = "__all__"







    
        













# Standart Serializer

class MakaleDefaultSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    yazar = serializers.CharField()
    baslik = serializers.CharField()
    aciklama = serializers.CharField()
    metin = serializers.CharField()
    sehir = serializers.CharField()
    yayinlanma_tarihi = serializers.DateField()
    aktif = serializers.BooleanField()
    yaratilma_tarihi = serializers.DateTimeField(read_only=True)
    güncellenme_tarihi = serializers.DateTimeField(read_only=True)


    def create(self, validated_data):
        print(validated_data)
        return Makale.objects.create(**validated_data)

    
    def update(self, instance, validated_data):
        instance.yazar = validated_data.get("yazar", instance.yazar)
        instance.baslik = validated_data.get("baslik", instance.baslik)
        instance.aciklama = validated_data.get("aciklama", instance.aciklama)
        instance.metin = validated_data.get("metin", instance.metin)
        instance.sehir = validated_data.get("sehir", instance.sehir)
        instance.yayinlanma_tarihi = validated_data.get("yayinlanma_tarihi", instance.yayinlanma_tarihi)
        instance.aktif = validated_data.get("aktif", instance.aktif)
        instance.save()
        return instance
    

    
    # Obje seviyesinde doğrulama
    
    def validate(self, data):  
        
        if data["baslik"] == data["aciklama"]:
           raise serializers.ValidationError("Başlık ve açıklama alanları aynı olamaz..")
        
        
        elif len(data["yazar"]) >= len(data["metin"]):
            raise serializers.ValidationError("Yazar adı metin yazısından uzun olamaz..")
        
        elif not ((data["yazar"][0].isupper()) and (data["baslik"][0].isupper()) and (data["aciklama"][0].isupper())):
            raise serializers.ValidationError("Yazar/Başlık/Açıklama alanlarında ilk harfi büyük yazınız lütfen..")
        
        return data
    
    
    
    # Alan seviyesinde doğrulama

    def validate_yazar(self, value):
        harfler = ["ç", "ğ", "ı", "ö", "ü", "Ç", "Ğ", "I", "Ö", "Ü"]
        bulunan_harfler = [harf for harf in harfler if harf in value]

        if bulunan_harfler:
                raise serializers.ValidationError(f"Yazar adı içinde {", ".join(bulunan_harfler)} harfi/harfleri bulunamaz.")
        return value
    
    

    def validate_sehir(self, value):
        rakamlar = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        bulunan_rakamlar = [rakam for rakam in rakamlar if rakam in value]

        if bulunan_rakamlar:
            raise serializers.ValidationError(f"Şehir adı içinde {", ".join(bulunan_rakamlar)} rakamı/rakamları bulunamaz.")
        return value
    

    
    def validate_aciklama(self, value):
        if len(value) <= 15:
            raise serializers.ValidationError(f"Açıklama alanı 15 karakterden az olamaz. Siz {len(value)} karakter girdiniz.")
        return value
    


    def validate_yayinlanma_tarihi(self, value):
        if value > datetime.now().date():
            raise serializers.ValidationError(f"Yayınlanma tarihi olarak {value} tarihini girdiniz. Yayınlanma tarihi bugünün tarihinden ileri bir tarih olamaz..")
        return value
    
    
    

from django.db import models

class Coordinate(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    logged_at = models.DateTimeField(auto_now_add=True,blank=True)

    def __str__(self):
        return f"({self.latitude}, {self.longitude})"

class TravelHistory(models.Model):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE)
    logged_coordinates = models.ManyToManyField(Coordinate)
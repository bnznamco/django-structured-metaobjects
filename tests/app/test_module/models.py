from django.db import models


class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True, default="")

    class Meta:
        app_label = "test_module"

    def __str__(self):
        return self.title

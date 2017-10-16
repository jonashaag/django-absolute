from django.conf.urls import url

urlpatterns = [
    url(r'^test$', lambda x:x, name='test_url')
]

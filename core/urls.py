from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from cric.views import home
from cric.views import login_page,register,logout_view,result,dash,profile, ask_ai_page, proxy_llm,feedback,feedback_view,upcoming
from cric.views import team_detail,team_list,player_detail,player_list,articles,result_model2,product

urlpatterns = [
    path('',dash,name="dash"),
    path('home/', home, name="home"),
    path('login_page/',login_page,name="login_page"),
    path('result_model2/',result_model2,name="result_model2"),
    path('logout_view/', logout_view, name='logout'),
    path('register/',register,name="register"),
    path('result/',result,name="result"),
    path('profile/',profile,name="profile"),
    path("ask-ai_page/", ask_ai_page, name="ask_ai_page"), 
    path('feedback/', feedback, name='feedback'),
    path('feedback_view/',feedback_view,name="feedback_view"),
    path('product/',product,name="product"),
    path('teams/', team_list, name='team_list'),
    path('teams/<int:team_id>/', team_detail, name='team_detail'),
    path('upcoming/', upcoming, name='upcoming'),
    path('players/', player_list, name='player_list'),
    path('players/<int:player_id>/', player_detail, name='player_detail'),
    path('articles/',articles,name="articles"),
    path('admin/', admin.site.urls),
    path("proxy_llm/", proxy_llm, name="proxy_llm"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
from django.urls import path

from .views import *

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('collect_user_data/', CollectData.as_view(), name='collect_user_data'),
    path('reset_the_questionnaire_data/', reset_the_questionnaire_data, name='reset_the_questionnaire_data'),
    path('show_menu/', go_to_monday, name='show_menu'),
    path('regenerate_menu/', regenerate_menu, name='regenerate_menu'),
    path('show_menu/<slug:day_slug>/', ShowMenu.as_view(), name='show_menu_by_days'),
    path('dishes/', Dishes.as_view(), name='dishes'),
    path('dishes/search', SearchView.as_view(), name='search'),
    path('ingredients/', Ingredients.as_view(), name='ingredients'),
    path('ingredients/<int:ing_id>/', DishesByIngredient.as_view(), name='show_dishes_by_ing'),
    path('cats/', Categories.as_view(), name='cats'),
    path('about/', about, name='about'),
    path('contacts/', contacts, name='contacts'),
    path('signin/', RegisterUser.as_view(), name='signin'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),

]
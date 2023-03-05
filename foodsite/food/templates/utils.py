from food.models import Menu

menu = [{'title': 'Сгенерировать меню', 'url_name': 'collect_user_data'},
        {'title': 'Показать меню', 'url_name': 'show_menu'},
        {'title': 'Рецепты', 'url_name': 'dishes'},
        {'title': 'Категории', 'url_name': 'cats'},
        {'title': 'Ингридиенты', 'url_name': 'ingredients'},
        {'title': 'О сайте', 'url_name': 'about'},
        {'title': 'Контакты', 'url_name': 'contacts'}
        ]


class DataMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        user_menu = menu.copy()
        if not self.request.user.is_authenticated:
            user_menu.pop(0)
            user_menu.pop(1)
        else:
            menu_exists = Menu.objects.filter(user=self.request.user).exists()
            if menu_exists:
                user_menu.pop(0)
            else:
                user_menu.pop(1)
        context['menu'] = user_menu
        return context

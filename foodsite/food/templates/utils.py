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


def get_filters(request):
    filters = {}
    min_calories = request.GET.get('min_cal')
    max_calories = request.GET.get('max_cal')
    min_active_cooking_time = request.GET.get('min_a_time')
    max_active_cooking_time = request.GET.get('max_a_time')
    min_total_cooking_time = request.GET.get('min_t_time')
    max_total_cooking_time = request.GET.get('max_t_time')
    if min_calories:
        filters['calories__gte'] = min_calories
    if max_calories:
        filters['calories__lte'] = max_calories
    if min_active_cooking_time:
        filters['active_cooking_time__gte'] = min_active_cooking_time
    if max_active_cooking_time:
        filters['active_cooking_time__lte'] = max_active_cooking_time
    if min_total_cooking_time:
        filters['total_cooking_time__gte'] = min_total_cooking_time
    if max_total_cooking_time:
        filters['total_cooking_time__lte'] = max_total_cooking_time
    return filters


days = {
    'monday': 'Понедельник',
    'tuesday': 'Вторник',
    'wednesday': 'Среда',
    'thursday': 'Четверг',
    'friday': 'Пятница',
    'saturday': 'Суббота',
    'sunday': 'Воскресенье'
}
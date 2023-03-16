// Находим кнопку "Фильтры" и форму фильтрации
var filterButton = document.querySelector('.filter-button');
var filterForm = document.querySelector('.filter-form');

// Скрываем форму фильтрации при загрузке страницы
filterForm.style.display = 'none';

// Добавляем обработчик события клика на кнопку "Фильтры"
filterButton.addEventListener('click', function() {
  // Если форма скрыта, показываем её, иначе скрываем
  if (filterForm.style.display === 'none') {
    filterForm.style.display = 'block';
  } else {
    filterForm.style.display = 'none';
  }
});
Этот код находит кнопку "Фильтры" и форму фильтрации на странице и добавляет обработчик события клика на кнопку. Когда пользователь кликает на кнопку, JavaScript проверяет, скрыта ли форма фильтрации. Если форма скрыта, JavaScript показывает её, иначе скрывает.

Обратите внимание, что для этого кода нужно, чтобы у кнопки был класс filter-button, а у формы - класс filter-form. Если у вас классы отличаются, замените их в коде на нужные.






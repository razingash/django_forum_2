//not used
document.addEventListener('DOMContentLoaded', function() {
    const items = document.querySelectorAll('.settings_menu__item');
    items[0].classList.add('current__item');

    items.forEach(function(item) {
        item.addEventListener('click', function() {

          items.forEach(function(innerItem) {
            innerItem.classList.remove('current__item');
          });

          item.classList.add('current__item');
        });
    });
});
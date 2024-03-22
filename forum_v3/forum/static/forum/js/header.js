const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
    document.querySelector('html').setAttribute('data-mode', savedTheme);
}

document.addEventListener('DOMContentLoaded', function () {
    const crossButton = document.querySelector('.header__svg-cross');
    const crossButton2 = document.querySelector('.header__search');
    const searchContainer = document.querySelector('.search__container');
    const searchResults = document.querySelector('.search__results')
    //switching theme
    const changeThemeButton = document.querySelector('.theme__button');
    const htmlElement = document.querySelector('html');

    let items = document.querySelectorAll('.subject__item');
    items[0].classList.add('active');

    crossButton.addEventListener('click', function() {
        searchContainer.classList.remove('active');
    });
    crossButton2.addEventListener('click', function() {
        searchContainer.classList.add('active');
    });

    items.forEach(function (item) {
        item.addEventListener('click', function () {

            items.forEach(function (innerItem) {
                innerItem.classList.remove('active');
            });
            searchResults.innerHTML = '';
            item.classList.add('active');
        });
    });

    //switching theme
    changeThemeButton.addEventListener('click', function () {
        const currentTheme = htmlElement.getAttribute('data-mode');
        if (currentTheme === 'dark') {
            htmlElement.setAttribute('data-mode', 'light');
            localStorage.setItem('theme', 'light');
        } else {
            htmlElement.setAttribute('data-mode', 'dark');
            localStorage.setItem('theme', 'dark');
        }
    });
});
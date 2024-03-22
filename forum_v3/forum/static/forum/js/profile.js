//user card
document.addEventListener('DOMContentLoaded', function() {
    const profileCard = document.querySelector('.profile__card');
    const closeBtn = document.querySelector('.card__close');
    const profileExtension = document.querySelector('.profile__extension');

    closeBtn.addEventListener('click', function() {
        profileCard.style.display = 'none';
    });
    profileExtension.addEventListener('click', function() {
        if (profileCard.style.display === 'flex') {
            profileCard.style.display = 'none';
        } else {
            profileCard.style.display = 'flex';
        }
    });
});
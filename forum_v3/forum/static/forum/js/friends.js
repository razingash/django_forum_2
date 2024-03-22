document.addEventListener("DOMContentLoaded", function() {
    const friendRemove = document.querySelectorAll(".friend__remove");
    const deleteJoke = document.querySelector(".delete_joke");
    const deleteFriendField = document.querySelector(".delete_friend_field");

    function toggleDeleteFriendField() {
        if (deleteFriendField.style.display === "flex") {
            deleteFriendField.style.display = "none";
        } else {
            deleteFriendField.style.display = "flex";
        }
    }

    friendRemove.forEach(function(removeButton) {
        removeButton.addEventListener("click", function() {
            toggleDeleteFriendField();

            const userId = this.closest(".content-field__friend").getAttribute("id");

            deleteFriendField.setAttribute("data-user-id", userId);
        });
    });

    deleteJoke.addEventListener("click", function() {
        deleteFriendField.style.display = "none";
    });
});


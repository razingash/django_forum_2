document.addEventListener('DOMContentLoaded', function() {
    const writeCheckboxes = document.querySelectorAll('.write_checkbox');

    // Проходимся по каждому элементу с классом "write_checkbox"
    writeCheckboxes.forEach(checkbox => {
        // Добавляем обработчик события на изменение состояния чекбокса
        checkbox.addEventListener('change', function() {
            // Если текущий чекбокс активирован
            if (this.checked) {
                // Деактивируем все остальные чекбоксы write_checkbox
                writeCheckboxes.forEach(otherCheckbox => {
                    if (otherCheckbox !== this) {
                        otherCheckbox.checked = false;

                        // Находим родительский элемент comments__field
                        const commentsField = otherCheckbox.closest('.comments__field');
                        // Скрываем editing__field для деактивированного чекбокса
                        commentsField.querySelector('.editing__field').style.display = 'none';
                    }
                });

                // Находим родительский элемент comments__field
                const commentsField = this.closest('.comments__field');

                // Находим элемент editing__field внутри текущего comments__field
                const editingField = commentsField.querySelector('.editing__field');

                // Если в классе чекбокса есть "edit__checkbox"
                if (this.classList.contains('edit__checkbox')) {
                    // Находим элемент comment внутри текущего comments__field
                    const comment = commentsField.querySelector('.comment');

                    // Находим textarea внутри editing__field и копируем текст из comment
                    editingField.querySelector('.editing__textarea').value = comment.textContent;
                }

                // Показываем editing__field для активированного чекбокса
                editingField.style.display = 'flex';
            }
        });
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const complaints = document.querySelectorAll(".movement__complaint");
    const complaintField = document.querySelector(".complaint__field");
    const complaintClose = document.querySelector(".complaint__close");

    function toggleComplaintField() {
        if (complaintField.style.display === "flex") {
            complaintField.style.display = "none";
        } else {
            complaintField.style.display = "flex";
        }
    }
    // handler for clicking on block movement__complaint
    complaints.forEach(function(complaint) {
        complaint.addEventListener("click", function() {
            toggleComplaintField();
            let reportedUser = this.closest(".comment__field").querySelector(".comment__nickname").innerText;

            document.querySelector(".reported__user").innerText = reportedUser;
        });
    });
    complaintClose.addEventListener("click", function() {
        complaintField.style.display = "none";
    });
});
//editing
document.addEventListener('DOMContentLoaded', function () {
    const editCheckboxes = document.querySelectorAll('.editing_checkbox');
    const editingFields = document.querySelectorAll('.editing__field');
    const annihilateButtons = document.querySelectorAll('.movement__annihilate');
    let lastCheckedIndex = -1;

    editCheckboxes.forEach((checkbox, index) => {
        checkbox.addEventListener('change', function () {
            const form = editingFields[index];
            const textarea = form.querySelector('.editing__textarea');
            const isChecked = checkbox.checked;
            const commentField = checkbox.closest('.comment__field');
            const commentElement = commentField.querySelector('.comment');

            //if anouther checkbox was selected, then reset state of previous
            if (lastCheckedIndex !== -1 && lastCheckedIndex !== index) {
                const lastForm = editingFields[lastCheckedIndex];
                const lastTextarea = lastForm.querySelector('.editing__textarea');
                const lastCommentField = editCheckboxes[lastCheckedIndex].closest('.comment__field');
                const lastCommentElement = lastCommentField.querySelector('.comment');
                lastTextarea.value = lastCommentElement.textContent.trim();
                lastForm.style.display = 'none';
                lastCommentElement.style.display = 'block';
            }

            // setting state of current checkbox
            textarea.value = isChecked ? commentElement.textContent.trim() : '';
            form.style.display = isChecked ? 'flex' : 'none';
            commentElement.style.display = isChecked ? 'none' : 'block';
            lastCheckedIndex = isChecked ? index : -1;
        });
    });

    editingFields.forEach((form, index) => {
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            const textarea = form.querySelector('.editing__textarea');
            const newCommentText = textarea.value;
            const commentField = form.closest('.comment__field');
            const commentElement = commentField.querySelector('.comment');
            commentElement.textContent = newCommentText;
            form.style.display = 'none';
            editCheckboxes[index].checked = false;
            commentElement.style.display = 'block';
        });
    });

    //annihilation
    annihilateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const commentsField = button.closest('.comments__field');
            commentsField.remove();
        });
    });
});

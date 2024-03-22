$(document).ready(function () {
    const csrfToken = $('meta[name=csrf-token]').attr('content');
    const sender_id = $(this).data('profile-id');
    const currentUrl = window.location.href
    $('.add_friend').click(function (event) {
        event.preventDefault();
        $.ajax({
            type: 'POST',
            url: currentUrl,
            headers: {
                'X-CSRFToken': csrfToken
            },
            data: {
                'event': 'friendship',
                'sender_id': sender_id
            },
            success: function (response) {
                console.log('POST запрос успешно отправлен');
                location.reload();
            },
            error: function (xhr, status, error) {
                console.error('Error during sending POST request:', error);
            }
        });
    });
});

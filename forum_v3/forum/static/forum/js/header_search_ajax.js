$(document).ready(function () {
    const csrfToken = $('meta[name=csrf-token]').attr('content');

    function sendPostRequest(search_request) {
        if (search_request.length >= 4) {
            let request_type = $('.subject__item.active').attr('id');
            $.ajax({
                type: 'POST',
                url: /forum/,
                headers: {
                    'X-CSRFToken': csrfToken
                },
                data: {
                    'request_type': request_type,
                    'search_request': search_request
                },
                success: function (response) {
                    if (response.message !== 'nothing founded') {
                        $('.search__results').empty();
                        console.log(response)
                        console.log(response.type)
                        if (response.type === 'result_users') {
                            response.message.forEach(function (item) {
                                $('.search__results').append('<a href="' + item.get_absolute_url + '" class="search__result">' + item.username + '</a>');
                            });
                        } else if (response.type === 'result_discussions') {
                            response.message.forEach(function (item) {
                                $('.search__results').append('<a href="' + item.get_absolute_url + '" class="search__result">' + item.theme + '</a>');
                            });
                        }
                    } else {
                        $('.search__results').empty().append('<div class="search__result_empty">nothing founded</div>');
                        console.log('Ничего не найдено');
                    }
                },
                error: function (xhr, status, error) {
                    console.error('Error during sending POST request:', error);
                }
            });
        } else {
            $('.search__results').empty().append('<div class="search__result_empty">nothing founded</div>');
        }
    }

    $('.search__form__input').on('input', function () {
        const search_request = $(this).val();
        sendPostRequest(search_request);
    });
});
//sorting
$(document).ready(function () {
    const currentUrl = window.location.href
    const csrfToken = $('meta[name=csrf-token]').attr('content');
    const userId = $('meta[name="user-id"]').attr('content');
    $('.bunch__apply').on('click', function () {
        let tags_p = [];
        let tags_n = [];
        let p_orients_p = [];
        let p_orients_n = [];
        let minLvl = $('#author__lvl__minimal').val().trim();
        let maxLvl = $('#author__lvl__maximal').val().trim();
        let level_limits = {};

        if (!isNaN(minLvl)) {
            level_limits['min'] = minLvl;
        }
        if (!isNaN(maxLvl)) {
            level_limits['max'] = maxLvl;
        }

        $('.bunch__tag__checkbox').each(function () {
            let id = $(this).attr('id');
            let value = $(this).val();

            if (value === '1') {
                tags_p.push(id);
            } else if (value === '2') {
                tags_n.push(id);
            }
        });
        $('.p_orientation__checkbox').each(function () {
            // getting id and value of current element
            let id = $(this).attr('id');
            let value = $(this).val();

            if (value === '1') {
                p_orients_p.push(id);
            }
            if (value === '2') {
                p_orients_n.push(id);
            }
        });

        $.ajax({
            type: "POST",
            headers: {
                'X-CSRFToken': csrfToken
            },
            url: currentUrl,
            contentType: 'application/json',
            data: JSON.stringify({
                'request_type': 'advanced_search',
                'level_limits': level_limits,
                'tags_p': tags_p,
                'tags_n': tags_n,
                'p_orients_p': p_orients_p,
                'p_orients_n': p_orients_n
            }),
            success: function (response) {
                if (response.reload_page) {
                    location.reload();
                }
            },
            error: function (xhr, status, error) {
                console.error('Error during sending POST request:', error);
            }
        });
    });
    //grading
    $('.grade_up').on('click', function () {
        let discussion_id = $(this).closest('.preview').attr('id');
        $.post({
            url: currentUrl,
            headers: {
                'X-CSRFToken': csrfToken
            },
            data: {
                'request_type': 'discussion_grade',
                'action': 'up',
                'discussion_id': discussion_id,
                'user_id': userId
            },
            success: function (response) {
                console.log(response.new_rating)
                $('#' + discussion_id + ' .preview-rating').text(response.new_rating);
            },
            error: function (xhr, status, error) {
                console.error('Error during sending POST request:', error);
            }
        });
    });
    $('.grade_down').on('click', function () {
        let discussion_id = $(this).closest('.preview').attr('id');
        $.post({
            url: currentUrl,
            headers: {
                'X-CSRFToken': csrfToken
            },
            data: {
                'request_type': 'discussion_grade',
                'action': 'down',
                'discussion_id': discussion_id,
                'user_id': userId
            },
            success: function (response) {
                console.log(response.new_rating)
                $('#' + discussion_id + ' .preview-rating').text(response.new_rating);
            },
            error: function (xhr, status, error) {
                console.error('Error during sending POST request:', error);
            }
        });
    });
});
$(document).ready(function () {
    $("a.comment-action").click(function (event) {
        event.preventDefault();
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                var csrftoken = $.cookie('csrftoken');
                if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });
        $.ajax({
            var: post_id = $(this).data('post_uuid'),
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/comments/submit_comment/",
            data: JSON.stringify({
                'content': $('textarea#post_comment_on_' + post_id).val(),
                'post_uuid': $(this).data('post_uuid'),
                'pleb': $(this).data('pleb')
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json"
        });
    });
});


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
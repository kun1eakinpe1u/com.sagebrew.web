/*global $, jQuery, ajax_security*/
$(document).ready(function () {
    "use strict";
    $(".submit_question-action").click(function (event) {
        event.preventDefault();
        $(".submit_question-action").attr("disabled", "disabled");
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings);
            }
        });
        var tags = $('#sb_tag_box').val();
        if (tags === "") {
            tags = [];
        }

        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: $(this).data('url'),
            data: JSON.stringify({
                'title': $('input#title_id').val(),
                'content': $('textarea#wmd-input-0').val(),
                'tags': tags
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                window.location.href = data.url;
            },
            error: function (XMLHttpRequest) {
                if (XMLHttpRequest.status === 500) {
                    $("#server_error").show();
                }
            }
        });
    });
    $(".cancel_question-action").click(function () {
        window.location.href = "/conversations/";
    });
});
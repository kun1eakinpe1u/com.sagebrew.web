/*global $, jQuery, enable_single_post_functionality*/
$(document).ready(function () {
    "use strict";
    // This function hits the Post API and saves off a given post from a user
    $(".post-action").click(function (event) {
        $("#sb_btn_post").attr("disabled", "disabled");
        event.preventDefault();

        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/v1/profiles/" + $('#user_info').data('page_user_username') + "/wall/?html=true",
            data: JSON.stringify({
                'content': $('textarea#post_input_id').val()
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                $('textarea#post_input_id').val("");
                $("#wall_app").prepend(data.html);
                $("#sb_btn_post").removeAttr("disabled");
                enable_single_post_functionality(data.ids);
                var placeHolder = $("#js-wall_temp_message");
                if (placeHolder !== undefined) {
                    placeHolder.remove();
                }
            },
            error: function () {
                $("#sb_btn_post").removeAttr("disabled");
            }
        });
    });
});

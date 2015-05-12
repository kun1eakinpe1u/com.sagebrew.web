$(document).ready(function () {
    $('.action').each(function(i,obj){

        $.ajax({
            xhrFields: {withCredentials: true},
            type: "GET",
            url: "/privilege/check/action/",
            data: {
                'action': $(this).data("action")
            },
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data) {
                if (data['detail'] === 'forbidden') {
                }
                else {
                    var button_obj = $(data['html_object']);
                    button_obj.prop('disabled', false);
                    button_obj.attr("data-url", data['url']);
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
});
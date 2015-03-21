$(document).ready(function(){
    console.log('test');
    $(".submit_edit-action").click(function(e){
        e.preventDefault();
        var title_success;
        var uuid = $(this).data('object_uuid');
        var type = $(this).data("object_type");
        var timestamp = $(this).data("datetime");
        console.log("test in click");
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/edit/edit_question_title_api/",
            data: JSON.stringify({
                'question_title': $("#question_title_id").val(),
                'object_uuid': uuid,
                'object_type': type
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                title_success = true
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                title_success = false;
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });
        $.ajaxSetup({
            beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
        });
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/edit/edit_object_content_api/",
            data: JSON.stringify({
                'content': $('textarea#wmd-input-0').val(),
                'object_uuid': uuid,
                'object_type': type
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                if (title_success) {
                    var current_url = window.location.href;
                    window.location.href = current_url.split("/edit")[0];
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                if(XMLHttpRequest.status === 500){
                    $("#server_error").show();
                }
            }
        });
    })
});
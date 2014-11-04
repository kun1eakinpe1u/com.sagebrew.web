$( document ).ready(function() {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            ajax_security(xhr, settings)
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "POST",
        url: "/questions/query_questions_api/",
        data: JSON.stringify({
           'current_pleb': $(".query_questions-action").data('current_pleb'),
           'sort_by': $(".query_questions-action").data('sort_by')
        }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            $("#question_wrapper").append(data);
            enable_post_functionality()
        }
    });
	$("a.query_questions-action").click(function(event){
		event.preventDefault();
		$.ajaxSetup({
		    beforeSend: function (xhr, settings) {
                ajax_security(xhr, settings)
            }
		});
	   	$.ajax({
			xhrFields: {withCredentials: true},
			type: "POST",
			url: "/questions/query_questions_api/",
			data: JSON.stringify({
               'current_pleb': $(this).data('current_pleb'),
               'sort_by': $(this).data('sort_by')
			}),
			contentType: "application/json; charset=utf-8",
			dataType: "json",
            success: function (data) {
                $("#question_wrapper").empty();
                $("#question_wrapper").append(data);
                enable_post_functionality()
            }
		});
	});
});


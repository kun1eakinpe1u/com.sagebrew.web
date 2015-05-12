$( document ).ready(function() {
        var timeOutId = 0;
        var solutionLoadFxn = function () {
            $.ajax({
                xhrFields: {withCredentials: true},
                type: "GET",
                url: "/v1/solutions/" + $('#submit_solution').data('object_uuid') + "/",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function (data) {
                    var solution_content = $('#wmd-input-0');
                    solution_content.html("");
                    solution_content.append(data['content']);
                    var solution_preview = $("#wmd-preview-0");
                    solution_preview.html("");
                    solution_preview.append(data['html_content']);
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    errorDisplay(XMLHttpRequest);
                    timeOutId = setTimeout(ajaxFn, 1000);
                }
            });
        };
        solutionLoadFxn();
});
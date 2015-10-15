/*global $, ajaxSecurity, errorDisplay*/
$(document).ready(function () {
    $("#submit_goal").click(function (event) {
        var $this = $(this);
        $this.attr("disabled", "disabled");
        event.preventDefault();
        var campaignId = $("#submit_goal").data('object_uuid');
        $.ajax({
            xhrFields: {withCredentials: true},
            type: "POST",
            url: "/v1/campaigns/" + campaignId + "/goals/?html=true",
            data: JSON.stringify({
                "title": $("#goal_title").val(),
                "summary": $("#goal_summary").val(),
                "description": $("#goal_description").val(),
                "pledged_vote_requirement": $("#goal_vote_req").val(),
                "monetary_requirement": $("#goal_monetary_req").val() * 100,
                "total_required": $("#goal_monetary_req").val() * 100,
                "pledges_required": $("#goal_vote_req").val()
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                $this.attr("disabled", false);
                $("#existing_goals").append(data);
                $.notify("Goals successfully created!", {type: 'success'});
                $("#goal_vote_req").val("");
                $("#goal_monetary_req").val("");
                $("#goal_description").val("");
                $("#goal_summary").val("");
                $("#goal_title").val("");
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                errorDisplay(XMLHttpRequest);
            }
        });
    });
});
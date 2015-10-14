/**
 * @file
 * Authed User Controller. Loaded on every page loaded by a logged in user.
 */
var navbar = require('./partials/navbar').initNavbar;



/**
 *  Scope - User Authed
 *  Adds an event handler to page unload that ajax posts all the user's actions that occured during the page.
 *  TODO: Stop doing this.
 *  Not only are non-async ajax calls deprecated it holds the page load up for the user.
 *  They can't even start loading the next page until this is completed.
 */
function collectAuthedActions() {
    $(document).ready(function () {
        "use strict";
        window.onbeforeunload = function () {
            var objectList = [];
            $(".js-page-object").each(function () {
                objectList.push($(this).data('object_uuid'));
            });
            if (objectList.length) {
                $.ajax({
                    xhrFields: {withCredentials: true},
                    type: "POST",
                    async: false,
                    url: "/docstore/update_neo_api/",
                    data: JSON.stringify({
                        'object_uuids': objectList
                    }),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    error: function (XMLHttpRequest) {
                        if (XMLHttpRequest.status === 500) {
                            $("#server_error").show();
                        }
                    }
                });
            }
        };
    });
}





export function init() {
    collectAuthedActions();

    $(document).ready(function() {
        navbar();
        console.log("Hello");
    });

}
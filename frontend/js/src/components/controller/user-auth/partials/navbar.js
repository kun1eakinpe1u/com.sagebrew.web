/**
 * @file
 * All the functionality for the navbar.
 * TODO: Reorganize.
 * App: .app-navbar
 */
var request = require('api').request,
    notificationTemplate = require('controller/user-auth/templates/notifications.hbs'),
    settings = require('settings').settings;


/**
 *  Scope - User Authed
 *  All things relating to the navbar.
 */
export function navbar() {
    var $navbar = $(".app-navbar");

    //
    // Load navbar count(s)
    request.get({url: "/v1/me/notifications/"})
        .done(function(data) {
            //Notifications
            if (data.count) {
                var notifications = notificationTemplate({
                    default_profile: settings.default_profile_pic,
                    notifications: data.results
                });
                $('#notification_wrapper').append(notifications);
                request.get({url: "/v1/me/notifications/unseen/"}).done(function (data) {
                    if (data.unseen > 0) {
                        $('#js-notification_notifier_wrapper').append('<span class="navbar-new sb_notifier" id="js-sb_notifications_notifier">' + data.unseen + '</span>');
                    }
                });
            } else {
                $('#notification_wrapper').append("No new notifications.");
            }
        });
    //Rep
    $("#reputation_total").append(settings.profile.reputation);

    //
    // Bind Navbar Events.
    $navbar
        // Shows the notifications when the notification icon is clicked
        // Notify backend user has viewed the notifications.
        .on('click', '.js-show-notifications', function() {
            if ($('#js-notification_notifier_wrapper').children().length > 0) {
                request.get({url: "/v1/me/notifications/?seen=true"})
                    .done(function () {
                        $('#js-sb_notifications_notifier').remove();
                });
            }

        })
        //
        // Show Rep
        .on('click', '.js-show-reputation', function() {
            request.patch({
                url: "/v1/me/",
                data: JSON.stringify({
                    "reputation_update_seen": true,
                    "update_time": true
                })
            }).done(function () {
                $('#js-reputation-change-notifier').remove();
            });
        })
        //
        // Shows the friend requests when the friend request icon is clicked
        .on('click', '.js-show-friend-requests', function() {
            if ($('#js-sb_friend_request_notifier').length > 0) {
                request.get({url: "/v1/me/friend_requests/?seen=true"})
                .done(function() {
                     $('#js-sb_friend_request_notifier').remove();
                });
            }
        });
    //
    // Search
    $(".full_search-action").click(function() {
        var search_param = ($('#sb_search_input').val());
        window.location.href = "/search/?q=" + search_param + "&page=1&filter=general";
    });
    $("#sb_search_input").keyup(function(event) {
        if(event.which === 10 || event.which === 13) {
            var search_param = ($('#sb_search_input').val());
            window.location.href = "/search/?q=" + search_param + "&page=1&filter=general";
            return false;
        }
    });
}

export function initNavbar() {
    return navbar();
}
var representatives = require('../partials/representatives'),
    postcreate = require('../partials/postcreate'),
    newsfeed = require('../partials/newsfeed'),
    solutions = require('controller/conversation/conversation-view/partials/solution'),
    request = require('api').request,
    settings = require('settings').settings;

/**
 * Meta.
 */
export const meta = {
    controller: "section-profile/newsfeed",
    match_method: "path",
    check: "^user/newsfeed$"
};

/**
 * Init
 */
export function init() {

}

/**
 * Load
 */
export function load() {
    require('plugin/contentloader');
    var $app = $(".app-sb"),
        greyPage = document.getElementById('sb-greyout-page');
    // Sidebar
    representatives.init();
    // Post create functionality.
    postcreate.init();
    // Newsfeed page.
    newsfeed.init();
    postcreate.load();
    solutions.load();
    $app
        .on('click', '#js-quest-signup', function(event) {
            event.preventDefault();
            greyPage.classList.remove('sb_hidden');
            if(settings.profile.quest !== null){
                greyPage.classList.add('sb_hidden');
                window.location.href = "/missions/select/";
            } else {
                request.post({url: "/v1/quests/", data: {}})
                    .done(function () {
                        greyPage.classList.add('sb_hidden');
                        window.location.href = "/missions/select/";
                    });
            }
        });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}
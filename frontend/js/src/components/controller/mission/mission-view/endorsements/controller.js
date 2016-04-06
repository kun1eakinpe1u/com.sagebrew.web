var missions = require('common/missions'),
    request = require('api').request,
    settings = require('settings').settings,
    missionSummaryTemplate = require('controller/quest/quest-view/templates/mission_summary.hbs'),
    questSummaryTemplate = require('controller/quest/quest-view/templates/quest_summary.hbs'),
    profileSummaryTemplate = require('controller/section-profile/templates/profile_summary.hbs');

export const meta = {
    controller: "mission/mission-view/endorsements",
    match_method: "path",
    check: [
       "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/endorsements$"
    ]
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
    require('common/handlebars_helpers');
    require('plugin/contentloader');
    var missionId = window.location.pathname.match("([A-Za-z0-9.@_%+-]{36})")[0],
        $endorsmentContainer = $('#js-endorsements-container'),
        $endorsementList = $("#js-endorsements-list");
    if($endorsementList !== undefined && $endorsementList !== "undefined") {
        $endorsementList.sb_contentLoader({
            emptyDataMessage: '<div class="block"><div class="block-content five-padding-bottom"><p>' + 'Check Back Later For New Endorsements</p></div></div>',
            url: '/v1/missions/' + missionId + '/endorsements/',
            loadingMoreItemsMessage: " ",
            itemsPerPage: 3,
            loadMoreMessage: " ",
            dataCallback: function(base_url, params) {
                var urlParams = $.param(params);
                var url;
                if (urlParams) {
                    url = base_url + "?" + urlParams;
                }
                else {
                    url = base_url;
                }
                return request.get({url:url});
            },
            renderCallback: function($container, data) {
                // TODO replace with summary quest and profile
                for(var i=0; i < data.results.length; i++){
                    if(data.results[i].title === undefined || data.results[i].title === "undefined"){
                        data.results[i].title = "" + data.results[i].first_name + " " + data.results[i].last_name;
                    } else {
                        data.results[i].title = missions.determineTitle(data.results[i]);
                    }
                    data.results[i].static_url = settings.static_url;
                    if(data.results[i].type === "profile") {
                        $endorsmentContainer.append(profileSummaryTemplate(data.results[i]));
                    } else if(data.results[i].type === "quest") {
                        $endorsmentContainer.append(questSummaryTemplate(data.results[i]));
                    } else {
                        $endorsmentContainer.append(missionSummaryTemplate(data.results[i]));
                    }
                }
            }
        });
    }
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}
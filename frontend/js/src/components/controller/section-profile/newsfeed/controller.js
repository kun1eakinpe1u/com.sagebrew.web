var representatives = require('../partials/representatives'),
    postcreate = require('../partials/postcreate'),
    newsfeed = require('../partials/newsfeed'),
    solutions = require('controller/conversation/conversation-view/partials/solution'),
    addresses = require('common/addresses'),
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
        addressForm = document.getElementById('address'),
        addressValidationForm = addresses.setupAddress(function callback() {});
    // Sidebar
    representatives.init();
    // Post create functionality.
    postcreate.init();
    // Newsfeed page.
    newsfeed.init();
    postcreate.load();
    solutions.load();
    $app
        .on('click', '#js-continue-btn', function (event) {
            event.preventDefault();
            completeAddress(addressValidationForm, addressForm);
            return false;
        })
        .on('keypress', '#address input', function(event) {
            if (event.which === 13 || event.which === 10) {
                completeAddress(addressValidationForm, addressForm);
                return false; // handles event.preventDefault(), event.stopPropagation() and returnValue for IE8 and earlier
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


function completeAddress(addressValidationForm, addressForm) {
    addressValidationForm.data('formValidation').validate();
    if(addressValidationForm.data('formValidation').isValid() === true) {
        document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
        addresses.submitAddress(addressForm, submitAddressCallback,
                                "/v1/profiles/" + settings.profile.username + "/");
    }
}


function submitAddressCallback() {
    var greyPage = document.getElementById('sb-greyout-page');
    greyPage.classList.add('sb_hidden');
    window.location.reload();
}
var requests = require('api').request,
    helpers = require('common/helpers'),
    validators = require('common/validators'),
    addresses = require('common/addresses'),
    moment = require('moment');

export const meta = {
    controller: "contribute/signup",
    match_method: "path",
    check: [
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/donate\/name",
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/volunteer\/name",
        "^missions\/[A-Za-z0-9.@_%+-]{36}\/[A-Za-z0-9.@_%+-]{1,140}\/endorse\/name"
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
    var $app = $(".app-sb"),
        accountForm = document.getElementById('account-info'),
        addressForm = document.getElementById('address'),
        accountValidationForm = $(accountForm);
    $(':checkbox').radiocheck();
    validators.accountValidator(accountValidationForm);
    var addressValidationForm = addresses.setupAddress(validateAddressCallback);
    $app
        .on('click', '#js-continue-btn', function (event) {
            event.preventDefault();
            completeRegistration(addressValidationForm, addressForm, 
                accountValidationForm, accountForm);
        }).on('keypress', '#account-info input', function(event) {
            if (event.which === 13 || event.which === 10) {
                completeRegistration(addressValidationForm, addressForm, 
                    accountValidationForm, accountForm);
                return false; // handles event.preventDefault(), event.stopPropagation() and returnValue for IE8 and earlier
            }
        }).on('keypress', '#address input', function(event) {
            if (event.which === 13 || event.which === 10) {
                completeRegistration(addressValidationForm, addressForm,
                    accountValidationForm, accountForm);
                return false; // handles event.preventDefault(), event.stopPropagation() and returnValue for IE8 and earlier
            }
        });

    $('#birthday').keyup(function (e) {
        helpers.birthdayInputManager(this, e);
    });
}

/**
 * Post Load
 */
export function postload() {
    //
    // Intercom Tracking
}


function completeRegistration(addressValidationForm, addressForm, accountValidationForm, accountForm) {
    addressValidationForm.data('formValidation').validate();
    accountValidationForm.data('formValidation').validate();
    if(addressValidationForm.data('formValidation').isValid() === true &&
            accountValidationForm.data('formValidation').isValid()){
        document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
        var accountData = helpers.getSuccessFormData(accountForm);


        // If employment and occupation info is available add it to the account info
        var campaignFinanceForm = document.getElementById('campaign-finance');
        if(campaignFinanceForm !== undefined && campaignFinanceForm !== null) {
            var employerName = document.getElementById('employer-name').value,
                occupationName = document.getElementById('occupation-name').value,
                retired = document.getElementById('retired-or-not-employed').checked;
            if (retired === true) {
                accountData.employer_name = "N/A";
                accountData.occupation_name = "Retired or Not Employed";
            } else {
                accountData.employer_name = employerName;
                accountData.occupation_name = occupationName;
            }
        }

        // The backend doesn't care about the user's password matching so
        // delete the second password input we use to help ensure the user
        // doesn't put int a password they don't mean to.
        delete accountData.password2;
        accountData.date_of_birth = moment(accountData.date_of_birth, "MM/DD/YYYY").format();
        requests.post({url: "/v1/profiles/", data: JSON.stringify(accountData)})
            .done(function () {
                addresses.submitAddress(addressForm, submitAddressCallback);
            });
        }
}


function validateAddressCallback() {
}

function submitAddressCallback() {
    var contributionType = helpers.args(3),
        missionSlug = helpers.args(2),
        donateToID = helpers.args(1);
    if(contributionType === "volunteer") {
        window.location.href = "/missions/" + donateToID + "/" +
            missionSlug + "/" + contributionType + "/option/";
    } else if (contributionType === "endorse") {
        window.location.href = "/missions/" + donateToID + "/" +
            missionSlug + "/" + contributionType + "/";
    } else {
        window.location.href = "/missions/" + donateToID + "/" +
            missionSlug + "/donate/payment/";
    }
}
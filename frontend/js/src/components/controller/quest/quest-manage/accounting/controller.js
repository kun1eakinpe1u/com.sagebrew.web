/*global Stripe*/
/**
 * @file
 */
var request = require('api').request,
    helpers = require('common/helpers'),
    moment = require('moment'),
    addresses = require('common/addresses'),
    validators = require('common/validators'),
    settings = require('settings').settings,
    questID = helpers.args(1);
/**
 * Meta.
 */
export const meta = {
    controller: "quest/quest-manage/accounting",
    match_method: "path",
    check: [
       "^quests\/[A-Za-z0-9.@_%+-]{1,36}\/manage\/banking"
    ]
};


/**
 * Load.
 */
export function load() {
    var $app = $(".app-sb"),
        greyPage = document.getElementById('sb-greyout-page'),
        addressForm = document.getElementById('address'),
        bankAccountForm = document.getElementById('banking-form'),
        bankAccountValidationForm = $(bankAccountForm),
        addressValidationForm = addresses.setupAddress(function callback() {});
    validators.bankAccountValidator(bankAccountValidationForm);
    Stripe.setPublishableKey(settings.api.stripe);
    if(settings.profile.quest.fields_needed_human_readable !== null && settings.profile.quest.fields_needed_human_readable !== "") {
        document.getElementById('js-fields-needed').innerHTML = String("Fields Needed: " + settings.profile.quest.fields_needed_human_readable);
    }
    if(settings.profile.quest.verification_due_date !== null) {
        document.getElementById('js-due-date').innerHTML = "Fields Needed By: " + moment.unix(settings.profile.quest.verification_due_date).format("dddd, MMMM Do YYYY, h:mm a");
    }
    if(settings.profile.quest.account_verification_details !== null && settings.profile.quest.account_verification_details !== undefined && settings.profile.quest.account_verification_details !== 'undefined') {
        document.getElementById('js-disabled-reason').innerHTML = "Disabled: " + settings.profile.quest.account_verification_details;
    }
    if(settings.profile.quest.verification_document_needed === true && (settings.profile.quest.identification_sent === false || settings.profile.quest.identification_sent === null)){
        document.getElementById("identification-upload").classList.remove("sb_hidden");
        document.getElementById('js-identification-warning').innerHTML = "Personal Identification Image Upload Required";
    }
    $('.fileinput').fileinput();
    $app
        .on('click', '#js-continue-btn', function (event) {
            event.preventDefault();
            submitAddress(addressValidationForm, addressForm);
        }).on('keypress', '#banking-form input', function(event) {
            if (event.which === 13 || event.which === 10) {
                submitAccountInfo(bankAccountValidationForm, bankAccountForm);
                return false;
            }
        }).on('keypress', '#address input', function(event) {
            if (event.which === 13 || event.which === 10) {
                submitAddress(addressValidationForm, addressForm);
                return false;
            }
        })
        .on('change', '#account-type', function() {
            var $this = $(this),
                accountOwner = $("#js-account-owner-wrapper"),
                ein = $("#js-ein-wrapper");
            if ($this.val() === "business") {
                accountOwner.show();
                ein.show();
            } else {
                accountOwner.hide();
                ein.hide();
            }
        })
        .on('click', '#submit', function(event) {
            event.preventDefault();
            submitAccountInfo(bankAccountValidationForm, bankAccountForm);
        })
        .on('change', "#image", function() {
            event.preventDefault();
            greyPage.classList.remove('sb_hidden');
            var formData = new FormData($('#identificationForm'));
            formData.append('img', $('#image')[0].files[0]);
            request.post({
                url: "/v1/quests/" + questID + "/upload_identification/",
                data: formData,
                cache: false,
                contentType: false,
                processData: false
            })
                .done(function () {
                    window.location.reload();
                })
                .fail(function () {
                    greyPage.classList.add('sb_hidden');
                });
        });
}


function submitAccountInfo(bankAccountValidationForm, bankAccountForm) {
    bankAccountValidationForm.data('formValidation').validate();
    var greyPage = document.getElementById('sb-greyout-page'),
        accountType;
    if(bankAccountValidationForm.data('formValidation').isValid()) {
        document.getElementById('sb-greyout-page').classList.remove('sb_hidden');
        var accountData = helpers.getSuccessFormData(bankAccountForm);
        if (accountData.stripe_account_type === "business") {
            accountType = "company";
        } else {
            accountType = "individual";
        }
        greyPage.classList.remove('sb_hidden');
        Stripe.bankAccount.createToken({
            country: "US",
            currency: "USD",
            routing_number: accountData.routing_number,
            account_number: accountData.account_number,
            account_holder_name: accountData.account_owner,
            account_holder_type: accountType
        }, stripeBankHandler);
    }
}

function submitAddress(addressValidationForm, addressForm) {
    addressValidationForm.data('formValidation').validate();
    if(addressValidationForm.data('formValidation').isValid() === true){
        addresses.submitAddress(addressForm, function callback() {
            window.location.reload();
        }, "/v1/quests/" + settings.profile.username + "/");
    }
}

function stripeBankHandler(status, response){
    var greyPage = document.getElementById('sb-greyout-page');
    if (response.error) {
        // This should be done in the first place before sending off to stripe
        // Maybe we want to pre-empt the user with a warning popup if they click
        // submit when this is verified. Alerting them that it may cause
        // delays in their donations being processed.
        if ($("#completed-stripe").data("completed_stripe") !== "True") {
                $.notify(response.error.message, {type: 'danger'});
            }
        greyPage.classList.add('sb_hidden');
    } else {
        var questID = helpers.args(1),
            data = helpers.getFormData(document.getElementById('banking-form'));
        data.stripe_token = response.id;
        data.tos_acceptance = true;
        request.patch({url: "/v1/quests/" + questID + "/",
            data: JSON.stringify(data)
        }).done(function (){
            window.location.reload();
        }).fail(function () {
            greyPage.classList.add('sb_hidden');
        });
    }
}

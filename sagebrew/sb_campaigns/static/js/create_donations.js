/*global $, jQuery, ajaxSecurity, errorDisplay, Stripe, StripeCheckout*/
$(document).ready(function () {
    'use strict';
    var donationAmount = 0,
        stripeKey = $("#stripe-publishable").data("stripe_key"),
        handler = StripeCheckout.configure({
            key: stripeKey,
            image: $("#stripe_img").data('stripe_image'),
            token: function (token) {
                var campaignId = $("#campaign_id").data('object_uuid');
                $.ajax({
                    xhrFields: {withCredentials: true},
                    type: "POST",
                    url: "/v1/campaigns/" + campaignId + "/donations/",
                    data: JSON.stringify({
                        "amount": donationAmount,
                        "token": token.id
                    }),
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function () {
                        $("#donationModal").modal("hide");
                        $.notify("Successfully Created Donation", {type: 'success'});
                    },
                    error: function (XMLHttpRequest) {
                        $(this).removeAttr("disabled");
                        errorDisplay(XMLHttpRequest);
                    }
                });
            }
        });
    $(".donation-amount-selector").click(function (event) {
        event.preventDefault();
        donationAmount = $(this).data("amount") * 100;
        handler.open({
            name: "Sagebrew LLC",
            description: "Quest Donation",
            amount: $(this).data("amount") * 100,
            panelLabel: "Pledge {{amount}}"
        });
    });
    $("#custom-donation-btn").click(function (event) {
        event.preventDefault();
        donationAmount = $("#custom-donation").val() * 100;
        handler.open({
            name: "Sagebrew LLC",
            description: "Quest Donation",
            amount: $("#custom-donation").val() * 100,
            panelLabel: "Pledge {{amount}}"
        });
    });
    $(window).on('popstate', function () {
        handler.close();
    });
});
/* global enableCommentFunctionality */
/**
 * TODO refactor and include the above globals.
 */
var request = require('api').request,
    commentInputTemplate = require('common/templates/comment_input.hbs'),
    showMoreCommentsTemplate = require('common/templates/show_more_comments.hbs'),
    helpers = require('common/helpers');

function queryComments(url, objectUuid) {
    request.get({url: url})
        .done(function (data) {
            if (data.next !== null) {
                queryComments(data.next, objectUuid);
            }
            var commentContainer = $('#sb_comments_container_' + objectUuid);
            commentContainer.prepend(data.results.html);
            // TODO refactor to have comment functionality applied on page load rather
            // than dynamically with ajax loading.
            enableCommentFunctionality(data.results.ids);
        });
}

export function load () {
    var $app = $(".app-sb");
    $app
        .on('click', '.js-comment', function (event) {
            event.preventDefault();
            var parent = helpers.findAncestor(this, 'js-comment-section'),
                commentInput = parent.getElementsByClassName('js-comment-input')[0],
                placeHolderText = "Help improve the " + parent.dataset.type.replace(/\w\S*/g, function (txt) {
                    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
                }) + " by providing feedback";
            if(parent.dataset.type === "post") {
                placeHolderText = "Leave a comment...";
            }
            commentInput.classList.remove('hidden');
            this.classList.add('hidden');
            commentInput.innerHTML = commentInputTemplate({
                parent_type: parent.dataset.type,
                parent_id: parent.dataset.id,
                placeholder_text: placeHolderText
            });
            var inputArea = document.getElementById('comment-input-' + parent.dataset.id),
                commentContainer = document.getElementById(
                    'sb_comments_container_' + parent.dataset.id);
            if (commentContainer.innerText.length > 0) {
                $("body").scrollTop($(inputArea).offset().top - 250);
            }
        })
        .on('click', '.additional-comments', function (event) {
            // TODO this is common for all content
            event.preventDefault();
            var parent = helpers.findAncestor(this, 'js-comment-section');
            request.get({url: "/v1/" + parent.dataset.type + "s/" + parent.dataset.id + "/comments/render/?expand=true&html=true&page_size=3&page=2"})
                .done(function (data) {
                    var commentContainer = document.getElementById(
                        'sb_comments_container_' + parent.dataset.id);
                    var additionalCommentWrapper = document.getElementById(
                        'additional-comment-wrapper-' + parent.dataset.id);
                    if (additionalCommentWrapper !== null) {
                        additionalCommentWrapper.remove();
                    }
                    $(commentContainer).prepend(data.results.html);
                    // TODO: May be able to use content loader here
                    // TODO opportunity to get rid of ?html=true in this file too
                    if (data.next !== null) {
                        queryComments(data.next, parent.dataset.id);
                    }
                    enableCommentFunctionality(data.results.ids);
                });
        })
        .on('click', '.comment-btn', function (event) {
            event.preventDefault();
            var $this = this;
            var parent = helpers.findAncestor(this, 'comment-input');
            var commentSection = helpers.findAncestor(this, 'js-comment-section');
            var textArea = parent.getElementsByTagName('textarea')[0];
            this.setAttribute('disabled', 'disabled');
            request.post({
                    url: "/v1/" + commentSection.dataset.type + "s/" + commentSection.dataset.id + "/comments/?html=true&expedite=true",
                    data: JSON.stringify({
                        'content': textArea.value
                    })
                })
                .done(function (data) {
                    var commentContainer = commentSection.getElementsByClassName('js-comment-container')[0];
                    $(commentContainer).append(data.html);
                    var additionalCommentWrapper = document.getElementById(
                        'additional-comment-wrapper-' + commentSection.dataset.id);
                    if (additionalCommentWrapper !== null) {
                        additionalCommentWrapper.remove();
                        $(commentContainer).append(showMoreCommentsTemplate({id: commentSection.dataset.id}));
                    }
                    textArea.value = "";
                    enableCommentFunctionality(data.ids);
                    $this.removeAttribute('disabled');
                })
                .fail(function () {
                    $this.removeAttribute('disabled');
                });
        });
}
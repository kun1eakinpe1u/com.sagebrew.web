
var request = require('api').request,
    Autolinker = require('autolinker'),
    helpers = require('common/helpers'),
    Handlebars = require('handlebars'),
    moment = require('moment'),
    showMoreCommentsTemplate = require('../templates/show_more_comments.hbs'),
    createCommentTemplate = require('../templates/create_comment.hbs'),
    commentsNewsTemplate = require('../templates/comments_news.hbs'),
    commentsTemplate = require('../templates/comments.hbs');


export function load () {
    require('plugin/contentloader');
    var $app = $(".app-sb"),
        newsfeed = helpers.args(1),
        commentsRenderTemplate;
    Handlebars.registerPartial('create_comment', createCommentTemplate);
    Handlebars.registerPartial('comments', commentsTemplate);
    if(newsfeed === "newsfeed"){
        commentsRenderTemplate = commentsNewsTemplate;
    } else {
        commentsRenderTemplate = commentsTemplate;
    }
    $app
        .on('click', '.additional-comments', function (event) {
            event.preventDefault();
            var commentContainer = document.getElementById(
                "comment-" + this.dataset.id),
                additionalCommentWrapper = document.getElementById(
                        'additional-comment-wrapper-' + this.dataset.id),
                currentPage = parseInt(this.dataset.page),
                nextPage = currentPage + 1,
                wrapperString = '<div class="row" id="additional-comment-wrapper-' + this.dataset.id + '">' +
                                '<div class="col-sm-5 col-xs-offset-1">' +
                                '<a href="javascript:;" class="additional-comments" ' +
                                'id="additional-comments-' + this.dataset.id + '"' +
                                'data-id="' + this.dataset.id + '"' +
                                'data-type="' + this.dataset.type + '"' +
                                'data-page="' + nextPage + '">Show Older Comments ...</a>' +
                                '</div>' +
                                '</div>';
            $(commentContainer).sb_contentLoader({
                emptyDataMessage: "",
                loadingMoreItemsMessage: "",
                loadMoreMessage: "",
                continuousLoad: false,
                itemsPerPage: 3,
                startingPage: currentPage,
                url: "/v1/" + this.dataset.type + "s/" + this.dataset.id + "/comments/",
                params: {
                    expand: 'true'
                },
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
                    if (additionalCommentWrapper !== null && data.next === null) {
                        additionalCommentWrapper.remove();
                    } else {
                        additionalCommentWrapper.remove();
                        $(commentContainer).append(wrapperString);
                    }
                    for (var i = 0; i < data.results.length; i++) {
                        // This needs to remain html_content otherwise when you go to edit the
                        // comment the content has an <a> tag in it. The user should never see
                        // html tags
                        data.results[i].html_content = Autolinker.link(data.results[i].content);
                    }
                    $(commentContainer).prepend(commentsRenderTemplate({comments: helpers.votableContentPrep(data.results)}));


                }
            });
        })
        .on('click', '.comment-btn', function (event) {
            event.preventDefault();
            var thisHolder = this,
                parent = helpers.findAncestor(this, 'comment-input'),
                textArea = parent.getElementsByTagName('textarea')[0];
            this.setAttribute('disabled', 'disabled');
            request.post({
                    url: "/v1/" + this.dataset.type + "s/" + this.dataset.id + "/comments/?expand=true",
                    data: JSON.stringify({
                        'content': textArea.value
                    })
                })
                .done(function (data) {
                    var commentContainer = document.getElementById("comment-" + thisHolder.dataset.id);
                    data.created = moment(data.created).format("dddd, MMMM Do YYYY, h:mm a");
                    // This needs to remain html_content otherwise when you go to edit the
                    // comment the content has an <a> tag in it. The user should never see
                    // html tags
                    data.html_content = Autolinker.link(data.content);
                    $(commentContainer).append(commentsRenderTemplate({comments: [data]}));
                    var additionalCommentWrapper = document.getElementById(
                        'additional-comment-wrapper-' + thisHolder.dataset.id);
                    if (additionalCommentWrapper !== null) {
                        additionalCommentWrapper.remove();
                        $(commentContainer).append(showMoreCommentsTemplate({id: thisHolder.dataset.id}));
                    }
                    textArea.value = "";
                    thisHolder.removeAttribute('disabled');
                })
                .fail(function () {
                    thisHolder.removeAttribute('disabled');
                });
        })
        .on('click', '.js-edit-comment', function () {
            $("#js-comment-" + this.dataset.id).hide();
            $('#js-edit-container-' + this.dataset.id).show();
        })
        .on('submit', '.js-edit-comment-form', function(event) {
            event.preventDefault();
            var update = helpers.getFormData(this),
                objectID = this.dataset.id;
            var $form = $(this);
            $form.find('button').prop('disabled', true);

            request.patch({
                url: "/v1/" + this.dataset.parent_type + "s/" + this.dataset.parent_id + "/comments/" + this.dataset.id + "/",
                data: JSON.stringify(update)
            }).done(function (data) {
                $form.find('button').prop('disabled', false);
                document.getElementById("js-comment-" + data.id).innerHTML = Autolinker.link(data.content);
                $('#js-edit-container-' + objectID).hide();
                $("#js-comment-" + objectID).show();
            }).fail(function () {
                $form.find('button').prop('disabled', false);
                $('#js-edit-container-' + objectID).hide();
                $("#js-comment-" + objectID).show();
            });
        })
        .on('click', '.js-delete-comment', function() {
            var objectID = this.dataset.id;
            request.remove({
                url: "/v1/" + this.dataset.parent_type + "s/" + this.dataset.parent_id + "/comments/" + objectID + "/"
            }).done(function () {
                document.getElementById("comment-block-" + objectID).remove();
            });
        })
        .on("sb:populate:comments", function (event, commentParentData) {
            request.get({url:"/v1/" + commentParentData.type + "s/" + commentParentData.id + "/comments/?expand=true&page_size=3"})
                .done(function (data) {
                    var commentContainer = $('#comment-' + commentParentData.id);
                    for (var i = 0; i < data.results.length; i++) {
                        // This needs to remain html_content otherwise when you go to edit the
                        // comment the content has an <a> tag in it. The user should never see
                        // html tags
                        data.results[i].html_content = Autolinker.link(data.results[i].content);
                    }
                    commentContainer.append(commentsRenderTemplate({"comments": helpers.votableContentPrep(data.results)}));
                    if (data.count > 3) {
                        // TODO this may break in IE
                        commentContainer.append(
                                '<div class="row" id="additional-comment-wrapper-' + commentParentData.id + '">' +
                                '<div class="col-sm-5 col-xs-offset-1">' +
                                '<a href="javascript:;" class="additional-comments" ' +
                                'id="additional-comments-' + commentParentData.id + '"' +
                                'data-id="' + commentParentData.id + '"' +
                                'data-type="' + commentParentData.type + '"' +
                                'data-page="2">Show Older Comments ...</a>' +
                                '</div>' +
                                '</div>');
                    }
                    $('[data-toggle="tooltip"]').tooltip();
                });
        });
}


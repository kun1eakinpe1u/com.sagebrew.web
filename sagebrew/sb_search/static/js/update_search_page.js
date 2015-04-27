/*global $, jQuery, ajaxSecurity*/
$(document).ready(function () {
    "use strict";
    var searchResults = $('#search_result_div'),
        searchId = $('#search_param'),
        searchParam = searchId.data('search_param'),
        searchPage = searchId.data('search_page'),
        filter = searchId.data('filter'),
        scrolled = false;
    if (filter === 'undefined') {
        filter = "";
    }
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            ajaxSecurity(xhr, settings);
        }
    });
    $.ajax({
        xhrFields: {withCredentials: true},
        type: "GET",
        url: "/search/api/?q=" + searchParam + "&page=" + searchPage + "&filter=" + filter,
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function (data) {
            if (data.next === null) {
                searchResults.append(data.html);
            } else {
                if (data.next !== 0) {
                    searchResults.append("<div class='load_next_page' style='display: none' data-next='" + data.next + " data-filter='" + data.filter + "'></div>");
                }
                var dataList = data.html;
                $.each(dataList, function (i, item) {
                    if (item.type === 'question') {
                        var objectUUID = item.question_uuid;
                        $.ajaxSetup({
                            beforeSend: function (xhr, settings) {
                                ajaxSecurity(xhr, settings);
                            }
                        });
                        $.ajax({
                            xhrFields: {withCredentials: true},
                            type: "GET",
                            url: "/conversations/search/" + objectUUID + '/',
                            contentType: "application/json; charset=utf-8",
                            dataType: "json",
                            success: function (data) {
                                searchResults.append(data.html);
                            }
                        });
                    }
                    if (item.type === 'profile') {
                        var username = item.username;
                        $.ajaxSetup({
                            beforeSend: function (xhr, settings) {
                                ajaxSecurity(xhr, settings);
                            }
                        });
                        $.ajax({
                            xhrFields: {withCredentials: true},
                            type: "GET",
                            url: "/user/search/" + username + '/',
                            contentType: "application/json; charset=utf-8",
                            dataType: "json",
                            success: function (data) {
                                searchResults.append(data.html);
                            }
                        });
                    }
                    if (item.type === 'sagas') {
                        var sagaUUID = item.object_uuid;
                        $.ajaxSetup({
                            beforeSend: function (xhr, settings) {
                                ajaxSecurity(xhr, settings);
                            }
                        });
                        $.ajax({
                            xhrFields: {withCredentials: true},
                            type: "GET",
                            url: "/action/" + sagaUUID + '/search',
                            contentType: "application/json; charset=utf-8",
                            dataType: "json",
                            success: function (data) {
                                searchResults.append(data.html);
                            }
                        });
                    }
                });
            }
        }
    });
    $(window).scroll(function () {
        if (scrolled === false) {
            if ($(window).scrollTop() + $(window).height() > ($(document).height() - $(document).height() * 0.5)) {
                scrolled = true;
                var loadNextPage = $('.load_next_page'),
                    nextPage = loadNextPage.data('next');
                loadNextPage.spin("small");
                $.ajaxSetup({
                    beforeSend: function (xhr, settings) {
                        ajaxSecurity(xhr, settings);
                    }
                });
                $.ajax({
                    xhrFields: {withCredentials: true},
                    type: "GET",
                    url: "/search/api/?q=" + searchParam + "&page=" + nextPage + "&filter=" + filter,
                    contentType: "application/json; charset=utf-8",
                    dataType: "json",
                    success: function (data) {
                        scrolled = false;
                        loadNextPage.spin(false);
                        loadNextPage.remove();
                        if (data.next !== 0 && data.next !== null) {
                            searchResults.append('<div class="load_next_page" style="display: none" data-next="' + data.next + ' data-filter="' + data.filter + '"></div>');
                        }
                        searchResults.append(data.html);
                    }
                });
            }
        }
    });
});




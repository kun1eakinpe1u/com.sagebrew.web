/* global Waypoint, jQuery */
/**
 * @file
 * An infinite pager jquery plugin using waypoints and jQuery.
 */

;(function ($) {
    'use strict';

    if (!$.sb) {
        $.sb = {};
    }

    $.sb.contentLoader = function (el, options) {
        var base = this;

        // Access to jQuery and DOM versions of element
        base.$el = $(el);
        base.el = el;

        // Add a reverse reference to the DOM object
        base.$el.data("sb.contentLoader", base);

        // Important elements.
        var $listContainer,
            $loadMore;

        // Data store.
        var totalItems,
            isInited = false;



        /**
         * Init With Content
         */
        base.initWithContent = function() {
            if (!isInited) {
                //
                // Insert List Container.
                if (base.options.specifiedContainer !== null) {
                    $listContainer = base.options.specifiedContainer;
                } else {
                    $listContainer = $('<div class="list-container"></div>');
                    base.$el.append($listContainer);
                }

                //
                // Insert load more link.
                $loadMore = $('<a class="load-more"></a>');
                base.$el.append($loadMore);

                $loadMore.waypoint(function(direction) {

                    //
                    // Load more data.
                    if (direction === "down" && base.options.startingPage && !$loadMore.hasClass("currently-loading")) {
                        base.loadMoreContent();
                    }

                }, {
                  offset: 'bottom-in-view'
                });


            }
            isInited = true;
        };

        /**
         * Init Without Content
         */
        base.initWithoutContent = function() {
            if (!isInited) {
                //
                // Insert List Container. I'm not sure if we should do this.
                if (base.options.specifiedContainer !== null) {
                    $listContainer = base.options.specifiedContainer;
                } else {
                    $listContainer = $('<div class="list-container"></div>');
                    base.$el.append($listContainer);
                }
                $listContainer.append($('<h3 class="list-empty">' + base.options.emptyDataMessage + '</h3>'));
            }
            isInited = true;
        };

        /**
         * Call the callback.
         */
        base.getData = function() {
            var params = base.options.params;

            params.page_size = base.options.itemsPerPage;
            params.page = base.options.startingPage;
            return base.options.dataCallback(base.options.url, params);
        };

        /**
         * Load up some content!
         */
        base.loadMoreContent = function() {
            //Do we even have more data to get?
            //Subtract one to fix not loading the last page of data from api
            if (totalItems > ((base.options.startingPage - 1) * base.options.itemsPerPage) &&
                    base.options.continuousLoad === true) {
                $loadMore.text(base.options.loadingMoreItemsMessage).addClass("currently-loading");
                base.getData().done(function(data) {
                    base.options.startingPage++;
                    if(base.options.endingPage !== null && base.options.startingPage < base.options.endingPage){
                        base.options.renderCallback($listContainer, data);
                    } else if (base.options.endingPage === null) {
                        base.options.renderCallback($listContainer, data);
                    }


                    $loadMore.text(base.options.loadMoreMessage).removeClass("currently-loading");
                    Waypoint.refreshAll();
                });

            } else {
                //Deregister stuff.
                $loadMore.remove();
                //$loadMore.text("No more data");
                Waypoint.disableAll();
            }

        };

        /**
         * Init contentLoader.
         */
        base.init = function () {

            base.options = $.extend({},
                $.sb.contentLoader.defaultOptions, options);


            //
            //Ensure there is a loader. Sometimes this is already on the page.
            if (!$(".loader", base.$el).length && base.options.showLoader === true) {
                base.$el.append($('<div class="loader">Loading...</div>'));
            }

            //
            // Get the first round of datas and init some shit.
            base.getData().done(function(data) {
                $(".loader", base.$el).remove();
                if (data.count !== 0) {
                    totalItems = data.count;
                    base.options.startingPage++;

                    base.initWithContent();

                    base.options.renderCallback($listContainer, data);

                    //I don't know, man.
                    Waypoint.refreshAll();

                } else {
                    base.initWithoutContent();
                }
            });

        };

        base.init();
    };

    $.sb.contentLoader.defaultOptions = {
        emptyDataMessage: 'Please add some data.',
        loadingMoreItemsMessage: "Please wait, loading more items",
        loadMoreMessage: "Load more.",
        itemsPerPage: 5,
        startingPage: 1,
        endingPage: null,
        showLoader: true,
        continuousLoad: true,
        url: '',
        specifiedContainer: null,
        params: {

        },
        dataCallback: function() {
            console.log("you did not supply a dataCallback");
            return false;
        },
        renderCallback: function() {
            console.log("you did not supply a renderCallback");
            return false;
        }
    };

    /**
     * Register sb_contentLoader.
     * @param options
     * @returns {*}
     */
    $.fn.sb_contentLoader = function
        (options) {
        return this.each(function () {
            (new $.sb.contentLoader(this,
                options));
        });
    };

})(jQuery);
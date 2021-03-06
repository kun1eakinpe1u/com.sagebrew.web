/*global Intercom, google, Bloodhound*/
var request = require('api').request,
    radioSelector = require('common/radioimage').radioSelector,
    helpers = require('common/helpers'),
    districtHolderTemplate = require('controller/mission/registration/political-mission/templates/district_holder.hbs'),
    districtOptionsTemplate = require('controller/mission/registration/political-mission/templates/district_options.hbs'),
    settings = require('settings').settings,
    onboarding = require('common/onboarding'),
    locationKey = 'advocateMissionLocationID',
    locationName = "advocateMissionLocationName",
    levelKey = 'advocateMissionLevel',
    districtKey = 'advocateDistrict',
    affectedAreaKey = "affectedArea",
    clickMessageKey = "displayClickMessage",
    inPlaceChangedKey = "inPlaceChangedKey";


export function load() {
    var $app = $(".app-sb"),
        placeInput = document.getElementById('pac-input'),
        stateInput = document.getElementById('state-input'),
        districtSelector = document.getElementById('js-district-selector'),
        districtRow = document.getElementById('district-row'),
        advocateInput = document.getElementById('advocate-input'),
        stateRequired = stateInput.options[0],
        greyPage = document.getElementById('sb-greyout-page'),
        advocateInputCharCount = $("#js-advocate-char-count"),
        advocateInputWrapper = $(".advocate-input-wrapper"),
        advocateInputCharacterLimit = 70;
    if(typeof(Storage) !== "undefined") {
        // Clear out all of the storage for the page, we're starting a new mission!
        localStorage.removeItem(locationKey);
        localStorage.removeItem(locationName);
        localStorage.removeItem(districtKey);
        localStorage.removeItem(levelKey);
    }
    var engine = new Bloodhound({
        prefetch: {
            url: "/v1/tags/suggestion_engine_v2/",
            cache: false
        },
        datumTokenizer: Bloodhound.tokenizers.whitespace,
        queryTokenizer: Bloodhound.tokenizers.whitespace
    });
    engine.initialize();
    $('#advocate-input').typeahead(
        {
            highlight: true,
            hint: true
        },
        {
             source: engine
        })
        .on('typeahead:selected', function() {
            $('#advocate-input').keyup();
        });
    $("#advocate-input-tokenfield").attr("name", "tag_box");

    $app
        .on('click', '.radio-image-selector', function(event) {
            event.preventDefault();
            if(this.classList.contains("js-level")){
                // TODO: REUSE
                // If we select a level that was already selected we need to disable the inputs
                // and clear the currently selected position and re-disable positions and districts
                stateInput.disabled = true;
                placeInput.disabled = true;
                districtSelector.innerHTML = districtHolderTemplate();
                localStorage.removeItem(districtKey);
                localStorage.removeItem(locationKey);
                localStorage.removeItem(locationName);
                localStorage.removeItem(levelKey);
                stateInput.selectedIndex = 0;
                districtRow.classList.add('hidden');
            }
            if (!(this.classList.contains("radio-selected") && this.classList.contains("js-level"))) {
                // TODO: REUSE
                // If we select a level, enable the inputs
                stateInput.disabled = false;
                placeInput.disabled = false;
                if (this.id === "local-selection") {
                    // The local level was selected
                    stateInput.classList.add('hidden');
                    placeInput.classList.remove('hidden');
                    districtRow.classList.add('hidden');
                    localStorage.setItem(levelKey, "local");
                    // To the user we clear the place input so we need to
                    // disable the start button and clear the locations
                    placeInput.value = "";
                    localStorage.removeItem(locationKey);
                    localStorage.removeItem(locationName);
                } else if (this.id === "state-selection") {
                    // The state level was selected
                    stateRequired.innerHTML = 'Select a State';
                    localStorage.setItem(levelKey, "state");
                    localStorage.removeItem(locationKey);
                    localStorage.removeItem(locationName);
                    districtRow.classList.remove('hidden');
                    districtSelection('state', stateInput, placeInput, districtRow);
                } else if (this.id === "federal-selection") {
                    // The federal level was selected
                    localStorage.removeItem(locationKey);
                    localStorage.removeItem(locationName);
                    stateRequired.innerHTML = 'Select a State';
                    districtSelection('federal', stateInput, placeInput, districtRow);
                }
            }
            radioSelector(this);
        })
        .on('change', '#js-district-selector select', function() {
            // TODO REUSE
            // A district has been selected, we're at the bottom of the page
            // enable the start button and store off the final item needed for
            // federal and state campaigns
            localStorage.setItem(districtKey, this.options[this.selectedIndex].innerHTML);
            // Since after the selection a click event isn't raised we need to add this to ensure
            // the user can move forward without needing to click somewhere
        })
        .on('change', '#pac-input', function() {
            localStorage.removeItem(locationKey);
        })
        .on('click', '#js-start-btn', function(){
            greyPage.classList.remove('sb_hidden');
            var location;
            Intercom('trackEvent', 'setup-mission');
            Intercom('trackEvent', 'setup-advocacy-mission');
            if(localStorage.getItem(levelKey) !== "local"){
                location = localStorage.getItem(locationName);
            } else {
                location = localStorage.getItem(locationKey);
            }
            if ((location === null || location === undefined || typeof location === "undefined") && advocateInput.value) {
                $.notify({message: "Please specify where you are advocating"},
                    {type: "danger"});
                greyPage.classList.add('sb_hidden');
                return;
            }
            request.post({
                url: "/v1/missions/",
                data: JSON.stringify({
                    focus_name: advocateInput.value,
                    district: localStorage.getItem(districtKey),
                    level: localStorage.getItem(levelKey),
                    formatted_location_name: localStorage.getItem(affectedAreaKey),
                    location_name: location,
                    focus_on_type: "advocacy"
                }),
                error: function(XMLHttpRequest) {
                    document.getElementById('sb-greyout-page').classList.add('sb_hidden');
                    request.errorDisplay(XMLHttpRequest, null, null, true);
                }
            }).done(function (data) {
                greyPage.classList.add('sb_hidden');
                onboarding.routeMissionSetupToEpic(data);
            });
        })
        .on('click', '#js-cancel-btn', function(event){
            event.preventDefault();
            window.location.href = "/quests/" + settings.user.username;
        })
        .on('keyup', '#advocate-input', function(){
            var $this = $(this),
                required = document.getElementById('js-required');
            helpers.characterCountRemaining(advocateInputCharacterLimit, $this, advocateInputCharCount);
            if ($this.val().length === 0) {
                required.classList.remove('sb_hidden');
                advocateInputWrapper.removeClass("has-success");
                advocateInputWrapper.addClass("has-error");
            } else if ($this.val().length > advocateInputCharacterLimit) {
                required.classList.add('sb_hidden');
                advocateInputWrapper.removeClass("has-success");
                advocateInputWrapper.addClass("has-error");
            } else {
                required.classList.add('sb_hidden');
                advocateInputWrapper.removeClass("has-error");
                advocateInputWrapper.addClass("has-success");
            }
        });
    helpers.loadMap(initAutocomplete, "places");
}

function districtSelection(level, stateInput, placeInput, districtRow) {
    /**
     * If the user had previous selected local we need to clear out
     * the running area since the location on the map now represents
     * what they had selected for local. This causes issues for grabbing
     * the position and districts as the place id is set to an incorrect location.
     */
    if(localStorage.getItem(levelKey) === "local"){
        // If the level was previously local and now we're changing it we need
        // to remove the location key and reset the state input to 0.
        localStorage.removeItem(locationKey);
        stateInput.selectedIndex = 0;
    }
    stateInput.classList.remove('hidden');
    placeInput.classList.add('hidden');
    localStorage.setItem(levelKey, level);
    if(level === "federal") {
        localStorage.removeItem(locationKey);
        stateInput.selectedIndex = 0;
        localStorage.removeItem(districtKey);
        districtRow.classList.add('hidden');
    } else if (level === "state") {
        districtRow.classList.remove('hidden');
    }
}


function fillDistricts(filterParam) {
    // TODO REUSE
    var identifier = localStorage.getItem(locationKey);
    var url = "/v1/locations/" + identifier + "/district_names/?lookup=external_id";
    if (filterParam !== "" && filterParam !== undefined){
        url = url + "&filter=" + filterParam;
    }
    request.get({url: url})
        .done(function (data) {
            var context, districtList = [], name;
            for(var i=0; i < data.results.length; i++) {
                name = data.results[i];
                context = {name: name};
                districtList.push(context);
            }
            document.getElementById('js-district-selector').innerHTML = districtOptionsTemplate({districts: districtList, option_holder: "Select a District (Optional)"});
        });
}

function initAutocomplete() {
    // TODO REUSE
    var $app = $(".app-sb");
    var latitude = 42.3314;
    var longitude = -83.0458;
    var affectedArea = null;
    var zoomLevel = helpers.determineZoom(affectedArea);
    var map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: latitude, lng: longitude},
        zoom: zoomLevel,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        disableDefaultUI: true,
        draggable: false,
        scrollwheel: false
    });
    var input = document.getElementById('pac-input');

    $app
        .on('change', '#state-input', function() {
            var query = this.options[this.selectedIndex].innerHTML,
                greyPage = document.getElementById('sb-greyout-page');
            greyPage.classList.remove('sb_hidden');
            localStorage.setItem(locationName, query);
            if (query === "New York") {
                query = query + " State, United States";
            } else {
                query = query + ", United States";
            }
            var requestQuery = {
                query: query
            };
            if(localStorage.getItem(levelKey) === "federal"){
                document.getElementById('district-row').classList.remove('hidden');
            }
            var service = new google.maps.places.PlacesService(map);
            service.textSearch(requestQuery, callback);

        });
    var autocomplete = new google.maps.places.Autocomplete(input),
        pacInput = $("#pac-input");
    autocomplete.setTypes(['(cities)']);
    autocomplete.bindTo('bounds', map);

    helpers.allowTabLocationSelection(input);
    
    helpers.allowClickErrorMessage(pacInput, clickMessageKey, locationKey, inPlaceChangedKey);
    
    autocomplete.addListener('place_changed', function() {
        localStorage.setItem(inPlaceChangedKey, true);
        var place = autocomplete.getPlace(),
            greyPage = document.getElementById('sb-greyout-page'),
            affectedArea = place.formatted_address;
        greyPage.classList.remove('sb_hidden');
        if (!place.geometry) {
            $.notify({message: "Sorry we couldn't find that location. Please try another."},
                {type: "danger"});
            greyPage.classList.add('sb_hidden');
            localStorage.removeItem(inPlaceChangedKey);
            return;
        }

        if (place.name === "Random") {
            $.notify({message: "Sorry we currently do not support that location. Please try another."},
                {type: "danger"});
            greyPage.classList.add('sb_hidden');
            localStorage.removeItem(inPlaceChangedKey);
            return;
        }

        if (place.geometry.viewport) {
            map.fitBounds(place.geometry.viewport);
        } else {
            map.setCenter(place.geometry.location);
            map.setZoom(12);
        }
        localStorage.setItem(locationKey, place.place_id);
        localStorage.setItem(affectedAreaKey, affectedArea);
        /**
         * If a location is selected the district should always be replaced by the holder and the position
         * removed from local storage
         * This selection always changes the positions and districts which is why this is necessary
         */
        localStorage.removeItem(inPlaceChangedKey);
        request.post({
            url: '/v1/locations/add_external_id/',
            data: JSON.stringify(place)
        }).done(function() {
            /** This is a local city search, if we find something
             * we should enable the start button
             */
            greyPage.classList.add('sb_hidden');
        });
    });

    function callback(results, status) {
        // TODO REUSE
        var greyPage = document.getElementById('sb-greyout-page');
        if (status === google.maps.places.PlacesServiceStatus.OK) {
            var place = results[0],
                affectedArea = place.formatted_address;
            if (place.geometry.viewport) {
                map.fitBounds(place.geometry.viewport);
            } else {
                map.setCenter(place.geometry.location);
                map.setZoom(12);
            }
            localStorage.setItem(locationKey, place.place_id);
            localStorage.setItem(affectedAreaKey, affectedArea);
            request.post({
                url: '/v1/locations/add_external_id/',
                data: JSON.stringify(place)
            }).done(function () {
                greyPage.classList.add('sb_hidden');
            });
        } else {
            greyPage.classList.add('sb_hidden');
        }
        fillDistricts('federal');
    }
}


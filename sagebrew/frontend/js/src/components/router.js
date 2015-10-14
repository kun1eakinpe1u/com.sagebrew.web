/**
 * @file
 * Dynamically load controllers and whatnot based on urls.
 */

var helpers = require('./common/helpers');
var ctrlHash = require('./controller/*/controller.js', {mode: 'hash'});
//
// Define all the controllers.
var controller_map = [
    {
        controller: "global",
        match_method: true,
        check: true
    },
    {
        controller: "user-anon",
        match_method: "user",
        check: "anon"
    },
    {
        controller: "user-anon",
        match_method: "user",
        check: "auth"
    }
];

/**
 * @param match_method
 * @param check
 */
function matchController(match_method, check) {
    var path = helpers.args().join("/");
    switch(match_method) {
        case true:
            return true;
        case 'user': //Need to output app settings in python for this.
            return false;
        case 'path':
            return path.match(check);

    }
}

function finder() {
    var load = [];
    for (var key in controller_map) {
        var controller = controller_map[key];
        if (matchController(controller.match_method, controller.check)) {
            load.push(controller.controller);
        }
    }
    return load;
}

export function controllers() {
    var found = finder();
    var loaded = [];
    if (found.length) {
        loaded = found.map(function(key){
            return ctrlHash[key+"/controller"];
        });
    }
    return loaded;
}


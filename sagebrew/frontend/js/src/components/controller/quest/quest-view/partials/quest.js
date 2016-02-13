var missions = require('common/missions'),
    helpers = require('common/helpers'),
    addCroppic = require('common/uploadimage').addCroppic;

export function load() {
    var $app = $(".app-sb"),
        missionList= document.getElementById('js-mission-list'),
        pageUser = helpers.args(1);

    missions.populateMissions(missionList, pageUser);
    $app
        .on('click', '.js-position', function () {
            if(this.id === "js-add-mission"){
                window.location.href = "/missions/select/";
            } else {
                window.location.href = "/missions/" + this.id + "/";
            }
        });
    var croppicContainerOptions = {
        wrapperDivID: "js-croppic-wrapper-div-id",
        imageID: "js-croppic-img-id",
        interfaceUrl: "/v1/quests/" + pageUser + "/",
        uploadProperty: "wallpaper_pic",
        imageClassList: "wallpaper quest-wallpaper",
        afterImgUploadCallback: afterImgUploadCallback,
        afterAfterImgCropCallback: afterAfterImgCropCallback
    };
    addCroppic(croppicContainerOptions);
    $('[data-toggle="tooltip"]').tooltip();
}


function afterImgUploadCallback(){
    var wrapperElement = document.getElementById("js-croppic-wrapper-div-id");
    wrapperElement.classList.add('quest-wallpaper-cropping');
}



function afterAfterImgCropCallback(){
    var wrapperElement = document.getElementById("js-croppic-wrapper-div-id");
    wrapperElement.classList.remove('quest-wallpaper-cropping');
}
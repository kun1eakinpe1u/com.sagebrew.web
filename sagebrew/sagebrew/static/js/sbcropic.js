/*
 * CROP
 * dependancy: jQuery
 * author: Ognjen "Zmaj Džedaj" Božičković and Mat Steinlin
 */
 !function(o,t){Croppic=function(o,t){var n=this;n.id=o,n.obj=$("#"+o),n.outputDiv=n.obj,n.options={uploadUrl:"",uploadData:{},cropUrl:"",cropData:{},outputUrlId:"",imgEyecandy:!0,imgEyecandyOpacity:.2,zoomFactor:10,rotateFactor:5,doubleZoomControls:!0,rotateControls:!0,modal:!1,customUploadButtonId:"",loaderHtml:"",scaleToFill:!0,processInline:!1,loadPicture:"",onReset:null,enableMousescroll:!1,onBeforeImgUpload:null,onAfterImgUpload:null,onImgDrag:null,onImgZoom:null,onImgRotate:null,onBeforeImgCrop:null,onAfterImgCrop:null,onError:null};for(i in t)n.options[i]=t[i];n.init()},Croppic.prototype={id:"",imgInitW:0,imgInitH:0,imgW:0,imgH:0,objW:0,objH:0,actualRotation:0,windowW:0,windowH:$(o).height(),obj:{},outputDiv:{},outputUrlObj:{},img:{},defaultImg:{},croppedImg:{},imgEyecandy:{},form:{},cropControlsUpload:{},cropControlsCrop:{},cropControlZoomMuchIn:{},cropControlZoomMuchOut:{},cropControlZoomIn:{},cropControlZoomOut:{},cropControlCrop:{},cropControlReset:{},cropControlRemoveCroppedImage:{},modal:{},loader:{},init:function(){var o=this;o.objW=o.obj.width(),o.objH=o.obj.height(),o.actualRotation=0,$.isEmptyObject(o.defaultImg)&&(o.defaultImg=o.obj.find("img")),o.createImgUploadControls(),$.isEmptyObject(o.options.loadPicture)?o.bindImgUploadControl():o.loadExistingImage()},createImgUploadControls:function(){var o=this,t="";""===o.options.customUploadButtonId&&(t='<i class="cropControlUpload"></i>');var i='<i class="cropControlRemoveCroppedImage"></i>';$.isEmptyObject(o.croppedImg)&&(i=""),$.isEmptyObject(o.options.loadPicture)||(t="");var n='<div class="cropControls cropControlsUpload"> '+t+" </div>";o.outputDiv.append(n),o.cropControlsUpload=o.outputDiv.find(".cropControlsUpload"),""===o.options.customUploadButtonId?o.imgUploadControl=o.outputDiv.find(".cropControlUpload"):(o.imgUploadControl=$("#"+o.options.customUploadButtonId),o.imgUploadControl.show()),$.isEmptyObject(o.croppedImg)||(o.cropControlRemoveCroppedImage=o.outputDiv.find(".cropControlRemoveCroppedImage"))},bindImgUploadControl:function(){var o=this,i='<form class="'+o.id+'_imgUploadForm" style="position: absolute; visibility: hidden; top:0;">  <input type="file" name="img">  </form>';o.outputDiv.append(i),o.form=o.outputDiv.find("."+o.id+"_imgUploadForm"),o.imgUploadControl.off("click"),o.imgUploadControl.on("click",function(){o.form.find('input[type="file"]').trigger("click")}),$.isEmptyObject(o.croppedImg)||o.cropControlRemoveCroppedImage.on("click",function(){o.croppedImg.remove(),$(this).hide(),$.isEmptyObject(o.defaultImg)||o.obj.append(o.defaultImg),""!==o.options.outputUrlId&&$("#"+o.options.outputUrlId).val("")}),o.form.find('input[type="file"]').change(function(){if(o.options.onBeforeImgUpload&&o.options.onBeforeImgUpload.call(o),o.showLoader(),o.imgUploadControl.hide(),o.options.processInline){var i=new FileReader;i.onload=function(t){var i=new Image;i.src=t.target.result,i.onload=function(){o.imgInitW=o.imgW=i.width,o.imgInitH=o.imgH=i.height,o.options.modal&&o.createModal(),$.isEmptyObject(o.croppedImg)||o.croppedImg.remove(),o.imgUrl=i.src,o.obj.append('<img src="'+i.src+'">'),o.initCropper(),o.hideLoader(),o.options.onAfterImgUpload&&o.options.onAfterImgUpload.call(o)}},i.readAsDataURL(o.form.find('input[type="file"]')[0].files[0])}else{var n=new FormData(o.form[0]);for(var r in o.options.uploadData)o.options.uploadData.hasOwnProperty(r)&&n.append(r,o.options.uploadData[r]);$.ajax({url:o.options.uploadUrl,data:n,context:t.body,cache:!1,contentType:!1,processData:!1,type:"POST"}).always(function(t){if(response="object"==typeof t?t:jQuery.parseJSON(t),"success"==response.status){o.imgInitW=o.imgW=response.width,o.imgInitH=o.imgH=response.height,o.options.modal&&o.createModal(),$.isEmptyObject(o.croppedImg)||o.croppedImg.remove(),o.imgUrl=response.url;var i=$('<img src="'+response.url+'">');o.obj.append(i),i.load(function(){o.initCropper(),o.hideLoader(),o.options.onAfterImgUpload&&o.options.onAfterImgUpload.call(o,response)})}400<=response.status&&(o.options.onError&&o.options.onError.call(o,response),o.hideLoader(),setTimeout(function(){o.reset()},5))})}})},loadExistingImage:function(){var o=this;if($.isEmptyObject(o.croppedImg)){o.options.onBeforeImgUpload&&o.options.onBeforeImgUpload.call(o),o.showLoader(),o.options.modal&&o.createModal(),$.isEmptyObject(o.croppedImg)||o.croppedImg.remove(),o.imgUrl=o.options.loadPicture;var t=$('<img src="'+o.options.loadPicture+'">');o.obj.append(t),t.load(function(){o.imgInitW=o.imgW=this.width,o.imgInitH=o.imgH=this.height,o.initCropper(),o.hideLoader(),o.options.onAfterImgUpload&&o.options.onAfterImgUpload.call(o)})}else o.cropControlRemoveCroppedImage.on("click",function(){o.croppedImg.remove(),$(this).hide(),$.isEmptyObject(o.defaultImg)||o.obj.append(o.defaultImg),""!==o.options.outputUrlId&&$("#"+o.options.outputUrlId).val(""),o.croppedImg="",o.reset()})},createModal:function(){var o=this,t=o.windowH/2-o.objH/2,i='<div id="croppicModal"><div id="croppicModalObj" style="width:'+o.objW+"px; height:"+o.objH+"px; margin:0 auto; margin-top:"+t+'px; position: relative;"> </div></div>';$("body").append(i),o.modal=$("#croppicModal"),o.obj=$("#croppicModalObj")},destroyModal:function(){var o=this;o.obj=o.outputDiv,o.modal.remove()},initCropper:function(){var o=this;o.img=o.obj.find("img"),o.img.wrap('<div class="cropImgWrapper" style="overflow:hidden; z-index:1; position:absolute; width:'+o.objW+"px; height:"+o.objH+'px;"></div>'),o.createCropControls(),o.options.imgEyecandy&&o.createEyecandy(),o.initDrag(),o.initialScaleImg()},createEyecandy:function(){var o=this;o.imgEyecandy=o.img.clone(),o.imgEyecandy.css({"z-index":"0",opacity:o.options.imgEyecandyOpacity}).appendTo(o.obj)},destroyEyecandy:function(){var o=this;o.imgEyecandy.remove()},initialScaleImg:function(){var o=this;o.zoom(-o.imgInitW),o.zoom(40),o.options.enableMousescroll&&o.img.on("mousewheel",function(t){t.preventDefault(),o.zoom(o.options.zoomFactor*t.deltaY)}),o.img.css({left:-(o.imgW-o.objW)/2,top:-(o.imgH-o.objH)/2,position:"relative"}),o.options.imgEyecandy&&o.imgEyecandy.css({left:-(o.imgW-o.objW)/2,top:-(o.imgH-o.objH)/2,position:"relative"})},createCropControls:function(){var o,t=this,i="",n='<i class="cropControlZoomIn"></i>',r='<i class="cropControlZoomOut"></i>',e="",p="",a="",s='<i class="cropControlCrop"></i>',c='<i class="cropControlReset"></i>';t.options.doubleZoomControls&&(i='<i class="cropControlZoomMuchIn"></i>',e='<i class="cropControlZoomMuchOut"></i>'),t.options.rotateControls&&(p='<i class="cropControlRotateLeft"></i>',a='<i class="cropControlRotateRight"></i>'),o='<div class="cropControls cropControlsCrop">'+i+n+r+e+p+a+s+c+"</div>",t.obj.append(o),t.cropControlsCrop=t.obj.find(".cropControlsCrop"),t.options.doubleZoomControls&&(t.cropControlZoomMuchIn=t.cropControlsCrop.find(".cropControlZoomMuchIn"),t.cropControlZoomMuchIn.on("click",function(){t.zoom(10*t.options.zoomFactor)}),t.cropControlZoomMuchOut=t.cropControlsCrop.find(".cropControlZoomMuchOut"),t.cropControlZoomMuchOut.on("click",function(){t.zoom(10*-t.options.zoomFactor)})),t.cropControlZoomIn=t.cropControlsCrop.find(".cropControlZoomIn"),t.cropControlZoomIn.on("click",function(){t.zoom(t.options.zoomFactor)}),t.cropControlZoomOut=t.cropControlsCrop.find(".cropControlZoomOut"),t.cropControlZoomOut.on("click",function(){t.zoom(-t.options.zoomFactor)}),t.cropControlZoomIn=t.cropControlsCrop.find(".cropControlRotateLeft"),t.cropControlZoomIn.on("click",function(){t.rotate(-t.options.rotateFactor)}),t.cropControlZoomOut=t.cropControlsCrop.find(".cropControlRotateRight"),t.cropControlZoomOut.on("click",function(){t.rotate(t.options.rotateFactor)}),t.cropControlCrop=t.cropControlsCrop.find(".cropControlCrop"),t.cropControlCrop.on("click",function(){t.crop()}),t.cropControlReset=t.cropControlsCrop.find(".cropControlReset"),t.cropControlReset.on("click",function(){t.reset()})},initDrag:function(){var t=this;t.img.on("mousedown touchstart",function(i){i.preventDefault();var n,r,e=o.navigator.userAgent;e.match(/iPad/i)||e.match(/iPhone/i)||e.match(/android/i)?(n=i.originalEvent.touches[0].pageX,r=i.originalEvent.touches[0].pageY):(n=i.pageX,r=i.pageY);var p=t.img.css("z-index"),a=t.img.outerHeight(),s=t.img.outerWidth(),c=t.img.offset().top+a-r,l=t.img.offset().left+s-n;t.img.css("z-index",1e3).on("mousemove touchmove",function(o){var i,n;if(e.match(/iPad/i)||e.match(/iPhone/i)||e.match(/android/i)?(i=o.originalEvent.touches[0].pageY+c-a,n=o.originalEvent.touches[0].pageX+l-s):(i=o.pageY+c-a,n=o.pageX+l-s),t.img.offset({top:i,left:n}).on("mouseup",function(){$(this).removeClass("draggable").css("z-index",p)}),t.options.imgEyecandy&&t.imgEyecandy.offset({top:i,left:n}),t.objH<t.imgH){parseInt(t.img.css("top"))>0&&(t.img.css("top",0),t.options.imgEyecandy&&t.imgEyecandy.css("top",0));var r=-(t.imgH-t.objH);parseInt(t.img.css("top"))<r&&(t.img.css("top",r),t.options.imgEyecandy&&t.imgEyecandy.css("top",r))}else{parseInt(t.img.css("top"))<0&&(t.img.css("top",0),t.options.imgEyecandy&&t.imgEyecandy.css("top",0));var r=t.objH-t.imgH;parseInt(t.img.css("top"))>r&&(t.img.css("top",r),t.options.imgEyecandy&&t.imgEyecandy.css("top",r))}if(t.objW<t.imgW){parseInt(t.img.css("left"))>0&&(t.img.css("left",0),t.options.imgEyecandy&&t.imgEyecandy.css("left",0));var m=-(t.imgW-t.objW);parseInt(t.img.css("left"))<m&&(t.img.css("left",m),t.options.imgEyecandy&&t.imgEyecandy.css("left",m))}else{parseInt(t.img.css("left"))<0&&(t.img.css("left",0),t.options.imgEyecandy&&t.imgEyecandy.css("left",0));var m=t.objW-t.imgW;parseInt(t.img.css("left"))>m&&(t.img.css("left",m),t.options.imgEyecandy&&t.imgEyecandy.css("left",m))}t.options.onImgDrag&&t.options.onImgDrag.call(t)})}).on("mouseup",function(){t.img.off("mousemove")}).on("mouseout",function(){t.img.off("mousemove")})},rotate:function(o){var t=this;t.actualRotation+=o,t.img.css({"-webkit-transform":"rotate("+t.actualRotation+"deg)","-moz-transform":"rotate("+t.actualRotation+"deg)",transform:"rotate("+t.actualRotation+"deg)"}),t.options.imgEyecandy&&t.imgEyecandy.css({"-webkit-transform":"rotate("+t.actualRotation+"deg)","-moz-transform":"rotate("+t.actualRotation+"deg)",transform:"rotate("+t.actualRotation+"deg)"}),"function"==typeof t.options.onImgRotate&&t.options.onImgRotate.call(t)},zoom:function(o){var t=this,i=t.imgW/t.imgH,n=t.imgW+o,r=n/i,e=!0;(n<t.objW||r<t.objH)&&(n-t.objW<r-t.objH?(n=t.objW,r=n/i):(r=t.objH,n=i*r),e=!1),!t.options.scaleToFill&&(n>t.imgInitW||r>t.imgInitH)&&(n-t.imgInitW<r-t.imgInitH?(n=t.imgInitW,r=n/i):(r=t.imgInitH,n=i*r),e=!1),t.imgW=n,t.img.width(n),t.imgH=r,t.img.height(r);var p=parseInt(t.img.css("top"))-o/2,a=parseInt(t.img.css("left"))-o/2;p>0&&(p=0),a>0&&(a=0);var s=-(r-t.objH);s>p&&(p=s);var c=-(n-t.objW);c>a&&(a=c),e&&t.img.css({top:p,left:a}),t.options.imgEyecandy&&(t.imgEyecandy.width(n),t.imgEyecandy.height(r),e&&t.imgEyecandy.css({top:p,left:a})),t.options.onImgZoom&&t.options.onImgZoom.call(t)},crop:function(){var o=this;o.options.onBeforeImgCrop&&o.options.onBeforeImgCrop.call(o),o.cropControlsCrop.hide(),o.showLoader();var i={imgUrl:o.imgUrl,imgInitW:o.imgInitW,imgInitH:o.imgInitH,resize_width:o.imgW,resize_height:o.imgH,image_y1:Math.abs(parseInt(o.img.css("top"))),image_x1:Math.abs(parseInt(o.img.css("left"))),crop_height:o.objH,crop_width:o.objW,rotation:o.actualRotation},n=new FormData;for(var r in i)i.hasOwnProperty(r)&&n.append(r,i[r]);for(var r in o.options.cropData)o.options.cropData.hasOwnProperty(r)&&n.append(r,o.options.cropData[r]);$.ajax({url:o.options.cropUrl,data:n,context:t.body,cache:!1,contentType:!1,processData:!1,type:"POST"}).always(function(t){response="object"==typeof t?t:jQuery.parseJSON(t),"success"==response.status&&(o.options.imgEyecandy&&o.imgEyecandy.hide(),o.destroy(),o.obj.append('<img class="croppedImg" src="'+response.url+'">'),""!==o.options.outputUrlId&&$("#"+o.options.outputUrlId).val(response.url),o.croppedImg=o.obj.find(".croppedImg"),o.init(),o.hideLoader()),400<=response.status&&(o.options.onError&&o.options.onError.call(o,response),o.hideLoader(),setTimeout(function(){o.reset()},2e3)),o.options.onAfterImgCrop&&o.options.onAfterImgCrop.call(o,response)})},showLoader:function(){var o=this;o.obj.append(o.options.loaderHtml),o.loader=o.obj.find(".loader")},hideLoader:function(){var o=this;o.loader.remove()},reset:function(){var o=this;o.destroy(),o.init(),$.isEmptyObject(o.croppedImg)||(o.obj.append(o.croppedImg),""!==o.options.outputUrlId&&$("#"+o.options.outputUrlId).val(o.croppedImg.attr("url"))),"function"==typeof o.options.onReset&&o.options.onReset.call(o)},destroy:function(){var o=this;o.options.modal&&!$.isEmptyObject(o.modal)&&o.destroyModal(),o.options.imgEyecandy&&!$.isEmptyObject(o.imgEyecandy)&&o.destroyEyecandy(),$.isEmptyObject(o.cropControlsUpload)||o.cropControlsUpload.remove(),$.isEmptyObject(o.cropControlsCrop)||o.cropControlsCrop.remove(),$.isEmptyObject(o.loader)||o.loader.remove(),$.isEmptyObject(o.form)||o.form.remove(),o.obj.html("")}}}(window,document);
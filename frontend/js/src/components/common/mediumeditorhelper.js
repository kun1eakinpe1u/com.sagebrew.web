/* global AutoList, MediumEditor*/

export function createMediumEditor(selectorString, placeholderText) {
    var autolist = new AutoList(),
        editor = new MediumEditor(".editable", {
            buttonLabels: 'fontawesome',
            placeholder: {text: placeholderText, hideOnClick: true},
            autoLink: true,
            targetBlank: true,
            toolbar: {
                buttons: ['bold', 'italic', 'underline', 'anchor', 'h2',
                    'h3', 'orderedlist', 'unorderedlist',
                    'justifyLeft', 'justifyCenter', 'quote']
            },
            extensions: {
                'autolist': autolist,
                'fileDragging': {}
            },
            anchor: {
                linkValidation: true
            }
        });
    // Uploading images here via fileUploadOptions because submitting the
    // binary data directly causes browsers to crash if the images are
    // too large/there are too many images
    $(selectorString).mediumInsert({
        editor: editor,
        addons: {
            images: {
                fileUploadOptions: {
                    url: "/v1/upload/?editor=true",
                    acceptFileTypes: /(.|\/)(gif|jpe?g|png)$/i,
                    paramName: "file_object"
                }
            },
            embeds: {
                oembedProxy: null
            }
        }
    });
    return editor;
}
$(document).ready(function(){
    $("#answerSubmitForm").bootstrapValidator({
        framework: 'bootstrap',
        err: {
            container: '#fname_errors'
        },
        feedbackIcons: {
            valid: 'glyphicon glyphicon-ok',
            validating: 'glyphicon glyphicon-refresh'
        },
        live: 'enabled',
        submitButtons: '#submit_answer',
        fields: {
            answer_content: {
                group: 'sb_answer_input',
                validators: {
                    notEmpty: {
                        message: "Email is required"
                    },
                    stringLength: {
                        max: 200,
                        message: "Email must not exceed 200 characters"
                    }
                }
            }
        }
    })
});

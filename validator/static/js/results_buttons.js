function ajax_delete_result(result_id, redirect) {
    if (!confirm('Do you really want to delete the result?')) {
           return;
    }
    var url = result_url.replace('00000000-0000-0000-0000-000000000000',result_id);

    $.ajaxSetup({
          headers: { "X-CSRFToken": csrf_token }
    });

    $.ajax({
        url: url,
        type: 'DELETE',
        success: function (return_data) {
            $('#result_row_'+result_id).remove();
            if (redirect) window.location.replace(result_list_url);
        }
    });
}

function ajax_stop_validation(result_id) {
    if (!confirm('Do you really want to stop the validation?')) {
        return;
    }
    var url = stop_validation_url.replace('00000000-0000-0000-0000-000000000000',result_id);

    $.ajaxSetup({
        headers : { "X-CSRFToken" : csrf_token }
    });

    $.ajax({
        url : url,
        type : 'DELETE',
        success : function(return_data) { location.reload(); }
    });
}

function ajax_archive_result(result_id, archive) {
    if (!confirm('Do you want to '+ (archive ? 'archive' : 'un-archive') +' the result'+ (archive ? '' : ' (allow auto-cleanup)') +'?')) {
        return;
    }
    var url = result_url.replace('00000000-0000-0000-0000-000000000000',result_id);

    $.ajaxSetup({
          headers: { "X-CSRFToken": csrf_token }
    });

    $.ajax({
        url: url,
        type: 'PATCH',
        data : { "archive" : archive },
        success : function(return_data) { location.reload(); }
    });
}

function ajax_publish_result(result_id) {
    $('#publishDialog').modal('hide');

    var url = result_url.replace('00000000-0000-0000-0000-000000000000', result_id);

    // convert publishing form to dictionary
    var formdata =  $('#publishing_form').serializeArray();
    formdata.push({ name: 'publish', value: 'true'});

    $.ajaxSetup({
          headers: { "X-CSRFToken": csrf_token }
    });

    $.ajax({
        url: url,
        type: 'PATCH',
        data : formdata,
        success: function (return_data) { location.reload(); },
        error : function(return_data) {
            if (return_data.status = '420') {
                // form validation error
                $('#publishDialog').replaceWith(return_data.responseText);
                $('#publishDialog').modal('show');
            } else {
                // other, unexpected error
                var errorText = return_data.responseText.replace(/.*\'(.*)\'.*/g, '$1');
                alert('Could not publish your results: ' + errorText + '\n\nPlease try again in a few minutes and if the issue persists email ' + admin_mail);
            }
        },
        beforeSend: function() {
            $('.publishingNote').show();
            $('.patchButtonGroup').hide();
        },
        complete: function() {
            $('.publishingNote').hide();
            $('.patchButtonGroup').show();
        }
    });
}

function ajax_extend_result(result_id) {
    if (!confirm('Do you want to extend the lifespan of this result?')) {
        return;
    }
    var url = result_url.replace('00000000-0000-0000-0000-000000000000',result_id);

    $.ajaxSetup({
          headers: { "X-CSRFToken": csrf_token }
    });

    $.ajax({
        url: url,
        type: 'PATCH',
        data : { "extend" : true },
        success : function(return_data) {
            var newExpiry = new Date(return_data);
            alert('The expiry date of your validation has been shifted to ' + newExpiry.toLocaleDateString())
            location.reload();
        }
    });
}

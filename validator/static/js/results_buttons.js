function ajax_delete_result(result_id) {
    if (!confirm('Do you really want to delete the result?')) {
           return;
    }
    var url = delete_result_url.replace('00000000-0000-0000-0000-000000000000',result_id);

    $.ajaxSetup({
          headers: { "X-CSRFToken": csrf_token }
    });

    $.ajax({
        url: url,
        type: 'DELETE',
        success: function (return_data) { $('#result_row_'+result_id).remove() }
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
    var url = archive_result_url.replace('00000000-0000-0000-0000-000000000000',result_id);

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

function ajax_extend_result(result_id) {
    if (!confirm('Do you want to extend the lifespan of this result?')) {
        return;
    }
    var url = extend_result_url.replace('00000000-0000-0000-0000-000000000000',result_id);

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

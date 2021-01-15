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
//    console.log(location, url)

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

function toggle_editing(obj){
    var target = obj.currentTarget;
    var target_parent = $(target).parent();
    target_parent.find('button.edit_name_btn').toggleClass('d-none');
    target_parent.find('button.save_name_btn').toggleClass('d-none');
    target_parent.find('button.cancel_editing_btn').toggleClass('d-none');
    target_parent.find('span.no_edit_name').toggleClass('d-none');
    target_parent.find('input.edit_name').toggleClass('d-none');
    return target_parent
}

function edit_name(obj){
    var target_parent = toggle_editing(obj)
    var old_name = target_parent.find('span.no_edit_name').html()
    target_parent.find('input.edit_name').val(old_name)
}

function cancel_editing(obj){
    toggle_editing(obj)
}


function ajax_save_name(obj, result_id){
    var target_parent = toggle_editing(obj)
    var new_name = target_parent.find('input.edit_name').val()

    var url =  result_url.replace('00000000-0000-0000-0000-000000000000', result_id);
    var formdata = { "save_name" : true,
                    "new_name" : new_name};

    $.ajaxSetup({
        headers : { "X-CSRFToken" : csrf_token }
    });

    $.ajax({
        url: url,
        type: 'PATCH',
        data : formdata,
        success : function(return_data) { location.reload(); }
    });

}

function ajax_attach_validation(result_id){
  var url =  result_url.replace('00000000-0000-0000-0000-000000000000', result_id);
  var formdata = { "add_validation" : true};
  $.ajaxSetup({
      headers : { "X-CSRFToken" : csrf_token }
  });

  $.ajax({
      url: url,
      type: 'POST',
      data: formdata,
      success : function(return_data) {
        location.reload();
        !alert(return_data);
      }
  });
}

function ajax_detach_validation(result_id){
  if (!confirm('Do you really want to remove this validation from your list?')) {
         return;
  }
  var url =  result_url.replace('00000000-0000-0000-0000-000000000000', result_id);
  var formdata = { "remove_validation" : true};
  $.ajaxSetup({
      headers : { "X-CSRFToken" : csrf_token }
  });

  $.ajax({
      url: url,
      type: 'POST',
      data: formdata,
      success : function(return_data) {
        location.reload();
      }
  });
}

function ajax_copy_validation(result_id){
  var url =  result_url.replace('00000000-0000-0000-0000-000000000000', result_id);
  var formdata = { "copy_validation" : true};
  $.ajaxSetup({
      headers : { "X-CSRFToken" : csrf_token }
  });

  $.ajax({
      url: url,
      type: 'POST',
      data: formdata,
      success : function(return_data) {
        new_url = result_url.replace('00000000-0000-0000-0000-000000000000', return_data['run_id']);
        window.location.href = new_url
      }
  });
}

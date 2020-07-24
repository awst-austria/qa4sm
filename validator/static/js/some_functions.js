console.log("I'm here")

function start_editing(obj){
    var target = obj.currentTarget;
    var target_parent = $(target).parent();
    target_parent.find('button.edit_name_btn').toggleClass('d-none');
    target_parent.find('button.save_name_btn').toggleClass('d-none');
    target_parent.find('span.no_edit_name').toggleClass('d-none');
    target_parent.find('input.edit_name').toggleClass('d-none');
    return target_parent
}

function edit_name(obj){
    var target_parent = start_editing(obj)
    var old_name = target_parent.find('span.no_edit_name').html()
    target_parent.find('input.edit_name').val(old_name)
    console.log(old_name)
}


function save_name(obj, result_id){
    var target_parent = start_editing(obj)
    var new_name = target_parent.find('input.edit_name').val()

    var url =  result_url.replace('00000000-0000-0000-0000-000000000000', result_id);
    var formdata = { "save_name" : true,
                    "new_name" : new_name};

    $.ajaxSetup({
        headers : { "X-CSRFToken" : csrf_token }
    });
//
    $.ajax({
        url: url,
        type: 'PATCH',
        data : formdata,
        success : function(return_data) { location.reload(); }
    });

}
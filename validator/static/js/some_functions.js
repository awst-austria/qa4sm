console.log("I'm here")

function edit_name(obj){

var target = obj.currentTarget;
var target_parent = $(target).parent();
target_parent.find('button.edit_name_btn').toggleClass('d-none')
target_parent.find('button.save_name_btn').toggleClass('d-none')
target_parent.find('span.no_edit_name').toggleClass('d-none')
target_parent.find('input.edit_name').toggleClass('d-none')

}


function monika(obj, result_id){
edit_name(obj)

}
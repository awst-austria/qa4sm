console.log("I'm here")

function toggle_children_class(element, class_name){
    $(element).toggleClass(class_name);
    $.each($(element).find("*"), function(id, child){
        $(child).toggleClass(class_name);
    })
}


function verify_html_element(element_class){
        var selector = '.'+element_class;
        if  ($(selector).length>1){
            $.each($(selector), function(ind, element){
                if (!$(element).hasClass('d-none')){
                    $(element).empty();
                    $(element).remove();
                } else {
                    toggle_children_class(element, 'd-none');
                }
            })
        }


}


//            if ($(".continent_container").length>1){
//                $.each($(".continent_container"), function(ind, element){
//                    if (!$(element).hasClass('d-none')){
//                        $(element).empty()
//                        $(element).remove()
//                    } else {
//                        $(element).toggleClass('d-none')
//                        $.each($(element).children(), function(id, child){
//                            $(child).toggleClass('d-none')
//                            $.each($(child).children(), function(id, grandchild){
//                                $(grandchild).toggleClass('d-none')
//                            })
//                        })
//                    }
//
//                })



function get_version_id(){
       var versionId = $(this).val();
       $('#id_target_hidden_input_version').val(versionId)
       console.log(versionId)
}
//
//        function ajax_get_default_version_id() {
//            var url = $("#validation_form").attr("data-options-url");
//            var datasetId = $(this).val();
//            var widgetId = $(this).attr('id');
//            var filterWidgetId = widgetId.replace(/dataset$/, "filters");
//            var paramFilterWidgetId = widgetId.replace(/dataset$/, "parametrised_filters");
//            $.ajax({
//                url: url,
//                data: { 'dataset_id': datasetId, 'filter_widget_id': filterWidgetId, 'param_filter_widget_id': paramFilterWidgetId },
//                success: function (return_data) {
//                    var dataset_widget = "#" + widgetId;
//                    var version_widget = dataset_widget.replace(/dataset$/, "version");
//                    console.log(return_data['versions'])
////                    var versions_id =
////                    $(version_widget).(return_data['versions']);
//
//                }
//            });
//        }





//for (var i=0; i<versions.length; i++){
//    console.log(versions[i])
//}



//function get_version_id(){
//       var datasetName = $(this).find('option:selected').text();
//       var versionId = '#' + $(this).attr('id').replace(/dataset$/, 'version');
//       console.log($(versionId).val());

//    var versionId = $(this).val();
//    console.log(versionId)
//    var url = $("#validation_form").attr("data-options-url");
//            $.ajax({
//                url: url,
//                success: function (return_data) {
//                    var dataset_widget = "#" + widgetId;
//                    var version_widget = dataset_widget.replace(/dataset$/, "version");
//                    var variable_widget = dataset_widget.replace(/dataset$/, "variable");
//                    var filter_widget = "#" + filterWidgetId;
//                    var param_filter_widget = "#" + paramFilterWidgetId;
//                    $(version_widget).html(return_data['versions']);
//                    $(variable_widget).html(return_data['variables']);
//                    $(filter_widget).html(return_data['filters']);
//                    $(param_filter_widget).html(return_data['paramfilters']);
//                }
//            });
//        }
//


//}

//       function ajax_change_dataset() {
//            var url = $("#validation_form").attr("data-options-url");
//            var datasetId = $(this).val();
//            var widgetId = $(this).attr('id');
//            var filterWidgetId = widgetId.replace(/dataset$/, "filters");
//            var paramFilterWidgetId = widgetId.replace(/dataset$/, "parametrised_filters");
//            $.ajax({
//                url: url,
//                data: { 'dataset_id': datasetId, 'filter_widget_id': filterWidgetId, 'param_filter_widget_id': paramFilterWidgetId },
//                success: function (return_data) {
//                    var dataset_widget = "#" + widgetId;
//                    var version_widget = dataset_widget.replace(/dataset$/, "version");
//                    var variable_widget = dataset_widget.replace(/dataset$/, "variable");
//                    var filter_widget = "#" + filterWidgetId;
//                    var param_filter_widget = "#" + paramFilterWidgetId;
//                    $(version_widget).html(return_data['versions']);
//                    $(variable_widget).html(return_data['variables']);
//                    $(filter_widget).html(return_data['filters']);
//                    $(param_filter_widget).html(return_data['paramfilters']);
//                }
//            });
//        }
console.log("I'm here")

function find_parents(obj){
    var target = obj.currentTarget;
    var target_parent = $(target).parent();
    return target_parent
}


function removeTab(tabContentClass, tabLinkClass, formsetPrefix, addButton, removeButton){
// taking tabs (referred as tabLinkClass in validate.html) and containers (referred as tabContentClass)
// and choosing the ones to be removed (the active ones)
    var tabs = $(tabLinkClass)
    var containers = $(tabContentClass)
    var tab_to_remove = $(tabLinkClass+'.active')
    var container_to_remove = $(tabContentClass+'.active.show')

// taking totalNoForms so that plus sign can be displayed again
    var totalSelector = '#id_' + formsetPrefix + '-TOTAL_FORMS';
    var totalNoForms = $(totalSelector).val();
//    console.log(totalNoForms)
    var maxSelector = '#id_' + formsetPrefix + '-MAX_NUM_FORMS';

// this condition enables removing datasets unless there is only one left
// additionally it's checked if there is the same number of tabs and containers to prevent unexpected errors
    if (tabs.length>1 && containers.length>1 && tabs.length == containers.length){

    // taking next tabs and containers, to change their id's
        var all_next_tabs = tab_to_remove.nextAll(tabLinkClass)
        var all_next_containers = container_to_remove.nextAll(tabContentClass)

    //taking next and previous tabs and containers, to make them active after removal current items
        var next_tab = tab_to_remove.next()
        var prev_tab = tab_to_remove.prev()

        var next_container = container_to_remove.next()
        var prev_container = container_to_remove.prev()

    //removing current tab and container
        tab_to_remove.remove()
        container_to_remove.remove()

    // showing add button again
        totalNoForms--
         $(totalSelector).val(totalNoForms);
         if (totalNoForms < $(maxSelector).val()) {
                addButton.show();
            }

    // changing attributes of following items
        for (var i=0; i < all_next_tabs.length; i++){
//            console.log(totalNoForms-(i+1))
            var current_tab = all_next_tabs.slice(i)
            var current_container = all_next_containers.slice(i)

//            var old_tab_id = current_tab.attr('id')
            var old_id = current_container.attr('id')
            var new_num = totalNoForms-(i+1)
            var new_id = old_id.slice(0,-1) + new_num
            var new_tab_id = new_id + '-tab'

            // setting new values
            current_tab.attr('id', new_tab_id)
            current_tab.attr('href', '#' + new_id)
            current_tab.attr('aria-controls', '#' + new_id)

            current_container.attr('id', new_id)
            current_container.attr('aria-labelledby', new_tab_id)

            current_container.find(':input').each(function() {
                var id = $(this).attr('id').replace(old_id, new_id);
                var name = id.replace(/^id_/, '')
                $(this).attr({'name': name, 'id': id});
            });

            current_container.find('label').each(function() {
                var newFor = $(this).attr('for').replace(old_id, new_id);
                $(this).attr('for', newFor);
            });

            current_container.find('.tabSpecific').each(function() {
                var id = $(this).attr('id').replace(old_id, new_id);
                $(this).attr('id', id);
            });

           $('#' + new_id + '-dataset').change()
        }

// checking if there is a tab and a container after the ones removed and set them to be active;
// if the last one is being removed, setting the previous ones as the active
// tabLinkClass and tabContentClass are sliced to remove the dot at the beginning
        if (next_tab.hasClass(tabLinkClass.slice(1, ))){
            next_tab.toggleClass('active')
        } else {
            prev_tab.toggleClass('active')
        }

        if (next_container.hasClass(tabContentClass.slice(1, ))){
            next_container.toggleClass('active show')
        } else {
            prev_container.toggleClass('active show')
        }
    }
}



$('#remove_dc_form').click(function() {
    removeTab('.dc_form', '.dc_form_link', 'datasets',  $('#add_dc_form'), $(this));
});



//    var active_tab = target.find('a.dc_form_link.active')
//    var active_container = $('div.dc_form.active.show')
//
//
//    console.log(containers)
//    console.log(tabs)
//    console.log(active_tab)
//    console.log(active_container)
//    console.log($(active_tab).next().hasClass('.dc_form_link'))
//
//if (tabs.length>1 && containers.length>1 && tabs.length == containers.length){
//    if($(active_tab).next().hasClass('.dc_form_link')){
//        $(active_tab).next().toggleClass('active')
//    } else{
//        $(active_tab).prev().toggleClass('active')
//        active_tab.remove()
//    }
//}
//    if (tabs.length>1 && containers.length>1 && tabs.length == containers.length){
//        for(var i=0; i<tabs.length; i++){
//            var tab = tabs[i];
//            var container = containers[i]
//
//            if($(tab).hasClass('active')){
//                console.log($(tab).prev())
//
//                if ($(tab).next().hasClass('.dc_form_link')){
//                    $(tab).next().toggleClass('active')
//                } else {
//                    $(tab).prev().toggleClass('active')
//                }
//
//                console.log($(tab).prev())
//                tab.remove()
//            }
//
//            if($(container).hasClass('active')){
//                console.log($(container).prev())
////                console.log($(container).next().length == 0)
//
//                if($(container).next().length == 0){
//                    $(container).prev().toggleClass('active show')
//                }
//                console.log($(container).prev())
//                container.remove()
//            }
//
//        }
////        var tab_to_remove = tabs.find('.active')
////        console.log(tab_to_remove)
//    }
//
//
//    $(tab).remove()
//    $(container).remove()
//
//    for(var i=0; i<tabs.length; i++){
//        console.log($(tabs[i]).hasClass('active'))
//        if($(tabs[i]).hasClass('active')){
//            $(tabs[i]).remove()
//        }
//    }
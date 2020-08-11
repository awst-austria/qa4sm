console.log("I'm here")

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
                $(removeButton).css('margin-left', '0.3rem')
                addButton.show();
            }
         if (totalNoForms == 1) {
                removeButton.hide();
            }

    // changing attributes of following items
        for (var i=0; i < all_next_tabs.length; i++){

            var current_tab = $(all_next_tabs[i])
            var current_container = $(all_next_containers[i])

            var old_id = current_container.attr('id')
            var new_num = parseInt(old_id.slice(-1)) - 1
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

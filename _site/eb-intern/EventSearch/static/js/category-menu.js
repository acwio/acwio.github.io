// Global JavaScript object for prior selections
var prior_selections = {};

/**
 * Checks if all dropdown menus have valid selections.
 * @returns {boolean}
 */
function validCategorySelections(){
    /*  retrieve the selected values */
    var cat1_sel = $('#cat_1').val();
    var cat2_sel = $('#cat_2').val();
    var cat3_sel = $('#cat_3').val();

    /*  validate the presence of a selection in each menu */
    if(cat1_sel && cat2_sel && cat3_sel){   /*  all selections have valid data! */
        return true;
    }
    else{   /*  at least one of the selections is nil */
        return false;
    }
}


/**
 * Updates Category selection form upon dropdown selection.
 * @param event
 */
function updateCategorySelectionForm(event){
   /* check if we have valid category selections */
    if(validCategorySelections()){
        /*  remove the disabled attribute of the submit button */
        $('#cat-submit').removeAttr('disabled');
    }
    else{
        /*  otherwise, disable the attribute of the submit button */
        $('#cat-submit').attr('disabled', 'disabled');
    }

    /* determine which dropdown fired the event */
    var sel_val;
    if(event.id === "cat_1"){
        /*  get the value of category 1 */
        sel_val = $('#cat_1').val();

        /*  disable the selection in the other two menus */
        $("#cat_2 option[value="+sel_val+"]").prop('disabled','disabled');
        $("#cat_3 option[value="+sel_val+"]").prop('disabled','disabled');

        /*  enable the previous selection in the other two menus */
        $("#cat_2 option[value="+prior_selections[event.id]+"]").removeAttr('disabled');
        $("#cat_3 option[value="+prior_selections[event.id]+"]").removeAttr('disabled');
    }
    else if(event.id === "cat_2"){
        /*  get the value of category 1 */
        sel_val = $('#cat_2').val();

        /*  disable the selection in the other two menus */
        $("#cat_1 option[value="+sel_val+"]").prop('disabled','disabled');
        $("#cat_3 option[value="+sel_val+"]").prop('disabled','disabled');

        /*  enable the previous selection in the other two menus */
        $("#cat_1 option[value="+prior_selections[event.id]+"]").removeAttr('disabled');
        $("#cat_3 option[value="+prior_selections[event.id]+"]").removeAttr('disabled');
    }
    else if(event.id === "cat_3"){
        /*  get the value of category 1 */
        sel_val = $('#cat_3').val();

        /*  disable the selection in the other two menus */
        $("#cat_1 option[value="+sel_val+"]").prop('disabled','disabled');
        $("#cat_2 option[value="+sel_val+"]").prop('disabled','disabled');

        /*  enable the previous selection in the other two menus */
        $("#cat_1 option[value="+prior_selections[event.id]+"]").removeAttr('disabled');
        $("#cat_2 option[value="+prior_selections[event.id]+"]").removeAttr('disabled');
    }

    /*  update the prior_selections object with the new selection */
    prior_selections[event.id] = sel_val;
}
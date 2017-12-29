//used for csrf 
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function change_icons(save, box) {
    if(save && (box === 1)){
        $("#save-icon-1").toggleClass("hidden");
        $("#edit-icon-1").removeClass("fa-close").addClass("fa-pencil");
        $("#edit-icon-1").removeClass("fa-close").addClass("fa-pencil");
        $("#alternate-id").removeClass("form-control").addClass("form-control-plaintext").prop("readonly", true);
    }
    else if(!save && (box === 1)){
        if($("#save-icon-1").hasClass("hidden")) {
            $("#save-icon-1").toggleClass("hidden");
            $("#edit-icon-1").removeClass("fa-pencil").addClass("fa-close");
            $("#alternate-id").removeClass("form-control-plaintext").addClass("form-control").removeAttr("readonly");
        }
        else {
            $("#save-icon-1").toggleClass("hidden");
            $("#edit-icon-1").removeClass("fa-close").addClass("fa-pencil");
            $("#alternate-id").removeClass("form-control").addClass("form-control-plaintext").prop("readonly", true);
        }
    }
    if(save && (box === 2)){
        $("#save-icon-2").toggleClass("hidden");
        $("#edit-icon-2").removeClass("fa-close").addClass("fa-pencil");
        $("#start-date").removeClass("form-control").addClass("form-control-plaintext").prop("readonly", true);
        $("#end-date").removeClass("form-control").addClass("form-control-plaintext").prop("readonly", true);
    }
    else if(!save && (box === 2)){
        if($("#save-icon-2").hasClass("hidden")) {
            $("#save-icon-2").toggleClass("hidden");
            $("#edit-icon-2").removeClass("fa-pencil").addClass("fa-close");
            $("#start-date").removeClass("form-control-plaintext").addClass("form-control").removeAttr("readonly");
            $("#end-date").removeClass("form-control-plaintext").addClass("form-control").removeAttr("readonly");
        }
        else {
            $("#save-icon-2").toggleClass("hidden");
            $("#edit-icon-2").removeClass("fa-close").addClass("fa-pencil");
            $("#start-date").removeClass("form-control").addClass("form-control-plaintext").prop("readonly", true);
            $("#end-date").removeClass("form-control").addClass("form-control-plaintext").prop("readonly", true);
        }
    }
    else if(save && (box === 3)){
        $("#save-icon-3").toggleClass("hidden");
        $("#edit-icon-3").removeClass("fa-close").addClass("fa-pencil");
        $("#description").removeClass("disappear");
        $("#variables").removeClass("disappear");
        $("#description-form").toggleClass("hidden").toggleClass("disappear");
        $("#variables-form").toggleClass("hidden").toggleClass("disappear");
    }
    else if(!save && (box === 3)){
        if($("#save-icon-3").hasClass("hidden")) {
            $("#save-icon-3").toggleClass("hidden");
            $("#edit-icon-3").removeClass("fa-pencil").addClass("fa-close");
            $("#description").addClass("disappear");
            $("#variables").addClass("disappear");
            $("#description-form").toggleClass("hidden").toggleClass("disappear");
            $("#variables-form").toggleClass("hidden").toggleClass("disappear");
        }
        else {
            $("#save-icon-3").toggleClass("hidden");
            $("#edit-icon-3").removeClass("fa-close").addClass("fa-pencil");
            $("#description").removeClass("disappear");
            $("#variables").removeClass("disappear");
            $("#description-form").toggleClass("hidden").toggleClass("disappear");
            $("#variables-form").toggleClass("hidden").toggleClass("disappear");
        }
    }
}

$(document).ready(function () {
    //caching frequently searched dom elements
    let $proj_orgs = $(".proj-orgs"),
        $proj_orgs_dd = $(".org-dropdown"),
        $act_date = $(".act-date"),
        $act_note = $(".act-note"),
        $header_row_2_tab = $(".header-row-2-tab");

    //project_id
    let proj_id = window.location.href.substr(window.location.href.lastIndexOf('/') + 1);

    /***** DESCRIPTION ******/

    //start date & end date, description & variable
    let current_start = $("#start-date").val().trim();
    let current_end = $("#end-date").val().trim();

    //description & variable
    let current_des = $("#description-form").val().trim();
    let current_var = $("#variables-form").val().trim();

    //current alternateid
    let current_alternateid = $("#alternate-id").val().trim();

    $(document).on("click", "#edit-icon-1", function () {
        change_icons(false,1);
        $("#alternate-id").val(current_alternateid);
    });

    $(document).on("click", "#edit-icon-2", function () {
        change_icons(false,2);
        $("#start-date").val(current_start);    //revert back to original value because it is not saved
        $("#end-date").val(current_end);
    });

    $(document).on("click", "#edit-icon-3", function () {
        change_icons(false,3);
    });

    $(document).on("click", "#save-icon-1", function () {
        let new_alternateid = $("#alternate-id").val().trim();

        if(current_alternateid === new_alternateid) {
            return;
            change_icons(true, 1);
        }
        else {
            $.ajax({
                method: "POST",
                url: "/dashboard/project/update_ajax/",
                data: {
                    "proj_id": proj_id,
                    "alternate_id": new_alternateid,
                },
                dataType: "json",
                success: function(data) {
                    if(data['alternate_success']) {
                        change_icons(true, 1);
                    }
                    else {

                    }
                }
            });
        }
    })

    $(document).on("click", "#save-icon-2", function () {
        let new_start = $("#start-date").val().trim();
        let new_end = $("#end-date").val().trim();

        if(current_start === new_start && current_end === new_end){
            change_icons(true, 2);
        }
        else if(current_start != new_start && current_end === new_end){
            $.ajax({
                method: "POST",
                url: "/dashboard/project/update_ajax/",
                data: {
                    "proj_id": proj_id,
                    "start_date": new_start,
                },
                dataType: "json",
                success: function(data){
                    if(data["start_success"]){
                        change_icons(true, 2);
                        current_start = new_start;
                    }
                    else{
                        
                    }
                }
            });
        }
        else if(current_start === new_start && current_end != new_end){
            $.ajax({
                method: "POST",
                url: "/dashboard/project/update_ajax/",
                data: {
                    "proj_id": proj_id,
                    "end_date": end_date,
                },
                dataType: "json",
                success: function(data){
                    if(data["end_success"]){
                        change_icons(true, 2);
                        current_end = new_end;
                    }
                    else{
                        
                    }
                }
            });
        }
        else if(current_start != new_start && current_end != new_end){
            $.ajax({
                method: "POST",
                url: "/dashboard/project/update_ajax/",
                data: {
                    "proj_id": proj_id,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                dataType: "json",
                success: function(data){
                    if(!data["end_success"]){
                        
                    }
                    if(!data["start_success"]){
                        
                    }
                    if(data["end_success"] && data["start_success"]){
                        change_icons(true, 2);
                        current_start = new_start;
                        current_end = new_end;
                    }
                }
            });
        }
    });

    $(document).on("click", "#save-icon-3", function () {
        let new_des = $("#description-form").val().trim();
        let new_var = $("#variables-form").val().trim();

        if(current_des === new_des && current_var === new_var){
            change_icons(true, 3);
        }
        else if(current_des != new_des && current_var === new_var){
            $.ajax({
                method: "POST",
                url: "/dashboard/project/update_ajax/",
                data: {
                    "proj_id": proj_id,
                    "new_des": new_des,
                },
                dataType: "json",
                success: function(data){
                    if(data["description_success"]){
                        change_icons(true, 3);
                        current_des = new_des;
                        $("#description").text(new_des);    //when in edit mode, a new dom element is shown (the text area element) and the ...
                                                            //old element is hidden temporarily. thus when we return to regular mode, the old div...
                                                            //(description) reappears. We need to update that to the new dsecription.
                    }
                    else{
                        
                    }
                }
            });
        }
    });



    /****** ACTIVITIES ******/

    //used for the activities section, we will save this and then dynamically fill out the textarea dom element with this
    let dict_of_original = {};

    //adding a new activity
    $(document).on("click", "#add-act", function () {
        console.log("Add activity");
    });

    //when one of the activity buttons gets pressed, we will toggle the the others button to appear while also making the activity row into a form
    $(document).on("click", ".act-edit", function () {
        if(!$(this).hasClass("disappear")){
            original_note = $(this).parent().prev().text().trim();
            original_date = $(this).parent().prev().prev().text().trim();
            dict_of_original[$(this).parent().parent().data("id")] = [original_note, original_date]
            $(this).parent().prev().html("<textarea class='form-control' rows='4'>" + original_note + "</textarea>");
            $(this).parent().prev().prev().html("<input type='text' class='form-control' value='" + original_date + "'>");
        }

        //used to hide the other buttons
        $(this).toggleClass("disappear").toggleClass("hidden");
        $(this).next().toggleClass("disappear").toggleClass("hidden");
        $(this).next().next().toggleClass("disappear").toggleClass("hidden");
        $(this).next().next().next().toggleClass("disappear").toggleClass("hidden");
    });

    $(document).on("click", ".act-save", function () {
        new_note = $(this).parent().prev().children().val();
        new_date = $(this).parent().prev().prev().children().val();
        act_id = $(this).parent().parent().data("id");
        let ajax_flag = 0;
        $this = $(this); //so we can change the icons in ajax. Without this, $(this) is not in the ajax function scope

        //check if the values are the same. Only send the data of the new as an ajax call
        send_data = {"proj_id": proj_id, "act_id": act_id};
        if(dict_of_original[$(this).parent().parent().data("id")][0] != new_note){
            send_data["new_note"] = new_note;
            ajax_flag = 1;
        }
        if(dict_of_original[$(this).parent().parent().data("id")][1] != new_date){
            send_data["new_date"] = new_date;
            ajax_flag = 1;
        }

        if(ajax_flag > 0) { //only execute if the row has been changed
            //make ajax call to save date and note
            $.ajax({
                method: "POST",
                url: "/dashboard/project/update_ajax/activity/",
                data: send_data,
                dataType: "json",
                success: function (data) {
                    if(data["success"]){      
                        //change icons back
                        if(!$this.hasClass("disappear")){
                            $this.parent().prev().html(new_note);
                            $this.parent().prev().prev().html(new_date);
                        }

                        $this.prev().toggleClass("disappear").toggleClass("hidden");
                        $this.toggleClass("disappear").toggleClass("hidden");
                        $this.next().toggleClass("disappear").toggleClass("hidden");
                        $this.next().next().toggleClass("disappear").toggleClass("hidden");
                    }
                }
            });
        } else {
            //change icons back
            if(!$(this).hasClass("disappear")){
                $(this).parent().prev().html(new_note);
                $(this).parent().prev().prev().html(new_date);
            }

            $(this).prev().toggleClass("disappear").toggleClass("hidden");
            $(this).toggleClass("disappear").toggleClass("hidden");
            $(this).next().toggleClass("disappear").toggleClass("hidden");
            $(this).next().next().toggleClass("disappear").toggleClass("hidden"); 
        }

    }); 

    $(document).on("click", ".act-undo", function () {
        if(!$(this).hasClass("disappear")){
            //using the key (the unique id for our row), find out the value (original note 0th index, original_date 1st index)
            $(this).parent().prev().html(dict_of_original[$(this).parent().parent().data("id")][0]);
            $(this).parent().prev().prev().html(dict_of_original[$(this).parent().parent().data("id")][1]);
        }

        $(this).prev().prev().toggleClass("disappear").toggleClass("hidden");
        $(this).prev().toggleClass("disappear").toggleClass("hidden");
        $(this).toggleClass("disappear").toggleClass("hidden");
        $(this).next().toggleClass("disappear").toggleClass("hidden");
    });

    $(document).on("click", ".act-arc", function () {

    });

    /****** TAB AJAX ******/

    $header_row_2_tab.on("click", function() {
        $tab_dom = $(this);

        $.ajax({
            method: "GET",
            url: "/dashboard/project/detail/ajax_tab/",
            data: {
                "proj_id": proj_id,
                "type": $(this).attr("id"),
            },
            dataType: "json",
            success: function (data) {
                $("#indiv-view-pane").html(data['html']);
                $header_row_2_tab.removeClass("header-row-2-tab-active");
                $tab_dom.addClass("header-row-2-tab-active");

                if(data['tab'] == "desc"){
                    current_start = $("#start-date").val().trim();
                    current_end = $("#end-date").val().trim();
                    current_des = $("#description-form").val().trim();
                    current_var = $("#variables-form").val().trim();
                    current_alternateid = $("#alternate-id").val().trim();
                }
                else if(data['tab'] == "users"){

                }
                else if(data['tab'] == "activity"){     //on activity page load

                }
                else if(data['tab'] == "requests"){

                }
                else if(data['tab'] == "documents"){

                }
            }
        });
    });

    // change open/closed notification
    $("#archive").on("click", function () {
        $.ajax({
            method: "POST",
            url: "/dashboard/project/update_ajax/",
            data: {
                "proj_id": proj_id,
                "archive": true,
            },
            dataType: "json",
            success: function(data) {
                //change the text to CLOSED and the archive-color to red
                if(data["archive_success"]){
                    if($("#archive").children().first().hasClass("notification-color-closed")){
                        $("#archive").children().first().removeClass("notification-color-closed");
                        $("#archive").children().first().addClass("notification-color-open");
                        $("#archive b").text("OPEN");
                    }
                    else{
                        $("#archive").children().first().removeClass("notification-color-open");
                        $("#archive").children().first().addClass("notification-color-closed");
                        $("#archive b").text("CLOSED");
                    }
                }
            }
        })
    });
});
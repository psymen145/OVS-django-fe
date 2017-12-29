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

$(document).ready(function () {
    //caching frequently used dom elements
    let $userorg = $("#user-org"),
        $bvs_requested = $(".requested"),
        $bvs_signed = $(".signed"),
        $user_org_dd = $("#user-org-dropdown"),
        $input = $("input"),
        $edit_icon_1 = $("#edit-icon-1"),   //used for the upper left box (email, phone, org)
        $edit_icon_2 = $("#edit-icon-2"),
        $save_icon_1 = $("#save-icon-1"),   //used for the bvs dates box
        $save_icon_2 = $("#save-icon-2"),
        $staticEmail = $("#staticEmail"),
        $staticPhone = $("#staticPhone"),
        $datatogglepop = $("[data-toggle='popover']"),
        $modalbody = $(".modal-body"),
        $userassoc = $(".user-assoc-checkbox");     //used for the checkbox in the project subsection

    let user_id = window.location.href.substr(window.location.href.lastIndexOf('/') + 1);

    //store the user's info right when the page loads
    let current_email = $staticEmail.val().trim();
    let current_phone = $staticPhone.val().trim();
    let current_org = $userorg.val().trim();
    //all bvs requested dates
    let num_requested = $bvs_requested.length;
    let current_requested = [];
    $bvs_requested.each(function (i, obj) {
        current_requested.push($(this).val().trim());
    });
    //all bvs signed dates
    let num_signed = $bvs_signed.length;
    let current_signed = [];
    $bvs_signed.each(function (i, obj) {
        current_signed.push($(this).val().trim());
    });

    //flags
    let org_populated_flag = false, //to prevent multiple ajax cals to populate the org dropdown
        popover_flag = 0,
        sameorgs = true,
        archived_flag = false;  //upon an organization change, the user must archive projects first. True indicates this has been done.   

    //misc declarations
    let new_email, new_phone, new_org;
    let info_dict = {};

    $edit_icon_1.on("click", function () {     //if we click to edit the document
        changeIcons(false, 1);
        if(!org_populated_flag){
            $.ajax({
                type: "GET",
                url: "/dashboard/project/ajax/filterchange/",     //since the filter_change view already gives us all organizations, we can use that
                data: {"option": "org"},
                dataType: "json",
                success: function(data) {
                    org_html = "<option selected hidden>" + current_org + "</option> <option></option>"; 
                    for(let i = 0; i < data["returnlist"].length; i++) {
                        org_html = org_html + "<option>" + data["returnlist"][i] + "</option>";
                    }
                    $user_org_dd.html(org_html);
                }
            });
        }
    });

    $edit_icon_2.on("click", function () {
        changeIcons(false, 2);
    });
    
    $save_icon_1.on("click", function () {     //make ajax call to decide whether or not to update tables
        new_email = $staticEmail.val().trim();
        new_phone = $staticPhone.val().trim();
        new_org = $user_org_dd.find(":selected").text();
        info_dict = {};

        if(new_email === current_email && new_phone === current_phone && new_org === current_org){
            changeIcons(true, 1);
        }
        else{
            info_dict["user_id"] = user_id;

            if(new_email != current_email){
                info_dict["new_email"] = new_email;
            }
            if(new_phone != current_phone){
                info_dict["new_phone"] = new_phone;
            }
            if( (new_org != current_org) && !archived_flag && $staticEmail[0].checkValidity() && $staticPhone[0].checkValidity()){
                info_dict["new_org"] = new_org;
                
                $.ajax({
                    type: "GET",
                    url: "/dashboard/user/update_ajax/archivemodal/",
                    data: {
                        "user_id": user_id
                    },
                    dataType: "json",
                    success: function(data) {
                        $modalbody.html(data["html_form"]);
                    }
                });

                //toggle only if the user has affiliated projects
                if($("#open-table").find(".clickable-row").length || $("#complete-table").find(".clickable-row").length){
                    $("#userviewmodalpane").modal("toggle");
                    return;
                }
            }
            else if( (new_org != current_org) && archived_flag){
                info_dict["new_org"] = new_org;
            }

            submit_info_box_1(info_dict);
        }
    });

    $save_icon_2.on("click", function () {
        let request_flag = false;
        let signed_flag = false;

        $bvs_requested.each( function (i, obj) {
            if($(this).val().trim() != current_requested[i]){
                request_flag = true;
            }

        });
        $bvs_signed.each( function (i, obj) {
            if($(this).val().trim() != current_signed[i]){
                signed_flag = true;
            }
        });

        //neither bvs agreement requested or bvs agreement signed changed
        if(!request_flag && !signed_flag){
            changeIcons(true, 2);
        }
        else if(request_flag && !signed_flag){
            $.ajax({
                type: "POST",
                url: "/dashboard/user/update_ajax/",
                data: {
                    "list_of_req": null
                },
                dataType: "json",
                success: function(data) {
                    changeIcons(true, 2);
                }
            });
        }
    });

    //disables submit button from the modal because it would do a regular form submission. Instead we want to block this and send and ajax request
    //to the view to process the changes. Once the request is returned, we close out the form and finish the second ajax call to change the email/phone/org
    $("#userviewsubmit").on("click", function (e) {
        e.preventDefault();

        let project_archive_pair = {};
        $(".user-project-row").each( function() {
            //creates a dictionary with the key being the CATid (what happens if we don't have a catid?)
            //assigns true if the checkbox is checked, or else it assigns false
            project_archive_pair[$(this).children(":first").text().trim()] = $(this).children(":nth-child(3)").children(":first")[0].checked;
        });

        $.ajax({
            type: "POST",
            url: "/dashboard/user/update_ajax/archivemodal/",
            data: {
                "user_id": user_id,
                "project_archive_pair": JSON.stringify(project_archive_pair),   //jquery breaks up your dictionary of dictionaries into individual keys
                                                                                //thus you have to stringify it
            },
            dataType: "json",
            success: function(data) {
                if(data['success']){
                    archived_flag = true;
                    submit_info_box_1(info_dict);
                    $("#userviewmodalpane").modal("toggle");
                }
                else{
                    console.log("there was an error passed");
                }
            }
        });
    });

    //check validity of inputs
    $input.focusout(function () {
        if(!$(this)[0].checkValidity()){
            $(this).parent().popover("show");
            popover_flag = 1;
        }
    });

    //handles the popover and makes it disappear on next click out of focus
    $(document).on("click", function () {
        if(popover_flag === 2){
            $datatogglepop.popover("hide");
            popover_flag = 0;
        }
        if(popover_flag === 1){
            popover_flag = 2;
        }
    });

    function submit_info_box_1(dict) {
        if($staticEmail[0].checkValidity() && $staticPhone[0].checkValidity()){
            $.ajax({
                type: "POST",
                url: "/dashboard/user/update_ajax/",
                data: dict,
                dataType: "json",
                success: function(data) {
                    if(data["email_success"]){
                        current_email = new_email;
                    }
                    else{   // if there was an error inputting into the database, you have to change the dom element
                        $staticEmail.parent().popover("show");
                        popover_flag = 1;
                    }

                    if(data["phone_success"]){
                        current_phone = new_phone;
                    }
                    else{
                        $staticPhone.parent().popover("show");
                        popover_flag = 1;
                    }

                    if(data["org_success"]){
                        $userorg.val(new_org);
                        current_org = new_org;
                        $user_org_dd.find(">:first-child").html(current_org);
                    }

                    if(data["email_success"] && data["phone_success"] && data["org_success"]){
                        changeIcons(true, 1);

                    }
                    // highlight the box that has an error saving into the database
                    if(!data["email_success"]) {
                        $staticEmail.addClass("form-error");
                    }
                    else {
                        $staticEmail.removeClass("form-error");
                    }

                    if(!data["phone_success"]) {
                        $staticPhone.addClass("form-error");
                    }
                    else {
                        $staticPhone.removeClass("form-error");
                    }

                    if(!data["org_success"]) {
                        $user_org_dd.addClass("form-error");
                    }
                    else {
                        $user_org_dd.removeClass("form-error");
                    }
                }
            });
        }
    }

    //handles the checkbox button in the projects section (Associated with project)
    $userassoc.on("click", function (e){
        e.stopPropagation();
        let assoc_proj_id = $(this).data("id");
        $.ajax({
            type: "POST",
            url: "/dashboard/user/update_ajax/",
            data: {
                'assoc_proj_id' : assoc_proj_id,
                'user_id' : user_id,
            },
            dataType: "json",
            success: function(data){

            }
        });
    });

    function changeIcons(save,box) {
        if(save && (box === 1)){
            $save_icon_1.toggleClass("hidden");
            $edit_icon_1.removeClass("fa-close").addClass("fa-pencil");
            $("#staticEmail, #staticPhone").removeClass("form-control").addClass("form-control-plaintext").prop("readonly", true);
            $userorg.toggleClass("hidden").toggleClass("disappear");
            $user_org_dd.addClass("disappear").addClass("hidden");
        }
        else if(!save && (box === 1)){
            if($save_icon_1.hasClass("hidden")){
                $save_icon_1.toggleClass("hidden");
                $edit_icon_1.removeClass("fa-pencil").addClass("fa-close");
                $("#staticEmail, #staticPhone").removeClass("form-control-plaintext").addClass("form-control").removeAttr("readonly");
                $userorg.toggleClass("hidden").toggleClass("disappear");
                $user_org_dd.removeClass("disappear").removeClass("hidden");
            }
            else{
                $save_icon_1.toggleClass("hidden");
                $edit_icon_1.removeClass("fa-close").addClass("fa-pencil");
                $("#staticEmail, #staticPhone").removeClass("form-control").addClass("form-control-plaintext").prop("readonly", true);
                $userorg.toggleClass("hidden").toggleClass("disappear");
                $user_org_dd.addClass("disappear").addClass("hidden");
                $staticEmail.val(current_email);    //change back to original values if we cancel;
                $staticPhone.val(current_phone);
            }
            //remove all popovers on close edit
            $('[data-toggle="popover"]').popover("hide");
        }
        else if(save && (box === 2)){
            $save_icon_2.toggleClass("hidden");
            $edit_icon_2.removeClass("fa-close").addClass("fa-pencil");
            $bvs_requested.removeClass("form-control").addClass("form-control-plaintext").prop("readonly", true);
            $bvs_signed.removeClass("form-control").addClass("form-control-plaintext").prop("readonly", true);
        }
        else if(!save && (box === 2)){
            if($save_icon_2.hasClass("hidden")){
                $save_icon_2.toggleClass("hidden");
                $edit_icon_2.removeClass("fa-pencil").addClass("fa-close");
                $bvs_requested.removeClass("form-control-plaintext").addClass("form-control").removeAttr("readonly");
                $bvs_signed.removeClass("form-control-plaintext").addClass("form-control").removeAttr("readonly");
            }
            else{
                $save_icon_2.toggleClass("hidden");
                $edit_icon_2.removeClass("fa-close").addClass("fa-pencil");
                $bvs_requested.removeClass("form-control").addClass("form-control-plaintext").prop("readonly", true);
                $bvs_signed.removeClass("form-control").addClass("form-control-plaintext").prop("readonly", true);
                $bvs_requested.each(function(i,e) {      //change back to original values if we cancel;
                    $(this).val(current_requested[i]);
                });
                $bvs_signed.each(function(i,e) {
                    $(this).val(current_signed[i]);
                });
            }
        }
    }
});
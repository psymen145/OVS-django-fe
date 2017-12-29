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

function removeErrors(divs) {
    $(divs).each(function(){
        $(this).children(":first").addClass("form-error-shadow");
        $(this).children(".errorlist").remove();
    });
}

function showMessage(divs) {
    if($(divs).length === 0){
        $("#message").css("visibility","visible");
        setTimeout(function(){
            $("#message").css("visibility","hidden");
        }, 5000);
    }
}

$(document).ready(function () {
    let $newProj = $("#newProj"),
        $newUser = $("#newUser"),
        $newOrg = $("#newOrg"),
        $modalbody = $(".modal-body"),
        $modalfooter = $(".modal-footer"),
        $formfield = $(".form-field"),
        $connectedSort = $(".connectedSort")
        $listgroup = $(".list-group"),
        $droppable = $(".droppable"),
        $ui_state_default = $(".ui-state-default"),
        $datepicker = $(".datepicker");

    //variable to hold information about the list element(the project) right when we begin to drag
    let original_phase, drag_project_id, new_phase;

    $datepicker.datepicker();

    /*** Draggable elements ***/
    $listgroup.sortable({
        connectWith: ".connectedSortable",
        start: function(event, ui) {
            drag_project_id = ui.item.data("id");
            original_phase = this.id;
        }
    }).disableSelection();

    /*** Event for droppable elements ***/
    $droppable.droppable({
        drop: function(event, ui) {
            if(original_phase != this.id){
                $.ajax({
                    type: "POST",
                    url: "/dashboard/update_phase/",
                    data: {
                        "proj_id": drag_project_id,
                        "new_phase": this.id,
                    },
                    dataType: "json",
                    success: function(data) {
                        console.log(data["success"])
                    }
                });
            }
        }
    });

    $newProj.click(function () {
        $.ajax({
            url: "/dashboard/project/new/",
            data: {},
            dataType: "json",
            success: function (data) {
                $modalbody.html(data.html_page);
                $("#id_startdate_month, #id_startdate_day, #id_startdate_year, #id_est_enddate_month, #id_est_enddate_day, #id_est_enddate_year").addClass("modaldate");
                $(".modal-footer button:last-child").attr("id","proj-submit")
            }
        });
    });

    $newUser.click(function () {
        $.ajax({
            url: "/dashboard/user/new/",
            data: {},
            dataType: "json",
            success: function (data) {
                $modalbody.html(data.html_page);
                $(".modal-footer button:last-child").attr("id","user-submit")
            }
        });
    });

    $newOrg.click(function () {
        $.ajax({
            url: "/dashboard/org/new/",
            data: {},
            dataType: "json",
            success: function (data) {
                $modalbody.html(data.html_page);
                $(".modal-footer button:last-child").attr("id","org-submit")
            }
        });
    });

    $modalfooter.on("click", "#proj-submit", function (e) {
        e.preventDefault();
        let form = $(this).closest("form");

        $.ajax({
            type: "POST",
            url: "/dashboard/project/new/",
            data: form.serialize(),
            dataType: "json",
            success: function (data) {
                $modalbody.html(data.html_page);
                $("#id_startdate_month, #id_startdate_day, #id_startdate_year, #id_est_enddate_month, #id_est_enddate_day, #id_est_enddate_year").addClass("modaldate");

                let divs = $formfield.has("ul");
                showMessage(divs);
                removeErrors(divs);
            }
        });
    });

    $modalfooter.on("click", "#user-submit", function (e) {
        e.preventDefault();
        let form = $(this).closest("form");

        $.ajax({
            type: "POST",
            url: "/dashboard/user/new/",
            data: form.serialize(),
            dataType: "json",
            success: function (data) {
                $modalbody.html(data.html_page);

                let divs = $formfield.has("ul");
                showMessage(divs);
                removeErrors(divs);
            }
        });
    });

    $modalfooter.on("click", "#org-submit", function (e) {
        e.preventDefault();
        let form = $(this).closest("form");

        $.ajax({
            type: "POST",
            url: "/dashboard/org/new/",
            data: form.serialize(),
            dataType: "json",
            success: function (data) {
                $modalbody.html(data.html_page);

                let divs = $formfield.has("ul");
                showMessage(divs);
                removeErrors(divs);
            }
        });
    });

});
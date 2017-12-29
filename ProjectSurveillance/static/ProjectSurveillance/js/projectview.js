function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

$(document).ready(function () {
    let $proj_sort_icon = $("#proj-sort-icon"),
        $filterdiv = $("#filterdiv"),
        $filterbutton = $("#filter-button"),
        $filterbox = $("#filterbox"),
        $pagination = $("#pagination-bar"),
        $dropdowntogglesplit = $(".dropdown-toggle-split"),
        $dropdowntoggle = $(".dropdown-toggle"),
        $tablebody = $("#table-body");
    
    $proj_sort_icon.on('click', function(){
        let sorttype;

        if ($(this).hasClass("fa-caret-down")) {
            //from Z - A (dsc)
            $(this).removeClass("fa-caret-down").addClass("fa-caret-up");
            sorttype = "dsc";
        }
        else {
            //from A - Z (asc)
            $(this).removeClass("fa-caret-up").addClass("fa-caret-down");
            sorttype = "asc";
        }
        
        passtoview(1);
    });

    $filterdiv.on('click', '.proj-filter-item', function() {
        opt = $(this).data('id');
        if (opt === "org") {
            $filterbutton.html("Organization");
        }
        else if (opt === "type") {
            $filterbutton.html("Project Type");
        }
        else if (opt === "open") {
            $filterbutton.html("Open/Close");
        }
        else {
            $filterbutton.html("");
        }
        $filterbutton.attr('data-id', opt)
        $filterbox.attr('name', opt);
        $.ajax({
            url: "/dashboard/project/ajax/filterchange/",
            data: {
                'option': $(this).data('id')
            },
            dataType: 'json',
            success: function (data) {
                var html_string = "<option selected='selected'></option>"
                for (i = 0; i < data.returnlist.length; i++) {
                    var tempstring = "<option>" + data.returnlist[i] + "</option>";
                    html_string += tempstring;
                }
                $filterbox.html(html_string);
            }
        });
    });
    
    $pagination.on("click", ".page-link", function (e) {
        e.preventDefault();

        desired_page = $(this).attr("data-id");
        
        passtoview(desired_page);
    });

    $dropdowntogglesplit.on("click", function(e) {
        $dropdowntoggle.dropdown();
    });

    function passtoview(desired_page) {
        //checks what sort option we want
        if ($proj_sort_icon.hasClass("fa-caret-down")) {
            sorttype = "asc";
        }
        else {
            sorttype = "dsc";
        }

        if(desired_page != 0 && desired_page != -1){

            let query_string, query_type = null;

            //check if last searched was from the filterbox or the searchbox
            if(getParameterByName("searchbox")){
                query_type = "search";
                query_string = getParameterByName("searchbox");
            }
            else if(getParameterByName("org")){
                query_type = "org"
                query_string = getParameterByName("org");
            }
            else if(getParameterByName("type")){
                query_type = "type"
                query_string = getParameterByName("type");
            }
            else if(getParameterByName("open")){
                query_type = "open"
                query_string = getParameterByName("open");
            }

            $.ajax({
                url: "/dashboard/project/ajax/",
                data: {
                    'query': query_string,
                    'query_type': query_type,
                    'desired_page': desired_page,
                    'sorttype': sorttype
                },
                dataType: 'json',
                success: function(data){
                    $pagination.html(data.html_page);
                    $tablebody.html(data.html_table);
                    $(".clickable-row").click(function () {
                        location.href = $(this).data('href');
                    });
                }
            });
        }
    }
})

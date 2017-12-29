function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
            results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return "";
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

$(document).ready(function () {
    //cache
    let $user_sort_icon = $(".user-sort-icon"),
        $pagination = $("#pagination-bar"),
        $tablebody = $("#table-body");
                    
    //store the last clicked icon
    let last_clicked_icon;

    $user_sort_icon.on("click", function(){
        last_clicked_icon = $(this).attr("id");
        let sorttype;

        //change the other icons to the default caret-bottom
        if ($(this).hasClass("fa-caret-down")) {
            $user_sort_icon.removeClass("fa-caret-up").removeClass("fa-caret-down").addClass("fa-caret-down");
            //from Z - A (dsc)
            $(this).removeClass("fa-caret-down").addClass("fa-caret-up");
            sorttype = "dsc";
        }
        else {
            //from A - Z (asc)
            $(this).removeClass("fa-caret-up").addClass("fa-caret-down");
            sorttype = "asc";
        }
        
        passtoview(1, sorttype, last_clicked_icon);
    });

    $pagination.on("click", ".page-link", function (e) {
        e.preventDefault();

        desired_page = $(this).attr("data-id");

        let sorttype = "asc";
        $user_sort_icon.each(function(){
            if($(this).hasClass("fa-caret-up")){
                sorttype = "dsc";
            }
        }); 

        passtoview(desired_page, sorttype, last_clicked_icon);

    });

    function passtoview(desired_page, sorttype, cattype) {
        //checks what sort option we want ( double bars checks if it is an optional parameter )
        sorttype = sorttype || "asc";           //ascending is default
        cattype = cattype || "First Name";

        if(desired_page != 0 && desired_page != -1){
            if (getParameterByName("searchbox")) {
                search_query = getParameterByName("searchbox");
            }
            else{
                search_query = "";
            }

            $.ajax({
                url: "/dashboard/user/ajax/",
                data: {
                    "search_query": search_query,
                    "desired_page": desired_page,
                    "sorttype": sorttype,
                    "cattype": cattype
                },
                dataType: "json",
                success: function(data){
                    $pagination.html(data.html_page);
                    $tablebody.html(data.html_table);
                    $(".clickable-row").click(function () {
                        location.href = $(this).data("href");
                    });
                }
            });
        }
    }
});
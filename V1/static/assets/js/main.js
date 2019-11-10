
$( document ).ready(function() {

    $(".fancybox").fancybox({
        openEffect: "none",
        closeEffect: "none"
    });


     $('.login_action').popover({
            html: true,
            trigger: 'manual',
            sanitize: false,
            container: 'body',
            content: function() {
            return $.ajax({url: '/login_page',

                     dataType: 'html',
                     async: false}).responseText;

            }
        }).click(function(e) {
            $(this).popover('toggle');

      });

     $('.terms').popover({
            html: true,
            trigger: 'manual',
            sanitize: false,
            // container: 'body',
            content: function() {
            return $.ajax({url: '/terms',

                     dataType: 'html',
                     async: false}).responseText;

            }
        }).click(function(e) {
            $(this).popover('toggle');

      });

    /*
    var str = "";
    $( "select option:selected" ).each(function() {
      str += $( this ).text() + " ";
    });
    $( "div" ).text( str );
     */
    $("#alert_iconList").change(function(){

        // alert_icon change class
        var iconClass = $('#alert_icon').attr('class');
        console.log("Current Class:", iconClass);

        $("#alert_icon").removeClass(iconClass);

        var value = $("#alert_iconList option:selected").val();
        $("#alert_icon").addClass(value).addClass("fa");
        $("#new_alert_icon").val(value);




    });

});





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




});




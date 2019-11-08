
$( document ).ready(function() {
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

});



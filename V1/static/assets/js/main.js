
$( document ).ready(function() {
     $('.loginAction').popover({
            html: true,
            trigger: 'manual',
            sanitize: false,
            container: 'body',
            content: function() {
            return $.ajax({url: '/login',

                     dataType: 'html',
                     async: false}).responseText;

            }
        }).click(function(e) {
            $(this).popover('toggle');

      });

});



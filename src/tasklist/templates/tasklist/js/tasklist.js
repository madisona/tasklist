$(document).ready(function() {
    $(".add_task").click(function() {
        $(".task_form").slideDown("fast");
    });

    $(".task_item").click(function(){
        var el = $(this);
        $.ajax({
            url: "{% url tasklist:toggle_status %}",
            type: 'POST',
            data: {'task': el.attr("id")},
            success: function(){
                el.toggleClass("completed");
            }
        });
    });
});
$(document).ready(function () {
    
    var delay = (function () {
        var timer = 0;
        return function (callback, ms) {
            clearTimeout(timer);
            timer = setTimeout(callback, ms);
        };
    })();

    var curi = -1;
    $(".search_res").hide();

    $("#username_search_box").keyup(function (e) {

        var code = e.keyCode || e.which;

        if (code === 38) { //Up arrow
            if (curi > 0)
            {
                $("#patag" + curi).removeClass("hovered");
                curi--;
                $("#patag" + curi).addClass("hovered");
                $("#username_search_box").val($("#patagval" + curi).text())

            }
            return;
        }

        if (code === 40) { //Down arrow

            if (curi < $(".search_res li").length - 1)
            {
                if(curi !== -1) $("#patag" + curi).removeClass("hovered");
                curi++;
                $("#patag" + curi).addClass("hovered");
                $("#username_search_box").val($("#patagval" + curi).text())

            }
            return;
        }
        
        if (code === 13) { //Enter arrow

            var q = $("#username_search_box").val();
            window.location.replace("/users/" + q);
            return;
        }

        delay(function () {
            
            var q = $("#username_search_box").val();
            var regex = new RegExp("[a-zA-Z0-9]+");
            if (q.length < 3 || !regex.test(q)) {
                $(".search_res").hide();
                return;
            }
            $(".search_res").show();
            $.getJSON("/search/" + q, function (result) {
                $(".search_res").empty();
                curi = -1;
                $.each(result, function (i, field) {
                    $(".search_res").append('<li><a id="patag' + i + '" href="/users/' + field + '"><span class = "glyphicon glyphicon-user"></span> <span id="patagval' + i + '">' + field + '</span></a></li>');
                });
            });
            
        }, 1000);
    });

    $(".search_res li").hover(function () {
        $(this).addClass("hovered");
    }, function () {
        $(this).removeClass("hovered");
    });
});
$(document).click(function (e) {
    if (e.target.id != 'search') {
        $(".search_res").hide();
        $("#username_search_box").val("");
        curi = -1;
    }
});

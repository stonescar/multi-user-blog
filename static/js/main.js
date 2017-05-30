$(document).ready(function() {
    //Show overlay on frontpage if long posts
    $(".front").each(function() {
        if ($(this).height() == 400) {
            $(this).append("<div class='post-overlay'>This article is longer</div>");
        }
    })
    //Add link to overlay
    $(".post-overlay").click(function() {
        window.location = $(this).parent(".post").siblings(".read-more").attr("href");
    })

    //Disable comments if not logged in
    if ("/post/" == window.location.pathname.substring(0, 6) && document.cookie.indexOf("user_id") < 0) {
        $(".comment-ta").attr("Placeholder", "Log in/register to comment").attr("disabled", "disabled");
        $(".submit-comment").attr("disabled", "disabled");
    }

    //Confirm when deleting post
    $(".del-post-btn1").click(function() {
        $(this).hide();
        $(".del-post-confirm").show();
    })

    //Delete post
    $(".del-post-btn2").click(function() {
        path = window.location.pathname.split("/");
        comm_id = path[path.length-1];
        window.location = "/post/del/"+comm_id;
    })

    //Confirm when deleting comment
    $(".del-comm-btn1").click(function() {
        $(this).hide();
        $(".del-comm-confirm").show();
    })

    //Delete comment
    $(".del-comm-btn2").click(function() {
        path = window.location.pathname.split("/");
        comm_id = path[path.length-1];
        window.location = "/comment/del/"+comm_id;
    })

    //Set appropriate content in header when logged in
    if (document.cookie.indexOf("user_id") >= 0) {
        user = "unknown";
        c = document.cookie.split("; ");
        for (var i = 0; i < c.length; i++) {
            n = c[i].split("=");
            if (n[0] == "user") {
                user = n[1];
            }
        }
        $(".head-cont-left").append(" - <a href='/newpost'>New post</a>");
        $(".head-cont-right").html("Logged in as <b><a href='/welcome'>"+user+"</a></b> - <a href='/logout'>Logout</a>");
    }

    //Autoexpand textarea when writing or editing post
    if ("/post/edit/" == window.location.pathname.substring(0, 11) ||
        "/newpost" == window.location.pathname.substring(0, 8)) {
        var resize = function() {
            var scroll = $(window).scrollTop();
            $(".post-ta").height(1).height(Math.max($(".post-ta")[0].scrollHeight-4, 300));
            $(window).scrollTop(scroll);
        };
        resize();
        $(".post-ta").keyup(function() {
            resize();
        });
    }

    //Highligh comment when linked directly to comment
    if (window.location.href.indexOf("#") > 0) {
        path = window.location.href.split("#");
        comment_id = "#"+path[1];
        $(comment_id).focus().addClass('active');
        $(document).click(function() {
            $(comment_id).removeClass('active');
        })
    }
})

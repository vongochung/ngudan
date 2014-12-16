$(function() {
    $(window).on("scroll", get_more_post);
});

$.ajaxSetup({
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                 if (cookie.substring(0, name.length + 1) == (name + '=')) {
                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                     break;
                 }
             }
         }
         return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     }
});


function loading(btn)
{
    var loading = btn.find('.loading').length
    if (loading) {
        btn.find('.loading').remove()
    } else {
        btn
            .html('<i class="fa fa-spinner fa-spin loading"></i>' + btn.html()).addClass("text-center")
    }
}

function toogleMenu(){
   $('#category').toggleClass('hides');
   if ($('#category').hasClass('hides')) {
        $('#category').animate({left:0});
        $('#btn-pullout').animate({left:242});
   } else{
        $('#category').animate({left: -242});
        $('#btn-pullout').animate({left:0});
   }
}


function get_more_post(){
    var scrollAmount = $(window).scrollTop(),
    documentHeight = $(document).height(),
    content = $(window).height();
    if(scrollAmount == (documentHeight - content)) {
        $(".viewmore-post").click();
    }
}

$(document).on("click",".viewmore-post",function(e) {
    var $ele = $(this);
    loading($ele)
    var page = $(this).data("page"),
    category = $(this).data("category");
    var data = {
        "page": page
    }
    if ( typeof category !== "undefined"){
        data["category"] = category;
    }
    $.ajax({
        url: '/get-posts/',
        type: 'POST',
        data: data,
    })
    .done(function(data) {        
        $("#post-wrap").append(data);
    })
    .fail(function() {
        console.log("error");
    })
    .always(function() {
        $ele.parent().remove();
        try{
            FB.XFBML.parse(); 
        }catch(ex){
            console.log(ex);
        }
    });
        
});

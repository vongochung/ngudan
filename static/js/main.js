function displayPlayer(){$(".player").each(function(){var e=$(this),t=e.next(),n=e.position(),r=e.width(),i=e.innerHeight(),s=n.top,o=n.left;t.css({left:o+r/2-t.width()/2,top:s+i/2-t.height()/2})})}function loading(e){var t=e.find(".loading").length;if(t){e.find(".loading").remove()}else{e.html('<i class="fa fa-spinner fa-spin loading"></i>'+e.html()).addClass("text-center")}}function toogleMenu(){$("#category").toggleClass("hides");if($("#category").hasClass("hides")){$("#btn-pullout").animate({left:242});$("#category").offset({top:$("#btn-pullout").offset().top});$("#category").animate({left:0})}else{$("#category").animate({left:-242});$("#btn-pullout").animate({left:0})}}function get_more_post(){var e=$(window).scrollTop(),t=$(document).height(),n=$(window).height();if(e==t-n){$(".viewmore-post").click()}}$(function(){$(window).on("scroll",get_more_post);$(window).on("resize",displayPlayer);displayPlayer()});$.ajaxSetup({beforeSend:function(e,t){function n(e){var t=null;if(document.cookie&&document.cookie!=""){var n=document.cookie.split(";");for(var r=0;r<n.length;r++){var i=jQuery.trim(n[r]);if(i.substring(0,e.length+1)==e+"="){t=decodeURIComponent(i.substring(e.length+1));break}}}return t}if(!(/^http:.*/.test(t.url)||/^https:.*/.test(t.url))){e.setRequestHeader("X-CSRFToken",n("csrftoken"))}}});$(document).on("click",".viewmore-post",function(e){var t=$(this);loading(t);var n=$(this).data("page"),r=$(this).data("category");var i={page:n};if(typeof r!=="undefined"){i["category"]=r}$.ajax({url:"/get-posts/",type:"POST",data:i}).done(function(e){$("#post-wrap").append(e.html)}).fail(function(){console.log("error")}).always(function(){t.parent().remove();displayPlayer();try{FB.XFBML.parse()}catch(e){console.log(e)}})});$(document).on("click",".viewmore-post-detail",function(e){var t=$(this);loading(t);var n=$(this).data("page"),r=$(this).data("type"),i=$(this).data("category");var s={page:n,type:r};if(typeof i!=="undefined"){s["category"]=i}$.ajax({url:"/get-posts-detail-more/",type:"POST",data:s}).done(function(e){$("#"+r).append(e.html);$('[data-toggle="popover"]').popover({trigger:"hover",placement:"top"})}).fail(function(){console.log("error")}).always(function(){t.parent().remove();displayPlayer()})});$(document).on("click",".active-language",function(e){$("#set-lang").val($(this).data("lang"));$("#form-language").submit()})
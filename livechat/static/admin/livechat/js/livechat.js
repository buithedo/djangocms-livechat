var chatSocket = false;

function get_csrfmiddlewaretoken(){
	return $("input[name='csrfmiddlewaretoken']").val();
}

$(document).ready(function(){

	function reset_chat_area(){
		$(".chat_area ul").empty();
		$(".room_title").text("");
       	$(".room_type").text("");
	}

    function run_chat_socket() {

    	var roomName = $("#roomName").text();

        var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
        chatSocket = new WebSocket(
            ws_scheme + '://' + window.location.host +
            '/ws/livechat/' + roomName + '/');

        chatSocket.onmessage = function(e) {
            var data = JSON.parse(e.data);
            var message = data['message'];
            var now_time = data['now_time'];
            var receive_user = data['user'];
            var user = $("#user_chat").text();
            if (receive_user === user) {

            	dt = {
                   'id_room': roomName,
                   'message': message,
                   'csrfmiddlewaretoken': get_csrfmiddlewaretoken(),
                }

                $.ajax({
                    type: 'POST',
                    url: '/livechat/api/backend_message',
                    dataType: 'json',
                    data: dt,
                    success: function(data){
                        if (data.error == true) {
                          //console.log(data.message);
                        } 
                    },
                });

                $('<li class="right clearfix"><span class="chat-img pull-right"><img src="'+default_avatar_url+'" alt="User Avatar" class="img-circle"/></span><div class="chat-body clearfix"><div class="header"><small class=" text-muted"><span class="glyphicon glyphicon-time"></span>'+now_time+'</small><strong class="pull-right primary-font">'+user+'</strong></div><p>'+message+'</p></div></li>').appendTo($('.chat_area ul'));
            }
            else{
                $('<li class="left clearfix"><span class="chat-img pull-left"><img src="'+$(".room_title").attr('url_avatar')+'" alt="User Avatar" class="img-circle"/></span><div class="chat-body clearfix"><div class="header"><strong class="primary-font">'+ receive_user+ '</strong><small class="pull-right text-muted"><span class="glyphicon glyphicon-time"></span>'+now_time+'</small></div><p>'+message+'</p></div></li>').appendTo($('.chat_area ul'));
            }

            $('.chat_area').scrollTop($('.chat_area')[0].scrollHeight);      
        };

        chatSocket.onclose = function(e) {
            //console.error('Chat socket closed unexpectedly');
        };

        document.querySelector('#chat-message-input').focus();
        document.querySelector('#chat-message-input').onkeyup = function(e) {
            if (e.keyCode === 13) {  // enter, return
                document.querySelector('#chat-message-submit').click();
            }
        };

        document.querySelector('#chat-message-submit').onclick = function(e) {
            var messageInputDom = document.querySelector('#chat-message-input');
            var message = messageInputDom.value;
            chatSocket.send(JSON.stringify({
                'message': message
            }));
            messageInputDom.value = '';
        };
    }


	function get_room_conversation(room_id) {
		
		reset_chat_area();
	
		dt = {
			'id_room': room_id,
			'csrfmiddlewaretoken': get_csrfmiddlewaretoken()
		}

		$.ajax({
            type: 'POST',
            url: '/livechat/api/get_room_conversation',
            dataType: 'json',
            data: dt,
            success: function(data){

                if (data.error == true) {
                 	alert(data.message);
                } else {

					$(".room_title").text(data.full_name);
                	$(".room_type").text(data.channel_type);
                	$("#roomName").text(data.key_hash);

                	if (chatSocket != false) {
                		chatSocket.close();
                	}

                	run_chat_socket();

                	if (data.chat != null && data.chat.length > 0) {

                		data.chat.forEach(function(chat_item){

							var url_avatar = default_avatar_url;
	                 		if (data.hash_email != "") {
	                 			url_avatar = "https://www.gravatar.com/avatar/" + data.hash_email;
	                 		}

	                 		$(".room_title").attr('url_avatar',url_avatar);

			                if (chat_item.chatter != data.full_name) {
				                $('<li class="right clearfix"><span class="chat-img pull-right"><img src="'+default_avatar_url+'" alt="User Avatar" class="img-circle"/></span><div class="chat-body clearfix"><div class="header"><small class=" text-muted"><span class="glyphicon glyphicon-time"></span>'+chat_item.created+'</small><strong class="pull-right primary-font">'+chat_item.chatter+'</strong></div><p>'+chat_item.message+'</p></div></li>').appendTo($('.chat_area ul'))
				            }
				            else{
				                $('<li class="left clearfix"><span class="chat-img pull-left"><img src="'+url_avatar+'" alt="User Avatar" class="img-circle"/></span><div class="chat-body clearfix"><div class="header"><strong class="primary-font">'+ chat_item.chatter+ '</strong><small class="pull-right text-muted"><span class="glyphicon glyphicon-time"></span>'+chat_item.created+'</small></div><p>'+chat_item.message+'</p></div></li>').appendTo($('.chat_area ul'))
				            }

	                		$('.chat_area').scrollTop($('.chat_area')[0].scrollHeight);   

				        });
	            	
	                }


                }
            },
        });

	}

	function in_list_room_showed(room_id){

		var check = $(".member_list ul").find("li[id_room="+room_id+"]")
		if (check.length > 0) {
			return true;
		} else {
			return false;
		}

	}

	function get_room_list(filter="all",search="",start=""){
		
		if (start == "") {
			start == 0;
		}

		dt = {
			'filter': filter,
			'start': start,
			'str_search': search,
			'csrfmiddlewaretoken': get_csrfmiddlewaretoken()
		}

		$.ajax({
            type: 'POST',
            url: '/livechat/api/get_all_conversation',
            dataType: 'json',
            data: dt,
            success: function(data){

                if (data.error == true) {
                 	alert(data.message);
                } else {

                	if (data.room_list != null) {

                		$(".member_list ul").empty();
                		index = start;
	                 	data.room_list.forEach(function(room){

	                 		var info = "";

	                 		if (room.phone != "") {
	                 			info = info + "" +room.phone + " ";	
	                 		}

	                 		if (room.email != "") {
	                 			if (info != "") {
	                 				info = info + "- ";
	                 			}
	                 			info = info + "" +room.email;
	                 		}
	                 		
	                 		var url_avatar = default_avatar_url;
	                 		if (room.hash_email != "") {
	                 			url_avatar = "https://www.gravatar.com/avatar/" + room.hash_email;
	                 		}

	                 		is_active = "";
	                 		if (index == 0) {
	                 			if ($("#chat-message-input").is(":focus") == false) {
		                 			is_active = "active";
		                 			get_room_conversation(room.id);
		                 		}
		                 	}

							if ($("#roomName").text() == room.key_hash) {
			                 	is_active = "active";
			                } 			                 	

			                var not_viewed = " ";
			                if (room.not_viewed > 0) {
			                	not_viewed = " ("+room.not_viewed+")";
			                }

	                 		var str = "<li class='left clearfix "+is_active+"' id_room='"+room.id+"'  > \
							               <span class='chat-img pull-left'> \
							               <img src='"+url_avatar+"' alt='"+room.full_name+" ("+room.channel_type+")' class='img-circle'> \
							               </span> \
							               <div class='chat-body clearfix'> \
							                  <div class='header_sec'> \
							                     <strong class='primary-font'>"+room.full_name+not_viewed+"</strong> \
							                     <strong class='pull-right'> \
							                     	"+room.created+" \
							                     </strong> \
							                  </div> \
							                  <div class='contact_sec'> \
							                     <span class='primary-font'>"+info+"</span> <span class='badge pull-right'></span> \
							                  </div> \
							               </div> \
						            </li>";
						    $(".member_list ul").append($.parseHTML(str));

						    index = index + 1;
						});
	                }
                }
            },
        });

	}

	get_room_list();

	$("#dropdownMenu2").click(function(){
		$(".all_conversation .dropdown-menu").show();
	});

	$(".all_conversation .dropdown-menu li a").click(function(){
		filter = $(this).attr('filter');
		$("#dropdownMenu2").attr('filter',filter);
		filter_text = $(this).text();
		var show_filter = "<i class='fa fa-weixin' aria-hidden='true'></i>"+filter_text+"<span class='caret pull-right'></span>";
		$("#dropdownMenu2").html($.parseHTML(show_filter));
		$(this).parent().parent().hide();
		str_search = $("#custom-search-input input.search-query").val();
		$(".member_list ul").empty();
		get_room_list(filter=filter,search=str_search);
		return false;
	});

	$("#custom-search-input input.search-query").change(function(){
		filter = $("#dropdownMenu2").attr('filter');
		str_search = $(this).val();
		$(".member_list ul").empty();
		get_room_list(filter=filter,search=str_search);
	});

	$(".glyphicon-search").click(function(){
		$(".member_list ul").empty();
		filter = $("#dropdownMenu2").attr('filter');
		str_search = $("#custom-search-input input.search-query").val();
		get_room_list(filter=filter,search=str_search);
	});

	$(".member_list ul").on("click","li",function(){
		$(this).parent().find("li").removeClass("active");
		$(this).addClass("active");
		var id_room = $(this).attr("id_room");
		get_room_conversation(id_room);
		filter = $("#dropdownMenu2").attr('filter');
		str_search = $("#custom-search-input input.search-query").val();
		get_room_list(filter=filter,search=str_search);
	});

	setInterval(function(){
		filter = $("#dropdownMenu2").attr('filter');
		str_search = $("#custom-search-input input.search-query").val();
		get_room_list(filter=filter,search=str_search);
	}, 10000);

});
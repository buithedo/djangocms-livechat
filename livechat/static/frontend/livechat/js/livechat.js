var roomName = $("#live_chat_key").text();

$(document).ready(function() {


	$('.chat_client_container .panel-heading a').click(function() {
	    if ($('.chat_client_container #collapse_livechat').hasClass("in") == true) {
			$(this).find('span').removeClass('glyphicon-chevron-down');
		    $(this).find('span').addClass('glyphicon-chevron-up');
	    } else {
			$(this).find('span').removeClass('glyphicon-chevron-up');
		    $(this).find('span').addClass('glyphicon-chevron-down');
	    }

        $('#all_messages').scrollTop($('#all_messages')[0].scrollHeight);
	    
	});

    function run_chat_socket() {

        var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
        var chatSocket = new WebSocket(
            ws_scheme + '://' + window.location.host +
            '/ws/livechat/' + roomName + '/');

        chatSocket.onmessage = function(e) {
            var data = JSON.parse(e.data);
            var message = data['message'];
            var now_time = data['now_time'];
            var receive_user = data['user'];
            var user = $("#user_chat").text();
            if (receive_user == "AnonymousUser") {

                dt = {
                   'id_room': roomName,
                   'message': message,
                   'csrfmiddlewaretoken': get_csrfmiddlewaretoken(),
                }

                $.ajax({
                    type: 'POST',
                    url: '/livechat/api/frontend_message',
                    dataType: 'json',
                    data: dt,
                    success: function(data){
                        if (data.error == true) {
                          //console.log(data.message);
                        } 
                    },
                });

                $('<li class="right clearfix"><span class="chat-img pull-right"><img src="https://placehold.it/50/FA6F57/fff&text=ME" alt="User Avatar" class="img-circle"/></span><div class="chat-body clearfix"><div class="header"><small class=" text-muted"><span class="glyphicon glyphicon-time"></span>'+now_time+'</small><strong class="pull-right primary-font">'+user+'</strong></div><p>'+message+'</p></div></li>').appendTo($('.chat'))

            }
            else{
                $('<li class="left clearfix"><span class="chat-img pull-left"><img src="https://placehold.it/50/55C1E7/fff&text=U" alt="User Avatar" class="img-circle"/></span><div class="chat-body clearfix"><div class="header"><strong class="primary-font">'+ receive_user+ '</strong><small class="pull-right text-muted"><span class="glyphicon glyphicon-time"></span>'+now_time+'</small></div><p>'+message+'</p></div></li>').appendTo($('.chat'))
            }
            $('#all_messages').scrollTop($('#all_messages')[0].scrollHeight);        
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

    if (roomName != "") {
        run_chat_socket();
    }

    $(".register_chatroom").on("submit","#chat_register_form",function(){

        $("#chat_register_form input").attr("readonly",true);
        $("#chat_register_form button").attr("disable",true);

        dt = {
            'chat_name': $("#chat_name").val(),
            'chat_email': $("#chat_email").val(),
            'chat_phone': $("#chat_phone").val(),
            'check_his': $('#chat_save_his').is(":checked"),
            'chat_type': $("#chat_type").val(),
            'csrfmiddlewaretoken': get_csrfmiddlewaretoken()
        }

        $.ajax({
            type: 'POST',
            url: '/livechat/api/register_chatroom',
            dataType: 'json',
            data: dt,
            success: function(data){
                if (data.error == true) {
                  $(".register_chatroom .error").text(data.message);
                } else {
                  $("#user_chat").text(data.user);
                  $("#live_chat_key").text(data.key_hash);
                  $(".register_chatroom").addClass("hide");
                  $("#collapse_livechat .panel-footer").removeClass("hide");
                  roomName = $("#live_chat_key").text();
                  run_chat_socket();
                }
            },
        });

        return false;
    });

    $('#all_messages').scrollTop($('#all_messages')[0].scrollHeight);

});
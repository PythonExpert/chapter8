function postEvidence(user_id, content_id, session_id, event) {

    var now = new Date();
    var month = now.getMonth() + 1;

    var dateString = now.getFullYear() + '-' + month + '-' + now.getDate() + ' ' + now.getUTCHours() + ':' + now.getMinutes();
    $.ajax({  
          type: 'GET',  
          url: 'http://moviegeek.com:8000/log/' 
          		+ content_id 
          		+ '/' + event 
          		+ '?date=' + dateString 
          		+ '&sessionid=' + session_id + "&userid=" + user_id ,  
    
          error: function(req, status, ex) { 
	          console.error("exception: " + ex);
          },  
          timeout:60000  
        });  

  };
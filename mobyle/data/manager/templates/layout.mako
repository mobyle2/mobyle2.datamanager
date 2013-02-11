# -*- coding: utf-8 -*- 
<!DOCTYPE html>  
<html>
<head>
	
  <meta charset="utf-8">
  <title>Mobyle data manager</title>
  <meta name="author" content="Mobyle team">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="shortcut icon" href="/static/favicon.ico">
  <link rel="stylesheet" href="/static/mobyle.css">
  <link rel="stylesheet" href="/static/bootstrap/css/bootstrap.min.css" media="screen">
  <link rel="stylesheet" href="/static/bootstrap/css/bootstrap-responsive.min.css">
  <script src="/static/jquery-1.9.0.min.js"></script>
  <script src="/static/fileupload/js/vendor/jquery.ui.widget.js"></script>
  <script src="/static/fileupload/js/jquery.iframe-transport.js"></script>
  <script src="/static/fileupload/js/jquery.fileupload.js"></script>

<!-- The Templates plugin is included to render the upload/download listings -->
<script src="http://blueimp.github.com/JavaScript-Templates/tmpl.min.js"></script>
<!-- The Load Image plugin is included for the preview images and image resizing functionality -->
<script src="http://blueimp.github.com/JavaScript-Load-Image/load-image.min.js"></script>
<!-- The Canvas to Blob plugin is included for image resizing functionality -->
<script src="http://blueimp.github.com/JavaScript-Canvas-to-Blob/canvas-to-blob.min.js"></script>
<!-- The File Upload file processing plugin -->
<script src="/static/fileupload/js/jquery.fileupload-fp.js"></script>
<!-- The File Upload user interface plugin -->
<script src="/static/fileupload/js/jquery.fileupload-ui.js"></script>
<!-- The main application script -->
<script src="/static/fileupload/js/main.js"></script>

</head>

<body>
  % if request.session.peek_flash():
  <div id="flash">
    <% flash = request.session.pop_flash() %>
	% for message in flash:
	${message}<br>
	% endfor
  </div>
  % endif

 <div id="page">
<ul class="nav nav-pills pull-right">
  <li class="active">
    % if user and user['last_name']:
    <a href="#">Welcome ${user['first_name']} ${user['last_name']} <i id="logout" class="icon-remove-sign"></i></a>
    % else:
    <form id="apiform" action="/login" class="form form-inline"><label for="key">API KEY </label><input name="apikey" id="apikey" value=""/><button id="login" class="btn">Login</button></form>
    % endif
  </li>
</ul>


<div class="container">
    <div class="page-header">
        <h1>Mobyle data manager</h1>
    </div>
</div>
<ul class="offset1 nav nav-tabs"><li><a href="/" ><h2>Add datasets</h2></a></li><li><a href="/my" ><h2>Manage datasets</h2></a></li></ul>

    ${next.body()}

  </div>
  <script src="/static/bootstrap/js/bootstrap.min.js"></script>

  <script>
  $(document).ready(function() {
      $("#logout").click(function() {
          window.location="/logout";
      });
  });
  </script>

</body>
</html>

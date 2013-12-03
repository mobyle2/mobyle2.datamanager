# -*- coding: utf-8 -*- 
<!DOCTYPE html>  
<html>
<head>

<%
from pyramid.url import route_url,static_url
%>
	
  <meta charset="utf-8">
  <title>Mobyle data manager</title>
  <meta name="author" content="Mobyle team">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="shortcut icon" href="/static/favicon.ico">
  <link rel="stylesheet" href="${static_url('mobyle.data.webmanager:static/mobyle.css', request)}">
  <link rel="stylesheet" href="${static_url('mobyle.data.webmanager:static/bootstrap/css/bootstrap.min.css',request)}" media="screen">
  <link rel="stylesheet" href="${static_url('mobyle.data.webmanager:static/bootstrap/css/bootstrap-responsive.min.css',request)}">
  <script src="${static_url('mobyle.data.webmanager:static/jquery-1.9.0.min.js',request)}"></script>
  <script src="${static_url('mobyle.data.webmanager:static/fileupload/js/vendor/jquery.ui.widget.js',request)}"></script>
  <script src="${static_url('mobyle.data.webmanager:static/fileupload/js/jquery.iframe-transport.js',request)}"></script>
  <script src="${static_url('mobyle.data.webmanager:static/fileupload/js/jquery.fileupload.js',request)}"></script>

<!-- The Templates plugin is included to render the upload/download listings -->
<script
src="${static_url('mobyle.data.webmanager:static/javascript-templates/tmpl.min.js',request)}"></script>
<!-- The Load Image plugin is included for the preview images and image resizing functionality -->
<script src="${static_url('mobyle.data.webmanager:static/javascript-templates/load-image.min.js',request)}"></script>
<!-- The Canvas to Blob plugin is included for image resizing functionality -->
<script src="${static_url('mobyle.data.webmanager:static/javascript-templates/canvas-to-blob.min.js',request)}"></script>
<!-- The File Upload file processing plugin -->
<script src="${static_url('mobyle.data.webmanager:static/fileupload/js/jquery.fileupload-fp.js',request)}"></script>
<!-- The File Upload user interface plugin -->
<script src="${static_url('mobyle.data.webmanager:static/fileupload/js/jquery.fileupload-ui.js',request)}"></script>
<!-- The main application script -->
<script src="${static_url('mobyle.data.webmanager:static/fileupload/js/main.js',request)}"></script>

</head>

<body>

 <div id="page">
<ul class="nav nav-pills pull-right">
  <li class="active">
    % if user and user['last_name']:
    <a href="#">Welcome ${user['first_name']} ${user['last_name']} <i id="logout" class="icon-remove-sign"></i></a>
    % else:
    <form id="apiform" action="${route_url('login',request)}" class="form form-inline"><label for="key">API KEY </label><input name="apikey" id="apikey" value=""/><button id="login" class="btn">Login</button></form>
    % endif
  </li>
</ul>


<div class="container">
    <div class="page-header">
        <h1>Mobyle data manager</h1>
    </div>
</div>
  % if request.session.peek_flash():
  <div id="flash">
    <% flash = request.session.pop_flash() %>
        % for message in flash:
        ${message|n}<br>
        % endfor
  </div>
  % endif

<ul class="offset1 nav nav-tabs"><li><a href="${route_url('main',request)}" ><h2>Add datasets</h2></a></li><li><a href="${route_url('my',request)}" ><h2>Manage datasets</h2></a></li></ul>

    ${next.body()}

  </div>
  <script src="${static_url('mobyle.data.webmanager:static/bootstrap/js/bootstrap.min.js',request)}"></script>

  <script>
  $(document).ready(function() {
      $("#logout").click(function() {
          window.location="${route_url('logout',request)}";
      });
  });
  </script>

</body>
</html>

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
  <link rel="//cdnjs.cloudflare.com/ajax/libs/x-editable/1.5.0/bootstrap-editable/js/bootstrap-editable.css" rel="stylesheet"/>
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


    ${next.body()}

  </div>
  <script src="${static_url('mobyle.data.webmanager:static/bootstrap/js/bootstrap.min.js',request)}"></script>
  <script src="${static_url('mobyle.data.webmanager:static//mobyle-datamanager.js',request)}"></script>
  <script src="//cdnjs.cloudflare.com/ajax/libs/x-editable/1.5.0/bootstrap-editable/js/bootstrap-editable.min.js"></script>
  <script>
  $(document).ready(function() {
      $("#logout").click(function() {
          window.location="${route_url('logout',request)}";
      });
  });
  </script>

</body>
</html>
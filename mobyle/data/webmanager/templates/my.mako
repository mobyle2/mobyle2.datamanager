<%inherit file="layout.mako"/>

<%
from pyramid.url import route_url,static_url
from mobyle.data.manager.objectmanager import ObjectManager
%>

<div class="container">
    <blockquote>
        <p>On this page, you manage your Mobyle datasets.<br>
    </blockquote>
    <br>
 <table class="table">
 <tr><th>Status</th><th>Project</th><th>Name</th><th>Format</th><th>Path</th><th>Size</th><th></th></tr>
% for d in data:
<%
  actions = ''
  status = ''
  if d['status'] == 0:
    status = '<span class="label">Queued</span>'
  if d['status'] == 1:
    status = '<span class="label label-info">Downloading</span>'
  if d['status'] == 3:
    status = '<span class="label label-important">Error</span>'
  if d['status'] == 2 or d['status'] == 3:
    actions = '<button class="btn btn-info download" data-uid="'+str(d['path'])+'">Download</button>'
    actions += '<button class="btn btn-info update" data-uid="'+str(d['_id'])+'">Update</button>'
    actions += '<button class="btn btn-warning delete" data-uid="'+str(d['_id'])+'">Delete</button>'
%>
<tr id="tr-${d['uid']}"><td>${status |n}</td><td>
% if 'project' in d:
  ${d['project']}
% endif
</td><td>${d['name']}</td><td>${d['format']}</td><td>${d['path']}</td><td>${d['size']}</td><td>${actions |n}</td></tr>
% endfor
</table>
</div>

<script>
$(function(){

$('.delete').click(function(e) {
        uid = $(this).attr('data-uid')
        $.ajax({
            type: 'delete',
            url: "${route_url('data',request,uid='')}/"+ uid,
            success: function() {
               $("#tr-"+uid).remove();
            }
        }); 
});

<%
objectmanager = ObjectManager()
downloadpath = objectmanager.get_storage_path()
%>

$('.download').click(function(e) {
        uid = $(this).attr('data-uid');
        window.open("${static_url(downloadpath, request)}/"+ uid);
});

$('.update').click(function(e) {
        uid = $(this).attr('data-uid');
        $(location).attr('href',"${route_url('main',request)}?id="+uid) ;
});

});

</script>

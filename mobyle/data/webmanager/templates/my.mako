<%inherit file="layout.mako"/>

<div class="container">
    <blockquote>
        <p>On this page, you manage your Mobyle datasets.<br>
    </blockquote>
    <br>
 <table class="table">
 <tr><th>Status</th><th>Project</th><th>Name</th><th>Path</th><th>Size</th><th></th></tr>
% for d in data:
<%
  status = ''
  if d['status'] == 0:
    status = '<span class="label">Queued</span>'
  if d['status'] == 1:
    status = '<span class="label label-info">Downloading</span>'
  if d['status'] == 3:
    status = '<span class="label label-important">Error</span>'

%>
<tr id="tr-${d['uid']}"><td>${status |n}</td><td>
% if 'project' in d:
  ${d['project']}
% endif
</td><td>${d['name']}</td><td>${d['path']}</td><td>${d['size']}</td><td><button class="btn btn-primary delete" data-uid="${d['uid']}">Delete</button></td></tr>
% endfor
</table>
</div>

<script>
$(function(){

$('.delete').click(function(e) {
        uid = $(this).attr('data-uid')
        $.ajax({
            type: 'delete',
            url: '/data/'+ uid,
            success: function() {
               $("#tr-"+uid).remove();
            }
        }); 
});

});

</script>

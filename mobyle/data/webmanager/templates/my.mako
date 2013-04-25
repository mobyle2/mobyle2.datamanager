<%inherit file="layout.mako"/>

<%
from pyramid.url import route_url,static_url
from mobyle.data.manager.objectmanager import ObjectManager
from mobyle.data.manager.pluginmanager import DataPluginManager

DataPluginManager.get_manager()

%>

<div class="container">
    <blockquote>
        <p>On this page, you manage your Mobyle datasets.<br>
    </blockquote>
    <br>
 <table class="table">
 <tr><th>Status</th><th>Project</th><th>Name</th><th>Type/Format</th><th>Path</th><th>Size</th><th></th></tr>
% for d in data:
<%
  actions = ''
  status = ''
  if d['status'] == 0:
    status = '<span class="label">Queued</span>'
  if d['status'] == 1:
    status = '<span class="label">Downloading</span>'
  if d['status'] == 3:
    status = '<span class="label">Uncompress</span>'
  if d['status'] == 1:
    status = '<span class="label">Format checking</span>'
  if d['status'] == 5:
    status = '<span class="label label-important">Error</span>'
    actions += '<button class="btn btn-info update" data-uid="'+str(d['_id'])+'"><li class="icon-refresh"> </li></button>'
    actions += '<button class="btn btn-warning delete" data-uid="'+str(d['_id'])+'" data-fileid="'+str(d['uid'])+'"><li class="icon-remove"> </li></button>'
  if d['status'] == 2:
    actions = '<a class="btn btn-info datasetmodal" data-uid="'+str(d['_id'])+'" role="button" href="#datasetModal"><li class="icon-eye-open"> </li></a>'
    actions += '<button class="btn btn-info download" data-uid="'+str(d['path'])+'"><li class="icon-download"> </li></button>'
    actions += '<button class="btn btn-info update" data-uid="'+str(d['_id'])+'"><li class="icon-refresh"> </li></button>'
    actions += '<button class="btn btn-warning delete" data-uid="'+str(d['_id'])+'" data-fileid="'+str(d['uid'])+'"><li class="icon-remove"> </li></button>'
%>
<tr id="tr-${d['uid']}"><td>${status |n}</td><td>
% if 'project' in d:
  ${d['project']}
% endif
</td><td>${d['name']}</td><td>${d['type']}/${d['format']}</td><td>${d['path']}</td><td>${d['size']}</td><td>${actions |n}</td></tr>
% endfor
</table>
</div>

<div id="datasetModal" class="modal hide fade" tabindex="-1" role="dialog" aria-labelledby="DataSet" aria-hidden="true">
  <div class="modal-header">
    <button type="button" class="close" data-dismiss="modal" aria-hidden="true">×</button>
    <h3 id="DataSet">DataSet</h3>
  </div>
  <div id="modal-body" class="modal-body">
  </div>
  <div class="modal-footer">
<%
    actions = ''
    for protocol in DataPluginManager.supported_protocols:
        actions += '<button class="btn btn-info btn-data-plugin" data-plugin="'+DataPluginManager.supported_protocols[protocol]+'" data-uid=""><li class="icon-upload"> </li>'+DataPluginManager.supported_protocols[protocol]+'</button>'
%>
    ${actions |n}
    <button class="btn" data-dismiss="modal" aria-hidden="true">Close</button>
  </div>
</div>

<script>
$(function(){

$('.datasetmodal').click(function(e) {
    uid = $(this).attr('data-uid');
        $.getJSON("${request.route_url('data',uid='')}"+ uid,function(data) {
                infoHtml = '<h2>'+data['dataset']['name']+' - '+data['dataset']['project']+'</h2>';
                infoHtml += '<div>Size: '+data['dataset']['size']+'</div>';
                infoHtml += '<div>Format: '+data['dataset']['format']+'</div>';
                infoHtml += '<h3>History</h3>'
                infoHtml += '<table class="table table-striped">';
                infoHtml += '<thead><tr><th>Date</th><th>Message</th></tr></thead>';
                $.each(data['history'], function(key, val) {
                    var a = new Date(val['committed_date'] * 1000);
                    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
                    var year = a.getFullYear();
                    var month = months[a.getMonth()];
                    var date = a.getDate();
                    var hour = a.getHours();
                    var min = a.getMinutes();
                    var sec = a.getSeconds();
                    var time = date+','+month+' '+year+' '+hour+':'+min+':'+sec ;
                    infoHtml += '<tr><td>'+time+'</td><td>'+val['message']+'</td></tr>'; 
                });
                infoHtml += '</table>';
                $('#modal-body').html(infoHtml);
                $('#datasetModal').find('button').attr('data-uid', data['dataset']['uid']);
                $('#datasetModal').modal({
                    show: true
                });
        });


});

$('.delete').click(function(e) {
        uid = $(this).attr('data-fileid')
        $.ajax({
            type: 'delete',
            url: "${request.route_url('data',uid='')}"+ uid,
            success: function() {
               $("#tr-"+uid).remove();
            }
        }); 
});

<%
objectmanager = ObjectManager()
downloadpath = objectmanager.get_storage_path()
%>

$('.btn-data-plugin').click(function(e) {
        window.open("${request.route_url('data_plugin')}/"+$(this).attr('data-plugin')+"/upload?protocol="+$(this).attr('data-plugin')+"&id="+$(this).attr('data-uid'));
});

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

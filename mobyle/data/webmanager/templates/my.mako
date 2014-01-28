<%inherit file="layout.mako"/>

<%
from pyramid.url import route_url,static_url
from mobyle.common.objectmanager import ObjectManager
from mobyle.data.manager.pluginmanager import DataPluginManager

DataPluginManager.get_manager()

%>

<div class="container">
    <blockquote>
        <p>On this page, you manage your Mobyle datasets.<br>
    </blockquote>
    <br>
 <div class="row">
 <div class="span3 facets">
 </div>
 <div class="span9 datasets">
 <table class="table">
 <tr><th>Status</th><th>Project</th><th>Name</th><th>Type/Format</th><th>Path</th><th>Size</th><th></th></tr>
</table>
</div>
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

function bytesToSize(bytes) {
    var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (bytes == 0) return 'n/a';
    var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
    return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
};

function basename(path) {
   return path.split('/').reverse()[0];
}

projects = {};
% for id in projectsname:
projects["${id}"] = "${projectsname[id]}";
% endfor


$(function(){

$(document).on("click",".filter", function(e) {
  var key = $(this).attr("data-key");
  var value = $(this).attr("data-uid");
  get_public_datasets(key,value);
  $("#filter").html("<ul class=\"breadcrumb\"><li>"+key+" = "+value+"</li></ul>");

});



$(document).on("click",'.datasetmodal',function(e) {
    showDataSet($(this).attr('data-uid'),"${request.route_url('data',uid='')}","datasetModal", true);
});

$(document).on('click','.delete',function(e) {
        uid = $(this).attr('data-uid')
        $.ajax({
            type: 'delete',
            url: "${request.route_url('data',uid='')}"+ uid,
            success: function() {
               $("#tr-"+uid).remove();
            }
        }); 
});


$('.btn-data-plugin').click(function(e) {
        window.open("${request.route_url('data_plugin')}/"+$(this).attr('data-plugin')+"/upload?protocol="+$(this).attr('data-plugin')+"&id="+$(this).attr('data-uid'));
});

$(document).on("click",'.download', function(e) {
        uid = $(this).attr('data-uid');
        fpath = $(this).attr('data-path');
        window.open("${request.route_url('main')}download/"+ uid + "/" + fpath);
});

$(document).on("click",'.btn-share', function(e) {
        var uid = $(this).attr('data-uid');
        var file_path = $(this).attr('data-path');
        var token_url = "${route_url('main',request)}data/"+ uid + "/token";
        $.getJSON(token_url,function(data) {
            if(file_path=="") {
                var download_url = "${route_url('main',request)}data-download/"+data['token']+"/";
               $("#token-share").html("You can now share this file for public download with the following url for the next 24 hours:<br/>"+download_url+"</a>/file_name_or_pat");
            }
            else {
                var download_url = "${route_url('main',request)}data-download/"+data['token']+"/"+file_path; 
                $("#token-share").html("You can now share this file for public download with the following url for the next 24 hours:<br/><a href=\""+download_url+"\">"+download_url+"</a>");
            }
        });
});


$(document).on("click",'.update',function(e) {
        uid = $(this).attr('data-uid');
        $(location).attr('href',"${route_url('main',request)}?id="+uid) ;
});

get_public_datasets(null,null);

});


function get_public_datasets(key,value) {
var filter = "";
if(key!=null && value!=null) {
  filter = "?filter="+key+"&"+key+"="+value;
}
$.getJSON("${request.route_url('my.json')}"+filter,function(data) {
    //var data = JSON.parse(data);
    var mylist = $(".datasets .table");
    mylist.html("");
    mylist.append("<tr><th>Status</th><th>Project</th><th>Name</th><th>Type/Format</th><th>Path</th><th>Size</th><th></th></tr>");
    var mylisthtml = "";
    for(var d=0;d<data.length;d++) {
        try{
            var dataset = data[d];
            mylisthtml += '<tr id="tr-'+dataset['_id']['$oid']+'">';
            var actions = '';
            var dstatus = '';
            if(dataset['status'] == 0) {
                dstatus = '<span class="label">Queued</span>';
            }
            else if(dataset['status'] == 1) {
                dstatus = '<span class="label">Downloading</span>';
            }
            else if(dataset['status'] == 3) {
                dstatus = '<span class="label">Uncompress</span>';
                actions += '<button class="btn btn-warning delete" \
                            data-uid="'+dataset['_id']['$oid']+'"> \
                            <li class="icon-remove"> </li></button>';
            }
            else if(dataset['status'] == 1) {
                dstatus = '<span class="label">Format checking</span>';
            }
            else if(dataset['status'] == 1) {
                dstatus = '<span class="label label-important">Error</span>';
                actions += '<button class="btn btn-info update" \
                            data-uid="'+dataset['_id']['$oid']+'"> \
                            <li class="icon-refresh"> </li></button>';
                actions += '<button class="btn btn-warning delete" \
                            data-uid="'+dataset['_id']['$oid']+'"> \
                            <li class="icon-remove"> </li></button>';
            }
            else if(dataset['status'] == 2) {
                actions = '<a class="btn btn-info datasetmodal" \
                            data-uid="'+dataset['_id']['$oid']+'" \
                            role="button" href="#datasetModal"> \
                            <li class="icon-eye-open"> </li></a>';
                if(dataset['data']['path']!=undefined) {
                    actions += "<button class=\"btn btn-info download\"" +
                               " data-uid=\""+dataset['_id']['$oid']+"\"" +
                               " data-path=\""+dataset['data']['path']+"\">" +
                               "<li class=\"icon-download\"> </li></button>";
                }
                actions += '<button class="btn btn-info update" \
                            data-uid="'+dataset['_id']['$oid']+'"> \
                            <li class="icon-refresh"> </li></button>';
                actions += '<button class="btn btn-warning delete" \
                            data-uid="'+dataset['_id']['$oid']+'"> \
                            <li class="icon-remove"> </li></button>';
            }

            mylisthtml += '<td>'+dstatus+'</td><td>';
            if(dataset['project'] != undefined) {
                mylisthtml+= projects[dataset['project']['$oid']];
            }
            mylisthtml += '</td>';
            mylisthtml += '<td>'+dataset['name']+'</td>';
            if(dataset['data']['type']!=undefined) {
                mylisthtml += '<td>'+dataset['data']['type']+ \
                              '/'+ dataset['data']['format']+"</td>";
            }
            else { mylisthtml += '<td>N/A</td>'; }
            if(dataset['data']['path']!=undefined) {
                mylisthtml += '<td>'+dataset['data']['path']+'</td>';
                mylisthtml += '<td>'+dataset['data']['size']+'</td>';
            }
            mylisthtml += '<td>'+actions+'</td>';
            mylisthtml += '</tr>';
        }catch(err){
            console.log("error while displaying dataset", dataset);
        }
    }
    mylist.append(mylisthtml);

    var facets = getFacets(data, projects);
    showFacets(facets);

});
}



</script>

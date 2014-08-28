<%inherit file="layout.mako"/>

<%
from pyramid.url import route_url,static_url
from mobyle.common.objectmanager import ObjectManager
from mobyle.data.manager.pluginmanager import DataPluginManager

DataPluginManager.get_manager()

%>

<div class="container">
    <blockquote>
        <p>On this page, you can access public data sets.<br>
    </blockquote>
    <br>
 <div class="row">
 <div class="span3 facets">
 </div>
 <div class="span9 datasets">
 <div id="filter"></div>
 <table class="table">
 <tr><th>Project</th><th>Name</th><th>Type/Format</th><th>Size</th><th></th></tr>
</table>
 </div>
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

$(function(){


$(document).on("click",'.download', function(e) {
        uid = $(this).attr('data-uid');
        fpath = $(this).attr('data-path');
        window.open("${request.route_url('main')}data/"+ uid + '/raw/' + fpath);
});

var projects = {};
% for id in projectsname:
projects["${id}"] = "${projectsname[id]}";
% endfor

function get_public_datasets(key,value) {
var filter = "";
if(key!=null && value!=null) {
  filter = "?filter="+key+"&"+key+"="+value;
}
$.getJSON("${request.route_url('public.json')}"+filter,function(data) {
    //var data = JSON.parse(data);
    var publiclist = $(".datasets .table");
    publiclist.html("<tr><th>Project</th><th>Name</th><th>Type/Format</th><th>Size</th><th></th></tr>");
    var publiclisthtml = "";
    for(var d=0;d<data.length;d++) {
        dataset = data[d];

        var uid = dataset['_id']['$oid'];
        publiclisthtml += "<tr data-uid=\""+uid+"\">";
        publiclisthtml += "<td>"+projects[dataset['project']['$oid']]+"</td>";
        publiclisthtml += "<td>"+dataset['name']+"</td>";
        publiclisthtml += "<td>"+dataset['data']['type']+"/"+dataset['data']['format']+"</td>";
        publiclisthtml += "<td>"+dataset['data']['size']+"</td>";
        publiclisthtml +="<td><a class=\"btn btn-info datasetmodal\" data-uid=\""+uid+"\" role=\"button\" href=\"#datasetModal\"><li class=\"icon-eye-open\"> </li></a>";
        if(dataset['data']['path']!=undefined) {
            publiclisthtml += '<button class="btn btn-info download"' +
                          ' data-uid="'+uid+'"'+
                          ' data-path="'+dataset['data']['path']+'">' +
                          '<li class="icon-download"> </li></button></td>';
        }
    }
    publiclist.append(publiclisthtml);

    var facets = getFacets(data, projects);
    showFacets(facets);

});
}


get_public_datasets(null,null);

$(document).on("click",".filter", function(e) {
  var key = $(this).attr("data-key");
  var value = $(this).attr("data-uid");
  get_public_datasets(key,value);
  $("#filter").html("<ul class=\"breadcrumb\"><li>"+key+" = "+value+"</li></ul>");

});


$(document).on("click",".datasetmodal", function(e) {
    showDataSet($(this).attr('data-uid'),"${request.route_url('data',uid='')}","datasetModal", false);
});

});

</script>

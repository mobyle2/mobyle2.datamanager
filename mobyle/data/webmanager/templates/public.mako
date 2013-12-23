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
        window.open("${request.route_url('main')}download/"+ uid);
});

var projects = {};
% for id in projectsname:
projects["${id}"] = "${projectsname[id]}";
% endfor

$.getJSON("${request.route_url('public.json')}",function(data) {
    facets = {'projects': {}, 'tags': {}}
    var data = JSON.parse(data);
    var publiclist = $(".datasets .table");
    var publiclisthtml = "";
    for(var d=0;d<data.length;d++) {
        dataset = data[d];
        if(dataset['status']!=2) {
            continue;
        }
        projectname = projects[dataset['project']['$oid']];
        if (facets['projects'][projectname] == undefined) {
            facets['projects'][projectname] = 0;
        }
        facets['projects'][projectname]++;
        for(var i=0;i<dataset['tags'].length;i++) {
            if (facets['tags'][dataset['tags'][i]] == undefined) {
            facets['tags'][dataset['tags'][i]] = 0;
            }
            facets['tags'][dataset['tags'][i]]++;
        }
        publiclisthtml += "<tr data-uid=\""+dataset['_id']['$oid']+"\">";
        publiclisthtml += "<td>"+projectname+"</td>";
        publiclisthtml += "<td>"+dataset['name']+"</td>";
        publiclisthtml += "<td>"+dataset['data']['type']+"/"+dataset['data']['format']+"</td>";
        publiclisthtml += "<td>"+dataset['data']['size']+"</td>";
        publiclisthtml +="<td><a class=\"btn btn-info datasetmodal\" data-uid=\""+dataset['_id']['$oid']+"\" role=\"button\" href=\"#datasetModal\"><li class=\"icon-eye-open\"> </li></a></td>";
    }
    publiclist.append(publiclisthtml);
    var facetdiv = $(".facets");
    var facetstable = "";
    facetstable += '<table class="table">';
    facetstable += "<tr><td><h5>Projects</h5></td></tr>";
    for(project in facets['projects']) {
        facetstable += "<tr><td>"+project+" ("+facets['projects'][project]+")</td></tr>";
    }
    facetstable += "<tr><td><h5>Tags</h5></td></tr>";
    for(tag in facets['tags']) {
        facetstable += "<tr><td>"+tag+" ("+facets['tags'][tag]+")</td></tr>";
    }
    facetstable += '</table>';
    facetdiv.html(facetstable);

});


$(document).on("click",".datasetmodal", function(e) {
    showDataSet($(this).attr('data-uid'),"${request.route_url('data',uid='')}","datasetModal", false);
});

});

</script>

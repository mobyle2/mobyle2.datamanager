


$(document).ready(function() {
    //$.fn.editable.defaults.mode = 'inline'
    $('#description').editable();
});

function bytesToSize(bytes) {
    var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    if (bytes == 0) return 'n/a';
    var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
    return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
};



/**
* Display a dataset in a modal dialog
*
* uid: dataset id
* url: url to get a dataset: http:/.../data/
* mymodal: id of the modal HTML element
* isowner: is the user owner of the dataset
*
*/
function showDataSet(uid, url, mymodal, isowner) {
        $.getJSON(url + uid,function(data) {
        infoHtml = "<div id=\"dataset\">";
        infoHtml += '<h2><span class="canedit" id="name" data-type="text" data-pk="'+uid+'\" data-title="Enter the name of the file" data-url="data/'+uid+'/edit">'+data['dataset']['name']+'</span> - <span class="canedit" id="project" data-source="projects" data-type="select" data-pk="'+uid+'\" data-title="Enter the name of the project" data-url="data/'+uid+'/edit">'+data['dataset']['project']+'</span></h2>';
        if(data['dataset']['description']!=undefined) {
            infoHtml += "<div class=\"canedit\" id=\"description\" data-type=\"textarea\" data-pk=\""+uid+"\" data-title=\"Enter description\" data-url=\"data/"+uid+"/edit\">"+data['dataset']['description']+"</div>";
        }
        is_private = "public";
        if (! data['dataset']['public']) {
            is_private = "private";
        }
        infoHtml += '<div><strong>Privacy</strong>: <span <span class="canedit" data-source="[{value:\'public\', text:\'Public\'},{value:\'private\', text:\'Private\'}]" id="privacy" data-type="select" data-pk="'+uid+'" data-title="Select if data should be public or private" data-url="data/'+uid+'/edit">'+is_private+'</span>';
        if('size' in data['dataset']['data']) {
            infoHtml += '<div><strong>Size</strong>: '+bytesToSize(data['dataset']['data']['size'])+'</div>';
        }
        if('format_terms' in data['dataset']['data']['type']) {
            infoHtml += '<div><strong>Format</strong>: '+data['dataset']['data']['type']['format_terms'][0]+'</div>';
        }
        if('path' in data['dataset']['data']) {
            // This is a RefData (one or more file
            var value = data['dataset']['data'];
            infoHtml += "<div><h3>Files</h3>";
            infoHtml += "<div>Size: " + bytesToSize(value['size']) + "</div>";
            infoHtml += "<table class=\"table\">";
            //for(i=0;i<value['path'].length;i++) {
                infoHtml += "<tr>";
                var fpath = value['path'];
                infoHtml += "<td>" + value['path'] + "</td>";
                infoHtml += "<td>";
                infoHtml += "<button class=\"btn btn-info download\""+
                                " data-uid=\""+uid+"\""+
                                " data-path=\""+fpath+"\">"+
                                "<li class=\"icon-download\">"+
                                "</li></button>";
                if(isowner) {
                    infoHtml += "<button class=\"btn btn-info btn-share\""+
                                "data-uid=\""+uid+"\""+
                                " data-path=\""+fpath+"\">"+
                                "<li class=\"icon-share\"></li>Share</button>";
                }
                infoHtml += "</td>";

                infoHtml += "</tr>";
            //}
            infoHtml += "</table>";

            infoHtml += "</div>";
        }
        else {
            // This is a struct data or other... TODO
            var value = data['dataset']['data'];
            infoHtml += "<div><h3>Files</h3>";
            infoHtml += "<table class=\"table\">";
            var available_types = "[";
            $.each(value['properties'], function(index, subvalue) {
                available_types+= '{ value:\''+index + '\',text: \''+ index +'\'},';
            });
            available_types += "]";
            var available_files = "[";
            for(i=0;i<value['files'].length;i++) {
            //$.each(value['files'], function(subvalue) {
                available_files+= '{ value:\''+value['files'][i]['path'] + '\',text: \''+ value['files'][i]['path']+' ('+ bytesToSize(value['files'][i]['size'])+')' +'\'},';
            //});
            }
            available_files += "]";
            $.each(value['properties'], function(index, subvalue) {
                infoHtml += "<tr>";
                var fpath = subvalue['path'];

                //infoHtml += "<td>" + subvalue['path'][0] +" ("+ bytesToSize(subvalue['size']) +")"+ "</td>";
                dowarn = '';
                if(subvalue['path']=='') {
                    dowarn = 'alert';
                }
                infoHtml += '<td><strong>'+index+'</strong>: <span class="canedit '+dowarn+'" data-source="'+available_files+'"  id="type" data-type="select" data-pk="'+index+'" data-title="Select the file or this type" data-url="data/'+uid+'/edit">'+subvalue['path']+' ('+bytesToSize(subvalue["size"])+') ' + '</span></td>';

                infoHtml += "<td>";
                infoHtml += "<button class=\"btn btn-info download\""+
                                " data-uid=\""+uid+"\""+
                                " data-path=\""+fpath+"\">"+
                                "<li class=\"icon-download\">"+
                                "</li></button>";
                if(isowner) {
                    infoHtml += "<button class=\"btn btn-info btn-share\""+
                                "data-uid=\""+uid+"\""+
                                " data-path=\""+fpath+"\">"+
                                "<li class=\"icon-share\"></li>Share</button>";
                }
                infoHtml += "</td>";

                infoHtml += "</tr>";
            });
            infoHtml += "</table>";

            infoHtml += "</div>";
        }
                infoHtml += '<div id="token-share"></div>';
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
                    var time = date+','+month+' '+year+' '+hour+':'+min+':'+sec
;
                    infoHtml += '<tr><td>'+time+'</td><td>'+val['message']+'</td></tr>';
                });
                infoHtml += '</table>';
                infoHtml += '</div>';
                $("#"+mymodal+' .modal-body').html(infoHtml);
                mymodal = $("#"+mymodal);
                mymodal.find('button').attr('data-uid', data['dataset']['uid']);
                mymodal.modal({
                    show: true
                });
                $('#dataset').editable( {
                    selector: ".canedit",
                    success: function(response, newValue) {
                    if(response.status == 'error') return response.msg; //msg will be shown in editable form
                    }
                });
        });




}


/**
* Generate a dict for faceting based on input datasets list
*
* projects is a dict matching projects name and projects ids
*
*/
function getFacets(datasets, projects) {
    facets = {'projects': {}, 'tags': {}, 'types': {}, 'formats': {}};
    for(var d=0;d<datasets.length;d++) {
        dataset = datasets[d];
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

        if (facets['types'][dataset['data']['type']['data_terms']] == undefined) {
            facets['types'][dataset['data']['type']['data_terms']] = 0;
        }
        facets['types'][dataset['data']['type']['data_terms']]++;

        if (facets['formats'][dataset['data']['type']['format_terms']] == undefined) {
            facets['formats'][dataset['data']['type']['format_terms']] = 0;
        }
        facets['formats'][dataset['data']['type']['format_terms']]++;
    }
    return facets;
}


/**
* Show facets in a div with class facet
*/
function showFacets(facets) {

    var facetdiv = $(".facets");
    var facetstable = "";
    facetstable += '<table class="table">';
    facetstable += "<tr><td><h5>Projects</h5></td></tr>";
    for(project in facets['projects']) {
        facetstable += "<tr class=\"filter\" data-key=\"project\" data-uid=\""+dataset['project']['$oid']+"\"><td>"+project+" ("+facets['projects'][project]+")</td></tr>";
    }
    facetstable += "<tr><td><h5>Tags</h5></td></tr>";
    for(tag in facets['tags']) {
        facetstable += "<tr class=\"filter\" data-key=\"tags\" data-uid=\""+tag+"\"><td>"+tag+" ("+facets['tags'][tag]+")</td></tr>";
    }
    facetstable += "<tr><td><h5>Types</h5></td></tr>";
    for(type in facets['types']) {
        facetstable += "<tr class=\"filter\" data-key=\"type\" data-uid=\""+type+"\"><td>"+type+" ("+facets['types'][type]+")</td></tr>";
    }
    facetstable += "<tr><td><h5>Formats</h5></td></tr>";
    for(format in facets['formats']) {
        facetstable += "<tr class=\"filter\" data-key=\"format\" data-uid=\""+format+"\"><td>"+format+" ("+facets['formats'][format]+")</td></tr>";
    }
    facetdiv.html(facetstable);
}

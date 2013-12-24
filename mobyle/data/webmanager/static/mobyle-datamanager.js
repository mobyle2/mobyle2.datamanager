

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
                infoHtml = '<h2>'+data['dataset']['name']+' - '+data['dataset']['project']+'</h2>';
                if(data['dataset']['description']!=undefined) {
                    infoHtml += "<div>"+data['dataset']['description']+"</div>";
                }
        if('size' in data['dataset']['data']) {
                    infoHtml += '<div><h3>Size: '+bytesToSize(data['dataset']['data']['size'])+'</h3></div>';
        }
        if('format' in data['dataset']['data']) {
                infoHtml += '<div><h3>Format: '+data['dataset']['data']['format']+'</h3></div>';
        }
        if('value' in data['dataset']['data'] && $.isArray(data['dataset']['data']['value'])) {
            // This is a ListData
            infoHtml += "<div><h3>Files</h3>";
            infoHtml += "<table class=\"table\">";
            $.each(data['dataset']['data']['value'], function(key,value) {
                infoHtml += "<tr>";
                if('path' in value) {
                    var fpath = value['path'];
                    infoHtml += "<td>" + value['path'] + "</td>";
                    infoHtml += "<td>" + bytesToSize(value['size']) + "</td>";
                    infoHtml += "<td><button class=\"btn btn-info download\""+
                                " data-uid=\""+uid+"\""+
                                " data-path=\""+fpath+"\">"+
                                "<li class=\"icon-download\">"+
                                "</li></button></td>";
                }
                else {
                    infoHtml += "<td>" + value['value'] + "</td>";
                }
                infoHtml += "</tr>";
            });
            infoHtml += "</table>";
            if(isowner) {
            infoHtml += "<button class=\"btn btn-info btn-share\" data-uid=\""+uid+"\" data-path=\"\"><li class=\"icon-share\"></li>Share</button>";
            }

            infoHtml += "</div>";
        }
        else {
            var fpath = data['dataset']['data']['path']; 
            if(isowner) {
            infoHtml += "<button class=\"btn btn-info btn-share\" data-uid=\""+uid+"\" data-path=\""+fpath+"\"><li class=\"icon-share\"></li>Share</button>";
            }
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
                $("#"+mymodal+' .modal-body').html(infoHtml);
                mymodal = $("#"+mymodal);
                mymodal.find('button').attr('data-uid', data['dataset']['uid']);
                mymodal.modal({
                    show: true
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

        if (facets['types'][dataset['data']['type']] == undefined) {
            facets['types'][dataset['data']['type']] = 0;
        }
        facets['types'][dataset['data']['type']]++;

        if (facets['formats'][dataset['data']['format']] == undefined) {
            facets['formats'][dataset['data']['format']] = 0;
        }
        facets['formats'][dataset['data']['format']]++;
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

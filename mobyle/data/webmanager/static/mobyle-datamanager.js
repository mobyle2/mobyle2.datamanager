

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
        if('size' in data['dataset']['data']) {
                    infoHtml += '<div><h3>Size: '+bytesToSize(data['dataset']['data']['size'])+'</h3></div>';
        }
        if('format' in data['dataset']['data']) {
                infoHtml += '<div><h3>Format: '+data['dataset']['data']['format']+'</h3></div>';
        }
        if('value' in data['dataset']['data'] && $.isArray(data['dataset']['data']['value'])) {
            // This is a ListData
            infoHtml+="<div><h3>Files</h3>";
            $.each(data['dataset']['data']['value'], function(key,value) {
                if('path' in value) {
                    var fpath = data['dataset']['rootpath']+"/"+value['path'];
                    infoHtml += "<div>";
                    infoHtml += basename(value['path']) ;
                    infoHtml += " ("+bytesToSize(value['size'])+")";
                    infoHtml += "<button class=\"btn btn-info download\" data-uid=\""+fpath+"\"><li class=\"icon-download\"> </li></button>";
                    infoHtml += "</div>";
                }
                else {
                    infoHtml += "<div>" + value['value'] + "</div>";
                }
            });
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

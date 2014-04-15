<%inherit file="layout.mako"/>

<div class="container">
    <blockquote>
        <p>On this page, you can upload files to your Mobyle projects.<br>
    </blockquote>
    <br>

% if user is None or not user['last_name']:
    <blockquote>
        <h3>Please login first using your API key.</h3><br>
    </blockquote>
% else:
<div class="row">
<div class="span6">
    <form id="remotefileupload" action="${request.route_url('upload_remote_data')}" method="POST">
    <legend>Load Remote dataset</legend>
    % if uid:
    <div class="control-group error">
      <label>Replacing file</label>
      <input type="text" value="${uid}" name="id"/>
    </div>
    % endif
    <div class="control-group">
    <label>Project</label>
    <select name="project">
    % for project in user['projects']:
	% if uid and project['id'] == dataset['project']:
		<option value="${project['id']}" selected>${project['name']}</option>
	% else: 
        	<option value="${project['id']}">${project['name']}</option>
        % endif
    % endfor
    </select>
    </div>
    <div class="control-group">
    <label>Name (optional)</label>
    % if uid:
    <input id="name" name="name" type="text"  value="${dataset['name']}"/>
    % else:
    <input id="name" name="name" type="text"/>
    % endif
    </div>
    <div class="control-group">
    <label>Description (optional)</label>
    % if uid:
    <textarea id="description" name="description" type="text">${dataset['description']}</textarea>
    % else:
    <textarea id="description" name="description" type="text"></textarea>
    % endif
    </div>
    <div class="control-group">
    <label>Privacy</label>
    <select name="privacy">
	%if uid and dataset['public']:
        <option value="private" selected>Private (project)</option>
        <option value="public">Public</option>
	%else:
        <option value="private">Private (project)</option>
        <option value="public" selected>Public</option>
	%endif
    </select>
    </div>

    <input type="hidden" class="apikey" name="apikey" value="${user['apikey']}"/>

    <div class="control-group">
    <label>Data type</label>
    <input id="type_selection" name="type" type="text" data-provide="typeahead"/>
    <span class="help-block">Type of the data</span>
    <span class="help-block" id="type_selection_desc"></span>
    <label>Data format</label>
    <input id="format_selection" name="format" type="text" data-provide="typeahead"/>
    <span class="help-block">Format of the data</span>
    <span class="help-block" id="format_selection_desc"></span>

    </div>
    <div class="control-group">
    <label>URL</label>
    <select name="protocol">
      % if protocols:
        % for protocol in protocols:
            <option value="${protocol}">${protocol}</option>
        % endfor
      % endif
    <%
       from mobyle.data.manager.pluginmanager import DataPluginManager
       DataPluginManager.get_manager()
    %>
    % for protocol in DataPluginManager.supported_protocols:
        <option value="${protocol}">${protocol}</option>
    % endfor 

    </select>
    <input type="text" name="rurl" value=""/>
    <span class="help-block">URL of remote element (http,ftp ...). Must be readable as anonymous.</span>
    </div>
    <div class="control-group">
    <label class="checkbox">
    <input type="checkbox" name="uncompress">Uncompress
    </label>
    <span class="help-block">In the case of an archive (zip, tar.gz, bz2), uncompress it</span>
    </div>
    <div class="control-group">
    <label class="checkbox">
    <input type="checkbox" name="group">Group dataset
    </label>
    <span class="help-block">If data is uncompressed, group the dataset as a single data. If not grouped, all files will be declared as individual data element</span>
    </div>
    <button class="btn btn-success">
         <i class="icon-download-alt icon-white"></i>
         <span>Start transfer</span>
    </button>
     
    </form>
</div>
<div class="span6">
    <!-- The file upload form used as target for the file upload widget -->
    <form id="fileupload" action="${request.route_url('upload_data')}" method="POST" enctype="multipart/form-data">

    <legend>Upload dataset</legend>
    % if uid:
    <div class="control-group error">
      <label>Replacing file</label>
      <input type="text" name="id" value="${uid}"/>
    </div>
    % endif
    <div class="control-group">
    <label>Project</label>
    <select name="project">
    % for project in user['projects']:
	% if uid and project['id'] == dataset['project']:
		<option value="${project['id']}" selected>${project['name']}</option>
	% else: 
        	<option value="${project['id']}">${project['name']}</option>
        % endif
    % endfor
    </select>
    </div>
    <div class="control-group">
    <label>Name (optional)</label>
    % if uid:
    <input id="name" name="name" type="text"  value="${dataset['name']}"/>
    % else:
    <input id="name" name="name" type="text"/>
    % endif
    </div>
    <div class="control-group">
    <label>Description (optional)</label>
    % if uid:
    <textarea id="description" name="description" type="text">${dataset['description']}</textarea>
    % else:
    <textarea id="description" name="description" type="text"></textarea>
    % endif
    </div>
    <div class="control-group">
    <label>Privacy</label>
    <select name="privacy">
	%if uid and dataset['public']:
        <option value="private" selected>Private (project)</option>
        <option value="public">Public</option>
	%else:
        <option value="private">Private (project)</option>
        <option value="public" selected>Public</option>
	%endif
    </select>
    </div>

    <div class="control-group">
    <label>Data type</label>
    <input id="type_selection_upload" name="type" type="text" data-provide="typeahead"/>
    <span class="help-block">Type of the data</span>
    <span class="help-block" id="type_selection_desc_upload"></span>
    <label>Data format</label>
    <input id="format_selection_upload" name="format" type="text" data-provide="typeahead"/>
    <span class="help-block">Format of the data</span>
    <span class="help-block" id="format_selection_desc_upload"></span>
    </div>

    <div class="control-group">
    <label class="checkbox">
    <input type="checkbox" name="uncompress">Uncompress
    </label>
    <span class="help-block">In the case of an archive (zip, tar.gz, bz2), uncompress it</span>
    </div>
    <div class="control-group">
    <label class="checkbox">
    <input type="checkbox" name="group">Group dataset
    </label>
    <span class="help-block">If data is uncompressed, group the dataset as a single data. If not grouped, all files will be declared as individual data element</span>
    </div>
    <input type="hidden" class="apikey" name="apikey" value="${user['apikey']}"/>



        <!-- The fileupload-buttonbar contains buttons to add/delete files and start/cancel the upload -->
        <div class="row fileupload-buttonbar">
            <div class="span8">
                <!-- The fileinput-button span is used to style the file input field as button -->
                <span class="btn btn-success fileinput-button">
                    <i class="icon-plus icon-white"></i>
                    <span>Add files...</span>
                    <input type="file" name="files[]" multiple>
                </span>
                <button type="submit" class="btn btn-primary start">
                    <i class="icon-upload icon-white"></i>
                    <span>Start upload</span>
                </button>
                <button type="reset" class="btn btn-warning cancel">
                    <i class="icon-ban-circle icon-white"></i>
                    <span>Cancel upload</span>
                </button>
                <button type="button" class="btn btn-danger delete">
                    <i class="icon-trash icon-white"></i>
                    <span>Delete</span>
                </button>
                <input type="checkbox" class="toggle">
            </div>
            <!-- The global progress information -->
            <div class="span5 fileupload-progress fade">
                <!-- The global progress bar -->
                <div class="progress progress-success progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100">
                    <div class="bar" style="width:0%;"></div>
                </div>
                <!-- The extended global progress information -->
                <div class="progress-extended">&nbsp;</div>
            </div>
        </div>
        <!-- The loading indicator is shown during file processing -->
        <div class="fileupload-loading"></div>
        <br>
        <!-- The table listing the files available for upload/download -->
        <table role="presentation" class="table table-striped"><tbody class="files" data-toggle="modal-gallery" data-target="#modal-gallery"></tbody></table>
    </form>
</div>
</div>
% endif
    <br>
</div>

<!-- modal-gallery is the modal dialog used for the image gallery -->
<div id="modal-gallery" class="modal modal-gallery hide fade" data-filter=":odd" tabindex="-1">
    <div class="modal-header">
        <a class="close" data-dismiss="modal">&times;</a>
        <h3 class="modal-title"></h3>
    </div>
    <div class="modal-body"><div class="modal-image"></div></div>
    <div class="modal-footer">
        <a class="btn modal-download" target="_blank">
            <i class="icon-download"></i>
            <span>Download</span>
        </a>
        <a class="btn btn-success modal-play modal-slideshow" data-slideshow="5000">
            <i class="icon-play icon-white"></i>
            <span>Slideshow</span>
        </a>
        <a class="btn btn-info modal-prev">
            <i class="icon-arrow-left icon-white"></i>
            <span>Previous</span>
        </a>
        <a class="btn btn-primary modal-next">
            <span>Next</span>
            <i class="icon-arrow-right icon-white"></i>
        </a>
    </div>
</div>
<!-- The template to display files available for upload -->
<script id="template-upload" type="text/x-tmpl">
{% for (var i=0, file; file=o.files[i]; i++) { %}
    <tr class="template-upload fade">
        <td class="preview"><span class="fade"></span></td>
        <td class="name"><span>{%=file.name%}</span></td>
        <td class="size"><span>{%=o.formatFileSize(file.size)%}</span></td>
        {% if (file.error) { %}
            <td class="error" colspan="2"><span class="label label-important">Error</span> {%=file.error%}</td>
        {% } else if (o.files.valid && !i) { %}
            <td>
                <div class="progress progress-success progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><div class="bar" style="width:0%;"></div></div>
            </td>
            <td class="start">{% if (!o.options.autoUpload) { %}
                <button class="btn btn-primary">
                    <i class="icon-upload icon-white"></i>
                    <span>Start</span>
                </button>
            {% } %}</td>
        {% } else { %}
            <td colspan="2"></td>
        {% } %}
        <td class="cancel">{% if (!i) { %}
            <button class="btn btn-warning">
                <i class="icon-ban-circle icon-white"></i>
                <span>Cancel</span>
            </button>
        {% } %}</td>
    </tr>
{% } %}
</script>
<!-- The template to display files available for download -->
<script id="template-download" type="text/x-tmpl">
{% for (var i=0, file; file=o.files[i]; i++) { %}
    <tr class="template-download fade">
        {% if (file.error) { %}
            <td></td>
            <td class="name"><span>{%=file.name%}</span></td>
            <td class="size"><span>{%=o.formatFileSize(file.size)%}</span></td>
            <td class="error" colspan="2"><span class="label label-important">Error</span> {%=file.error%}</td>
        {% } else { %}
            <td class="preview">{% if (file.thumbnail_url) { %}
                <a href="{%=file.url%}" title="{%=file.name%}" data-gallery="gallery" download="{%=file.name%}"><img src="{%=file.thumbnail_url%}"></a>
            {% } %}</td>
            <td class="name">
                <a href="{%=file.url%}" title="{%=file.name%}" data-gallery="{%=file.thumbnail_url&&'gallery'%}" download="{%=file.name%}">{%=file.name%}</a>
            </td>
            <td class="size"><span>{%=o.formatFileSize(file.size)%}</span></td>
            <td colspan="2"></td>
        {% } %}
        <td class="delete">
            <button class="btn btn-danger" data-type="{%=file.delete_type%}" data-url="{%=file.delete_url%}"{% if (file.delete_with_credentials) { %} data-xhr-fields='{"withCredentials":true}'{% } %}>
                <i class="icon-trash icon-white"></i>
                <span>Delete</span>
            </button>
            <input type="checkbox" name="delete" value="1">
        </td>
    </tr>
{% } %}
</script>

<script>
$(function() {

   //var edam_types = { 'EDAM:123' : 'sequence', 'EDAM:456': 'something' };
   //var edam_formats = { 'EDAM:323' : 'fasta', 'EDAM:356': 'text' };

   var service_type_terms = [];

   var t_edams = [];
   //for(edam in edam_types) {
   //    t_edams.push(edam+"|"+edam_types[edam]);
   //}
   //var f_edams = ["auto"]
   var f_edams = {};
   //for(edam in edam_formats) {
   //    f_edams.push(edam+"|"+edam_formats[edam]);
   //}

   $.getJSON("servicetypeterms", function(data) {
     var nbelt = data.length;
     service_type_terms = data;
     for(i=0;i<nbelt;i++) {
        if('properties' in data[i]) {
            var term_id = '';
            for(key in data[i]['properties']) {
                if(term_id!='') { term_id+= "+"; }
                term_id += data[i]['properties'][key]['term_id'];
            }
            t_edams.push(term_id+"|"+data[i]["name"]);
        }
        else {
            t_edams.push(data[i]["term_id"]+"|"+data[i]["name"]);
        }
     }
     updateTypes();
   });

   $("#format_selection_upload").typeahead({
      source: f_edams["format_selection_upload"],
      updater: function (item) {
        var elts = item.split('|');
        $("#format_selection_desc_upload").html("<span class=\"label label-info\">"+item+"</span>");
        return elts[0];
      },
      matcher: function(item) {
        return item.toLowerCase().indexOf(this.query.toLowerCase()) != -1;
      },
      minLength: 3
   });

   $("#format_selection").typeahead({
      source: f_edams["format_selection"],
      updater: function (item) {
        var elts = item.split('|');
        $("#format_selection_desc").html("<span class=\"label label-info\">"+item+"</span>");
        return elts[0];
      },
      matcher: function(item) {
        return item.toLowerCase().indexOf(this.query.toLowerCase()) != -1;
      },
      minLength: 3
   });


   /**
   * Update list of available formats according to selected term type
   */
   function updateFormats(elt, value) {
     f_edams[elt] = [];
     var nbelt = service_type_terms.length;
     for(i=0;i<nbelt;i++) {
        if(service_type_terms[i]["name"]==value) {
            if("properties" in service_type_terms[i]) {
                var keys = value.split('+');
                var complexedam = '';
                var complexname = ''
                for(j=0;j<keys.length;j++) {
                    if(complexedam!='') { complexedam += '+'; complexname += '+'; }
                    var subelt = service_type_terms[i]['properties'][keys[j]]
                    complexedam += subelt["format_terms"][0]["term_id"]
                    complexname += subelt["format_terms"][0]["name"];
                }
                f_edams[elt].push(complexedam+"|"+complexname);
            }
            else {
                var nbfmt = service_type_terms[i]["format_terms"].length;
                for(j=0;j<nbfmt;j++) {
                    f_edams[elt].push(service_type_terms[i]["format_terms"][j]["term_id"]+"|"+service_type_terms[i]["format_terms"][j]["name"]);
                }
            }
        break;
        }
     }
   $('#'+elt).data('typeahead').source =  f_edams[elt];
   /*
   $('#'+elt).typeahead({
      source: f_edams[elt],
      updater: function (item) {
        var elts = item.split('|');
        $("#"+elt+"_desc").html("<span class=\"label label-info\">"+item+"</span>");
        return elts[0];
      },
      matcher: function(item) {
        return item.toLowerCase().indexOf(this.query.toLowerCase()) != -1;
      },
      minLength: 3
   });
   */
   /*
   $('#format_selection_upload').typeahead({
      source: f_edams,
      updater: function (item) {
        var elts = item.split('|');
        $("#format_selection_desc_upload").html("<span class=\"label label-info\">"+item+"</span>");
        return elts[0];
      },
      matcher: function(item) {
        return item.indexOf(this.query) != -1;
      },
      minLength: 3
   });
   */


   }

   /**
   * Update list of available term types according to downloaded list
   */
   function updateTypes() {
   $('#type_selection').typeahead({
      source: t_edams,
      updater: function (item) {
        var elts = item.split('|');
        $("#type_selection_desc").html("<span class=\"label label-info\">"+item+"</span>");
        updateFormats("format_selection",elts[1]);
        return elts[0];
      },
      matcher: function(item) {
        return item.toLowerCase().indexOf(this.query.toLowerCase()) != -1;
      },
      minLength: 3
   });

   $('#type_selection_upload').typeahead({
      source: t_edams,
      updater: function (item) {
        var elts = item.split('|');
        updateFormats("format_selection_upload",elts[1]);
        $("#type_selection_desc_upload").html("<span class=\"label label-info\">"+item+"</span>");
        return elts[0];
      },
      matcher: function(item) {
        return item.toLowerCase().indexOf(this.query.toLowerCase()) != -1;
      },
      minLength: 3
   });

   }

});

</script>

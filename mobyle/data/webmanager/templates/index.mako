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

    <form id="remotefileupload" action="${request.route_url('upload_remote_data')}" method="POST">
    <legend>Remote dataset</legend>
    <div class="control-group">
    <label>Project</label>
    <select name="project">
    % for project in user['projects']:
        <option value="${project['id']}">${project['name']}</option>
    % endfor
    </select>
    </div>
    <input type="hidden" class="apikey" name="apikey" value="${user['apikey']}"/>
    % if uid:
    <div class="control-group error">
      <label>Replacing file</label>
      <input type="text" value="${uid}" name="id"/>
    </div>
    % endif
    <div class="control-group">
    <label>Data type</label>
    <select name="type">
      <option value="sequence">Sequence</option>
    </select>
    <span class="help-block">Type of the data</span>
    <label>Data format</label>
    <select name="format">
      <option value="auto">Auto-detect</option>
      <option value="fasta">Fasta</option>
    </select>
    <span class="help-block">Format of the data</span>

    </div>
    <div class="control-group">
    <label>URL</label>
    <select name="protocol">
        <option value="http://">http://</option>
        <option value="ftp://">ftp://</option>
        <option value="scp">scp</option>
        <option value="symlink">symlink</option>
    <%
       from mobyle.data.manager.pluginmanager import DataPluginManager
       DataPluginManager.get_manager()
    %>
    % for protocol in DataPluginManager.supported_protocols:
        <option value="${protocol}">${protocol}</option>
    % endfor 

    </select>
    <input type="text" name="rurl" value=""/>
    <span class="help-block">URL of remote element (http,ftp,cp). Must be readable as anonymous.</span>
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
    <br>
    <!-- The file upload form used as target for the file upload widget -->
    <form id="fileupload" action="${request.route_url('upload_data')}" method="POST" enctype="multipart/form-data">

    <legend>Upload dataset</legend>
    <div class="control-group">
    <label>Project</label>
    <select name="project">
    % for project in user['projects']:
        <option value="${project['id']}">${project['name']}</option>
    % endfor
    </select>
    </div>
    <div class="control-group">
    <label>Data type</label>
    <select name="type">
      <option value="sequence">Sequence</option>
    </select>
    <span class="help-block">Type of the data</span>
    <label>Data format</label>
    <select name="format">
      <option value="auto">Auto-detect</option>
      <option value="fasta">Fasta</option>
    </select>
    <span class="help-block">Format of the data</span>
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
    % if uid:
    <div class="control-group error">
      <label>Replacing file</label>
      <input type="text" name="id" value="${uid}"/>
    </div>
    % endif


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

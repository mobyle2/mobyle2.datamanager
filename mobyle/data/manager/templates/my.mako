<%inherit file="layout.mako"/>

<div class="container">
    <blockquote>
        <p>On this page, you manage your Mobyle datasets.<br>
    </blockquote>
    <br>
 <table class="table">
 <tr><th>Project</th><th>Name</th><th>Path</th><th>Size</th><th></th></tr>
% for d in data:
    <tr class="status${d['status']}"><td>
% if 'project' in d:
  ${d['project']}
% endif
</td><td>${d['name']}</td><td>${d['path']}</td><td>${d['size']}</td><td><button class="btn btn-primary">Delete</button></td></tr>
% endfor
</table>
</div>


<%inherit file="oauth_layout.mako"/>

<div class="row">
<div class="offset4 span4">
<div class="alert">
<strong>Application from ${referer} requests access to the following resources:</strong>
<p>${requested_scope}</p>
</div>
</div>
</div>
<div class="row">
<div class="offset4 span4">
<form action="/data-manager/oauth/v2/authorize?response_type=code&client_id=${client_id}&state=${state}&redirect_uri=${redirect_uri}&scope=${scope}" method="post">
<label for="email">Email</label>
<input name="email" type="email" value=""/>
<label for="apikey">API key</label>
<input name="apikey" value=""/>
<button>Authenticate</button>
</form>
</div>
</div>

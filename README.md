#### Python OAuth Client

A super light python command line app that walks through a provider's OAuth
based on the parameters in `config.json`

#### Set up

* pip install -r requirements.txt
* `cp config.example.json config.json`
* open config.json
* fill in provider details
* be sure to add the redirect_uri to your app's list of valid redirects
* python oauth_client.python

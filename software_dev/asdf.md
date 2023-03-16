# asdf
CLI Tool used to install & manage multiple versions of the same programming language on your machine.

asdf uses shims to re-direct applications to use different versions of the same programming languages depending on your needs.

## How to Use
1. Install asdf
2. Add startup script to your `~/.bashrc` (`echo ". $HOME/.asdf/asdf.sh" >> ~/.bashrc`)
3. Install the plugin for the programming language of choice (`asdf plugin add python`)
4. Install the version of the programming language you want (`asdf install python latest` or `asdf install python 3.9.14`)
   1. See all available versions with `asdf list all python`
5. Set your default version globally with `asdf global python latest` or locally in that specific direcotry with `asdf local python latest`

Pipenv for Python will automatically detect & use the appropriate Python version from the ones installed on your machine.
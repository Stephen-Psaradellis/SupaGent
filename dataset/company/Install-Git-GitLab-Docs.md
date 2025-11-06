# Install Git | GitLab Docs

Source: https://docs.gitlab.com/topics/git/how_to_install_git/

Install Git | GitLab Docs
Install Git
To contribute to GitLab projects, you must download, install, and configure the Git client on
your local machine. GitLab uses the SSH protocol to securely communicate with Git.
With SSH, you can authenticate to the GitLab remote server without entering your username
and password each time.
After you install and configure Git,
generate and add an SSH key pair
to your GitLab account.
Install and update Git
macOS
Though a version of Git is supplied by macOS, you should install the latest version of Git. A common way to
install Git is with
Homebrew
.
To install the latest version of Git on macOS with Homebrew:
If you’ve never installed Homebrew before, follow the
Homebrew installation instructions
.
In a terminal, install Git by running
brew install git
.
Verify that Git works on your local machine:
git --version
Keep Git up to date by periodically running the following command:
brew update
&&
brew upgrade git
Ubuntu Linux
Though a version of Git is supplied by Ubuntu, you should install the latest version of Git. The latest version is
available using a Personal Package Archive (PPA).
To install the latest version of Git on Ubuntu Linux with a PPA:
In a terminal, configure the required PPA, update the list of Ubuntu packages, and install
git
:
sudo apt-add-repository ppa:git-core/ppa
sudo apt-get update
sudo apt-get install git
Verify that Git works on your local machine:
git --version
Keep Git up to date by periodically running the following command:
sudo apt-get update
&&
sudo apt-get install git
Other operating systems
For information on downloading and installing Git on other operating systems, see the
official Git website
.
Configure Git
To start using Git from your local machine, you must enter your credentials
to identify yourself as the author of your work.
You can configure your Git identity locally or globally:
Locally: Use for the current project only.
Globally: Use for all current and future projects.
Local setup
Configure your Git identity locally to use it for the current project only.
The full name and email address should match the ones you use in GitLab.
In your terminal, add your full name. For example:
git config --local user.name
"Alex Smith"
Add your email address. For example:
git config --local user.email
"your_email_address@example.com"
To check the configuration, run:
git config --local --list
Global setup
Configure your Git identity globally to use it for all current and future projects on your machine.
The full name and email address should match the ones you use in GitLab.
In your terminal, add your full name. For example:
git config --global user.name
"Sidney Jones"
Add your email address. For example:
git config --global user.email
"your_email_address@example.com"
To check the configuration, run:
git config --global --list
Check Git configuration settings
To check your configured Git settings, run:
git config user.name
&&
git config user.email
Related topics
Git configuration documentation
Use SSH keys to communicate with GitLab

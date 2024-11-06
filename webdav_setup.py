import os
import subprocess

def run_command(command, description=""):
    """Run a shell command and check for errors."""
    print(f"{description}...") if description else None
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr.strip()}")
        exit(result.returncode)
    print(result.stdout.strip())

def install_apache():
    """Install Apache web server."""
    run_command("sudo apt update", "Updating package list")
    run_command("sudo apt install apache2 -y", "Installing Apache2")

def enable_webdav_modules():
    """Enable WebDAV modules in Apache."""
    run_command("sudo a2enmod dav", "Enabling dav module")
    run_command("sudo a2enmod dav_fs", "Enabling dav_fs module")

def create_webdav_directory():
    """Create WebDAV directory and set permissions."""
    run_command("sudo mkdir -p /var/www/webdav", "Creating WebDAV directory")
    run_command("sudo chown -R www-data:www-data /var/www/webdav", "Setting ownership for WebDAV directory")
    run_command("sudo chmod -R 755 /var/www/webdav", "Setting permissions for WebDAV directory")

def configure_webdav():
    """Configure WebDAV in Apache."""
    config = """
<VirtualHost *:80>
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/html

    # WebDAV Configuration
    Alias /webdav /var/www/webdav

    <Directory /var/www/webdav>
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted

        Dav On
        DirectorySlash Off
    </Directory>

    # Restrict access to WebDAV-compatible methods only
    <Location /webdav>
        # Allow only WebDAV methods
        <LimitExcept PROPFIND OPTIONS>
            Require all denied
        </LimitExcept>

        # Additional restrictions for browser user agents
        SetEnvIfNoCase User-Agent "mozilla" browser_request
        SetEnvIfNoCase User-Agent "chrome" browser_request
        SetEnvIfNoCase User-Agent "safari" browser_request
        SetEnvIfNoCase User-Agent "edge" browser_request
        SetEnvIfNoCase User-Agent "trident" browser_request
        SetEnvIfNoCase User-Agent "firefox" browser_request

        # Deny access if it's a browser
        <RequireAll>
            Require all granted
            Require not env browser_request
        </RequireAll>
    </Location>

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
"""
    with open("/tmp/000-default.conf", "w") as file:
        file.write(config)
    run_command("sudo mv /tmp/000-default.conf /etc/apache2/sites-available/000-default.conf", "Configuring Apache for WebDAV")

def restart_apache():
    """Restart Apache service to apply changes."""
    run_command("sudo systemctl restart apache2", "Restarting Apache service")

def main():
    print("Starting WebDAV setup...")
    install_apache()
    enable_webdav_modules()
    create_webdav_directory()
    configure_webdav()
    restart_apache()
    print("WebDAV setup complete. Test the setup by accessing http://<your-server-ip>/webdav/")

if __name__ == "__main__":
    main()

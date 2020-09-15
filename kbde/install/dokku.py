from . import bash_installer


class Installer(bash_installer.Installer):
    commands = [
        "rm bootstrap.sh",
        "dokku plugin:install https://github.com/dokku/dokku-postgres.git postgres",
        "dokku plugin:install https://github.com/dokku/dokku-mysql.git mysql",
        "dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git",
        "dokku plugin:install https://github.com/dokku/dokku-redis.git redis",
    ]

    dokku_version = "v0.21.4"

    def run(self):
        # Install dokku manually

        # Get the bootstrap script
        self.run_command(
            f"wget https://raw.githubusercontent.com/dokku/dokku/{self.dokku_version}/bootstrap.sh",
        )

        # Install with tag variable
        self.run_command(f"DOKKU_TAG={self.dokku_version} bash bootstrap.sh")

        super().run()

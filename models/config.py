import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

class Config:
    def __init__(self):
        self.db_url = os.getenv("DB_URL")
        self.db_password = os.getenv("DB_PASSWORD")
        self.ssl_root_cert = os.getenv("DB_SSL_ROOT_CERT")

    def validate(self):
        if not self.db_url:
            raise ValueError("Missing DB_URL in environment.")

        if "<PASSWORD-HIDDEN>" in self.db_url and not self.db_password:
            raise ValueError(
                "DB_URL still contains <PASSWORD-HIDDEN>. Set DB_PASSWORD in .env or replace the password in DB_URL."
            )

    def connection_options(self):
        options = {}
        if self.ssl_root_cert:
            options["sslrootcert"] = self.ssl_root_cert
        if self.db_password:
            options["password"] = self.db_password
        return options
from . import gcloud

import requests


class CloudRun:

    def __init__(self, project_name,
                       app_name,
                       region="us-east1",
                       env_vars={},
                       canary_env_vars={},
                       health_check_path="/",
                       health_check_status_code=200):
        self.gcloud = gcloud.Gcloud()

        self.app_name = app_name
        self.project_name = project_name

        self.region = region
        self.env_vars = env_vars
        self.canary_env_vars = canary_env_vars

        self.health_check_path = health_check_path
        self.health_check_status_code = health_check_status_code

        self.app_name_dash = self.app_name.replace("_", "-")
        self.build_tag = f"gcr.io/{self.project_name}/{self.app_name_dash}"

        # Command args

        self.build_args = ["builds", "submit"]
        self.build_kwargs = {
            "tag": self.build_tag,
            }

        self.deploy_args = ["run", "deploy"]
        self.deploy_kwargs = {
            "image": self.build_tag,
            "platform": "managed",
            "region": self.region,
            "allow-unauthenticated": "",
            }

        self.get_service_detail_args = ["run", "services", "describe"]
        self.get_service_detail_kwargs = {
            "platform": "managed",
            "region": self.region,
            }

    def build(self):
        return self.gcloud.run_raw(*self.build_args, **self.build_kwargs)

    def deploy_canary(self):
        args = self.deploy_args + [f"{self.app_name_dash}-canary"]

        env_vars = {}
        env_vars.update(self.env_vars)
        env_vars.update(self.canary_env_vars)
        env_var_string = self.get_env_var_string(env_vars)

        kwargs = {"max-instances": 1, "set-env-vars": env_var_string}
        kwargs.update(self.deploy_kwargs)

        return self.gcloud.run(*args, **kwargs)

    def check_canary(self):
        single = self.get_service_detail(f"{self.app_name_dash}-canary")
        health_check_url = single["status"]["url"]
        health_check_url = (f"{health_check_url}"
                            f"{self.health_check_path}")

        response = requests.get(health_check_url, allow_redirects=False)
        if response.status_code == self.health_check_status_code:
            return None

        raise self.HealthCheckException(f"Got {response.status_code} from health check url {health_check_url}")

    def deploy_main(self):
        args = self.deploy_args + [self.app_name_dash]
        kwargs = {"set-env-vars": self.get_env_var_string(self.env_vars)}
        kwargs.update(self.deploy_kwargs)

        return self.gcloud.run(*args, **kwargs)

    def get_service_env_vars(self, app_name=None):
        if app_name is None:
            app_name = self.app_name_dash
        
        detail = self.get_service_detail(app_name)
        containers = detail["spec"]["template"]["spec"]["containers"]

        assert len(containers), "no containers"

        env_vars = containers[0]["env"]
        return {item["name"]: item["value"] for item in env_vars}

    def get_service_detail(self, app_name):
        args = self.get_service_detail_args + [app_name]
        return self.gcloud.run(*args, **self.get_service_detail_kwargs)

    def get_env_var_string(self, var_dict):
        return ",".join([f"{key}={var_dict[key]}" for key in var_dict])

    class CloudRunException(Exception):
        pass

    class HealthCheckException(CloudRunException):
        pass

"Example to illustrate how to use XDG config"
# pylint: disable=unused-import, too-few-public-methods, too-many-statements, unused-variable

import os
from pprint import pprint

from superconf.configuration import NOT_SET, Configuration
from superconf.extra.xdg import XDGConfig
from superconf.fields import Field, FieldBool, FieldConf, FieldString
from superconf.loaders import Environment

ENV_VARS = {
    "XDG_CONFIG_DIRS": "$HOME/dir1:dir2:dir3",
    "SUP3RCONF__CONFIG__DATA_DIR": "/usr/local/data",
}

os.environ.update(ENV_VARS)


class AppConfig(Configuration):
    "Application Config example"

    debug = FieldBool(default=False)
    notify_url = FieldString()

    # root_dir = FieldString(default=NOT_SET)
    # root_dir = FieldString()
    root_dir = Field()
    # root_dir = Field(default=NOT_SET)
    # root_dir = Field(default=None)
    # module_dir = FieldString(default="~/projects/module")
    module_dir = Field()  # default="~/projects/module")
    data_dir = FieldString(default="~/projects/data")


class App(Configuration):
    "Main Application example"

    class Meta:
        "App config"
        cache = True
        app_name = "superconf-demo"
        env_prefix = "SUP3RCONF"

    # Used to fetch XDG config
    runtime = FieldConf(children_class=XDGConfig)

    # Simple Custom app config
    config = FieldConf(children_class=AppConfig)

    def check_stacks(self):
        "Check all stacks"

        print("Try contextes")
        # root_dir = self.get_root_dir()
        print(f"Root dir is: {self.root_dir}")
        print(f"Module dir is: {self.module_dir}")
        print(f"Data dir is: {self.data_dir}")

    # Create 3 top level properties
    @property
    def root_dir(self):
        "Return root dir"

        # Check explicit config first
        ret = self.config.root_dir
        if ret is NOT_SET:
            # Fallback on default XDG config
            ret = os.path.join(self.runtime.get_dir("XDG_CONFIG_HOME"), "projects")

        return ret

    @property
    def module_dir(self):
        "Return module dir"

        # Check explicit config first
        ret = self.config.module_dir
        if ret is NOT_SET:
            # Fallback on root_dir sub directory
            ret = os.path.join(self.root_dir, "modules")

        return ret

    @property
    def data_dir(self):
        "Return module dir"

        # Check explicit config first
        ret = self.config.data_dir
        if ret is NOT_SET:
            # Fallback on default XDG config
            ret = os.path.join(self.runtime.get_dir("XDG_STATE_HOME"), "data")
        return ret


def run1():
    "Main example"

    # Start app
    app = App()

    # Get runtime
    runtime = app.runtime

    # Get current the default config file path
    out = runtime.get_config_file()
    print("Main configuration file:", out)
    print("Returned value is always type of Path:", type(out))

    # Show alt config usage
    out1 = runtime.get_config_file("subconfig")
    print("Additional 'subconfig' configuration file:", out1)
    out2 = runtime.get_config_file("subconfig.yml")
    print("Additional 'subconfig.yml' configuration file:", out2)
    print("Both should be the same path:", out1 == out2)

    # Get current config files, we should have None
    out1 = runtime.read_file("XDG_CONFIG_HOME")
    out2 = runtime.read_file(
        "XDG_CONFIG_HOME", "subconfig"
    )  # We use default format then
    out3 = runtime.read_file(
        "XDG_CONFIG_HOME", "subconfig.yml"
    )  # We use explicit format
    # Because files don't exists yet, we should get none
    print("We should only have None values:", out1, out2, out3)

    # Let's imagine some data
    conf1 = {"main_conf": "my main conf"}
    conf2 = {"subconf1": "my subconf in yaml"}
    # And write them in config
    runtime.write_file("XDG_CONFIG_HOME", conf1)
    runtime.write_file("XDG_CONFIG_HOME", conf2, "subconfig")

    # Get current config files again, we should have values
    out1 = runtime.read_file("XDG_CONFIG_HOME")
    out2 = runtime.read_file("XDG_CONFIG_HOME", "subconfig")
    # Because files now exists, we should get values
    print("We should NOT have None values:", out1, out2)

    # Let's say we want to use json insteal of yaml
    f1 = runtime.get_file("XDG_CONFIG_HOME", "subconfig")
    print("Let's store data in json instead in:", f1)

    conf3 = {"subconf1": "my subconf in json"}
    runtime.write_file("XDG_CONFIG_HOME", conf3, "subconfig.json")
    out1 = runtime.read_file("XDG_CONFIG_HOME", "subconfig.json")
    out2 = runtime.read_file("XDG_CONFIG_HOME", "subconfig.yml")
    out3 = runtime.read_file("XDG_CONFIG_HOME", "subconfig")
    print("Since we explicitely setup the format, we have:", out1, out2)

    # Check default return
    print("Default priority order", runtime.query_cfg("xdg_file_fmt"))
    print("And by default, it will return the yml because of priority order:", out3)

    # Change default format priority
    runtime.meta__xdg_file_fmt = ["json", "toml", "yml", "yaml"]
    print("Default priority order", runtime.query_cfg("xdg_file_fmt"))
    out4 = runtime.read_file("XDG_CONFIG_HOME", "subconfig")
    print(
        "And now by default, it will return the json because of new priority order:",
        out4,
    )

    # Disable file formats
    runtime.meta__xdg_file_fmt = ["json"]
    out4 = runtime.read_file("XDG_CONFIG_HOME", "subconfig")
    print(
        "And now by default, it will return the json because this is the only one left:",
        out4,
    )

    runtime.meta__xdg_file_fmt = []
    out4 = runtime.read_file("XDG_CONFIG_HOME", "subconfig")
    print("When empty, should return None:", out4)
    print(
        "Expect some common output with get_file and get_dir when no extensions are set"
    )

    # Add more file formats: TODO

    # Let's see how is it impacted by environment vars
    out4 = runtime["XDG_CONFIG_DIRS"]
    print("Should return list of overrided vars:", out4)
    print("Should return list (not a string):", isinstance(out4, list))

    # Let's see how is it impacted by environment vars
    out4 = app.config.module_dir
    print("Should return overrided value /usr/local/modules:", out4)
    out4 = app.config.root_dir
    print("Should return default value ~/projects/data:", out4)

    # How to determine what environment var is looked up
    e = Environment()
    out = e.get_env_name(runtime, "XDG_CONFIG_DIRS")
    print("So the looked up name for XDG_CONFIG_DIRS is:", out)
    out = e.get_env_name(app.config, "module_dir")
    print("So the looked up name for module_dir is:", out)


def run2():
    "Main example"

    # Start app wihtout config
    app = App()
    print("=========================")
    pprint(app.get_values())
    app.check_stacks()

    # Start app with config
    custom_conf = {
        "config": {
            "root_dir": "/tmp/new_root_dir",
        },
    }
    print("=========================")
    app = App(value=custom_conf)
    pprint(app.get_values())
    app.check_stacks()


if __name__ == "__main__":
    run1()
    run2()

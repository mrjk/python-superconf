from .common import NOT_SET, UNSET


# Store Mixins Class
# ==================


class StoreMixin:
    "StroceValue Mixinx"


class StoreValueMixin(StoreMixin):
    "StroceValue Mixinx"


class StoreContainerMixin(StoreMixin):
    "StroceValue Mixinx"


# Store Mixins
# ==================


class StoreExtra(StoreMixin):
    "Handle extra methods"

    def get_info(self):
        "Return short help"
        val = self.get_value()
        default = self.get_default()

        out = f"value={self.get_value()} [default={self.get_default()}]"
        if val == default:
            out = f"value={self.get_value()} [is default]"

        if self._help:
            out = f"{out} - {self._help}"

        return out

    def dump_keys(self, lvl=-1, mode="keys"):
        "Return a list of keys"

        out2 = {self.fname: self}

        for child in self.walk_children(mode=mode, lvl=lvl):
            out2[child.get_key("parents")] = child

        return out2

    # Helper method
    def explain(self, lvl=-1):

        mro = self.__class__.__mro__
        mro_short = [x.__name__ for x in mro]
        mro_short = ", ".join(mro_short)

        print(f"===> Tree of {self.closest_type}: {self} <===")
        print(f"  inst      => {hex(id((self)))}")
        print(f"  mro       => {mro_short}")
        print(f"  key       => {self.key}")
        print(f"  name      => {self.name}")
        print(f"  fname     => {self.fname}")
        print(f"  default   => {str(self.get_default())}")
        print(f"  value     => {str(self.get_value())}")
        print(f"  parents   => {[str(x) for x in self.get_hier(mode='full')]}")
        print(f"  children cls  => {str(self.get_children_class())}")
        print(f"  children  => {len(self._children)}")

        children = self._children
        for key, child in children.items():
            print(f"    {key:<20} => {str(child)}")

        print()

    def explain_tree(self, lvl=-1, mode="default"):

        out = {}

        if lvl != 0:
            lvl = lvl - 1
            children = self.get_children()
            if children == UNSET:
                if mode == "default":
                    # out[key] = child.get_children()# or child.get_value()
                    # out[key] = child.explain_tree(lvl=lvl, mode=mode) #or
                    out = self.get_value()
                elif mode == "struct":
                    out = self.get_info()
                    # out = {}

                # out = self.get_info()
                # out = self.get_value()
                # out = "TRUNCATED"
            else:
                for key, child in children.items():

                    if mode == "default":
                        # out[key] = child.get_children()# or child.get_value()
                        out[key] = child.explain_tree(
                            lvl=lvl, mode=mode
                        )  # or child.get_value()
                    elif mode == "struct":
                        out[str(child)] = child.explain_tree(lvl=lvl, mode=mode) or str(
                            child.get_info()
                        )
        else:
            if mode == "default":
                out = str(self.get_value())
            elif mode == "struct":
                child_count = len(self.get_children())
                # out = str(self.get_info()) # self.get_value()
                out = f"{self.get_info()} (has {child_count} childrens)"

        return out

        # while children:


class StoreValueEnvVars(StoreMixin):
    "Handle env vars"

    # Environment var management
    def get_envvar_prefix(self):

        out = getattr(self.Meta, "env_prefix", UNSET)
        if out != UNSET:
            return out

        out = getattr(self, "_env_prefix", UNSET)
        if out != UNSET:
            return out

        # out =
        for node in self.get_hier(mode="full"):
            if node == self:
                continue
            ret = node.get_envvar_prefix()
            if isinstance(ret, str):
                out = ret
                break

        if out != UNSET:
            return out

        out = node.name
        return out  # "WIP_____"
        assert False, "WIPPP"

        pass
        # self._env_var_prefix =

    def get_envvar(self, **kwargs):
        """
        Get current env.var

        Prefix from top level name key
        """

        out = self.fname
        out = out.replace(".", "__")
        out = out.upper()

        out = f"{self.get_envvar_prefix()}{out}"
        return out

    def get_envvars(self, mode="keys", lvl=-1):
        "Return a list of all children envvars"
        out = {}

        for child in self.walk_children(mode=mode, lvl=lvl):
            key_name = child.get_envvar()
            out[key_name] = child

        return out

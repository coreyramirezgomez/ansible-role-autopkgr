"""convertAutoPkgOverride.py file contents."""
import yaml
import json
import os
import re
import argparse
from plistlib import load as load_plist
from plistlib import Data
import traceback
import ast


class override_processor(object):
    """Class to format overrides."""

    REQUIRED_INPUT_KEYS = {
        "display_name": None,
        "name": None,
        "munki_repo_subdir": None,
        "catalogs": None,
        "description": None,
        "developer": None,
    }
    KNOWN_INPUT_KEYS = {
        "app_destination": None,
        "disable_code_signature_verification": None,
        "download_url": None,
        "include_prereleases": None,
        "locale": None,
        "language": None,
        "makepkginfo_pkgname": None,
        "munkitools_admin_description": None,
        "munkitools_admin_displayname": None,
        "munkitools_admin_name": None,
        "munkitools_app_description": None,
        "munkitools_app_displayname": None,
        "munkitools_app_name": None,
        "munkitools_app_usage_description": None,
        "munkitools_app_usage_displayname": None,
        "munkitools_app_usage_name": None,
        "munkitools_core_description": None,
        "munkitools_core_displayname": None,
        "munkitools_core_name": None,
        "munkitools_launchd_description": None,
        "munkitools_launchd_displayname": None,
        "munkitools_launchd_name": None,
        "munkitools_python_description": None,
        "munkitools_python_displayname": None,
        "munkitools_python_name": None,
        "munki_category": "category",
        "munki_description": "description",
        "munki_developer": "developer",
        "munki_icon": None,
        "release": None,
        "sparkle_feed_url": None,
        "blocking_applications": None,
        "category": None,
        "minimum_os_version": None,
        "maximum_os_version": None,
        "unattended_install": None,
        "unattended_uninstall": None,
        "preinstall_script": None,
        "postinstall_script": None,
        "postuninstall_script": None,
    }

    KNOWN_INPUT_KEYS.update(REQUIRED_INPUT_KEYS)

    def __init__(self, *args, **kwargs):
        """See class DOCSTRINGS."""
        self.DEBUG = kwargs['debug']
        self.OVERRIDE_FILE_LIST = []
        self.INPUT_KEY_OVERRIDES = {}

        if kwargs['file']:
            for f in kwargs['file']:
                self.OVERRIDE_FILE_LIST.append(f)
        if kwargs['path']:
            for f in os.listdir(kwargs['path']):
                self.OVERRIDE_FILE_LIST.append(os.path.join(kwargs['path'], f))
        if kwargs['input_key_overrides']:
            for v in kwargs['input_key_overrides']:
                try:
                    self.INPUT_KEY_OVERRIDES[v.split("=")[0]] = ast.literal_eval(v.split("=")[1])
                except (SyntaxError, ValueError):
                    self.INPUT_KEY_OVERRIDES[v.split("=")[0]] = v.split("=")[1]

    def generate(self, return_type='yaml'):
        """Run the main process for processing overrides and return results."""
        override_data = []
        for of in self.OVERRIDE_FILE_LIST:
            try:
                override_data.append(self.process_override(of))
            except Exception as e:
                print("WARN: Failed to process {}.\nException Message: {}".format(of, e))
                if self.DEBUG:
                    traceback.print_exc()
        if return_type == 'yaml':
            return yaml.dump(override_data)
        elif return_type == 'dict':
            return override_data
        else:
            raise Exception("ERROR: invalid return_type: {}. Must either be 'yaml' or 'dict'".format(return_type))

    def inject_input_key_overrides(self, source_dict):
        """Force the input_keys to conform to a specific value."""
        for ok in self.INPUT_KEY_OVERRIDES.keys():
            source_dict[ok] = self.INPUT_KEY_OVERRIDES[ok]
        return source_dict

    def inject_required_keys(self, source_dict):
        """Ensure certain input_keys exist before deploying."""
        for k in self.REQUIRED_INPUT_KEYS.keys():
            if k not in list(source_dict.keys()):
                if k == 'display_name':
                    source_dict['display_name'] = source_dict['name']
                elif k == 'name':
                    source_dict['name'] = source_dict['display_name'].replace(" ", "")
                elif k == 'munki_repo_subdir':
                    source_dict['munki_repo_subdir'] = source_dict['name']
                else:
                    source_dict[k] = "Undefined."
        return source_dict

    def format_input_keys(self, source_dict):
        """Cleanup the input keys to an expected format.

        Note
        ----
        2 main processes here:

        1. Cycle through all the input keys in source_dict and find keys that
        should be collapsed into a single entry. This is based on
        self.KNOWN_INPUT_KEYS. If the key has a value, it should be replaced
        with that value as the key.

        2. Cycle through all the input keys in source_dict and find keys that
        aren't defined in self.KNOWN_INPUT_KEYS and move them to a sub-dict
        entry called "extra_input_keys".
        """
        for input_key in self.KNOWN_INPUT_KEYS.keys():
            if self.KNOWN_INPUT_KEYS[input_key]:  # Skip over None value entries.
                if input_key in source_dict.keys():
                    if self.DEBUG:
                        print("DEBUG: Found input_key {} in {}".format(input_key, source_dict.keys()))
                    if self.KNOWN_INPUT_KEYS[input_key] in source_dict.keys():
                        if self.DEBUG:
                            print("DEBUG: Found duplicate input_key {} in {}".format(self.KNOWN_INPUT_KEYS[input_key], source_dict.keys()))
                        if "%{}%".format(input_key.upper()) == source_dict[self.KNOWN_INPUT_KEYS[input_key]]:
                            if self.DEBUG:
                                print("DEBUG: input_key {} has substitution value. Using duplicate input_key value {}".format(self.KNOWN_INPUT_KEYS[input_key], input_key))
                            source_dict[self.KNOWN_INPUT_KEYS[input_key]] = source_dict[input_key]
                            source_dict.pop(input_key, None)
                        elif source_dict[input_key] == source_dict[self.KNOWN_INPUT_KEYS[input_key]]:
                            source_dict.pop(input_key, None)
                        else:
                            source_dict[self.KNOWN_INPUT_KEYS[input_key]] += source_dict.pop(input_key)
                    else:
                        if self.DEBUG:
                            print("DEBUG: Using input_key {} value for input_key {}".format(input_key, self.KNOWN_INPUT_KEYS[input_key]))
                        source_dict[self.KNOWN_INPUT_KEYS[input_key]] = source_dict.pop(input_key)

        extra_input_keys = []
        for input_key in list(source_dict.keys()):
            if input_key not in self.KNOWN_INPUT_KEYS.keys():
                if self.DEBUG:
                    print("DEBUG: Storing unknown input key in extra_input_keys dict: {}".format(input_key))
                extra_input_keys.append({input_key: source_dict.pop(input_key)})
        source_dict['extra_input_keys'] = extra_input_keys

        return source_dict

    def process_override(self, filename):
        """Process the override provided to an expected format."""
        if self.DEBUG:
            print("DEBUG: Attempting process_override on {}".format(filename))
        with open(filename, 'rb') as file:
            plist_dict = load_plist(file)
        inner_dict = self.extract_input_keys(plist_dict)
        inner_dict.update(self.extract_parent_recipe_keys(plist_dict))
        inner_dict.update(self.inject_input_key_overrides(inner_dict))
        inner_dict.update(self.inject_required_keys(inner_dict))
        if self.DEBUG:
            print("DEBUG: inner_dict: {}".format(json.dumps(inner_dict, indent=4)))
        inner_dict['identifier'] = plist_dict['Identifier']
        return inner_dict

    def extract_input_keys(self, source_plist_dict):
        """Retrieve the key data from the Input array."""
        input_key_dict = {}
        if "Input" in source_plist_dict.keys():
            for key in source_plist_dict['Input']:
                if key == 'pkginfo':
                    for pkginfo_key in source_plist_dict['Input']['pkginfo']:
                        if pkginfo_key.lower() in input_key_dict.keys():
                            if not re.search("^%[A-Z]*%.*$", source_plist_dict['Input']['pkginfo'][pkginfo_key]):
                                input_key_dict[pkginfo_key.lower()] = source_plist_dict['Input']['pkginfo'][pkginfo_key]
                            elif re.search("^%[A-Z]*%.*$", input_key_dict[pkginfo_key.lower()]):
                                input_key_dict[pkginfo_key.lower()] = source_plist_dict['Input']['pkginfo'][pkginfo_key]
                        else:
                            input_key_dict[pkginfo_key.lower()] = source_plist_dict['Input']['pkginfo'][pkginfo_key]
                else:
                    input_key_dict[key.lower()] = source_plist_dict['Input'][key]
        return self.format_input_keys(input_key_dict)

    def extract_parent_recipe_keys(self, source_plist_dict):
        """Retrieve the key data from the ParentRecipe arrays."""
        parent_recipe_dict = {}
        if "ParentRecipe" in source_plist_dict.keys():
            parent_recipe_dict['parent_recipe'] = source_plist_dict['ParentRecipe']
        if "ParentRecipeTrustInfo" in source_plist_dict.keys():
            for ParentRecipeTrustInfo_key in source_plist_dict['ParentRecipeTrustInfo']:
                if ParentRecipeTrustInfo_key == "non_core_processors" or ParentRecipeTrustInfo_key == "parent_recipes":
                    t_list = []
                    for ParentRecipeTrustInfo_sub_key in source_plist_dict['ParentRecipeTrustInfo'][ParentRecipeTrustInfo_key]:
                        t_dict = {"name": ParentRecipeTrustInfo_sub_key}
                        for processor_data in source_plist_dict['ParentRecipeTrustInfo'][ParentRecipeTrustInfo_key][ParentRecipeTrustInfo_sub_key]:
                            t_dict[processor_data] = source_plist_dict['ParentRecipeTrustInfo'][ParentRecipeTrustInfo_key][ParentRecipeTrustInfo_sub_key][processor_data]
                        t_list.append(t_dict)
                    parent_recipe_dict[ParentRecipeTrustInfo_key] = t_list
        return parent_recipe_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--debug", "-d", action="store_true", help="Enable debugging output.")
    parser.add_argument("--quiet", action="store_true", help="Disable stdout.")
    parser.add_argument("--save", type=str, help="Specifiy a file to save output to.")
    parser.add_argument("--override", type=str, nargs='+', help="Define a key to override.")
    parser.add_argument("--return_type", choices=['yaml', 'dict'], help='Specifiy the output type.', default='yaml')

    sources_group = parser.add_mutually_exclusive_group(required=True)
    sources_group.add_argument("--file", type=str, nargs='+', help="Specifiy one or more filenames (absolute path) to operate on.")
    sources_group.add_argument("--path", type=str, help="Specifiy a path to files to operate on.")

    args = parser.parse_args()

    if args.debug:
        print("DEBUG: Received Args: {}".format(args))

    op = override_processor(debug=args.debug, file=args.file, path=args.path, input_key_overrides=args.override)
    results = op.generate(return_type=args.return_type)

    if not args.quiet:
        print(results)
    if args.save:
        with open(args.save, 'w+') as output:
            output.write(results)

AutoPkgr
=========

Install and configure autopkgr and munki. Run recipes and deploy packages to munki repo.

## Requirements

- macOS host
- User with sudo privileges (when installing autopkgr/munki packages)
- Access to an existing munki repo. See https://www.munki.org/munki/

## Role Variables
Most of the configure and build variables overlap.

Action handling, defaults to all.
```
autopkgr_actions:
  - "install"
  - "configure"
  - "build"
```
### Install
```
autopkgr_autopkg_install_version: "latest"
autopkgr_munki_install_version: "latest"
```
### Configure
```
autopkgr_user: "{{ ansible_user_id }}"
autopkgr_remote_base_path: "{{ ansible_user_dir }}/autopkgr-ansible"
autopkgr_munki_repo: "{{ autopkgr_remote_base_path }}/munki/repo"
autopkgr_recipe_override_dir: "{{ autopkgr_remote_base_path }}/autopkgr/overrides"
autopkgr_recipe_repos: []
autopkgr_override_files: []
autopkgr_update_trust_info: true
autopkgr_fail_recipes_without_trust: false
autopkgr_munki_configuration:
  - name: "repo_url"
    type: "string"
    value: "file://{{ autopkgr_munki_repo }}"
  - name: "editor"
    type: "string"
    value: ""
  - name: "pkginfo_extension"
    type: "string"
    value: ".plist"
  - name: "plugin"
    type: "string"
    value: ""
  - name: "default_catalog"
    type: "string"
    value: "test"
autopkgr_autopkg_configuration: {}
autopkgr_post_processors: {}
autopkgr_client_resources_name: "site_default"
```
### Build
```
autopkgr_client_resources_footers:
  - href: "category-all.html"
    title: "Software"
  - href: "updates.html"
    title: "Updates"
  - href: "categories.html"
    title: "Categories"
autopkgr_client_resources_sidebar:
  title: "Quick Links"
  category_selector: true
  links:
    - class: "link"
      href: "http://www.apple.com/osx/whats-new/"
      title: "What's new in macOS"
    - class: "link"
      target: "_blank"
      href: "http://www.apple.com"
      title: "Apple"
    - class: "link"
      target: "_blank"
      href: "http://www.google.com"
      title: "Search Google"
    - class: "link"
      target: "_blank"
      href: "http://www.bing.com"
      title: "Search Bing"
    - class: "separator"
    - class: "link"
      target: "_blank"
      href: "http://www.apple.com/support"
      title: "Apple Support"
    - class: "link"
      target: "_blank"
      href: "http://www.apple.com/support/mac"
      title: "Mac"
    - class: "link"
      target: "_blank"
      href: "http://www.apple.com/support/mac-apps"
      title: "Mac Apps"
autopkgr_client_resources_showcases:
  - target: "_blank"
    href: "http://www.apple.com"
    src_filename: "branding.png"
  - href: "detail-GoogleChrome.html"
    src_filename: "branding1.png"
  - href: "developer-GoogleChrome.html"
    src_filename: "branding2.png"
autopkgr_client_resources_files:
  - "branding.png"
  - "branding1.png"
  - "branding2.png"
```

## Example Playbook
### Install and configure munki and autopkg
```
    - hosts: macos
      roles:
        - role: coreyramirezgomez.autopkgr
          autopkgr_actions:
            - install
            - configure
          autopkgr_autopkg_install_version: "v2.2"
          autopkgr_munki_install_version: "v5.1.2"
          autopkgr_munki_repo: "/Volumes/share/munki/repo"
          autopkgr_post_processors:
            - name: "Slack"
              repo: "https://github.com/coreyramirezgomez/autopkg-recipes.git"
              enabled: true
              command: "com.github.coreyramirezgomez.autopkg-recipes.postprocessors/Slacker"
              configuration: # All of these are required in order to work.
                - name: "webhook_url"
                  type: "string"
                  value: "somereallylongurlgoeshere"
            - name: "VirusTotal"
              repo: "https://github.com/hjuutilainen/autopkg-virustotalanalyzer.git"
              command: "io.github.hjuutilainen.VirusTotalAnalyzer/VirusTotalAnalyzer"
              enabled: true
              configuration:
                - name: "VIRUSTOTAL_API_KEY"
                  type: "string"
                  value: "SECRETKEY"
                - name: "VIRUSTOTAL_ALWAYS_REPORT"
                  type: "bool"
                  value: false
                - name: "VIRUSTOTAL_AUTO_SUBMIT"
                  type: "bool"
                  value: false
                - name: "VIRUSTOTAL_AUTO_SUBMIT_MAX_SIZE"
                  type: "int"
                  value: 419430400
                - name: "VIRUSTOTAL_SLEEP_SECONDS"
                  type: "int"
                  value: 15
```
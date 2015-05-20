import os
import codecs
import json
from abc import ABCMeta, abstractmethod


class ExtensionBuilderBase(object):
    __metaclass__ = ABCMeta

    key = ''
    package_extension = ''

    DEFAULT_CONTENT_SCRIPTS_MATCHES = ['http://*/*', 'https://*/*']
    DEFAULT_XHR_PERMISSIONS = ['http://*/*', 'https://*/*']

    @abstractmethod
    def build(self, out_path):
        pass

    @abstractmethod
    def pack(self, output_path, extension_path, project_src_path, certificates_path):
        pass

    @abstractmethod
    def setup_update(self, output_path):
        pass

    @abstractmethod
    def migrate(self, src_path):
        pass

    def get_domain_from_id(self, info):
        return (''.join(filter(lambda x: (x.isalpha() or x.isdigit() or x == '-'), info.id))).lower()

    def get_package_name(self, info):
        return (''.join(filter(lambda x: x.isalpha(), info.name)) + '_' + info.version).lower()

    def get_full_package_name(self, info):
            return self.get_package_name(info) + self.package_extension

    def insert_modules(self, text, scripts):
        placeholder_sign = '<!-- MODULES_PLACEHOLDER -->'
        content = '<!-- Modules -->\n'
        for script in scripts:
            content += '<script src="' + script + '" type="text/javascript"></script>\n'
        return text.replace(placeholder_sign, content)

    def patch_background_host(self, path, modules):
        with codecs.open(path, 'r+', 'utf-8-sig') as f:
            content = f.read()
            content = self.insert_modules(content, modules)
            f.truncate(0)
            f.seek(0)
            f.write(content)

    def merge_files(self, out_path, scripts):
        encoding = 'utf-8-sig'
        content = ''
        for script in scripts:
            content += codecs.open(script, 'r', encoding).read()
        codecs.open(out_path, 'w', encoding).write(content)

    def get_locales(self, locale_names, out_path):
        for name in locale_names:
            with codecs.open(os.path.join(out_path, 'locales', ('%s.json' % name)), 'r', 'utf-8-sig') as f:
                locale = json.load(f, encoding='utf-8')
                yield  name, locale
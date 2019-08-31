'''
mirror package from source
'''
import requests
import json
import base64
import pprint
import os
import hashlib
from config import cache_root, mirror_root, http_proxy
from backports import lzma
from packaging import version

class httpClient():
    @classmethod
    def get(self, url):
        print(url)
        cache_name = base64.b64encode(url)
        content = None
        try:
            with open(cache_root+cache_name) as f:
                content = f.read()
                return content
        except:
            pass
        proxy_dict = {}
        if http_proxy != '':
            proxy_dict['http'] = 'http://' + http_proxy
        response = requests.get(url, proxies=proxy_dict)
        content = response.content
        try:
            print(cache_root+cache_name)
            with open(cache_root+cache_name, 'w') as f:
                f.write(content)
        except:
            pass
        return content


class DebSource():
    def __init__(self, source):
        # parse source url
        token = source.split(' ')
        self.is_multi_deb = False
        if len(token) >= 4:
            self.deb, self.uri, self.distribution = token[0], token[1], token[2]
            self.components = token[3:]
            self.arch = 'amd64'
        else:
            self.is_multi_deb = True
            self.deb, self.uri, self.components = token[0], token[1], [token[2]]
            self.arch = ''

    def init_index(self):
        if self.is_multi_deb:
            self.index_path = '/'.join([self.components[0]])
            url = '/'.join([self.uri, self.components[0], 'Packages.xz'])
        else:
            self.index_path = '/'.join(['dists', self.distribution,
                                        self.components[0], 'binary-'+self.arch])
            url = '/'.join([self.uri, 'dists', self.distribution,
                            self.components[0], 'binary-'+self.arch, 'Packages.xz'])
        content = httpClient.get(url)
        index_data = lzma.decompress(content)
        self.index_list = self.parse_package_file(index_data)
        self.index = {}
        for entry in self.index_list:
            if self.index.get(entry.get('Package')) is None:
                self.index[entry.get('Package')] = []
            self.index[entry.get('Package')].append(entry)
        # sort package with same name with version lastest -> oldest
        for key in self.index:
            self.index[key] = sorted(self.index[key], cmp=lambda l,r: -1 if version.parse(l.get('Version', '0.0')) >= version.parse(r.get('Version', '0.0')) else 0)

    def _clone(self, obj):
        return json.loads(json.dumps(obj))

    def parse_package_file(self, data):
        result = []
        block = {}
        for line in data.split('\n'):
            if line.strip() == '':
                result.append(self._clone(block))
                block = {}
                continue
            tokens = line.split(' ')
            key = tokens[0][:-1]
            value = ' '.join(tokens[1:])
            block[key] = value
        return result

    def get_package_info(self, package, version=None):
        if version is None:
            return self.index.get(package)[0]
        for pkg in self.index.get(package):
            if pkg['Version'] == version:
                return pkg
        return None

    def get_index_path(self):
        return self.index_path

    def find_deps(self, package):
        target = [package]
        in_deps = []
        out_deps = []
        while len(target) > 0:
            pkg_info = self.get_package_info(target[0])
            if pkg_info is not None:
                deps = [i.strip() for i in pkg_info['Depends'].split(',')]
                for dep in deps:
                    pkg_name = dep.split(' ')[0]
                    if pkg_name in source.index:
                        target.append(pkg_name)
                        in_deps.append(pkg_name)
                    else:
                        out_deps.append(pkg_name)
            target = target[1:]
        # print(out_deps)
        return set(in_deps)

    def export_index(self, packages):
        seq = ['Package', 'Version', 'Installed-Size', 'Maintainer', 'Architecture',
               'Pre-Depends', 'Suggests', 'Description', 'Homepage', 'Description-md5',
               'Tag', 'Section', 'Priority', 'Filename', 'Size', 'MD5sum', 'SHA256']
        result = ''
        for pkg in packages:
            info = self.get_package_info(pkg)
            for key in seq:
                if key in info:
                    result += key + ': ' + info[key] + '\n'
            for key in info:
                if key not in seq:
                    result += key + ': ' + info[key] + '\n'
            result += '\n'
        return result

    def export_release(self, index_full_path, index_compress_full_path):
        content = '''Origin: main
Label: main
Suite: main
Codename: main
Date: Thu, 29 Aug 2019 17:36:06 UTC
Architectures: all amd64
Acquire-By-Hash: no
Description: ppa-mirror Stable Repository
SHA256:
'''
        for index, path in enumerate([index_full_path, index_compress_full_path]):
            with open(path) as f:
                bindata = f.read()
                hash_result = hashlib.sha256(bindata).hexdigest()
                size = os.stat(path).st_size
                if index == 0:
                    content += ' ' + hash_result + \
                        ' ' + str(size) + ' Packages\n'
                else:
                    content += ' ' + hash_result + ' ' + \
                        str(size) + ' Packages.xz\n'
        return content

    def export_download_map(self, packages):
        result = {}
        for pkg in packages:
            info = self.get_package_info(pkg)
            local_path = info['Filename']
            result[local_path] = dict(
                url=self.uri + '/' + local_path, size=int(info['Size']))
        return result


def load_json_config(file_name):
    with open(file_name) as f:
        s = f.read()
        d = json.loads(s)
        return d


def update_source(source_url):
    source = DebSource(source_url)
    source.init_index()
    return source


def sync(package, source):
    # update local package with source
    # add package -> mirror url in
    deps = source.find_deps(package)
    all_pkgs = [package] + list(deps)
    index_file = source.export_index(all_pkgs)

    # save file into local
    # if you use deb http://[hostname]/ubuntu main/, then use this
    index_folder = mirror_root + '/main'
    # else you use deb http://[hostname]/ubuntu bionic main, then use this
    # index_folder = mirror_root + '/' + source.get_index_path()

    os.system('mkdir -p '+index_folder)

    index_full_path = index_folder+'/'+'Packages'
    with open(index_full_path, 'w') as f:
        f.write(index_file)

    index_compress_full_path = index_folder+'/'+'Packages.xz'

    with open(index_compress_full_path, 'w') as f:
        data = lzma.compress(index_file)
        f.write(data)

    release_full_path = index_folder + '/' + 'Release'
    with open(release_full_path, 'w') as f:
        f.write(source.export_release(
            index_full_path, index_compress_full_path))

    download_map = source.export_download_map(all_pkgs)
    for key in download_map:
        bin_full_path = mirror_root + '/' + key
        bin_folder = mirror_root + '/' + '/'.join(key.split('/')[:-1])
        print(bin_folder)
        os.system('mkdir -p ' + bin_folder)
        size = 0
        try:
            size = os.stat(bin_full_path).st_size
        except:
            pass
        if size == download_map[key]['size']:
            continue
        if http_proxy == "":
            command = 'wget '+ download_map[key]['url'] + ' -O ' + bin_full_path
        else:
            command = 'wget -e use_proxy=yes -e http_proxy=' + http_proxy + ' ' + download_map[key]['url'] + ' -O ' + bin_full_path
        print(command)
        os.system(command)


if __name__ == '__main__':
    d = load_json_config('ppa-mirror/config.json')
    source = update_source(d['repos'][1]['deb'])
    sync(d['repos'][1]['name'], source)

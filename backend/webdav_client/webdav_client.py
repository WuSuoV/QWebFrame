import os
import re
from typing import Optional, List, Dict
from xml.etree import ElementTree as ET

import requests
from requests.auth import HTTPBasicAuth


class WebDAVManager:
    def __init__(self, base_url: str, username: Optional[str] = None, password: Optional[str] = None) -> None:
        """
        初始化 WebDAVManager 类。

        :param base_url: WebDAV 服务器的基础 URL
        :param username: 用户名（可选）
        :param password: 密码（可选）
        """
        self.base_url = base_url.rstrip('/')  # 移除末尾的 '/'，防止拼接路径时重复
        self.auth = HTTPBasicAuth(username, password) if username and password else None
        self.path = self.get_path_from_url(self.base_url)

    @staticmethod
    def get_path_from_url(url: str) -> str:
        # 定义正则表达式来匹配 URL 的路径部分
        pattern = r'^(?:https?://)?(?:www\.)?[^/]+(/[^?]*)'

        # 使用 re.search 来找到路径部分
        match = re.search(pattern, url)
        if match:
            return match.group(1)
        return ""

    def is_folder(self, remote_path: str) -> bool:
        """判断是否是文件夹"""

        if remote_path.endswith('/'):
            return True
        response = requests.request('PROPFIND', f"{self.base_url}{remote_path}", auth=self.auth, headers={'Depth': '1'})

        if response.status_code == 207:
            return True

        return False

    def list_files(self, remote_path: str = '/') -> List[Dict[str, str]]:
        """
        列出远程路径下的文件和目录。

        :param remote_path: 远程路径
        :return: 服务器返回的响应文本
        """
        url = f"{self.base_url}{remote_path}"
        response = requests.request('PROPFIND', url, auth=self.auth, headers={'Depth': '1'})
        if response.status_code == 207:
            return self._parse_propfind_response(response.text)  # 返回多状态响应文本（XML 格式）
        else:
            response.raise_for_status()

    def list(self, remote_path: str) -> List[Optional[str]]:
        """显示某目录下的所有文件和文件夹，不包含自身"""
        list_files_info = self.list_files(remote_path)

        if not list_files_info:
            return []

        return [item['href'] for item in list_files_info[1:]]

    def _parse_propfind_response(self, xml_response: str) -> List[Dict[str, str]]:
        """
        解析 PROPFIND 请求的 XML 响应，并返回 JSON 格式的结构。

        :param xml_response: XML 格式的响应文本
        :return: JSON 格式的文件和目录列表
        """
        # 解析 XML
        root = ET.fromstring(xml_response)
        namespaces = {'d': 'DAV:'}  # 默认的 WebDAV 命名空间
        items: List[Dict[str, str]] = []

        for response in root.findall('.//d:response', namespaces):
            item_info: Dict[str, str] = {}

            # 获取 href 和 displayname（如果有）
            href: str = response.find('d:href', namespaces).text
            display_name_elem = response.find('.//d:displayname', namespaces)
            display_name = display_name_elem.text if display_name_elem is not None else href
            item_info['href'] = href.replace(self.path, '')
            item_info['display_name'] = display_name

            # 获取其他可能的属性
            creation_date_elem = response.find('.//d:creationdate', namespaces)
            if creation_date_elem is not None:
                item_info['creation_date'] = creation_date_elem.text

            content_length_elem = response.find('.//d:getcontentlength', namespaces)
            if content_length_elem is not None:
                item_info['content_length'] = content_length_elem.text

            last_modified_elem = response.find('.//d:getlastmodified', namespaces)
            if last_modified_elem is not None:
                item_info['last_modified'] = last_modified_elem.text

            # 将收集的信息添加到列表中
            items.append(item_info)

        # 将解析结果转换为 JSON 格式
        return items

    def upload(self, local_path: str, remote_path: str) -> None:
        """
        上传本地文件或目录到 WebDAV 服务器。

        :param local_path: 本地文件或目录路径
        :param remote_path: 远程上传路径
        """
        if os.path.isfile(local_path):
            # 如果是文件，则调用上传文件方法
            self._upload_file(local_path, remote_path)

        elif os.path.isdir(local_path):
            # 如果是目录，递归上传目录中的文件和子目录
            self._create_directory(remote_path)

            for root, _, files in os.walk(local_path):
                relative_path = os.path.relpath(root, local_path)
                remote_subdir = os.path.join(remote_path, relative_path).replace("\\", "/")
                if not remote_subdir.endswith('/'):
                    remote_subdir += '/'
                self._create_directory(remote_subdir)

                for file in files:
                    local_file_path = os.path.join(root, file)
                    remote_file_path = os.path.join(remote_subdir, file).replace("\\", "/")
                    self._upload_file(local_file_path, remote_file_path)

    def _upload_file(self, local_path: str, remote_path: str) -> None:
        """
        上传单个文件到 WebDAV 服务器。

        :param local_path: 本地文件路径
        :param remote_path: 远程上传路径
        """
        url = f"{self.base_url}{remote_path}"
        with open(local_path, 'rb') as file_data:
            response = requests.put(url, data=file_data, auth=self.auth)
        if response.status_code in (200, 201, 204):
            print(f"文件 '{local_path}' 上传到 '{remote_path}' 成功。")
        else:
            response.raise_for_status()

    def _create_directory(self, remote_path: str) -> None:
        """
        在 WebDAV 服务器上创建目录。

        :param remote_path: 远程目录路径
        """
        url = f"{self.base_url}{remote_path}"
        response = requests.request('MKCOL', url, auth=self.auth)
        if response.status_code not in (201, 405):  # 201表示创建成功，405表示目录已存在
            response.raise_for_status()

    def download_file(self, remote_path: str, local_path: str) -> None:
        """
        从 WebDAV 服务器下载文件。

        :param remote_path: 远程文件路径
        :param local_path: 本地存储路径
        """
        url = f"{self.base_url}{remote_path}"
        response = requests.get(url, auth=self.auth)
        if response.status_code == 200:
            with open(local_path, 'wb') as file_data:
                file_data.write(response.content)
            print(f"文件 '{remote_path}' 下载到本地 '{local_path}' 成功。")
        else:
            response.raise_for_status()

    def delete(self, remote_path: str) -> None:
        """
        删除远程路径下的文件或目录。

        :param remote_path: 远程路径
        """
        url = f"{self.base_url}{remote_path}"
        response = requests.request('PROPFIND', url, auth=self.auth, headers={'Depth': '1'})
        if response.status_code == 207:
            # 解析返回内容并递归删除子内容（简单处理未解析 XML）
            sub_entries = [item['href'] for item in self.list_files(remote_path)[1:]]
            for entry in sub_entries:
                entry_path = f"{entry}".replace("//", "/")
                self.delete(entry_path)

        # 删除文件或空目录
        response = requests.delete(url, auth=self.auth)
        if response.status_code in (200, 204):
            print(f"'{remote_path}' 删除成功。")
        else:
            response.raise_for_status()

    def clean_folder(self, remote_path: str) -> None:
        """
        清空远程路径下的所有文件。
        """
        # 判断是否是文件夹
        if not self.is_folder(remote_path):
            print('清空失败！目标不是文件夹。')
            return None

        for item in self.list(remote_path):
            self.delete(item)

        print('清空完成！')

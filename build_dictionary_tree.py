import os
from yaml import load as yaml_load, dump as yaml_dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class Node:
    def __init__(self):
        pass


class DictionaryTreeBuilder:
    def __init__(self, root_dir='docs'):
        self.root_dir = root_dir  # 根路径名称
        self.root_node = dict()  # 使用dict来作为节点
        self.build()
        self.yaml_nav = yaml_dump(self.root_node, default_flow_style=False)

    def build(self):
        """
        构造一棵树
        :return:
        """
        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            """dirpath is a string, the path to the directory.  dirnames is a list of
            the names of the subdirectories in dirpath (excluding '.' and '..').
            filenames is a list of the names of the non-directory files in dirpath.
            Note that the names in the lists are just names, with no path components.
            To get a full path (which begins with top) to a file or directory in
            dirpath, do os.path.join(dirpath, name)."""
            if dirpath == self.root_dir:
                self.add_descend_node(self.root_node, '', dirnames, filenames)
            else:
                # 非第一级
                sub_dir_pathes = self.split_path(dirpath)
                current_node = self.root_node
                path = os.path.join(*sub_dir_pathes[1:])
                for sub_dir_path in sub_dir_pathes[1:]:
                    """沿着路径找到所属的节点"""

                    if sub_dir_path in current_node:
                        current_node = current_node[sub_dir_path]
                    else:
                        error = '{}未添加'.format(sub_dir_path)
                        raise Exception(error)
                self.add_descend_node(current_node, path, dirnames, filenames)

    def add_descend_node(self, node, dirpath, dirnames, filenames):
        """
        添加后裔节点
        :param node:
        :param dirnames:
        :param filenames:
        :return:
        """
        # 第一级
        for dirname in dirnames:
            key = self.key_name(dirname)
            node[key] = dict()  # 内节点
        for filename in filenames:
            if filename.endswith('.md'):
                key = self.key_name(filename[0:-3])
                node[key] = os.path.join(dirpath, filename)  # 叶子节点

    @staticmethod
    def key_name(dirname_or_filename):
        return '- ' + dirname_or_filename

    @staticmethod
    def split_path(path):
        path = os.path.normpath(path)
        return path.split(os.sep)


class NavBuilder:
    """
    每个目录下都有一个配置文件mkdocs.yml，根据配置文件中的内容来进行组装，最终的组装结果是一棵树，下面描述的是组装过程：
    - 如果值是一个文件，则是叶子节点
    - 如果值是一个目录，则是一个内节点，需要进行扩展
    显然这个过程是非常类似于top-down parsing的
    从root_dir开始

    {'docs': [{'Home': 'index.md'},
    {'Chapter1': 'Chapter1-Introduction'},
    {'Chapter2': 'Chapter2-A-Simple-Syntax-Directed-Translator'},
    {'Chapter3': 'Chapter3-Lexical-Analysis'},
    {'Chapter4': 'Chapter4-Syntax-Analysis'},
    {'Chapter5': 'Chapter5-Syntax-Directed-Translation'},
    {'Chapter6': 'Chapter6-Intermediate-Code-Generation'},
    {'Chapter7': 'Chapter7-Run-Time Environments'},
    {'Chapter9': 'Chapter9-Machine-Independent-Optimizations'}]}

    """
    MKDOCS_File = 'mkdocs.yml'

    def __init__(self, root_dir='docs'):
        self.root_dir = root_dir  # 根路径名称
        self.nav = dict()  # 保存结果（最终结果就是一棵树），它表示一个树节点，key作为节点的label(type hint str)，value作为节点的子节点(type hint: list of dict)

    def build(self):
        """
        首先检查当前目录下是否存在root_dir，如果不存在，则需要抛出异常
        总的来说，还是一棵树
        每个目录，使用目录名称作为key
        :return:
        """
        mkdocs_file_path = os.path.join(self.root_dir, self.MKDOCS_File)
        nav_path = self.root_dir
        self.__expand__(nav_path, mkdocs_file_path)

    def __expand__(self, nav_path, mkdocs_file_path):
        """
        采用深度优先
        :param mkdocs_file_path:
        :return:
        """
        if os.path.exists(mkdocs_file_path):
            with open(mkdocs_file_path, encoding='utf-8') as f:
                split_file_path = os.path.split(mkdocs_file_path)
                split_nav_path = os.path.split(nav_path)
                node_label = split_nav_path[-1]

                current_file_path = os.path.join(split_file_path[0:-1])
                nav = yaml_load(f, Loader=Loader)['docs']  # type hint list of dict
                self.nav[node_label] = nav
                for item in nav:  # type hint: dict
                    for k, v in item:
                        file = os.path.join(current_file_path, v)

        else:
            log = "配置文件有误，当前目录不存在'{}'"
            raise Exception(log)

    def __add_node__(self, nav_path):
        node = self.__find_parent_node__(nav_path)
        if node is None:
            self.nav = None
        else:
            pass

    def __find_parent_node__(self, nav_path):
        """
        寻找指定路径对应的节点
        :param nav_path:
        :return:
        """
        split_nav_path = os.path.split(nav_path)
        node = self.nav
        nodes = [self.nav] # type hint: list of dict
        for node_label in split_nav_path:
            node = self.__find__(node_label, nodes)
            nodes = node[node_label]
        return node

    def __find__(self, node_label, nodes):
        for node in nodes:
            if node_label in node:
                return node
        return None

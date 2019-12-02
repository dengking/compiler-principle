import os


class Node:
    def __init__(self):
        pass


class DictionaryTreeBuilder:
    def __init__(self, root_dir='docs'):
        self.root_dir = root_dir  # 根路径名称
        self.root_node = dict()  # 使用dict来作为节点

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

    @staticmethod
    def add_descend_node(node, dirpath, dirnames, filenames):
        """
        添加后裔节点
        :param node:
        :param dirnames:
        :param filenames:
        :return:
        """
        # 第一级
        for dirname in dirnames:
            node[dirname] = dict()  # 内节点
        for filename in filenames:
            if filename.endswith('.md'):
                key = filename[0:-3].replace('-', ' ')
                node[key] = os.path.join(dirpath, filename)  # 叶子节点

    @staticmethod
    def split_path(path):
        path = os.path.normpath(path)
        return path.split(os.sep)

import os

import configparser


class Configuration(object):

    def __init__(self, config_file='config.ini'):
        """
        获得配置文件内容
        :param config_file: str  文件名
        """
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   config_file)
        if not os.path.exists(config_path):
            raise IOError("Config Read ENV Not Found : {0}".format(config_file))
        self.config = configparser.ConfigParser()
        self.config.read(config_path)


class GoogleImageSpiderConfig(Configuration):
    """
    服务器配置获取
    可选： SERVER_CONFIG
    """

    def __init__(self, config_file='config.ini'):
        super(GoogleImageSpiderConfig, self).__init__(config_file=config_file)

    def get_api_key(self, section="SETTINGS"):
        return self.config.get(section, 'API_KEY')

    def get_cx(self, section="SETTINGS"):
        return self.config.get(section, 'CX')

googleSettings = GoogleImageSpiderConfig()


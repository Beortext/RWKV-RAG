import os

import yaml


class Configuration:
    def __init__(self, config_file):
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file {config_file} not found")
        with open(config_file) as f:
            try:
                self.config = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                raise ValueError(f"Invalid config file {config_file}")
        self.config_file_path = config_file
        self.default_base_model_path = ''  # 默认基座模型路径
        self.default_bgem3_path = ''  # 默认bgem3路径
        self.default_rerank_path = ''  # 默认rerank路径
        self.default_state_path = '' # 默认state文件

        self.validate()

    def validate(self):
        """
        Validate Configuration File
        """
        service_list = self.config.keys()
        for key in service_list:
            if not isinstance(self.config[key], dict):
                raise ValueError(f"Invalid config for {key}")
            settings = self.config[key]

            service_module_name = settings.get("service_module")
            if not service_module_name:
                raise ValueError(f"service_module is required for {key}")
            function_name = f'_validate_{service_module_name}_config'
            if hasattr(self, function_name) and callable(getattr(self, function_name)):
                getattr(self, function_name)(key, settings)

    def _validate_llm_service_config(self,key, settings):
        base_model_file = settings.get("base_model_path", '')
        if not base_model_file:
            raise ValueError(f"base_model_path is required for llm service")
        if not os.path.exists(base_model_file):
            raise FileNotFoundError(f"base_model_path {base_model_file} not found for {key}")

        bgem3_path = settings.get("embedding_path", '')
        if not bgem3_path:
            raise ValueError(f"embedding_path is required for llm service")
        if not os.path.exists(bgem3_path):
            raise FileNotFoundError(f"embedding_path {bgem3_path} not found for {key}")
        rerank_path = settings.get("reranker_path", '')
        if not rerank_path:
            raise ValueError(f"reranker_path is required for llm service")
        if not os.path.exists(rerank_path):
            raise FileNotFoundError(f"reranker_path {rerank_path} not found for {key}")
        state_path = settings.get("state_path", '') or ''
        if not os.path.exists(state_path):
            raise FileNotFoundError(f"state_path {state_path} not found for {key}")
        self.default_base_model_path = base_model_file
        self.default_bgem3_path = bgem3_path
        self.default_rerank_path = rerank_path
        self.default_state_path = state_path

    @staticmethod
    def _validate_index_service_config(key, settings):
        if not settings.get("enabled", False):
            settings['enabled'] = True
        chroma_path = settings.get("chroma_path", '')
        if not chroma_path:
            raise ValueError(f"chroma_path is required for index service")
        if not os.path.exists(chroma_path):
            raise NotADirectoryError(f"chroma_path {chroma_path} not found for {key}")
        chroma_host = settings.get("chroma_host", '')
        if not chroma_host:
            raise ValueError(f"chroma_host is required for index service")

        chroma_port = settings.get("chroma_port", '')
        if not (isinstance(chroma_port, int) or (isinstance(chroma_port, str) and chroma_port.isdigit())):
            raise ValueError(f"chroma_port is required for index service")

        sqlite_db_path = settings.get("sqlite_db_path", '')
        if not sqlite_db_path:
            raise ValueError(f"sqlite_db_path is required for index service")
        sqlite_db_path_dir = os.path.dirname(sqlite_db_path)
        if not os.path.exists(sqlite_db_path_dir):
            raise NotADirectoryError(f"sqlite_db_path {sqlite_db_path_dir} not found for {key}")

    def set_llm_service_config(self, base_model_path=None, embedding_path=None, reranker_path=None, state_path=None):
        is_save = False
        if base_model_path and base_model_path != self.default_base_model_path:
            self.default_base_model_path = base_model_path
            self.config['llm']['base_model_path'] = base_model_path
            is_save = True
        if embedding_path and embedding_path != self.default_bgem3_path:
            self.default_bgem3_path = embedding_path
            self.config['llm']['embedding_path'] = embedding_path
            is_save = True
        if reranker_path and reranker_path != self.default_rerank_path:
            self.default_rerank_path = reranker_path
            self.config['llm']['reranker_path'] = reranker_path
        if state_path and state_path != self.default_state_path:
            self.default_state_path = state_path
            self.config['llm']['state_path'] = state_path
            is_save = True
        if is_save:
            with open(self.config_file_path, "w") as f:
                yaml.dump(self.config, f)

config = Configuration("ragq.yml")

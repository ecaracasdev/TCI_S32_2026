from pathlib import Path

from autoconfig import ConfigMaker

from config import Config
from utils import load_config, update_config


def test_config_definition_generates_without_runtime_metadata(tmp_path: Path):
    path = ConfigMaker(Config, tmp_path).generate()
    text = path.read_text(encoding="utf-8")

    assert "[server]" in text
    assert "[database]" in text
    assert "\nNAME =" not in text
    assert "\nCONFIG_FILE =" not in text


def test_existing_template_loads_through_autoconfig():
    config = load_config("default", reload=True)

    assert isinstance(config, Config)
    assert config.server.PORT == 8300
    assert config.NAME == "config"
    assert config.CONFIG_FILE.name == "config.toml"


def test_runtime_overrides_keep_nested_models():
    config = load_config("default", reload=True)
    updated = update_config({"server": {"PORT": 9999}})

    assert updated.server.PORT == 9999
    assert updated.database.DB_NAME == config.database.DB_NAME

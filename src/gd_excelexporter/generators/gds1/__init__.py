import glob
import os
import logging
import jinja2
import pkg_resources

from gd_excelexporter.core.generator import Generator, Table
from gd_excelexporter.config import Configuration
from gd_excelexporter.core.models import Variant
from gd_excelexporter.type_defines import Function

# jinja2 docs: http://doc.yonyoucloud.com/doc/jinja2-docs-cn/templates.html#id2

logger = logging.getLogger(__name__)


def converter(var: Variant):
    type_define = var.type_define
    if isinstance(var.value, str):
        value = var.value.replace("\n", "\\n")
        return f"'{value}'"
    if isinstance(type_define, Function):
        func_name = f"{var.type_define.type_name}_{var.field_name}_{var.id}"
        return f"funcref(self,'{func_name}')"
    return var.value


class GDS1Generator(Generator):
    # 导出格式
    __extension__ = "gd"

    loader = jinja2.FileSystemLoader(
        pkg_resources.resource_filename(__package__, "")  # type: ignore
    )
    env = jinja2.Environment(autoescape=False, loader=loader)
    env.filters["cvt"] = converter

    @classmethod
    def generate(cls, table: Table, config: Configuration):
        # 表格数据脚本模板
        template = cls.env.get_template("data_template.gd")
        code = template.render(table=table)
        return code

    @classmethod
    def completed_hook(cls, config: Configuration):
        output = config.output
        settings_file_path = os.path.join(output, "settings.gd")
        project_root = config.project_root

        lines = []

        for path in glob.glob(f"{output}/**/*.{cls.__extension__}", recursive=True):
            if path == settings_file_path:
                continue  # 跳过 settings.gd
            basename = os.path.basename(path)
            setting_name = os.path.splitext(basename)[0]
            relpath = os.path.relpath(path, project_root).replace("\\", "/")
            lines.append(f"var {setting_name} = load('res://{relpath}').new()")

        template = cls.env.get_template("setting_template.gd")
        code = template.render(lines=lines)

        with open(settings_file_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(code)
            logger.info(f"创建：{settings_file_path}")

import unittest
import os
from excelexporter.config import Configuration
from excelexporter.engine import Engine


class TestEngine(unittest.TestCase):

    def test_excel_to_dict(self):

        engine = Engine(Configuration())
        data = engine._excel2dict(
            r"test\Setting\data\示例.xlsx"
        )
        print(data)

    def test_discover_generators(self):
        engine = Engine(Configuration())
        generators = engine.discover_generator()
        self.assertTrue(generators["GDS2.0"])

    def test_gen(self):
        os.chdir(r"test\Setting")
        config = Configuration.load()
        engine = Engine(config)
        engine.gen_one(r"data\示例.xlsx")

        self.assertTrue(
            os.path.exists("dist/示例/demo.gd")
        )

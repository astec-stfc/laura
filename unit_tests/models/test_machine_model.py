from laura.models.base_models import Aliases
from laura.models.element_list import (
    ElementList,
    MachineLayout,
    MachineModel,
    BaseElement,
)
from laura.models.element import PhysicalBaseElement, Element
import unittest


class TestMachineModel(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.elements = {
            "elem1": {
                "name": "MAG-01",
                "hardware_class": "Magnet",
                "hardware_type": "Quadrupole",
                "machine_area": "AREA-01",
                "alias": ["elem1"],
            },
            "elem2": {
                "name": "BPM-01",
                "hardware_class": "Monitor",
                "hardware_type": "BPM",
                "machine_area": "AREA-01",
                "alias": ["elem2", "bpm1"],
            },
            "elem3": {
                "name": "CAV-01",
                "hardware_class": "RF",
                "hardware_type": "Cavity",
                "machine_area": "AREA-02",
                "alias": ["elem3", "cav1"],
            },
        }
        return super().setUp()

    def test_empty_machine_model(self):
        with self.assertWarns(Warning):
            mm = MachineModel()
        self.assertEqual(mm.elements, {})
        self.assertEqual(mm.sections, {})
        self.assertEqual(mm.lattices, {})

    def test_add_element_after_init(self):
        with self.assertWarns(Warning):
            mm = MachineModel()
        self.assertEqual(mm.elements, {})
        self.assertEqual(mm.sections, {})
        self.assertEqual(mm.lattices, {})
        mm.append({name: Element(**info) for name, info in self.elements.items()})
        self.assertListEqual(
            sorted(list(mm.sections.keys())),
            ["AREA-01", "AREA-02"],
        )
        for name, info in self.elements.items():
            with self.subTest(name=name):
                self.assertIn(name, mm.elements)
                self.assertIsInstance(mm.elements[name], BaseElement)
                self.assertEqual(
                    mm.elements[name].name,
                    info["name"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_class,
                    info["hardware_class"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_type,
                    info["hardware_type"],
                )
                self.assertEqual(
                    mm.elements[name].machine_area,
                    info["machine_area"],
                )
                self.assertEqual(
                    mm.elements[name].alias,
                    info["alias"],
                )
        for name, section in mm.sections.items():
            with self.subTest(name=name):
                self.assertIn(name, ["AREA-01", "AREA-02"])
                self.assertIsInstance(section.elements, ElementList)
                if name == "AREA-01":
                    self.assertListEqual(
                        section.names,
                        [
                            "MAG-01",
                            "BPM-01",
                        ],
                    )
                elif name == "AREA-02":
                    self.assertListEqual(section.names, ["CAV-01"])

    def test_machine_model_with_dict_elements_only(self):
        with self.assertWarns(Warning):
            mm = MachineModel(
                elements=self.elements,
            )
        self.assertListEqual(
            sorted(list(mm.sections.keys())),
            ["AREA-01", "AREA-02"],
        )
        for name, info in self.elements.items():
            with self.subTest(name=name):
                self.assertIn(name, mm.elements)
                self.assertIsInstance(mm.elements[name], BaseElement)
                self.assertEqual(
                    mm.elements[name].name,
                    info["name"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_class,
                    info["hardware_class"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_type,
                    info["hardware_type"],
                )
                self.assertEqual(
                    mm.elements[name].machine_area,
                    info["machine_area"],
                )
                self.assertEqual(
                    mm.elements[name].alias,
                    info["alias"],
                )
        for name, section in mm.sections.items():
            with self.subTest(name=name):
                self.assertIn(name, ["AREA-01", "AREA-02"])
                self.assertIsInstance(section.elements, ElementList)
                if name == "AREA-01":
                    self.assertListEqual(
                        section.names,
                        [
                            "MAG-01",
                            "BPM-01",
                        ],
                    )
                elif name == "AREA-02":
                    self.assertListEqual(section.names, ["CAV-01"])

    def test_machine_model_with_elements_only(self):
        with self.assertWarns(Warning):
            mm = MachineModel(
                elements={
                    name: Element(**info) for name, info in self.elements.items()
                },
            )
        self.assertListEqual(
            sorted(list(mm.sections.keys())),
            ["AREA-01", "AREA-02"],
        )
        for name, info in self.elements.items():
            with self.subTest(name=name):
                self.assertIn(name, mm.elements)
                self.assertIsInstance(mm.elements[name], BaseElement)
                self.assertEqual(
                    mm.elements[name].name,
                    info["name"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_class,
                    info["hardware_class"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_type,
                    info["hardware_type"],
                )
                self.assertEqual(
                    mm.elements[name].machine_area,
                    info["machine_area"],
                )
                self.assertEqual(
                    mm.elements[name].alias,
                    info["alias"],
                )
        for name, section in mm.sections.items():
            with self.subTest(name=name):
                self.assertIn(name, ["AREA-01", "AREA-02"])
                self.assertIsInstance(section.elements, ElementList)
                if name == "AREA-01":
                    self.assertListEqual(
                        section.names,
                        [
                            "MAG-01",
                            "BPM-01",
                        ],
                    )
                elif name == "AREA-02":
                    self.assertListEqual(section.names, ["CAV-01"])

    def test_machine_model_with_elements_and_areas(self):
        sections = {
            "sections": {
                "AREA-01": ["MAG-01", "BPM-01"],
                "AREA-02": ["CAV-01"],
            }
        }
        with self.assertWarns(Warning):
            mm = MachineModel(
                elements={
                    name: Element(**info) for name, info in self.elements.items()
                },
                section=sections,
            )
        self.assertListEqual(
            list(mm.sections.keys()),
            ["AREA-01", "AREA-02"],
        )
        for name, info in self.elements.items():
            with self.subTest(name=name):
                self.assertIn(name, mm.elements)
                self.assertIsInstance(mm.elements[name], BaseElement)
                self.assertEqual(
                    mm.elements[name].name,
                    info["name"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_class,
                    info["hardware_class"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_type,
                    info["hardware_type"],
                )
                self.assertEqual(
                    mm.elements[name].machine_area,
                    info["machine_area"],
                )
                self.assertEqual(
                    mm.elements[name].alias,
                    info["alias"],
                )
        for name, section in mm.sections.items():
            with self.subTest(name=name):
                self.assertIn(name, ["AREA-01", "AREA-02"])
                self.assertIsInstance(section.elements, ElementList)
                if name == "AREA-01":
                    self.assertListEqual(
                        section.names,
                        [
                            "MAG-01",
                            "BPM-01",
                        ],
                    )
                elif name == "AREA-02":
                    self.assertListEqual(section.names, ["CAV-01"])
        self.assertDictEqual(mm.lattices, {})

    def test_machine_model_with_elements_areas_and_layout(self):
        sections = {
            "sections": {
                "AREA-01": ["MAG-01", "BPM-01"],
                "AREA-02": ["CAV-01"],
            }
        }
        layout = {
            "layouts": {
                "line1": ["AREA-01", "AREA-02"],
            }
        }
        mm = MachineModel(
            elements={
                name: PhysicalBaseElement(**info)
                for name, info in self.elements.items()
            },
            section=sections,
            layout=layout,
        )
        self.assertListEqual(
            list(mm.sections.keys()),
            ["AREA-01", "AREA-02"],
        )
        for name, info in self.elements.items():
            with self.subTest(name=name):
                self.assertIn(name, mm.elements)
                self.assertIsInstance(mm.elements[name], BaseElement)
                self.assertEqual(
                    mm.elements[name].name,
                    info["name"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_class,
                    info["hardware_class"],
                )
                self.assertEqual(
                    mm.elements[name].hardware_type,
                    info["hardware_type"],
                )
                self.assertEqual(
                    mm.elements[name].machine_area,
                    info["machine_area"],
                )
                self.assertEqual(
                    mm.elements[name].alias,
                    info["alias"],
                )
        for name, section in mm.sections.items():
            with self.subTest(name=name):
                self.assertIn(name, ["AREA-01", "AREA-02"])
                self.assertIsInstance(section.elements, ElementList)
                if name == "AREA-01":
                    self.assertListEqual(
                        section.names,
                        [
                            "MAG-01",
                            "BPM-01",
                        ],
                    )
                elif name == "AREA-02":
                    self.assertListEqual(section.names, ["CAV-01"])
        self.assertNotEqual(mm.lattices, {})
        self.assertIsInstance(mm.lattices["line1"], MachineLayout)
        self.assertListEqual(list(mm.lattices.keys()), ["line1"])
        self.assertListEqual(
            mm.lattices["line1"].elements,
            ["MAG-01", "BPM-01", "CAV-01"],
        )
        self.assertListEqual(
            list(mm.lattices["line1"].sections.keys()),
            ["AREA-01", "AREA-02"],
        )

    def test_machine_model_with_inline_typed_sections(self):
        sections = {
            "sections": {
                "AREA-01": {
                    "type": "beam",
                    "elements": ["MAG-01", "BPM-01"],
                },
                "AREA-02": {
                    "type": "rf",
                    "elements": ["CAV-01"],
                },
            }
        }
        layout = {
            "layouts": {
                "line1": ["AREA-01", "AREA-02"],
            }
        }
        mm = MachineModel(
            elements={
                name: PhysicalBaseElement(**info)
                for name, info in self.elements.items()
            },
            section=sections,
            layout=layout,
        )
        self.assertEqual(mm.sections["AREA-01"].section_type, "beam")
        self.assertEqual(mm.sections["AREA-02"].section_type, "rf")

    def test_machine_model_with_layout_metadata_types(self):
        sections = {
            "sections": {
                "AREA-01": ["MAG-01", "BPM-01"],
                "AREA-02": ["CAV-01"],
            }
        }
        layout = {
            "layouts": {
                "line1": ["AREA-01", "AREA-02"],
                "line2": ["AREA-02"],
            },
            "layout_metadata": {
                "line1": {"type": "beam"},
                "line2": {"type": "rf"},
            },
        }
        mm = MachineModel(
            elements={
                name: PhysicalBaseElement(**info)
                for name, info in self.elements.items()
            },
            section=sections,
            layout=layout,
        )
        self.assertEqual(mm.lattices["line1"].layout_type, "beam")
        self.assertEqual(mm.lattices["line2"].layout_type, "rf")

    def test_get_sections_by_type(self):
        sections = {
            "sections": {
                "AREA-01": {
                    "type": "beam",
                    "elements": ["MAG-01", "BPM-01"],
                },
                "AREA-02": {
                    "type": "rf",
                    "elements": ["CAV-01"],
                },
            }
        }
        layout = {
            "layouts": {
                "line1": ["AREA-01", "AREA-02"],
            }
        }
        mm = MachineModel(
            elements={
                name: PhysicalBaseElement(**info)
                for name, info in self.elements.items()
            },
            section=sections,
            layout=layout,
        )
        beam_sections = mm.get_sections_by_type("beam")
        self.assertListEqual(list(beam_sections.keys()), ["AREA-01"])

    def test_get_layouts_by_type(self):
        sections = {
            "sections": {
                "AREA-01": ["MAG-01", "BPM-01"],
                "AREA-02": ["CAV-01"],
            }
        }
        layout = {
            "layouts": {
                "line1": ["AREA-01", "AREA-02"],
                "line2": ["AREA-02"],
            },
            "layout_metadata": {
                "line1": {"type": "beam"},
                "line2": {"type": "rf"},
            },
        }
        mm = MachineModel(
            elements={
                name: PhysicalBaseElement(**info)
                for name, info in self.elements.items()
            },
            section=sections,
            layout=layout,
        )
        rf_layouts = mm.get_layouts_by_type("rf")
        self.assertListEqual(list(rf_layouts.keys()), ["line2"])

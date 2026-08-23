import json
import unittest
from pathlib import Path

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]


class RegistryMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pyproject = tomllib.loads(
            (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        )

    def test_project_metadata_is_registry_ready(self):
        project = self.pyproject["project"]

        self.assertEqual(project["name"], "flux-faceir")
        self.assertEqual(project["version"], "0.1.0")
        self.assertEqual(project["license"], {"file": "LICENSE"})
        self.assertIn("flux faceir", project["description"].lower())
        self.assertEqual(
            project["urls"]["Repository"],
            "https://github.com/cosmicrealm/ComfyUI-Flux-FaceIR",
        )
        self.assertEqual(
            project["urls"]["BugTracker"],
            "https://github.com/cosmicrealm/ComfyUI-Flux-FaceIR/issues",
        )

        requirements = {
            line.strip()
            for line in (REPO_ROOT / "requirements.txt")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        self.assertEqual(set(project["dependencies"]), requirements)

    def test_comfy_metadata_identifies_the_node(self):
        comfy = self.pyproject["tool"]["comfy"]

        self.assertEqual(comfy["PublisherId"], "cosmicrealm")
        self.assertEqual(comfy["DisplayName"], "Flux FaceIR")
        self.assertEqual(
            comfy["Repository"], "https://github.com/cosmicrealm/ComfyUI-Flux-FaceIR"
        )
        self.assertTrue(
            {"face-restoration", "flux", "reference-guided"}.issubset(comfy["Tags"])
        )

    def test_registry_package_excludes_development_artifacts(self):
        ignored = (REPO_ROOT / ".comfyignore").read_text(encoding="utf-8")

        for pattern in ("__pycache__/", "*.py[cod]", ".DS_Store", ".git/", "tests/"):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, ignored)


class RegistryAutomationTests(unittest.TestCase):
    def test_publish_workflow_uses_the_official_action(self):
        workflow = (REPO_ROOT / ".github/workflows/publish_node.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("tags:", workflow)
        self.assertIn("actions/checkout@v4", workflow)
        self.assertIn("Comfy-Org/publish-node-action@main", workflow)
        self.assertIn("secrets.REGISTRY_ACCESS_TOKEN", workflow)


class WorkflowTemplateTests(unittest.TestCase):
    def test_each_workflow_is_valid_and_has_a_thumbnail(self):
        workflow_paths = sorted((REPO_ROOT / "workflows").glob("*.json"))
        self.assertEqual(
            [path.name for path in workflow_paths],
            ["aligned_face_restore.json", "full_image_restore.json"],
        )

        for workflow_path in workflow_paths:
            with self.subTest(workflow=workflow_path.name):
                payload = json.loads(workflow_path.read_text(encoding="utf-8"))
                self.assertIsInstance(payload.get("nodes"), list)
                self.assertGreater(len(payload["nodes"]), 0)
                self.assertTrue(workflow_path.with_suffix(".jpg").is_file())


if __name__ == "__main__":
    unittest.main()

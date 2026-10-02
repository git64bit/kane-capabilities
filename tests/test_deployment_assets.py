import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class DeploymentAssetTests(unittest.TestCase):
    def read(self, relative):
        return (ROOT / relative).read_text(encoding="utf-8")

    def test_ct105_unit_carries_current_authenticated_publication_inputs(self):
        unit = self.read("deploy/civic-orchestrator.service")
        self.assertIn("--listen 127.0.0.1", unit)
        self.assertIn("--publication-base-url http://10.110.0.21:8046", unit)
        self.assertIn(
            "--publication-budget-policy /etc/civic-orchestrator/publication-budget-v1.json",
            unit,
        )
        self.assertIn(
            "LoadCredential=usermin-adapter.json:/etc/civic-orchestrator/credentials/usermin-adapter.json",
            unit,
        )
        self.assertIn(
            "LoadCredential=publication-service.json:/etc/civic-orchestrator/credentials/publication-service.json",
            unit,
        )
        self.assertIn("--publication-credential-name publication-service.json", unit)
        self.assertIn("--adapter-credential-name usermin-adapter.json", unit)

    def test_ct106_unit_is_restart_safe_and_authenticated(self):
        unit = self.read("services/publication/civic-publication.service")
        self.assertIn("--listen 192.168.1.106", unit)
        self.assertIn("--port 8046", unit)
        self.assertIn(
            "LoadCredential=publication-service.json:/etc/civic-publication/credentials/publication-service.json",
            unit,
        )
        self.assertIn("--credential-name publication-service.json", unit)

    def test_ipfs1_is_explicitly_excluded_from_kane_publication_stack(self):
        safety = self.read("docs/KANE_PRODUCTION_DEPLOYMENT_SAFETY.md")
        self.assertIn(
            "proxmox1 / CT102 / ipfs1.diagnostics.kane-il.us",
            safety,
        )
        self.assertIn("not part of this stack", safety)


if __name__ == "__main__":
    unittest.main()

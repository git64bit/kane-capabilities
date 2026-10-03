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

    def test_usermin_base_unit_remains_local_only(self):
        unit = self.read("deploy/usermin/civic-usermin-broker.service")
        self.assertIn("RestrictAddressFamilies=AF_UNIX", unit)
        self.assertNotIn("--orchestrator-base-url", unit)
        self.assertNotIn("LoadCredential=", unit)

    def test_custom_command_validation_service_is_af_unix_only(self):
        unit = self.read(
            "deploy/usermin/civic-custom-command-broker.service"
        )
        socket_unit = self.read(
            "deploy/usermin/civic-custom-command-broker.socket"
        )

        self.assertIn(
            "ListenStream=/run/civic-orchestrator/custom-command.sock",
            socket_unit,
        )
        self.assertIn("SocketGroup=civic-participants", socket_unit)
        self.assertIn("SocketMode=0660", socket_unit)
        self.assertIn("RestrictAddressFamilies=AF_UNIX", unit)
        self.assertIn(
            "/opt/civic-custom-command-broker/venv/bin/python",
            unit,
        )
        self.assertNotIn(
            "/opt/civic-usermin-broker/venv/bin/python",
            unit,
        )
        self.assertIn(
            "-m civic_orchestrator.custom_command_broker",
            unit,
        )
        self.assertIn("--command-registry", unit)
        self.assertIn("--help-catalog", unit)
        self.assertIn(
            "--access-policy /etc/civic-orchestrator/custom-command-access-v1.yaml",
            unit,
        )
        self.assertIn(
            "--access-schema /etc/civic-orchestrator/custom-command-access-v1.schema.json",
            unit,
        )
        self.assertNotIn("--orchestrator-base-url", unit)
        self.assertNotIn("--adapter-credential-name", unit)
        self.assertNotIn("LoadCredential=", unit)
        self.assertNotIn("AF_INET", unit)

    def test_custom_command_wrapper_uses_isolated_venv(self):
        wrapper = self.read("deploy/usermin/civic-custom-command")
        self.assertIn(
            "/opt/civic-custom-command-broker/venv/bin/python",
            wrapper,
        )
        self.assertNotIn(
            "/opt/civic-usermin-broker/venv/bin/python",
            wrapper,
        )
        self.assertIn(
            "-m civic_orchestrator.usermin_command",
            wrapper,
        )

    def test_custom_command_validation_service_does_not_replace_production_socket(self):
        publication_socket = self.read(
            "deploy/usermin/civic-usermin-broker.socket"
        )
        generic_socket = self.read(
            "deploy/usermin/civic-custom-command-broker.socket"
        )

        self.assertIn(
            "ListenStream=/run/civic-orchestrator/usermin.sock",
            publication_socket,
        )
        self.assertIn(
            "ListenStream=/run/civic-orchestrator/custom-command.sock",
            generic_socket,
        )
        self.assertNotEqual(publication_socket, generic_socket)

    def test_usermin_u003_overlay_is_explicit_and_credential_bound(self):
        overlay = self.read("deploy/usermin/20-orchestrator.conf.example")
        self.assertIn(
            "EnvironmentFile=/etc/civic-orchestrator/usermin-broker.env",
            overlay,
        )
        self.assertIn(
            "LoadCredential=usermin-adapter.json:/etc/civic-orchestrator/credentials/usermin-adapter.json",
            overlay,
        )
        self.assertIn("--orchestrator-base-url ${CIVIC_ORCHESTRATOR_BASE_URL}", overlay)
        self.assertIn("--adapter-credential-name usermin-adapter.json", overlay)
        self.assertIn("RestrictAddressFamilies=\n", overlay)
        self.assertIn(
            "RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6",
            overlay,
        )

    def test_usermin_u003_endpoint_is_deployment_specific(self):
        env = self.read("deploy/usermin/usermin-broker.env.example")
        self.assertIn("CIVIC_ORCHESTRATOR_BASE_URL=", env)
        self.assertIn("ORCHESTRATOR_HOST", env)


if __name__ == "__main__":
    unittest.main()

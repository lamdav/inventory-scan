from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="INVENTORY_SCAN",
    settings_files=["settings.yaml", "settings.local.yaml", ".secrets.yaml"],
)

scans_metadata = {scan.url: scan for scan in settings.get("scans", [])}

print(list(scans_metadata.keys()))

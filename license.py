LICENSE_KEYS={"DEMO-V9-LIFETIME":{"type":"lifetime","expires":None,"max_devices":1}}
def validate_license(key): return key in LICENSE_KEYS and LICENSE_KEYS[key]["type"]=="lifetime"

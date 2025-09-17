class CLIInterface:
    def __init__(self, modules, registry):
        self.modules = modules
        self.registry = registry

    def run(self):
        print("🛠️ FleetBridge CLI Online")
        print("Type 'status <worker>', 'calibrate <worker> <param> <value>', 'codes <worker>', or 'exit'.")

        while True:
            try:
                cmd = input(">> ").strip()
                if cmd == "exit":
                    print("Shutting down CLI...")
                    break

                elif cmd.startswith("status "):
                    worker_name = cmd.split(" ", 1)[1]
                    self.status(worker_name)

                elif cmd.startswith("codes "):
                    worker_name = cmd.split(" ", 1)[1]
                    self.codes(worker_name)

                elif cmd.startswith("calibrate "):
                    parts = cmd.split(" ")
                    if len(parts) == 4:
                        self.calibrate(parts[1], parts[2], parts[3])
                    else:
                        print("Usage: calibrate <worker> <param> <value>")

                else:
                    print("Unknown command.")
            except Exception as e:
                print(f"Error: {e}")

    def status(self, worker_name):
        worker = self.modules.get(worker_name)
        if worker:
            worker.report_status()
        else:
            print(f"No such worker: {worker_name}")

    def codes(self, worker_name):
        codes = self.registry.get_codes(worker_name)
        if codes:
            for code in codes:
                print(f"{code['code']}: {code['desc']}")
        else:
            print("No trouble codes logged.")

    def calibrate(self, worker_name, param, value):
        worker = self.modules.get(worker_name)
        if hasattr(worker, "calibrate"):
            worker.calibrate(param, value)
            print(f"{worker_name} calibrated: {param} = {value}")
        else:
            print(f"{worker_name} does not support calibration.")


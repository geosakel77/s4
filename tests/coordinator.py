from s4lib.libapiserver import APIServerCoordinator

if __name__ == "__main__":
    coordinator = APIServerCoordinator("COORD")
    print(coordinator.agent_uuid)

    coordinator.run()
